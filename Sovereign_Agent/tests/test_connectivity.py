
import pytest
from fastapi.testclient import TestClient
import sys
import os

# Fix Path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cortex import app

client = TestClient(app)

def test_health_check():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "online", "system": "Cortex V1"}

def test_unknown_command():
    response = client.post("/execute", json={"action": "flying_kick"})
    assert response.status_code == 200
    assert response.json()['status'] == "unknown_command"
