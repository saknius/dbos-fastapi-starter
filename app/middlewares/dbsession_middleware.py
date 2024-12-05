import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.orm import sessionmaker
from database.session import engine
from fastapi.responses import JSONResponse
from fastapi import status
from traceback import format_exc
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
class DBSessionMiddleware(BaseHTTPMiddleware):
    """
    Middleware to manage DB sessions and transactions per request.
    """

    async def dispatch(self, request: Request, call_next):
        response = None
        try:
            start_time = time.time()
            request.state.db = SessionLocal()
            response = await call_next(request)
            if 200 <= response.status_code < 400:
                request.state.db.commit()
            else:
                request.state.db.rollback()
            process_time = (time.time() - start_time) * 1000
            logger.info(f"Request completed in {process_time:.2f} ms")
        except Exception as e:
            request.state.db.rollback()
            logger.error(f"Unhandled error: {str(e)}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"success": False, "error": str(e), "traceback": format_exc()},
            )
        finally:
            request.state.db.close()
        return response
