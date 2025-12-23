from rest_framework.views import exception_handler as drf_exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    response = drf_exception_handler(exc, context)

    if response is None:
        logger.error(
            f"Unhandled exception in {context['view'].__class__.__name__}: {str(exc)}",
            exc_info=True
        )
        return Response(
            {
                'error': 'Internal server error',
                'detail': str(exc) if hasattr(exc, 'args') else 'An unexpected error occurred.',
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    return response
