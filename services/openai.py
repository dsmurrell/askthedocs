import re
import sys
import time

import openai
from sqlalchemy import select
from sqlalchemy.orm import Session

from alchemy.models import Section
from config import config

openai.api_key = config["openai_key"]


def fetch_and_save_embeddings(session: Session):
    # Select sections without an embedding
    sections_without_embedding = (
        session.query(Section).filter(Section.embedding.is_(None)).all()
    )
    sys.stdout.write(
        f"Fetching embeddings for {len(sections_without_embedding)} sections..."
    )

    for section in sections_without_embedding:
        sys.stdout.write(".")
        sys.stdout.flush()
        # Fetch an embedding for the section
        res = openai.Embedding.create(
            input=section.text,
            model="text-embedding-ada-002",
        )
        embedding = res["data"][0]["embedding"]
        section.embedding = embedding
        session.add(section)
        session.commit()

        # Add a delay of 0.4 seconds to stay within the rate limit of 150 per minute
        time.sleep(0.4)

    print("Done!")


def find_closest_sections(session: Session, query: str):
    res = openai.Embedding.create(
        input=query,
        model="text-embedding-ada-002",
    )
    query_embedding = res["data"][0]["embedding"]

    match_count = 10
    similarity_threshold = 0.75

    # l2_distance_alias = func.l2_distance(Section.embedding, query_embedding).label(
    #     "l2_distance"
    # )

    # query = session.scalars(
    #     select(Section, l2_distance_alias)
    #     .where(l2_distance_alias <= match_threshold)
    #     .order_by(l2_distance_alias)
    #     .limit(match_count)
    # )

    1 - similarity_threshold

    query = session.scalars(
        select(Section)
        # .where(Section.embedding.l2_distance(query_embedding) <= distance_threshold)
        .order_by(Section.embedding.l2_distance(query_embedding)).limit(match_count)
    )

    # # Look up the match_count sections with an embedding closest to the query embedding
    # query = session.scalars(
    #     select(Section)
    #     .order_by(Section.embedding.l2_distance(query_embedding))
    #     .limit(match_count)
    # )

    # Execute the query and fetch the results
    closest_sections = query.all()

    total_word_count = sum(len(section.text.split()) for section in closest_sections)

    print(f"Total word count: {total_word_count}")

    # Print the results
    for section in closest_sections:
        print(section.text)
        print("----------------------------------------")

    return closest_sections


def get_first_completion(query: str, context: str):
    messages = [
        {
            "role": "system",
            # "content": "You are a bot that reads a question and some context and tried to provide an answer that is context specific.",
            # "content": "You are a very enthusiastic Sano Genetics representative who loves to help people!  that reads a question and some context and tries to provide an answer that is context specific.",
            "content": """You are a very enthusiastic Sano Genetics representative who loves to help people!""",
        },
        {
            "role": "user",
            "content": f"""Given the following sections from the Sano Genetics documentation, answer the question using only that information, outputted in Slack mrkdwn format. If you are unsure and the answer is not explicitly written in the documentation, say "Sorry, don't know how to help with that."

Context sections:
{context}

Question:
\"\"\"
{query}
\"\"\"
"""
            #             "content": f"""
            # Question:
            # {query}
            # Context:
            # {context}
            # """,
        },
    ]

    print(messages)

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
    )

    print(response)

    return response["choices"][0]["message"]["content"]


def get_query_response(session: Session, query):
    closest_sections = find_closest_sections(session, query)

    # Initialize the context string.

    context_string = ""

    # Define a separator between sections.
    separator = (
        " "  # You can also use "\n" for newlines, or any other string as a separator.
    )

    # Iterate through the Section objects and append the text field to the context string.
    for section in closest_sections:
        context_string += section.text + separator

    # Remove the trailing separator.
    context_string = context_string.rstrip(separator)

    # The pattern to match: <@ followed by a combination of uppercase letters and numbers, and then >
    pattern = r"<@[A-Z0-9]+>"

    # Substitute the pattern with an empty string
    stripped_query = re.sub(pattern, "", query)

    # Remove extra whitespace (if any)
    stripped_query = " ".join(stripped_query.split())

    return get_first_completion(stripped_query, context_string)
