import json
import logging
import random
from time import sleep

from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.orm import Session
from starlette.requests import Request
from starlette.responses import HTMLResponse, RedirectResponse

from alchemy.database import get_db

logger = logging.getLogger(__name__)


router = APIRouter()  # Create a router instance


def init_app(app):
    app.include_router(router)


def example_background_task():
    for i in range(10):
        print("inside background task")
        logger.info("inside background task")
        sleep(5)

    return False


@router.get("/dbtest")
async def example_route(db: Session = Depends(get_db)):
    # Your route logic here
    pass


@router.get("/hello")
def hello_world_example(bgt: BackgroundTasks):
    logger.info("starting background task")
    bgt.add_task(example_background_task)
    logger.info("returning from endpoint")
    return {"message": "Hello World"}


@router.get("/redirect")
def redirect_example():
    options = [
        "http://www.google.com",
        "http://www.twitter.com",
        "http://www.reddit.com",
        "http://www.github.com",
    ]
    response = RedirectResponse(url=random.choice(options))
    return response


@router.get("/error")
def error_example():
    logger.info("info message")
    logger.warning("warning message")
    logger.error("error message")
    a = {}
    b = a["hello"]
    logger.error(b)
    return {"message": "Hello World"}


@router.post("/post-example")
async def post_example(request: Request):
    content = await request.body()
    data = json.loads(content)
    return HTMLResponse(content="<pre>" + data["param"] + "</pre>")
    return HTMLResponse(content="<pre>" + data["param"] + "</pre>")
