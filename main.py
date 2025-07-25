from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from app.api.v1 import auth, users, chats
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="RAG Legal Backend",
    description="API backend for RAG legal document processing",
    version="1.0.0"
)

app.include_router(auth.router, prefix="/auth")
app.include_router(users.router)
app.include_router(chats.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
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
    openapi_schema["security"] = [{"BearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi 
