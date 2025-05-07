# flask/event_tracker.py
from flask import current_app, request
from flask.signals import _signals, request_started, request_finished, got_request_exception

class EventTracker:
    """
    An extension to track various events in a Flask application using the Observer pattern.
    This leverages Flask's signals system to subscribe to events.
    """
    
    def __init__(self, app=None):
        self.app = app
        self._storage = []
        
        # Create our custom signal
        self.event_recorded = _signals.signal('event-recorded')
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize the extension with Flask app"""
        self.app = app
        
        # Subscribe to built-in Flask signals
        request_started.connect(self._on_request_started, app)
        request_finished.connect(self._on_request_finished, app)
        got_request_exception.connect(self._on_request_exception, app)
        
        # Register extension
        if not hasattr(app, 'extensions'):
            app.extensions = {}
        app.extensions['event_tracker'] = self
        
    def _on_request_started(self, sender, **extra):
        """Handler for request_started signal"""
        self.record_event('request_started', {
            'path': request.path,
            'method': request.method,
            'remote_addr': request.remote_addr
        })
    
    def _on_request_finished(self, sender, response, **extra):
        """Handler for request_finished signal"""
        self.record_event('request_finished', {
            'path': request.path,
            'status_code': response.status_code
        })
    
    def _on_request_exception(self, sender, exception, **extra):
        """Handler for got_request_exception signal"""
        self.record_event('request_exception', {
            'path': request.path,
            'exception': str(exception),
            'exception_type': exception.__class__.__name__
        })
    
    def record_event(self, event_type, data=None):
        """Record a custom event"""
        event = {
            'type': event_type,
            'data': data or {}
        }
        self._storage.append(event)
        
        # Notify observers that a new event was recorded
        self.event_recorded.send(self, event=event)
        
        return event
    
    def get_events(self, event_type=None):
        """Retrieve events, optionally filtered by type"""
        if event_type is None:
            return self._storage
        return [event for event in self._storage if event['type'] == event_type]
    
    def clear_events(self):
        """Clear recorded events"""
        self._storage = []