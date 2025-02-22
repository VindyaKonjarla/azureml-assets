# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""Entry script for Annotation Metrics Computing Spark Component."""

import argparse
import re
from pyspark.sql.functions import col, lit, sum, udf
from pyspark.sql.types import IntegerType, StructField, StructType, StringType
from shared_utilities.io_utils import (
    init_spark,
    save_spark_df_as_mltable,
    try_read_mltable_in_spark_with_error,
)

GROUP_COLUMN = "group"
GROUP_DIMENSION_COLUMN = "group_dimension"
METRIC_NAME_COLUMN = "metric_name"
METRIC_VALUE_COLUMN = "metric_value"
THRESHOLD_COLUMN = "threshold_value"

THRESHOLD_PARAMS = [
    "groundedness_passrate_threshold",
    "similarity_passrate_threshold",
    "relevance_passrate_threshold",
    "fluency_passrate_threshold",
    "coherence_passrate_threshold",
]

ALL_METRIC_NAMES = [
    "AcceptableGroundednessScorePerInstance",
    "AggregatedGroundednessPassRate",
    "AverageGroundednessScore",
    "AcceptableCoherenceScorePerInstance",
    "AggregatedCoherencePassRate",
    "AverageCoherenceScore",
    "AcceptableFluencyScorePerInstance",
    "AggregatedFluencyPassRate",
    "AverageFluencyScore",
    "AcceptableSimilarityScorePerInstance",
    "AggregatedSimilarityPassRate",
    "AverageSimilarityScore",
    "AcceptableRelevanceScorePerInstance",
    "AggregatedRelevancePassRate",
    "AverageRelevanceScore",
]


def _get_per_instance_threshold(df, metric_name):
    return df.filter(col(METRIC_NAME_COLUMN).contains(metric_name)).select(THRESHOLD_COLUMN
                                                                           ).collect()[0][THRESHOLD_COLUMN]


def _calculate_passrate(df, metric_name):
    threshold = _get_per_instance_threshold(df, metric_name)

    df_with_buckets = df.filter(
        col(METRIC_NAME_COLUMN).contains(metric_name)
    ).withColumn(
        "bucket",
        udf(lambda group: int(group), IntegerType())(
            col(GROUP_COLUMN)
        ),
    )
    passing = (
        df_with_buckets.filter(col("bucket") >= int(threshold))
        .select(sum(METRIC_VALUE_COLUMN))
        .head()[0]
    )
    total = df_with_buckets.select(sum(METRIC_VALUE_COLUMN)).head()[0]
    # if there are no metric value, we should mark as fail since there was probably a
    # parsing error or request error that resulted in no metrics
    if total == 0:
        return "NaN"
    passrate = passing / total
    return str(passrate)


def _calculate_average_metric_score(df, metric_name):
    # get the counts per scoring group
    average_metric_scores_df = df.filter(
        col(METRIC_NAME_COLUMN).contains(metric_name)).select(
            [METRIC_VALUE_COLUMN, GROUP_COLUMN]).toPandas()
    average_metric_score = 0
    sum_metric_scores = 0.0
    sum_row_count = 0.0
    for index, row in average_metric_scores_df.iterrows():
        group = float(row[GROUP_COLUMN])
        metric_value = row[METRIC_VALUE_COLUMN]
        sum_metric_scores += metric_value * group
        sum_row_count += metric_value
    if sum_row_count != 0:
        average_metric_score = sum_metric_scores / sum_row_count
    return average_metric_score


