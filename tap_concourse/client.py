"""REST client handling, including MeshObjectStream base class."""

import re
import json
from pathlib import Path
from urllib.parse import parse_qsl

from singer_sdk.streams import RESTStream
from singer_sdk.authenticators import BearerTokenAuthenticator
from singer_sdk.pagination import BaseHATEOASPaginator

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
 