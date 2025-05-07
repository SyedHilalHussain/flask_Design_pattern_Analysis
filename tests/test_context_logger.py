import pytest
import logging
import io
from flask import Flask, jsonify, current_logger
from flask.views import MethodView

def test_context_logger():
    app = Flask(__name__)
    app.secret_key = "test_secret_key"

    @app.route('/test')
    def test_route():
        current_logger.info("Test log message")
        return jsonify({"status": "ok"})

    # Capture log output
    log_stream = io.StringIO()
    handler = logging.StreamHandler(log_stream)
    handler.setFormatter(logging.Formatter("[request_id=%(request_id)s, user_id=%(user_id)s] %(levelname)s: %(message)s"))
    logging.getLogger("flask.request").addHandler(handler)

    client = app.test_client()

    # Set user_id in session
    with client.session_transaction() as sess:
        sess["user_id"] = "42"

    # Make a request
    with client:
        response = client.get('/test')
        assert response.status_code == 200

    # Check log output
    log_output = log_stream.getvalue()
    assert "[request_id=" in log_output
    assert ", user_id=42] INFO: Test log message" in log_output

if __name__ == "__main__":
    pytest.main(["-v", "test_context_logger.py"])