def run():
    """Run method for compute metrics."""
    # Parse argument
    parser = argparse.ArgumentParser()
    parser.add_argument("--metric_names", type=str)
    parser.add_argument("--annotation_histogram", type=str)
    parser.add_argument("--signal_metrics", type=str)

    parser.add_argument("--groundedness_passrate_threshold", type=float, default=0.7)
    parser.add_argument("--similarity_passrate_threshold", type=float, default=0.7)
    parser.add_argument("--relevance_passrate_threshold", type=float, default=0.7)
    parser.add_argument("--fluency_passrate_threshold", type=float, default=0.7)
    parser.add_argument("--coherence_passrate_threshold", type=float, default=0.7)

    args = parser.parse_args()
    histogram_df = try_read_mltable_in_spark_with_error(args.annotation_histogram, "annotation_histogram")
    threshold_args = {
        arg: getattr(args, arg) for arg in THRESHOLD_PARAMS if hasattr(args, arg)
    }
    metric_names = args.metric_names
    aggregated_metrics_df = compute_metrics(histogram_df, threshold_args, metric_names)
    save_spark_df_as_mltable(aggregated_metrics_df, args.signal_metrics)


def compute_metrics(histogram_df, threshold_args, metric_names):
    """Compute metrics for given histogram and return them."""
    spark = init_spark()
    # Cast to float because metric_value was integer so far
    # but we're adding percentages now.
    histogram_df = histogram_df.withColumn(
        METRIC_VALUE_COLUMN, histogram_df[METRIC_VALUE_COLUMN].cast("float")
    )
    # remove all but groundedness/fluency/coherence/relevance/similarity from metric names and
    # remove duplicates
    input_metric_names = [m.strip() for m in metric_names.split(",")]
    pruned_metric_names = [re.sub(r'^(.*?)(Groundedness|Fluency|Coherence|Relevance|Similarity)(.*?)$', r'\2', m) for
                           m in input_metric_names]
    compact_metric_names = list(set(pruned_metric_names))

    aggregated_metrics_df = histogram_df.withColumn(GROUP_DIMENSION_COLUMN, lit(""))

    # overwrite threshold value column
    aggregated_metrics_df = aggregated_metrics_df.withColumn(THRESHOLD_COLUMN, lit("nan").cast("float"))
    metadata_schema = StructType(
            [
                StructField(GROUP_COLUMN, StringType(), True),
                StructField(METRIC_VALUE_COLUMN, StringType(), True),
                StructField(METRIC_NAME_COLUMN, StringType(), True),
                StructField(THRESHOLD_COLUMN, StringType(), True),
                StructField(GROUP_DIMENSION_COLUMN, StringType(), True)
            ]
        )
    for metric_name in compact_metric_names:
        passrate_threshold = threshold_args[f"{metric_name.lower()}_passrate_threshold"]
        full_pass_rate_metric_name = f"Aggregated{metric_name}PassRate"
        full_per_instance_score_metric_name = f"Acceptable{metric_name}ScorePerInstance"
        average_score_metric_name = f"Average{metric_name}Score"
        if full_pass_rate_metric_name in input_metric_names:
            metric_df = spark.createDataFrame(
                    [
                        (
                            "",
                            _calculate_passrate(histogram_df, metric_name),
                            full_pass_rate_metric_name,
                            passrate_threshold,
                            ""
                        )
                    ],
                    metadata_schema,
                )
            aggregated_metrics_df = aggregated_metrics_df.union(metric_df)
        if full_per_instance_score_metric_name not in input_metric_names:
            aggregated_metrics_df = aggregated_metrics_df.filter(col(METRIC_NAME_COLUMN)
                                                                 != full_per_instance_score_metric_name)
        else:
            threshold = _get_per_instance_threshold(histogram_df, metric_name)
            threshold_row = spark.createDataFrame(
                    [
                        (
                            "",
                            "",
                            full_per_instance_score_metric_name,
                            threshold,
                            "",
                        )
                    ],
                    metadata_schema,
                )
            aggregated_metrics_df = aggregated_metrics_df.union(threshold_row)
        if average_score_metric_name in input_metric_names:
            average_metric_score = _calculate_average_metric_score(
                histogram_df, full_per_instance_score_metric_name)
            metric_df = spark.createDataFrame(
                    [
                        (
                            "",
                            average_metric_score,
                            average_score_metric_name,
                            "",
                            "",
                        )
                    ],
                    metadata_schema,
                )
            aggregated_metrics_df = aggregated_metrics_df.union(metric_df)
    return aggregated_metrics_df


if __name__ == "__main__":
    run()
