# tests/test_rate_limiter.py
import pytest
from flask import Flask

def test_rate_limit():
    app = Flask(__name__)

    @app.route('/limited')
    @app.rate_limit(requests=2, window=1)  # 2 requests per minute
    def limited():
        return "Success"

    client = app.test_client()

    # First two requests should succeed
    response1 = client.get('/limited', environ_base={'REMOTE_ADDR': '127.0.0.1'})
    assert response1.status_code == 200, f"Expected 200, got {response1.status_code}"
    assert response1.data.decode() == "Success"

    response2 = client.get('/limited', environ_base={'REMOTE_ADDR': '127.0.0.1'})
    assert response2.status_code == 200, f"Expected 200, got {response2.status_code}"
    assert response2.data.decode() == "Success"

    # Next four requests (3rd to 6th) should fail
    for i in range(3, 7):  # Requests 3, 4, 5, 6
        response = client.get('/limited', environ_base={'REMOTE_ADDR': '127.0.0.1'})
        assert response.status_code == 429, f"Request {i}: Expected 429, got {response.status_code}"
        assert "Rate limit exceeded" in response.data.decode(), f"Request {i}: Expected 'Rate limit exceeded' in response"

if __name__ == "__main__":
    pytest.main(["-v", "test_rate_limiter.py"])