import os
import time
import redis


def is_redis_up(host, port, password):
    try:
        redis_obj = redis.Redis(
            host=host,
            port=port,
            password=password,
            db=0,
            decode_responses=True,
        )
        redis_obj.ping()
        return True
    except Exception as err:
        print(err)
        return False


if __name__ == "__main__":
    host = os.environ["REDIS_HOST"]
    port = os.environ["REDIS_PORT"]
    password = os.environ["REDIS_PASS"]
    while True:
        print("Trying to connect to Redis...")
        if is_redis_up(host, port, password):
            print("Successfully connected to Redis")
            break
        time.sleep(1)
