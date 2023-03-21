"""Stream type classes for tap-concourse."""

from pathlib import Path
from singer_sdk import typing as th  # JSON Schema typing helpers
from tap_concourse.client import ConcourseStream

SCHEMAS_DIR = Path(__file__).parent / Path("./schemas")

class BuildsStream(ConcourseStream):
    path = "/api/v1/builds"
    name = "builds"
    records_jsonpath = "$.[*]"
    primary_keys = ["id"]
       