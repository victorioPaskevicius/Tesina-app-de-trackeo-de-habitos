import os

class Config:
    USERNAME = 'root'
    PASSWORD = ''
    HOST = 'localhost'
    DATABASE = 'habit_tracker'

    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{USERNAME}:{PASSWORD}@{HOST}/{DATABASE}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
