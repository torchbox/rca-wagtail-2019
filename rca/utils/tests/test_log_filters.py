from django.core.cache import caches
from django.test import SimpleTestCase, override_settings

# Nothing listens on port 1, so every cache call fails to connect.
UNREACHABLE_REDIS = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:1/0",
        "OPTIONS": {"IGNORE_EXCEPTIONS": True, "SOCKET_CONNECT_TIMEOUT": 1},
    }
}


@override_settings(CACHES=UNREACHABLE_REDIS, DJANGO_REDIS_LOG_IGNORED_EXCEPTIONS=True)
class IgnoredRedisExceptionLoggingTests(SimpleTestCase):
    def test_a_failed_cache_call_logs_one_line_without_a_traceback(self):
        # In AHM-291 Redis refused connections thousands of times a second, and
        # a traceback for each one filled the logs.
        with self.assertLogs("django_redis.cache", "ERROR") as logs:
            self.assertIsNone(caches["default"].get("anything"))

        [record] = logs.records
        self.assertIsNone(record.exc_info)
        self.assertNotIn("\n", record.getMessage())
        self.assertIn("Exception ignored", record.getMessage())
        self.assertIn("ConnectionError", record.getMessage())
