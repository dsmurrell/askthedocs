from notion_client import Client as NotionClient

from config import config


def notion():
    return NotionClient(auth=config["notion_key"])
