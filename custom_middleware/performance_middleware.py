import time
import logging

logger = logging.getLogger(__name__)

class PerformanceMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()
        response = self.get_response(request) 
        duration = time.time() - start_time

        logger.info(f"Performance Middleware : Request to {request.path} took {duration:.2f} seconds")
        logger.info(f"------------------------------------------------------------------------------")

        if duration > 1.0:
            logger.warning(f"Performance Middleware :  Slow request to {request.path} took {duration:.2f} seconds")
            logger.info(f"------------------------------------------------------------------------------")

        return response
