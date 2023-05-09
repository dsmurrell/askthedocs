import json
import logging
import os

from fastapi import FastAPI, Request
from fastapi.middleware import Middleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

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
        "connection_string": "postgresql://simon:Irw5cDeOlCF3@ep-dark-bird-751763.eu-central-1.aws.neon.tech/askthedocs",
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


class JSONResponseMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        if isinstance(response, JSONResponse):
            formatted_data = json.dumps(response.content, indent=2)
            return JSONResponse(
                content=formatted_data,
                headers=response.headers,
                media_type="application/json",
            )
        return response


config = get_config()


def create_app():
    app = FastAPI(title="Ask The Docs", middleware=[Middleware(JSONResponseMiddleware)])
    app.state.config = config
    return app
