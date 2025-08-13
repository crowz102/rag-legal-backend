from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from app.api.v1 import auth, users, chats, admin, documents
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="RAG Legal Backend",
    description="API backend for RAG legal document processing",
    version="1.0.0"
)

# Include routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router)
app.include_router(chats.router)
app.include_router(admin.router)
app.include_router(documents.router)

from app.api.v1 import tasks as tasks_api
app.include_router(tasks_api.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }
    for path, methods in openapi_schema["paths"].items():
        for method in methods.values():
            if path not in ["/api/v1/login", "/api/v1/register"]:
                method["security"] = [{"BearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
