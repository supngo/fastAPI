from fastapi import FastAPI
from fastapi.responses import JSONResponse

# Import routers
from app.api.v1.users import router as users_router
from app.api.v1.admin import router as admin_router
from app.api.v1.auth import router as auth_router

# Import custom exceptions
from app.core.exceptions import UnauthorizedError, ForbiddenError

# Setup logging once
from app.core.logging import setup_logging, get_logger

setup_logging()
logger = get_logger("main")

app = FastAPI(
    title="Python Backend JWT + RBAC Example",
    description="Backend with JWT authentication and role-based authorization",
    version="1.0.0",
)

# ---------------------------
# Register routers
# ---------------------------
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(admin_router)


# ---------------------------
# Global exception handlers
# ---------------------------
@app.exception_handler(UnauthorizedError)
def unauthorized_handler(request, exc: UnauthorizedError):
    return JSONResponse(
        status_code=401,
        content={"error": str(exc)},
    )


@app.exception_handler(ForbiddenError)
def forbidden_handler(request, exc: ForbiddenError):
    return JSONResponse(
        status_code=403,
        content={"error": str(exc)},
    )


# ---------------------------
# Health check endpoint
# ---------------------------
@app.get("/health")
def health_check():
    logger.info("Health check called")
    return {"status": "ok"}
