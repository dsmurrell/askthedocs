import logging
import sys
import threading
from time import time

import coloredlogs
from mangum import Mangum
from starlette.requests import Request

from alchemy.database import get_db_session
from alchemy.models import Document, Node
from alchemy.schema_migration import perform_schema_migrations
from config import create_app
from helpers import preprocess_text, remove_html_tags
from plotting import plot_text_lengths_density
from routes import test
from services.markdown import update_nodes
from services.slack import start_slack_bot

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
test.init_app(app)


logger.info("Ask the docs service started...")
logger.info(app.state)

session = get_db_session().__next__()
perform_schema_migrations(app.state.config, session)


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


@app.on_event("startup")
async def startup_event():
    # Start the Slack bot in a separate thread
    bot_thread = threading.Thread(target=start_slack_bot, daemon=True)
    bot_thread.start()


@app.on_event("startup")
async def plot_density():
    # Get an idea of the distribution of text lengths in nodes
    if app.state.config["env"] == "local":
        print("Plotting text lengths density...")
        output_file = "notes/density_plot.png"
        plot_text_lengths_density(get_db_session().__next__(), output_file)


@app.on_event("startup")
async def test():
    # try:
    #     # Clean the text of the documents
    #     print("Cleaning document text...")
    #     documents = session.query(Document).all()
    #     print(len(documents))
    #     for i, document in enumerate(documents):
    #         document.text_no_html = remove_html_tags(document.text)
    #         if i % 100 == 0:
    #             print(i)
    #         sys.stdout.write(".")
    #         sys.stdout.flush()
    #     session.commit()
    #     print("Done")

    #     print("Updating nodes...")
    #     update_nodes(session)

    #     print("Cleaning node text...")
    #     # Clean the text of the nodes
    #     nodes = session.query(Node).all()
    #     print(len(nodes))
    #     for i, node in enumerate(nodes):
    #         node.text_processed = preprocess_text(node.text)
    #         if i % 100 == 0:
    #             print(i)
    #         sys.stdout.write(".")
    #         sys.stdout.flush()
    #     session.commit()
    #     print("Done")

    # except Exception as e:
    #     print(f"An error occurred: {e}")
    #     session.rollback()
    # finally:
    #     session.close()
    pass


handler = Mangum(app)
