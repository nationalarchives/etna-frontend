import os
from distutils.util import strtobool


class Config(object):
    SECRET_KEY = os.environ.get("SECRET_KEY")
    DEBUG = strtobool(os.getenv("DEBUG", "False"))


cache_config = {
    "CACHE_TYPE": "SimpleCache"
    if os.environ.get("environment") == "production"
    else "FileSystemCache",
    "CACHE_DEFAULT_TIMEOUT": int(os.environ.get("CACHE_DEFAULT_TIMEOUT", 300)),
    "CACHE_IGNORE_ERRORS": True,
    "CACHE_DIR": "/tmp",
}
