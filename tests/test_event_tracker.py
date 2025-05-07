# tests/test_event_tracker.py
import pytest
from flask import Flask, jsonify
from flask.event_tracker import EventTracker

def test_event_tracker():
    # Create a Flask app
    app = Flask(__name__)
    
    # Initialize our event tracker
    tracker = EventTracker(app)
    
    # Create a simple view
    @app.route('/hello')
    def hello():
        # Record a custom event
        tracker.record_event('custom_event', {'message': 'Hello World'})
        return 'Hello World'
    
    # Create an endpoint that raises an exception
    @app.route('/error')
    def error():
        raise ValueError("Intentional error for testing")
    
    # Create an endpoint to view events
    @app.route('/events')
    def view_events():
        return jsonify(tracker.get_events())
    
    @app.route('/events/<event_type>')
    def view_events_by_type(event_type):
        return jsonify(tracker.get_events(event_type))
    
    # Create a test client
    client = app.test_client()
    
    # Test tracking of normal requests
    response = client.get('/hello')
    assert response.status_code == 200
    assert response.data.decode() == 'Hello World'
    
    # Check if events were recorded
    events_response = client.get('/events')
    events = events_response.json
    
    # Verify request_started event
    request_started_events = [e for e in events if e['type'] == 'request_started' and e['data']['path'] == '/hello']
    assert len(request_started_events) > 0
    assert request_started_events[0]['data']['method'] == 'GET'
    
    # Verify request_finished event
    request_finished_events = [e for e in events if e['type'] == 'request_finished' and e['data']['path'] == '/hello']
    assert len(request_finished_events) > 0
    assert request_finished_events[0]['data']['status_code'] == 200
    
    # Verify custom event
    custom_events = [e for e in events if e['type'] == 'custom_event']
    assert len(custom_events) > 0
    assert custom_events[0]['data']['message'] == 'Hello World'
    
    # Test exception tracking
    response = client.get('/error')
    assert response.status_code == 500  # Should return 500 for internal server error
    
    # Check if exception was recorded
    events_response = client.get('/events/request_exception')
    exception_events = events_response.json
    
    assert len(exception_events) > 0
    assert exception_events[0]['data']['exception_type'] == 'ValueError'
    assert 'Intentional error for testing' in exception_events[0]['data']['exception']
    
    # Test event filtering
    custom_events_response = client.get('/events/custom_event')
    filtered_events = custom_events_response.json
    
    assert len(filtered_events) > 0
    assert all(event['type'] == 'custom_event' for event in filtered_events)
    
    # Test subscriber to event_recorded signal
    recorded_events = []
    
    @tracker.event_recorded.connect
    def on_event_recorded(sender, event):
        recorded_events.append(event)
    
    # Trigger a new event
    tracker.record_event('test_signal', {'value': 42})
    
    # Verify the subscriber was notified
    assert len(recorded_events) > 0
    assert recorded_events[-1]['type'] == 'test_signal'
    assert recorded_events[-1]['data']['value'] == 42

if __name__ == "__main__":
    pytest.main(["-v", "test_event_tracker.py"])