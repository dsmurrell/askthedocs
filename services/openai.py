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


def find_closest_sections(session: Session):
    res = openai.Embedding.create(
        input="How does shared parental leave work?",
        model="text-embedding-ada-002",
    )
    query_embedding = res["data"][0]["embedding"]

    match_count = 10

    # Look up the match_count sections with an embedding closest to the query embedding
    query = session.scalars(
        select(Section)
        .order_by(Section.embedding.l2_distance(query_embedding))
        .limit(match_count)
    )

    # Execute the query and fetch the results
    closest_sections = query.all()

    total_word_count = sum(len(section.text.split()) for section in closest_sections)

    print(f"Total word count: {total_word_count}")

    # Print the results
    for section in closest_sections:
        print(section.text)
        print("----------------------------------------")
