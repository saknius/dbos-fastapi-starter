from fastapi import FastAPI
from fastapi.security import HTTPBearer
from fastapi.openapi.utils import get_openapi
from dbos import DBOS


from services.user.routers import user_api_router
from services.core.routers import core_api_router
from services.cluster.routers import cluster_api_router
from services.deployment.routers import deployment_api_router
from services.organization.router import organization_router
from middlewares.dbsession_middleware import DBSessionMiddleware
from middlewares.permission_middleware import PermissionMiddleware

app = FastAPI(title="MLOps Platform")


# Register the middleware
app.add_middleware(PermissionMiddleware)
app.add_middleware(DBSessionMiddleware)


# Include routers
app.include_router(core_api_router)
app.include_router(user_api_router)
app.include_router(cluster_api_router)
app.include_router(deployment_api_router)
app.include_router(organization_router)

DBOS(fastapi=app)

# Security scheme
security = HTTPBearer()

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="MLOps Platform",
        version="1.0.0",
        description="API documentation for the MLOps platform",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    # Apply BearerAuth to all endpoints
    for path in openapi_schema["paths"].values():
        for method in path.values():
            method["security"] = [{"BearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
