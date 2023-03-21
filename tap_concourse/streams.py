"""Stream type classes for tap-concourse."""

import datetime
import re
import time
from typing import cast
from urllib.parse import parse_qsl

from pathlib import Path
from pyparsing import Iterable
import requests
from tap_concourse.client import ConcourseStream
from singer_sdk.pagination import BaseHATEOASPaginator

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
    path = "/api/v1/builds"
    name = "builds"
    records_jsonpath = "$.[*]"
    primary_keys = ["id"]
    
    replication_key="id"
    
    
    def get_url_params(self, context, next_page_token):
        params = {}
        
        starting_id = self.get_starting_replication_key_value(context)
        self.logger.info("COMPUTING PARAMS from: %s starting_id: %s",  self.get_context_state(context), starting_id)

        if next_page_token:
            # we already are in the middle of sync, fetch next page
            params.update(parse_qsl(next_page_token.query))
        elif starting_id:
            # we are on the first page but have existing state
            params["from"] = starting_id
        else:
            # we are on the first page, but have no state, i.e. full refresh
            params["from"] = 58190814 # for testing
            params["limit"] = 5
            
        self.logger.info("QUERY PARAMS: %s", params)
        return params       


    def get_new_paginator(self) -> BuildStreamPaginator:
        return BuildStreamPaginator()

    def parse_response(self, response: requests.Response) -> Iterable[dict]:
        # reverse the order because meltano expects the "highest id" records to always come last in a response
        return reversed(list(super().parse_response(response)))