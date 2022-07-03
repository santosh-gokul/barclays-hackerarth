from pydantic import  BaseSettings
import os

class Settings(BaseSettings):
    HOST: str = os.environ["HOST"]
    PORT: int = os.environ["PORT"]
    SECRET: str = os.environ["SECRET"]
    CASHFREE_ENDPOINT = os.environ["CASHFREE_ENDPOINT"]
    CASHFREE_APPID = os.environ["CASHFREE_APPID"]
    CASHFREE_SECRETKEY = os.environ["CASHFREE_SECRETKEY"]
    class Config:
        env_file = '/Users/santosh/mum_mum-idlis/.env'
settings = Settings()
