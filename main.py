import logging
from time import time

import coloredlogs
from mangum import Mangum
from starlette.requests import Request

from config import create_app
from routes import example_routes

logger = logging.getLogger(__name__)
format_string = (
    "%(levelname)s: %(asctime)s %(funcName)s() %(name)s:%(lineno)s %(message)s"
)

coloredlogs.install(
    level="INFO",
    fmt=format_string,
)

app = create_app()

# Initialize the routes
example_routes.init_app(app)


logger.info("Ask the docs service started...")
logger.info(app.state)


@app.middleware("http")
async def info(request: Request, call_next):
    logger.info(f"{request.method} - {request.url.path} - [start]")
    start_time = time()
    response = await call_next(request)
    process_time = time() - start_time
    logger.info(
        f"{request.method} - {request.url.path} - [{str(round(process_time, 3))}]"
    )
    response.headers["X-Process-Time"] = str(process_time)
    return response


handler = Mangum(app)
