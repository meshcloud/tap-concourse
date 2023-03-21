"""Stream type classes for tap-concourse."""

import requests
import re

from typing import Any, Optional
from pathlib import Path
from singer_sdk import typing as th  # JSON Schema typing helpers
from singer_sdk.plugin_base import PluginBase as TapBaseClass
from tap_concourse.client import ConcourseStream

SCHEMAS_DIR = Path(__file__).parent / Path("./schemas")

class BuildsStream(ConcourseStream):
    path = "/api/v1/builds"
    name = "builds"
    records_jsonpath = "$.[*]"
    primary_keys = ["id"]

    def get_next_page_token(self, response: requests.Response, previous_token: Optional[Any]) -> Any:
        links = response.headers['link'].split(',')
        
        for x in links:
            match = re.search('<(.*)>; rel="next"', x)
            next_link = match.group(1)
            if next_link:
                return next_link

        return None