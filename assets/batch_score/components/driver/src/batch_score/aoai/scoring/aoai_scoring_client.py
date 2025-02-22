# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""This file contains the definition for AOAI scoring client."""

import aiohttp

from .aoai_response_handler import AoaiHttpResponseHandler
from ...common.header_providers.header_provider import HeaderProvider
from ...common.scoring.generic_scoring_client import GenericScoringClient
from ...common.scoring.scoring_request import ScoringRequest
from ...common.scoring.scoring_result import ScoringResult
from ...common.scoring.tally_failed_request_handler import TallyFailedRequestHandler


class AoaiScoringClient:
    """Defines the AOAI scoring client."""

    def __init__(
        self,
        header_provider: HeaderProvider,
        scoring_url: str = None,
        tally_handler: TallyFailedRequestHandler = None,
    ):
        """Initialize AoaiScoringClient."""
        self._generic_scoring_client = GenericScoringClient(
            header_provider=header_provider,
            http_response_handler=AoaiHttpResponseHandler(tally_handler),
            scoring_url=scoring_url,
        )

    async def score_once(
        self,
        session: aiohttp.ClientSession,
        scoring_request: ScoringRequest,
        timeout: aiohttp.ClientTimeout = None,
        worker_id: str = "1",
    ) -> ScoringResult:
        """Score a single request until terminal status is reached."""
        return await self._generic_scoring_client.score(
            session=session,
            scoring_request=scoring_request,
            timeout=timeout,
            worker_id=worker_id
        )

    def validate_auth(self):
        """Validate the auth by sending dummy request to the scoring url."""
        self._generic_scoring_client.validate_auth()
