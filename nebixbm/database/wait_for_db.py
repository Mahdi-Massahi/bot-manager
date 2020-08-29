import sys
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
        res = redis_obj.ping()
        if res:
            return True
        return False
    except Exception as err:
        print(err)
        return False


if __name__ == '__main__':
    arguments = sys.argv
    host = str(arguments[0])
    port = str(arguments[1])
    password = str(arguments[2]) if len(arguments) > 2 else None
    while True:
        print("Trying to connect to Redis...")
        if is_redis_up(host, port, password):
            print("Successfully connected to Redis")
            break
        time.sleep(1)
