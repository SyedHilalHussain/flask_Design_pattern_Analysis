from __future__ import annotations

import typing as t
from werkzeug.routing import Map, MapAdapter, Rule
from werkzeug.exceptions import NotFound, HTTPException

if t.TYPE_CHECKING:
    from .app import Flask
    from .wrappers import Request


class VersionedMapAdapter(MapAdapter):
    """An adapter that supports versioned routing based on API version."""
    def __init__(
        self,
        map: Map,
        versions: dict[str, Map],
        default_version: str,
        version_header: str = "X-API-Version",
        version_prefix: str = "/v",
    ) -> None:
        super().__init__(map)
        self.versions = versions  # Maps version (e.g., "1", "2") to a Map object
        self.default_version = default_version
        self.version_header = version_header
        self.version_prefix = version_prefix

    def bind_to_environ(self, environ: dict, *args: t.Any, **kwargs: t.Any) -> VersionedMapAdapter:
        """Bind the adapter to the request environment and determine the version."""
        super().bind_to_environ(environ, *args, **kwargs)
        request = self._get_request(environ)
        self.version = self._determine_version(request)
        self.active_map = self.versions.get(self.version, self.map)
        return self

    def _get_request(self, environ: dict) -> Request:
        """Extract the request object from the environment."""
        from .globals import request
        return request

    def _determine_version(self, request: Request) -> str:
        """Determine the API version from the request URL or headers."""
        # Check URL prefix (e.g., /v1/resource)
        path = request.path
        if path.startswith(self.version_prefix):
            version = path[len(self.version_prefix):].split("/")[0]
            if version in self.versions:
                return version

        # Fallback to header (e.g., X-API-Version: 1)
        version = request.headers.get(self.version_header, self.default_version)
        return version if version in self.versions else self.default_version

    def match(self, path_info: str | None = None, *args: t.Any, **kwargs: t.Any) -> tuple[str, dict]:
        """Match the request against the active map for the determined version."""
        try:
            return self.active_map.match(path_info or self.path_info, *args, **kwargs)
        except HTTPException as e:
            raise
        except Exception as e:
            raise NotFound() from e


class VersionedRouter:
    """Manages versioned routing for the Flask app."""
    def __init__(self, app: Flask) -> None:
        self.app = app
        self.versions: dict[str, Map] = {}
        self.default_version = "1"

    def add_version(self, version: str, rules: list[Rule]) -> None:
        """Add a version with its routing rules."""
        self.versions[version] = Map(rules)

    def get_adapter(self) -> VersionedMapAdapter:
        """Create a VersionedMapAdapter with the configured versions."""
        return VersionedMapAdapter(
            self.app.url_map,
            self.versions,
            self.default_version
        )