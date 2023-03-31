"""Stream type classes for tap-concourse."""

import re
import requests

from typing import Optional
from urllib.parse import parse_qsl
from pyparsing import Iterable
from pathlib import Path
from singer_sdk.pagination import BaseHATEOASPaginator

from tap_concourse.client import ConcourseStream

SCHEMAS_DIR = Path(__file__).parent / Path("./schemas")

class BuildStreamPaginator(BaseHATEOASPaginator):
    def get_next_url(self, response):
        links = response.headers['link'].split(',')
        
        # print("LINKS: %s", links)

        # concourse is weird in that it orders its API reversed, i.e. it starts at the "latest" build as the
        # first result by default, which is why we have to follow the "previous" link instead of "next" link
        for x in links:
            match  = re.search('<(.*)>; rel="previous"', x) 
            if match:
                next_link = match.group(1)
                if next_link:
                    return next_link

        return None


class BuildsStream(ConcourseStream):
    name = "builds"
    records_jsonpath = "$.[*]"
    primary_keys = ["id"]
    
    replication_key="id"

    @property
    def path(self):
        return f"/api/v1/teams/{self.config['team']}/builds"


    def get_url_params(self, context, next_page_token):
        params = {}
        
        starting_id = self.get_starting_replication_key_value(context)
    
        if next_page_token:
            # we already are in the middle of sync, fetch next page
            params.update(parse_qsl(next_page_token.query))
        elif starting_id:
            # we are on the first page but have existing state
            params["from"] = starting_id
            params["limit"] = 200
            
        self.logger.info("QUERY PARAMS: %s", params)
        return params       

    def get_starting_replication_key_value(
        self, context: Optional[dict]
    ) -> Optional[int]:
        """
        Builds can continue to have status updates as they are running,
        so we cannot assume that we have scraped all builds in a final state.
        This function will return the starting id minus some lookback window
        to ensure we also get some builds before the last collected build
        """
        state = self.get_context_state(context)
        replication_key_value = state.get("replication_key_value")
        
        lookback = self.config["build_lookback_count"]
        start = self.config["build_start_id"]
        
        if replication_key_value:
            return max(replication_key_value - lookback, start, 1)

        if start:
            return start
        
    
        self.logger.info("Setting first build id to 1 to perform full historical sync.")
        return 1    


    def get_new_paginator(self) -> BuildStreamPaginator:
        return BuildStreamPaginator()

    def parse_response(self, response: requests.Response) -> Iterable[dict]:
        # reverse the order because meltano expects the "highest id" records to always come last in a response
        return reversed(list(super().parse_response(response)))