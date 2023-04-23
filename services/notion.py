import logging

from notion_client import Client as NotionClient
from sqlalchemy.orm import Session
from termcolor import colored

from alchemy.models import Document, Section
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


# def split_sections(text_blocks):
#     sections = []
#     current_section = []

#     for text in text_blocks:
#         if text.startswith("#"):
#             if current_section and not all(line.isspace() for line in current_section):
#                 sections.append("\n".join(current_section))
#                 current_section = []
#         current_section.append(text)

#     if current_section and not all(line.isspace() for line in current_section):
#         sections.append("\n".join(current_section))

#     return sections


def split_sections(text_blocks, min_chars=100, max_chars=1000):
    sections = []
    current_section = []

    def section_size(section):
        return sum(len(line) for line in section)

    for text in text_blocks:
        if text.startswith("#"):
            if current_section:
                if section_size(current_section) > min_chars or not all(
                    line.isspace() for line in current_section
                ):
                    sections.append("\n".join(current_section))
                    current_section = []
        current_section.append(text)

        if section_size(current_section) > max_chars:
            sections.append("\n".join(current_section))
            current_section = []

    if current_section and not all(line.isspace() for line in current_section):
        sections.append("\n".join(current_section))

    # Merge small sections
    merged_sections = []
    for section in sections:
        if len(section) < min_chars and merged_sections:
            merged_sections[-1] = "\n".join([merged_sections[-1], section])
        else:
            merged_sections.append(section)

    return merged_sections


def save_page_to_database(session: Session, page, sections):
    try:
        document_hash = compute_hash(page)
        # Check if the page with the same hash already exists in the database
        document = session.query(Document).filter_by(hash=document_hash).first()

        if not document:
            # If the Document object is not found by its hash, try to find it by its URL
            document = session.query(Document).filter_by(url=page["url"]).first()

        if document:
            # If the page already exists, update its title and URL
            document.title = page["properties"]["title"]["title"][0]["plain_text"]
            document.url = page["url"]
        else:
            # If the page doesn't exist, create a new Document object and add it to the session
            document = Document(
                url=page["url"],
                title=page["properties"]["title"]["title"][0]["plain_text"],
                hash=document_hash,
            )
            session.add(document)
            session.commit()  # Commit the document to get an ID for the sections

    except Exception as e:
        session.rollback()
        pretty_print_dict(page)
        raise e

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

    except Exception as e:
        session.rollback()
        pretty_print_dict(page)
        raise e


def process_page(session: Session, notion: NotionClient, page_id):
    print(colored(f"Processing page with ID: {page_id}", "green"))
    try:
        page = notion.pages.retrieve(page_id)
    except Exception:
        print(colored(f"Error retrieving page with ID: {page_id}", "red"))
        return
    # pretty_print_dict(page)
    block_children = notion.blocks.children.list(page_id)["results"]

    text_blocks = [extract_text(block) for block in block_children]
    text_blocks = list(filter(None, text_blocks))
    sections = split_sections(text_blocks)

    # for i, section in enumerate(sections):
    #     print(f"Section {i + 1}:\n{section}\n")

    # Save the page and sections to your database
    save_page_to_database(session, page, sections)

    # Recurse through the subpages
    for block in block_children:
        if block["type"] == "child_page":
            child_page_id = block["id"]
            process_page(session, notion, child_page_id)
            process_page(session, notion, child_page_id)
            process_page(session, notion, child_page_id)
