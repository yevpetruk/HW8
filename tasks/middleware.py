import logging
import time
from django.utils.deprecation import MiddlewareMixin

# Получаем логгер для HTTP запросов
http_logger = logging.getLogger('django.request')
# Получаем логгер для нашего middleware
app_logger = logging.getLogger('tasks')


class RequestLoggingMiddleware(MiddlewareMixin):
    """
    Middleware для детального логирования HTTP запросов
    """

    def process_request(self, request):
        """Засекаем время начала обработки запроса"""
        request.start_time = time.time()
        return None

    def process_response(self, request, response):
        """Логируем информацию о запросе и ответе"""
        # Вычисляем время выполнения
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
        else:
            duration = 0

        # Логируем информацию о запросе
        log_data = {
            'method': request.method,
            'path': request.path,
            'status_code': response.status_code,
            'duration': round(duration, 4),
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            'remote_addr': request.META.get('REMOTE_ADDR', ''),
        }

        # Логируем в HTTP логгер
        http_logger.info(
            f"{request.method} {request.path} {response.status_code} {duration}s",
            extra=log_data
        )

        # Логируем в логгер приложения для дополнительной информации
        if response.status_code >= 400:
            app_logger.warning(f"HTTP Error {response.status_code}: {request.method} {request.path}")

        return response

    def process_exception(self, request, exception):
        """Логируем исключения"""
        app_logger.error(
            f"Exception in {request.method} {request.path}: {str(exception)}",
            exc_info=True
        )
        return None