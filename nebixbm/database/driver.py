from nebixbm.log.logger import create_logger
import redis
import os


class RedisDB:
    """Redis database class"""

    def __init__(self, database_num=0):
        self.logger, self.log_filepath = create_logger(
            f"redis_db_{database_num}",
            f"redis_db_{database_num}",
        )
        self.redis_host = os.environ["REDIS_HOST"]
        self.redis_port = os.environ["REDIS_PORT"]
        self.redis_password = os.environ["REDIS_PASS"]
        self.database_num = database_num
        self.logger.info("RedisDB class initialized")
        self.redis = self.create_redis_obj()
        if self.redis:
            self.logger.info("Successfully created redis object")

    def create_redis_obj(self):
        """Return redis object"""
        try:
            redis_obj = redis.Redis(
                host=self.redis_host,
                port=self.redis_port,
                # password=self.redis_password,
                db=self.database_num,
                decode_responses=True,
            )
            redis_obj.ping()
            return redis_obj
        except Exception as err:
            self.logger.error(f"Error in creating redis object: {err}")
            return None

    def set(self, key, value):
        """Set value to key"""
        res = self.redis.set(key, value)
        if res:
            self.logger.info(
                f'Successfully set value:"{value}" to key:"{key}"'
            )
        else:
            self.logger.info(f'Failed to set value:"{value}" to key:"{key}"')
        return res

    def get(self, key):
        """Get value of key"""
        res = self.redis.get(key)
        self.logger.info(f'Got value:"{res}" for key:"{key}"')
        return res

    def delete(self, key):
        """Delete given key"""
        res = self.redis.delete(key)
        if res:
            self.logger.info(f'Successfully deleted key:"{key}"')
        else:
            self.logger.info(f'Failed to delete key:"{key}"')
        return
