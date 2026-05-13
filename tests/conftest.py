import sys
import os
import pytest
from fastapi.testclient import TestClient

# Add project root to PYTHONPATH
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)

from src.main import app 

@pytest.fixture
def client():

    with TestClient(app) as test_client:
        yield test_client