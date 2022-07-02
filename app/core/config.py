from pydantic import  BaseSettings
import os

class Settings(BaseSettings):
    HOST: str = os.environ["HOST"]
    PORT: int = os.environ["PORT"]
    SECRET: str = os.environ["SECRET"]
    class Config:
        env_file = '/Users/santosh/mum_mum-idlis/.env'
settings = Settings()
