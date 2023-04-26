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
    print(query_embedding)

    # Cast the target_embedding list to ARRAY(Float)
    # target_embedding_array = cast(target_embedding, ARRAY(Float))

    # # Query the 10 sections with embeddings closest to the target embedding
    # closest_sections = (
    #     session.query(Section)
    #     .filter(Section.embedding is not None)  # Ignore sections without an embedding
    #     .order_by(func.pgv_distance(Section.embedding, target_embedding))
    #     .limit(10)
    #     .all()
    # )

    # match_threshold = 0.7  # Replace with your desired match threshold
    # match_count = 10  # Replace with your desired match count

    # # Define the similarity expression
    # similarity_expr = 1 - func.cube_distance(Section.embedding, query_embedding)

    # similarity_expr = 1 - func.vector_distance(Section.embedding, query_embedding)

    # # Define the custom L2 distance operator
    # def l2_distance(a, b):
    #     return a.op("<->")(b)

    # # Define the similarity expression
    # similarity_expr = 1 - l2_distance(Section.embedding, query_embedding)

    # Create the query using SQLAlchemy
    # query = (
    #     session.query(
    #         Section.id,
    #         Section.text,
    #         similarity_expr.label("similarity"),
    #     )
    #     .filter(similarity_expr > match_threshold)
    #     .order_by(similarity_expr.desc())
    #     .limit(match_count)
    # )

    query = session.scalars(
        select(Section)
        .order_by(Section.embedding.l2_distance(query_embedding))
        .limit(10)
    )

    # Execute the query and fetch the results
    closest_sections = query.all()

    total_word_count = sum(len(section.text.split()) for section in closest_sections)

    print(f"Total word count: {total_word_count}")

    # # Make sure to convert the list to a PgVector object
    # target_vector = pgvector.Vector(target_embedding)

    # # Query the 10 sections with embeddings closest to the target embedding
    # closest_sections = (
    #     session.query(Section)
    #     .filter(Section.embedding is not None)  # Ignore sections without an embedding
    #     .order_by(func.pgv_distance(Section.embedding, target_vector))
    #     .limit(10)
    #     .all()
    # )

    # Print the results
    for section in closest_sections:
        print(section.text)
        print("----------------------------------------")
