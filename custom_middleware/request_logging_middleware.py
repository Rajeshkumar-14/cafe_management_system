import logging

logger = logging.getLogger(__name__)

class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Log the incoming request
        logger.info(f"Request Logginf Middleware : Incoming request to {request.path} from {request.META['REMOTE_ADDR']}")

        response = self.get_response(request)

        return response
