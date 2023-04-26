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
from services.notion import process_page
from services.openai import fetch_and_save_embeddings, find_closest_sections

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


@router.get("/embedding-test")
async def embedding_test(session: Session = Depends(get_db_session)):
    fetch_and_save_embeddings(session)


@router.get("/embedding-run")
async def embedding_run(session: Session = Depends(get_db_session)):
    find_closest_sections(session)


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
    process_page(session, notion, "311bf9ead72a4c5f95c4b1de7bb77078")
    process_page(session, notion, "1b34ea1c8dd04879bc3c3618b58602e5")
    process_page(session, notion, "3ebab0d1bfb3417eab45296b34e4bd63")
    process_page(session, notion, "419847568ba64f6582acc326225d22cb")
    process_page(session, notion, "b51643654ed94fcc84c6e22fe28c9f94")
    process_page(session, notion, "89ad57f6600b42ff93b3b936b8739e17")
    process_page(session, notion, "4ff5b0e5ceac433bbed07619d0209284")
    process_page(session, notion, "b137d5f2ffae457cbbf72ffd1e44a130")
    process_page(session, notion, "f234c8d091f647ac848afcbf3b979680")
    process_page(session, notion, "070330ff871e4fcea3a58757d99cc3da")
    process_page(session, notion, "5010ce70930a48d38c56090c5d5cbe58")
    process_page(session, notion, "e93a6eff2396433a915af0d9034dd2a1")

    # # Permission to send granted
    # https://www.notion.so/sanogenetics/Remote-Working-Recommendations-311bf9ead72a4c5f95c4b1de7bb77078
    # https://www.notion.so/sanogenetics/Parental-Leave-Policy-1b34ea1c8dd04879bc3c3618b58602e5
    # https://www.notion.so/sanogenetics/Bereavement-Policy-3ebab0d1bfb3417eab45296b34e4bd63
    # https://www.notion.so/sanogenetics/Mental-Health-Wellbeing-Guidance-419847568ba64f6582acc326225d22cb
    # https://www.notion.so/sanogenetics/Health-Safety-Policy-b51643654ed94fcc84c6e22fe28c9f94
    # https://www.notion.so/sanogenetics/Daily-Standup-Routine-89ad57f6600b42ff93b3b936b8739e17
    # https://www.notion.so/sanogenetics/How-we-live-our-values-4ff5b0e5ceac433bbed07619d0209284
    # https://www.notion.so/sanogenetics/No-Meeting-Wednesdays-b137d5f2ffae457cbbf72ffd1e44a130
    # https://www.notion.so/sanogenetics/Slack-Channels-f234c8d091f647ac848afcbf3b979680
    # https://www.notion.so/sanogenetics/Communication-Channels-070330ff871e4fcea3a58757d99cc3da
    # https://www.notion.so/sanogenetics/Meeting-Guidelines-5010ce70930a48d38c56090c5d5cbe58
    # https://www.notion.so/sanogenetics/Future-of-Work-e93a6eff2396433a915af0d9034dd2a1


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
