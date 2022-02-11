from datetime import timedelta
import os

dbURL = os.environ["DATABASE_URL"]

class Configuration ( ):
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://root:root@{dbURL}/elections"
    JWT_SECRET_KEY = "JWT_SECRET_KEY"



