import json
import logging
import random
from time import sleep, time

import coloredlogs
from fastapi import BackgroundTasks, Depends, HTTPException
from mangum import Mangum
from sqlalchemy.orm import Session
from starlette.requests import Request
from starlette.responses import HTMLResponse, RedirectResponse

from alchemy.database import get_db
from config import create_app

logger = logging.getLogger(__name__)
format_string = (
    "%(levelname)s: %(asctime)s %(funcName)s() %(name)s:%(lineno)s %(message)s"
)

coloredlogs.install(
    level="INFO",
    fmt=format_string,
)

app = create_app()


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


# rudimentary check of a header token that is passed to an endpoint
def check_token(token):
    if token != app.state.config["submit_token"]:
        raise HTTPException(status_code=403, detail="Not authorised")


def example_background_task():
    for i in range(10):
        print("inside background task")
        logger.info("inside background task")
        sleep(5)

    return False


@app.get("/dbtest")
async def example_route(db: Session = Depends(get_db)):
    # Your route logic here
    pass


@app.get("/hello")
def hello_world_example(bgt: BackgroundTasks):
    logger.info("starting background task")
    bgt.add_task(example_background_task)
    logger.info("returning from endpoint")
    return {"message": "Hello World"}


@app.get("/redirect")
def redirect_example():
    options = [
        "http://www.google.com",
        "http://www.twitter.com",
        "http://www.reddit.com",
        "http://www.github.com",
    ]
    response = RedirectResponse(url=random.choice(options))
    return response


@app.get("/error")
def error_example():
    logger.info("info message")
    logger.warning("warning message")
    logger.error("error message")
    a = {}
    b = a["hello"]
    logger.error(b)
    return {"message": "Hello World"}


@app.post("/post-example")
async def post_example(request: Request):
    content = await request.body()
    data = json.loads(content)
    return HTMLResponse(content="<pre>" + data["param"] + "</pre>")


handler = Mangum(app)
