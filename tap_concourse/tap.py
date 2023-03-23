"""meshStack tap class."""

from typing import List

from singer_sdk import Tap, Stream
from singer_sdk import typing as th  # JSON schema typing helpers

from tap_concourse.streams import (
    BuildsStream,
)

STREAM_TYPES = [
    BuildsStream
]

class TapConcourse(Tap):
    """concourse tap class."""
    name = "tap-concourse"

    config_jsonschema = th.PropertiesList(
         th.Property(
            "base_url",
            th.StringType,
            required=True,
            description="The url of the Concourse ATC (excluding the /api prefix!)"
        ),
        th.Property(
            "build_lookback_count",
            th.IntegerType,
            required=False,
            default=1000,
            description="The number of builds to look back when performing an incremental sync. Set this high enough to re-sync pending builds on the next sync run"
        ),
        th.Property(
            "build_start_id",
            th.IntegerType,
            required=False,
            description="The first build id to fetch. Set this to limit historical build data."
        ),
        th.Property(
            "auth",
            th.ObjectType(
                th.Property(
                    "bearer_token",
                    th.StringType,
                    required=True,
                    description="The HTTP bearer token"
                )
            ),
            required=True,
            description="API authentication configuration",
        ),
    ).to_dict()

    def discover_streams(self) -> List[Stream]:
        """Return a list of discovered streams."""
        return [stream_class(tap=self) for stream_class in STREAM_TYPES]

if __name__ == "__main__":
    TapConcourse.cli()