import logging
import redis


# class Redis:
#     """Redis database class"""
#
#     def __init__(self):
#         self.redis_host = "localhost"
#         self.redis_port = 6379
#         self.redis_password = ""
#
#     def connect(self):
#         """Return redis object"""
#         try:
#             r = redis.Redis(
#                 host=self.redis_host,
#                 port=self.redis_port,
#                 password=self.redis_password,
#                 decode_responses=True
#             )
#             return r
#         except Exception as err:
#             print(err)
#             return None
