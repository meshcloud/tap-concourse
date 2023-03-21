"""REST client handling, including MeshObjectStream base class."""

from typing import Any, Iterable, Optional, cast

import requests
import json
from pathlib import Path
from typing import Any, Optional, cast

from singer_sdk import typing as th  # JSON schema typing helpers
from singer_sdk.streams import RESTStream
from singer_sdk.authenticators import BearerTokenAuthenticator
from singer_sdk.plugin_base import PluginBase as TapBaseClass

SCHEMAS_DIR = Path(__file__).parent / Path("./schemas")
 

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
    
    @property
    def schema(self) -> dict:
        """Get dynamic schema including the configured tag schema

        Returns:
            JSON Schema dictionary for this stream.
        """
    
        schema_filepath = SCHEMAS_DIR / f"{self.name}.json"
        schema = json.loads(Path(schema_filepath).read_text())

        return schema

    def prepare_request(
        self, context: Optional[dict], next_page_token: Optional[Any]
    ) -> requests.PreparedRequest:
        """Prepare a request object.

        If partitioning is supported, the `context` object will contain the partition
        definitions. Pagination information can be parsed from `next_page_token` if
        `next_page_token` is not None.

        Args:
            context: Stream partition or context dictionary.
            next_page_token: Token, page number or any request argument to request the
                next page of data.

        Returns:
            Build a request with the stream's URL, path, query parameters,
            HTTP headers and authenticator.
        """
        http_method = self.rest_method
        
        # the next_page_token is be the next page link, if set use it to overwrite the URL
        url: str = next_page_token if next_page_token is not None else self.get_url(context)
        
        params: dict = self.get_url_params(context, next_page_token)
        request_data = self.prepare_request_payload(context, next_page_token)
        headers = self.http_headers

        authenticator = self.authenticator
        if authenticator:
            headers.update(authenticator.auth_headers or {})
            params.update(authenticator.auth_params or {})

        request = cast(
            requests.PreparedRequest,
            self.requests_session.prepare_request(
                requests.Request(
                    method=http_method,
                    url=url,
                    params=params,
                    headers=headers,
                    json=request_data,
                ),
            ),
        )
        return request
