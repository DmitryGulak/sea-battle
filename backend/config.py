from envparse import Env

env = Env()

SECRET = env('SECRET')
DEBUG = env('DEBUG', cast=bool)
