"""REST client handling, including MeshObjectStream base class."""


import requests
import json
from pathlib import Path

from singer_sdk.streams import RESTStream
from singer_sdk.authenticators import OAuthAuthenticator
from memoization import cached

from singer_sdk.helpers._util import utc_now

SCHEMAS_DIR = Path(__file__).parent / Path("./schemas")

class ConcourseAuthenticator(OAuthAuthenticator):
    """
    Implements the undocumented concourse API authentication flow, see
    https://github.com/concourse/concourse/issues/1122
    """

    @property
    def oauth_request_body(self) -> dict:
        return {
            'grant_type': 'password',
            'scope': 'openid profile email federated:id groups',
            'username': self.config["auth"]["basic"]["username"],
            'password': self.config["auth"]["basic"]["password"],
        }

    def update_access_token(self) -> None:
        """Update `access_token` along with: `last_refreshed` and `expires_in`.
        Raises:
            RuntimeError: When OAuth login fails.
        """
        request_time = utc_now()
        auth_request_payload = self.oauth_request_payload

        req_sessions = requests.Session() #load session instance
        req_sessions.auth = ('fly', 'Zmx5')
        
        token_response = req_sessions.post(
            self.auth_endpoint,
            data=auth_request_payload,
            timeout=60,
        )
        try:
            token_response.raise_for_status()
        except requests.HTTPError as ex:
            raise RuntimeError(
                f"Failed OAuth login, response was '{token_response.json()}'. {ex}",
            ) from ex

        self.logger.info("OAuth authorization attempt was successful.")

        token_json = token_response.json()
        self.access_token = token_json["access_token"]
        self.expires_in = token_json.get("expires_in", self._default_expiration)
        if self.expires_in is None:
            self.logger.debug(
                "No expires_in receied in OAuth response and no "
                "default_expiration set. Token will be treated as if it never "
                "expires.",
            )
        self.last_refreshed = request_time


class ConcourseStream(RESTStream):
    """Concourse stream class."""
    
    @property
    def url_base(self) -> str:
        """Return the API URL root, configurable via tap settings."""
        return self.config.get("base_url")
    
    @property
    @cached # reuse the authenticator for every request, see https://gitlab.com/meltano/sdk/-/blob/main/docs/code_samples.md#make-a-stream-reuse-the-same-authenticator-instance-for-all-requests
    def authenticator(self) -> ConcourseAuthenticator:
        """Return a new authenticator object."""
        return ConcourseAuthenticator(
            stream=self,
            auth_endpoint=self.config["base_url"] + "/sky/issuer/token"
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
 