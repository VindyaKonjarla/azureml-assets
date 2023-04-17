DeBERTa is an improvement of BERT and RoBERTa using disentangled attention and enhanced mask decoder. With 80GB training data, it outperforms BERT and RoBERTa on the majority of NLU tasks. The fine-tuned DeBERTa with MNLI task results in the best performance on SQuAD 1.1/2.0 and GLUE benchmark tasks. Further information is available in the official repository and the related paper.


> The above summary was generated using ChatGPT. Review the <a href="https://huggingface.co/microsoft/deberta-large-mnli" target="_blank">original model card</a> to understand the data used to train the model, evaluation metrics, license, intended uses, limitations and bias before using the model.

### Inference samples

Inference type|Python sample (Notebook)|CLI with YAML
|--|--|--|
Real time|<a href="https://aka.ms/azureml-infer-online-sdk-text-classification" target="_blank">entailment-contradiction-online.ipynb</a>|<a href="https://aka.ms/azureml-infer-online-cli-text-classification" target="_blank">text-classification-online-endpoint.sh</a>
Batch | coming soon


### Finetuning samples

Task|Use case|Dataset|Python sample (Notebook)|CLI with YAML
|---|--|--|--|--|
Text Classification|Emotion Detection|<a href="https://huggingface.co/datasets/dair-ai/emotion" target="_blank">Emotion</a>|<a href="https://aka.ms/azureml-ft-sdk-emotion-detection" target="_blank">emotion-detection.ipynb</a>|<a href="https://aka.ms/azureml-ft-cli-emotion-detection" target="_blank">emotion-detection.sh</a>
Token Classification|Token Classification|<a href="https://huggingface.co/datasets/conll2003" target="_blank">Conll2003</a>|<a href="https://aka.ms/azureml-ft-sdk-token-classification" target="_blank">token-classification.ipynb</a>|<a href="https://aka.ms/azureml-ft-cli-token-classification" target="_blank">token-classification.sh</a>


### Model Evaluation

| Task                | Use case          | Dataset                                                   | Python sample (Notebook)                                                                        | CLI with YAML                                                                                 |
|---------------------|-------------------|-----------------------------------------------------------|-------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------|
| Text Classification | Emotion Detection | <a href="https://huggingface.co/datasets/go_emotions" target="_blank">GoEmotions</a> | <a href="https://aka.ms/azureml-eval-sdk-text-classification" target="_blank">evaluate-model-text-classification.ipynb</a> | <a href="https://aka.ms/azureml-eval-cli-text-classification" target="_blank">evaluate-model-text-classification.yml</a> |


### Sample inputs and outputs (for real-time inference)

#### Sample input
```json
{
    "inputs": {
        "input_string": ["Today was an amazing day!", "It was an unfortunate series of events."]
    }
}
```

#### Sample output
```json
[
    {
        "label": "NEUTRAL",
        "score": 0.9605958461761475
    },
    {
        "label": "NEUTRAL",
        "score": 0.98270583152771
    }
]
```