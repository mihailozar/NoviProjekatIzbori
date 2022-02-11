from datetime import timedelta
import os


redisHostName=os.environ["REDIS_HOST"]

class Configuration ( ):
    JWT_SECRET_KEY = "JWT_SECRET_KEY"
    REDIS_HOST = redisHostName
    REDIS_VOTES = "votesProba"



