
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, HTTPException, status
from utils.dependencies import get_current_user
from utils.authorization import get_user_permissions
import json
class PermissionMiddleware(BaseHTTPMiddleware):
    """
    Middleware to enforce endpoint-level permission checks for authenticated users.
    """

    async def dispatch(self, request: Request, call_next):
        """
        Intercepts each request to:
        - Skip permission checks for specific public endpoints (e.g., OpenAPI docs).
        - Authenticate the user and fetch their permissions.
        - Verify if the user has access to the requested endpoint.
        """
        # Skip authentication for public endpoints
        if request.url.path in ["/docs", "/openapi.json", "/user/login_user", "/user/create_user", "/core/create_tables", '/', "/health", "/core/health", "/core/drop_tables"]:
            response = await call_next(request)
            return response

        # Authenticate and get the current user
        try:
            user = await get_current_user(request)
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

        # Get user permissions and verify if the user can access the resource
        # permissions = get_user_permissions(user.role_id, request)
        # if not self.has_permission(permissions, request):
        #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

        # Proceed with the request if permission checks pass
        if request.url.path == '/organization/create_organization':
            # Read the original body as JSON
            body = await request.json()

            # Inject the user ID into the request body
            body['user_id'] = str(user.id)

            # Create a new request with the modified body
            request._body = (json.dumps(body)).encode("utf-8")

        # Proceed with the request
        response = await call_next(request)
        return response


    def has_permission(self, permissions, request: Request) -> bool:
        from fnmatch import fnmatch

        request_path = request.url.path
        request_method = request.method.upper()

        for resource in permissions:
            if fnmatch(request_path, resource.path) and request_method == resource.method.upper():
                return True
        return False
