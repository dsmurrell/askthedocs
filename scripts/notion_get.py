#!/usr/bin/env python3
"""
Get all shared pages from current space.
"""
import itertools
from argparse import ArgumentParser

from notion.client import NotionClient

# from notion_client import Client as NotionClient


def main():
    parser = ArgumentParser()
    parser.add_argument("--token", required=True, help="token v2 for notion.so")
    args = parser.parse_args()

    client = NotionClient(token_v2=args.token)
    space = client.current_space
    store = client._store
    user_id = client.current_user.id

    # Fetch all pages, collections and space root
    all_pages = [space] + [
        client.get_block(page_id)
        for page_id in store._values["space"][client.current_space.id]["pages"]
    ]

    blocks = list(all_pages)
    while blocks:
        page_ids = set((page.id for page in all_pages))
        children_page_iter = itertools.chain.from_iterable(
            (block.children for block in blocks if hasattr(block, "children"))
        )
        children = [
            page
            for page in children_page_iter
            if page.id not in page_ids
            and page.type
            in (
                "page",
                "collection",
            )
        ]
        all_pages.extend(children)
        blocks = children
        print(
            "Collected %s blocks, current children %s" % (len(all_pages), len(children))
        )

    print("Total %s blocks" % len(all_pages))

    for page in all_pages:
        permissions = page.get("permissions")
        if not permissions:
            continue
        permissions = [p for p in permissions if p.get("user_id") != user_id]
        if permissions:
            print("%s %s:" % (page.type, page.title))
            for permission in permissions:
                print("  > %s" % permission)


if __name__ == "__main__":
    main()
