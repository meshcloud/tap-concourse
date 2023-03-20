"""Tests standard tap features using the built-in SDK tests library."""

import os
from multiprocessing import Process
from time import sleep

from flask import Flask
from flask import send_from_directory

from singer_sdk.testing import get_standard_tap_tests

from tap_concourse.tap import TapConcourse

SAMPLE_CONFIG = {
    "auth": {
        "bearer_token": "1234",
    },
    "base_url": "http://localhost:8000"
}

# Run standard built-in tap tests from the SDK:
def test_standard_tap_tests():
    """Run standard tap tests from the SDK."""
    tests = get_standard_tap_tests(
        TapConcourse,
        config=SAMPLE_CONFIG
    )
    
    for test in tests:
        test()
