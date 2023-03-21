"""REST client handling, including MeshObjectStream base class."""

import re
import json
from pathlib import Path
from urllib.parse import parse_qsl

from singer_sdk.streams import RESTStream
from singer_sdk.authenticators import BearerTokenAuthenticator
from singer_sdk.pagination import BaseHATEOASPaginator

SCHEMAS_DIR = Path(__file__).parent / Path("./schemas")

from singer_sdk.pagination import BaseHATEOASPaginator

class ConcoursePaginator(BaseHATEOASPaginator):
    def get_next_url(self, response):
        links = response.headers['link'].split(',')
        
        for x in links:
            match = re.search('<(.*)>; rel="next"', x)
            next_link = match.group(1)
            if next_link:
                return next_link

        return None



# todo: authentication via https://github.com/concourse/concourse/issues/1122
# for now just enter a full-blown bearer token retrieved via `fly lo`

class ConcourseStream(RESTStream):
    """Concourse stream class."""
    
    @property
    def url_base(self) -> str:
        """Return the API URL root, configurable via tap settings."""
        return self.config.get("base_url")
    
    @property
    def authenticator(self) -> BearerTokenAuthenticator:
        """Return a new authenticator object."""
        return BearerTokenAuthenticator.create_for_stream(
            self,
            token=self.config.get("auth").get("bearer_token")
        )
    
    def get_new_paginator(self) -> ConcoursePaginator:
        return ConcoursePaginator()

    def get_url_params(self, context, next_page_token):
        params = {}

        # Next page token is a URL, so we can to parse it to extract the query string
        if next_page_token:
            params.update(parse_qsl(next_page_token.query))

        return params

    @property
    def schema(self) -> dict:
        """Get dynamic schema including the configured tag schema

        Returns:
            JSON Schema dictionary for this stream.
        """
    
        schema_filepath = SCHEMAS_DIR / f"{self.name}.json"
        schema = json.loads(Path(schema_filepath).read_text())

        return schema
 