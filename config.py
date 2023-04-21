import logging
import os

from fastapi import FastAPI

from secret_config import s

logger = logging.getLogger(__name__)


def get_config():
    """
    Get configuration from (in increasing priority order):

    - DEFAULT CONFIG
    - ENVIRONMENT VARIABLES

    Note: for cross-platform compatability, keys should be lowercase
    """

    # DEFAULT CONFIG
    config = {
        "env": "local",
        "connection_string": "postgresql://postgres@localhost/askthedocs",
    }

    # SECRET CONFIG
    config.update(s)

    # ENVIRONMENT VARIABLES
    for key in sorted(os.environ):
        key = key.lower()
        logger.debug(f"Loading {key} from environment variables")
        config[key] = os.getenv(key)

    # log the config that's being picked up
    for key, _ in sorted(config.items()):
        logger.debug(f"Config {key} exists")

    return config


config = get_config()


def create_app():
    app = FastAPI(title="Ask The Docs")
    app.state.config = config
    return app
    return app
