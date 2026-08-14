"""Shared pytest fixtures."""

import json
from pathlib import Path

import pytest

_FIXTURE_PATH = Path(__file__).parent / "fixtures" / "images.json"


@pytest.fixture(scope="session")
def image_records() -> list[dict]:
    """Load the recorded compartment snapshot once per test session."""
    with _FIXTURE_PATH.open() as f:
        return json.load(f)
