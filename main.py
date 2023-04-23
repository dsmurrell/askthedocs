import logging
from time import time

import coloredlogs
from mangum import Mangum
from starlette.requests import Request

from alchemy.database import get_db_session
from alchemy.schema_migration import perform_schema_migrations
from config import create_app
from plotting import plot_text_lengths_density
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

perform_schema_migrations(app.state.config, get_db_session().__next__())

# get an idea of the distribution of text lengths
if app.state.config["env"] == "local":
    print("Plotting text lengths density...")
    output_file = "notes/density_plot.png"
    plot_text_lengths_density(get_db_session().__next__(), output_file)


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
