import redis
import time


def is_redis_up():
    try:
        redis_obj = redis.Redis(
            host="localhost",
            port=6379,
            password=None,
            db=0,
            decode_responses=True,
        )
        res = redis_obj.ping()
        if res:
            return True
        return False
    except Exception as err:
        print(err)
        return False


while True:
    print("Trying to connect to Redis...")
    if is_redis_up():
        print("Successfully connected to Redis")
        break
    time.sleep(1)
