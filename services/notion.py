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

from alchemy.models import Document, Node, Section
from helpers import compute_hash, pretty_print_dict

logger = logging.getLogger(__name__)


def extract_text(block):
    try:
        block_type = block["type"]

        if block_type in ["paragraph", "to_do"]:
            text = (
                block[block_type]["rich_text"][0]["plain_text"]
                if block[block_type]["rich_text"]
                else ""
            )
        elif block_type in ["heading_1", "heading_2", "heading_3"]:
            text = f"{'#' * int(block_type[-1])} {block[block_type]['rich_text'][0]['plain_text']}"
        elif block_type == "bulleted_list_item":
            text = f"- {block[block_type]['rich_text'][0]['plain_text']}"
        else:
            text = ""
    except Exception as e:
        print(block)
        raise e

    return text


# def split_sections(text_blocks, min_chars=100, max_chars=1000):
#     sections = []
#     current_section = []

#     def section_size(section):
#         return sum(len(line) for line in section)

#     for text in text_blocks:
#         if text.startswith("#"):
#             if current_section:
#                 if section_size(current_section) > min_chars or not all(
#                     line.isspace() for line in current_section
#                 ):
#                     sections.append("\n".join(current_section))
#                     current_section = []
#         current_section.append(text)

#         if section_size(current_section) > max_chars:
#             sections.append("\n".join(current_section))
#             current_section = []

#     if current_section and not all(line.isspace() for line in current_section):
#         sections.append("\n".join(current_section))

#     # Merge small sections
#     merged_sections = []
#     for section in sections:
#         if len(section) < min_chars and merged_sections:
#             merged_sections[-1] = "\n".join([merged_sections[-1], section])
#         else:
#             merged_sections.append(section)

#     return merged_sections


# def split_into_blocks(content):
#     return content.split("\n\n")


# def split_sections(text_blocks, min_chars=100, max_chars=1000):
#     sections = []
#     current_section = []

#     def section_size(section):
#         return sum(len(line) for line in section)

#     for text in text_blocks:
#         if text.startswith("#"):
#             if current_section:
#                 if section_size(current_section) > min_chars or not all(
#                     line.isspace() for line in current_section
#                 ):
#                     sections.append("\n".join(current_section))
#                     current_section = []
#         current_section.append(text)

#         if section_size(current_section) > max_chars:
#             sections.append("\n".join(current_section))
#             current_section = []

#     if current_section and not all(line.isspace() for line in current_section):
#         sections.append("\n".join(current_section))

#     # Merge small sections
#     merged_sections = []
#     for section in sections:
#         if len(section) < min_chars and merged_sections:
#             merged_sections[-1] = "\n".join([merged_sections[-1], section])
#         else:
#             merged_sections.append(section)

#     return merged_sections


def save_page_to_database(session: Session, page, text, sections):
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
            text = text
        else:
            # If the page doesn't exist, create a new Document object and add it to the session
            document = Document(
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
        # raise e

    try:
        for i, section_text in enumerate(sections):
            section_hash = compute_hash(section_text)
            print(colored(f"Section {i + 1}:", "blue"))
            print(colored(section_text, "green"))

            # Check if the section with the same hash already exists in the database
            section = session.query(Section).filter_by(hash=section_hash).first()

            if not section:
                # If the section doesn't exist, create a new Section object and add it to the session
                section = Section(
                    text=section_text,
                    document_id=document.id,
                    number=i + 1,
                    hash=section_hash,
                )
                session.add(section)
                session.commit()

        # Remove any old sections that are not in the current sections
        session.query(Section).filter(
            Section.document_id == document.id,
            ~Section.hash.in_([compute_hash(s) for s in sections]),
        ).delete(synchronize_session="fetch")

    except Exception:
        session.rollback()
        pretty_print_dict(page)
        # raise e


# def process_page_2(session: Session, notion: NotionClient, page_id):
#     print(colored(f"Processing page with ID: {page_id}", "green"))
#     try:
#         page = notion.pages.retrieve(page_id)
#     except Exception:
#         print(colored(f"Error retrieving page with ID: {page_id}", "red"))
#         return
#     pretty_print_dict(page)
#     block_children = notion.blocks.children.list(page_id)["results"]

#     text_blocks = [extract_text(block) for block in block_children]
#     text_blocks = list(filter(None, text_blocks))
#     sections = split_sections(text_blocks)

#     # for i, section in enumerate(sections):
#     #     print(f"Section {i + 1}:\n{section}\n")

#     # Save the page and sections to your database
#     save_page_to_database(session, page, sections)

#     # Recurse through the subpages
#     for block in block_children:
#         if block["type"] == "child_page":
#             child_page_id = block["id"]
#             process_page(session, notion, child_page_id)


# def split_markdown_by_title(content):
#     sections = {}
#     titles = re.findall(r"^# (.*)", content, re.MULTILINE)
#     split_content = re.split(r"^# .*", content, flags=re.MULTILINE)

#     for index, title in enumerate(titles):
#         sections[title] = split_content[index + 1].strip()
#     return sections


def read_markdown_file(filename):
    with open(filename, "r") as file:
        content = file.read()
    return content


# def split_md_sections(md_text, delimiter="##"):
#     pattern = r"(^|\n){}".format(re.escape(delimiter))
#     sections = re.split(pattern, md_text)
#     return [section.strip() for section in sections if section.strip()]


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


def process_page(session: Session, notion: NotionClient, page_id):
    sleep(1)
    print(colored(f"Processing page with ID: {page_id}", "green"))
    try:
        page = notion.pages.retrieve(page_id)

        output_dir = "notion_output"
        output_file = f"{output_dir}/{page_id}.md"

        if not os.path.exists(output_file):
            cmd = f"notion2md --download --unzipped -p {output_dir} -i {page_id}"
            subprocess.run(cmd, shell=True, check=True)

        text = read_markdown_file(output_file)
    except Exception:
        print(colored(f"Error retrieving page with ID: {page_id}", "red"))
        return

    sections = split_md_sections(text, delimiter="#")
    print(sections)

    md_parser = MarkdownIt()

    for i, section in enumerate(sections):
        print(f"Section {i + 1}:")
        print(md_parser.render(section))
        print()

    # pretty_print_dict(sections)
    print("------")

    # for i, section in enumerate(sections):
    #     print(f"Section {i + 1}:\n{section}\n")

    # Save the page and sections to your database
    save_page_to_database(session, page, text, sections)

    # Recurse through the subpages
    block_children = notion.blocks.children.list(page_id)["results"]
    for block in block_children:
        if block["type"] == "child_page":
            child_page_id = block["id"]
            process_page(session, notion, child_page_id)


md = MarkdownIt()


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
