from prometheus_client import Counter, Histogram, Gauge
import time


# Счетчики
REQUESTS_TOTAL = Counter(
    'phoenix_bot_requests_total', 
    'Total requests processed',
    ['method', 'endpoint']
)

ERRORS_TOTAL = Counter(
    'phoenix_bot_errors_total',
    'Total errors occurred',
    ['method', 'endpoint']
)

# Гистограммы
REQUEST_DURATION = Histogram(
    'phoenix_bot_request_duration_seconds',
    'Request duration in seconds',
    ['method', 'endpoint']
)

GAME_DURATION = Histogram(
    'phoenix_bot_game_duration_seconds',
    'Game session duration in seconds',
    ['game_type']
)

# Гейджи
ACTIVE_USERS = Gauge(
    'phoenix_bot_active_users',
    'Number of active users'
)

ACTIVE_GAMES = Gauge(
    'phoenix_bot_active_games',
    'Number of active games',
    ['game_type']
)

TOTAL_USERS = Gauge(
    'phoenix_bot_total_users',
    'Total number of registered users'
)

TOTAL_CHIPS = Gauge(
    'phoenix_bot_total_chips',
    'Total chips in circulation'
)


class MetricsMiddleware:
    """Промежуточное ПО для сбора метрик"""
    
    def __init__(self):
        self.start_time = None
    
    async def __call__(self, handler, update, context):
        self.start_time = time.time()
        
        try:
            # Выполняем обработчик
            result = await handler(update, context)
            
            # Собираем метрики
            method = update.effective_message.text.split()[0] if update.effective_message.text else 'unknown'
            endpoint = update.effective_message.text[:50] if update.effective_message.text else 'unknown'
            
            REQUESTS_TOTAL.labels(method=method, endpoint=endpoint).inc()
            
            duration = time.time() - self.start_time
            REQUEST_DURATION.labels(method=method, endpoint=endpoint).observe(duration)
            
            return result
        except Exception as e:
            # Собираем метрики ошибок
            method = update.effective_message.text.split()[0] if update.effective_message.text else 'unknown'
            endpoint = update.effective_message.text[:50] if update.effective_message.text else 'unknown'
            
            ERRORS_TOTAL.labels(method=method, endpoint=endpoint).inc()
            raise