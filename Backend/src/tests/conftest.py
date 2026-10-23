import os

for name, value in {
    "DB_HOST": "127.0.0.1",
    "DB_PORT": "5432",
    "DB_USER": "athena_test",
    "DB_PASSWORD": "athena_test",
    "DB_CONECTION": "athena_test",
    "REDIS_HOST": "127.0.0.1",
    "REDIS_PORT": "6379",
    "REDIS_PASSWORD": "athena_test",
}.items():
    os.environ.setdefault(name, value)
