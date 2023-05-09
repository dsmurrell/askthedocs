import json
import logging
import random
from time import sleep

from fastapi import APIRouter, BackgroundTasks, Depends
from notion_client import Client as NotionClient
from sqlalchemy.orm import Session
from starlette.requests import Request
from starlette.responses import HTMLResponse, RedirectResponse

from alchemy.database import get_db_session
from deps import notion
# from services.markdown import test_parse_markdown
from services.notion import process_page
from services.openai import fetch_and_save_embeddings, find_closest_nodes

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


@router.get("/embedding-fetch")
async def embedding_fetch(session: Session = Depends(get_db_session)):
    fetch_and_save_embeddings(session)


@router.get("/embedding-run")
async def embedding_run(session: Session = Depends(get_db_session)):
    find_closest_nodes(session)


# @router.get("/refactor")
# async def refactor(session: Session = Depends(get_db_session)):
#     test_parse_markdown()


#     res = openai.Embedding.create(
#         input="""The idea is to have a day in the week where no internal meetings are booked and communications are kept as minimal as possible. This is to ensure all of us have a full day during the week to focus on getting work done without being interrupted by conversations/meetings. Just a few guidelines below:
# - If you have recurring meetings on wednesdays please move them to another day of the week
# - Please do not book a new internal meeting on a Wednesday
# - Regarding external meetings - it is up to you to decide whether you want to group them the rest of the week to have that focused time or if you prefer using this day to get them done (that may be the case if having external conversations is a core part of your job)
# - Please try to avoid communications on this day including emails/slack. You are welcome/encouraged to mute notification. You can tag on Notion and Github as people can check that at a later date and if you want to send an email schedule it for the next day if possible. We understand that in some cases you may be blocked to progress on things without speaking to someone else and in that case it is fine to slack/call but please use your judgement to keep that up to a minimum (i.e only if you are blocked - long conversations or debates on strategy/implementation are best kept another day)""",
#         model="text-embedding-ada-002",
#     )
#     pretty_print_dict(res)
#     embedding = res["data"][0]["embedding"]
#     pretty_print_dict(embedding)
#     print(len(embedding))


@router.get("/notion-scraper")
async def notion_scraper(
    notion: NotionClient = Depends(notion), session: Session = Depends(get_db_session)
):
    # A list of page IDs that you want to process
    page_ids = [
        # From General
        # "3dac6f4a22a34fac9ff19a210f66833d",
        # "a7287d82fb424de08b13b6ecfdcdd12c",
        # "69658b555ef34447b2f2222b1e1b8a32", # still need to pick up a few subpages from here... got to https://www.notion.so/sanogenetics/Study-Delivery-Meeting-ab85e12c67db4e6b97b69c88d65e2c13
        # "12f8eb4b45ab47ce9d0937f90478618a",
        # "f038d949e4cc4e3ea068afa791081854",
        # "4fb284f5f13041299fd050a1ea40c256",
        # "f5f06b20222343999c84bf65389bb1b0", # still need to pick up a few subpages
        "d50e3d2d19f04c8184e41b11cf35b4a1",
        "7d828fd54e8b40dc84be8780dbf60d78",
        "03c536a0ddba4a33b50a83267c5b2287",
        "71d010e3dadf411aa1ee1ca4e19c582f",
        "8f466b0bc8ac43eb9325867efccecc2b",
        "fb73373266054ba381c52e4548e30c2a",
        "2dd0972b32484016a299b33948c1c65a",
        "1b5090d03be84f94b475ced575dc79b4",
        # Engineering
        "644ad2ba55be41b49c0009806aa8880d",
        "6cfadefd906143bda6dbfc0cf13b6c9f",
        "0a1db9b6b99d40ef93540cab2bd8f6a6",
        "ba14e9ea62c043bb930310eb9ded6ac1",
        "4a87da6ea94a4bd0a667700d9fd22069",
        "738c825c08164bf89750d9e572239310",
        "3d1b94c8b2174fdfa884135b1f577afd",
        "2d17200e6ac94d4796c702108239c4ef",
        "cde347e6b36040539d62a0918371f83c",
        "b1d970ddbdea41b292ca527bb69a81cc",
        "cd620a5533a74202b5d06c1ca65dd1ea",
        "9f660f591f174147924854e059dfe641",
        "833fb2146bf34147ae2cd71104477a49",
        "3579fc1990ba4bf8b417b28fda4653b3",
        "c3b398c3dcb644b6a2c0cf3be819546f",
        "5ec53c347aa94cefbef10ba02799d366",
        "11074d18e7b74baf9fb3481bb87a55b4",
        "4d01d28a93824bf1abaffa3b7851a13c",
        "f8cb9328e4a0469daf022f5da7745a8f",
        # # "e42323054a484dbeac3f40b7aa8ae51b",  # problematic one
        # # "28fbe227694d4e5fbd2522dd1f9d360c",  # problematic one also potentially
        "c0ccff6484434756aef6cf49d335acec",
        "5bf99ee078a4452a8a08229869987609",
        "cd8cd6c15832483cab2f71fb691e55b4",
        "42738a3b26514945bb270bcf3c6265aa",
        # "5f0a0b731fd843908208e22b50ae8769",   # problematic one
        # "0526acd7872549e99951aa977aee09fe",   # problematic one
    ]

    # Loop through the page IDs and call the notion2md command
    for page_id in page_ids:
        process_page(session, notion, page_id)


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
