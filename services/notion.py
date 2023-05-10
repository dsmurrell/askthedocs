import fnmatch
import logging
import os
import re
import subprocess
from time import sleep
from typing import Dict, List, Optional

from markdown_it import MarkdownIt
from markdown_it.token import Token
from notion_client import Client as NotionClient
from sqlalchemy.orm import Session
from termcolor import colored

from alchemy.models import Document, Node
from helpers import compute_hash, pretty_print_dict

logger = logging.getLogger(__name__)


def save_page_to_database(session: Session, page_id, page, text):
    try:
        document_hash = compute_hash(page)
        # Check if the page with the same hash already exists in the database
        document = session.query(Document).filter_by(hash=document_hash).first()

        if not document:
            # If the Document object is not found by its hash, try to find it by its URL
            document = session.query(Document).filter_by(url=page["url"]).first()

        if document:
            # If the page already exists, update its title, URL, and text
            document.title = page["properties"]["title"]["title"][0]["plain_text"]
            document.url = page["url"]
            document.external_id = page_id
            text = text
        else:
            # If the page doesn't exist, create a new Document object and add it to the session
            document = Document(
                external_id=page_id,
                url=page["url"],
                title=page["properties"]["title"]["title"][0]["plain_text"],
                hash=document_hash,
                text=text,
            )
            session.add(document)
            session.commit()  # Commit the document to get an ID for the sections

    except Exception:
        session.rollback()
        pretty_print_dict(page)
        logger.warn("Exception hit")


def read_markdown_file(filename):
    with open(filename, "r") as file:
        content = file.read()
    return content


def split_md_sections(md_text, delimiter="##", min_chars=100, max_chars=1000):
    pattern = r"(^|\n){}".format(re.escape(delimiter))
    sections = re.split(pattern, md_text)
    sections = [section.strip() for section in sections if section.strip()]

    adjusted_sections = []
    current_section = ""
    for section in sections:
        if len(current_section) + len(section) < min_chars:
            current_section += f"\n{delimiter} {section}"
        else:
            if len(current_section) > 0:
                adjusted_sections.append(current_section.strip())
            current_section = section

        if len(current_section) > max_chars:
            split_current_section = [
                current_section[i : i + max_chars]
                for i in range(0, len(current_section), max_chars)
            ]
            adjusted_sections.extend(split_current_section)
            current_section = ""

    if len(current_section) > 0:
        adjusted_sections.append(current_section.strip())

    return adjusted_sections


def get_child_pages(notion, page_id):
    child_pages = []

    # Query the child pages
    children = notion.blocks.children.list(page_id)

    while True:
        for child in children["results"]:
            if child["object"] == "block" and child["type"] == "child_page":
                child_pages.append(child)
            elif child["object"] == "block" and child["has_children"]:
                child_pages.extend(get_child_pages(notion, child["id"]))

        if not children["has_more"]:
            break
        else:
            children = notion.blocks.children.list(
                page_id, start_cursor=children["next_cursor"]
            )

    return child_pages


def process_page(session: Session, notion: NotionClient, page_id):
    sleep(1)
    print(colored(f"Processing page with ID: {page_id}", "green"))
    try:
        page = notion.pages.retrieve(page_id)
        print(page["url"])

        output_dir = "notion_output"
        output_file = f"{output_dir}/{page_id}.md"

        if not os.path.exists(output_file):
            cmd = f"notion2md --download --unzipped -p {output_dir} -i {page_id}"
            subprocess.run(cmd, shell=True, check=True)

        text = read_markdown_file(output_file)
    except Exception:
        print(colored(f"Error retrieving page with ID: {page_id}", "red"))
        return

    # Save the page and sections to your database
    save_page_to_database(session, page_id, page, text)

    for child in get_child_pages(notion, page_id):
        process_page(session, notion, child["id"])


md = MarkdownIt()


# takes a list of Token objects (produced by the MarkdownIt library) and returns a list of dictionaries, where each dictionary represents a header in the Markdown text. Each dictionary has two keys: level (the header's depth) and content (the header's text).
def parse_headers(tokens: List[Token]) -> List[Dict[str, Optional[str]]]:
    headers = []
    current_header = None

    for token in tokens:
        if token.type == "heading_open":
            current_header = {"level": int(token.tag[1]), "content": None}
        elif token.type == "inline" and current_header is not None:
            current_header["content"] = token.content
        elif token.type == "heading_close" and current_header is not None:
            headers.append(current_header)
            current_header = None

    return headers


def create_nodes_from_headers(
    headers: List[Dict[str, Optional[str]]],
    parent_id: Optional[str],
    session: Session,
) -> None:
    for i in range(len(headers)):
        current_header = headers[i]
        next_header = headers[i + 1] if i + 1 < len(headers) else None

        node = Node(
            title=current_header["content"],
            text="",
            depth_level=current_header["level"],
            parent_id=parent_id,
        )
        session.add(node)
        session.flush()  # To get the generated id for the new node

        if next_header and next_header["level"] > current_header["level"]:
            # If the next header is a child of the current header, create its node
            create_nodes_from_headers(headers[i + 1 :], node.id, session)
            break


def populate_db_with_nodes(markdown_text: str, session: Session) -> None:
    tokens = md.parse(markdown_text)
    headers = parse_headers(tokens)
    create_nodes_from_headers(headers, None, session)
    session.commit()


# def extract_hash_from_filename(filename):
#     match = re.search(r"(\w{32})\.md$", filename)
#     if match:
#         return match.group(1)
#     else:
#         return None


def extract_hash_from_filename(filename):
    match = re.search(r"(\w{32}|[\w-]{36})\.md$", filename)
    if match:
        return match.group(1)
    else:
        return None


# Function to extract text from a markdown file
def extract_text_from_md(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()


# Updated save_page_to_database function
def save_page_to_database_export(session: Session, page_id, text):
    try:
        document_hash = compute_hash(text)
        # Check if the page with the same hash already exists in the database
        document = session.query(Document).filter_by(hash=document_hash).first()

        if not document:
            # If the Document object is not found by its hash, try to find it by its URL
            document = session.query(Document).filter_by(url=page_id).first()

        if document:
            # If the page already exists, update its title, URL, and text
            document.title = "No title"
            document.url = page_id
            document.external_id = page_id
            document.text = text  # Set text from the passed argument
            document.tag = "notion"
        else:
            # If the page doesn't exist, create a new Document object and add it to the session
            document = Document(
                external_id=page_id,
                url=page_id,
                title="No title",
                hash=document_hash,
                text=text,
                tag="notion",
            )
            session.add(document)
            session.commit()  # Commit the document to get an ID for the sections

    except Exception:
        session.rollback()
        print(page_id)
        logger.warn("Exception hit")


def update_from_notion_export(session: Session) -> None:
    print("got here")

    def find_md_files(directory):
        md_files = []

        for root, dirs, files in os.walk(directory):
            for file in files:
                if fnmatch.fnmatch(file, "*.md"):
                    md_files.append(os.path.join(root, file))

        return md_files

    md_files = find_md_files("./notion_output")

    # Assuming you have a list of .md files in `md_files`
    for md_file in md_files:
        text = extract_text_from_md(md_file)
        filename = os.path.basename(md_file)
        page_id = extract_hash_from_filename(filename)

        if page_id:
            # Call save_page_to_database with the extracted text and page_id
            save_page_to_database_export(session, page_id, text)
        else:
            print(f"Could not extract hash from filename: {filename}")
