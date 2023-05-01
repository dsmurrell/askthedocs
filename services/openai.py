import re
import sys
import time

import openai
from sqlalchemy import select
from sqlalchemy.orm import Session
from termcolor import colored

from alchemy.models import Node
from config import config

openai.api_key = config["openai_key"]


def fetch_and_save_embeddings(session: Session):
    # Select nodes without an embedding
    nodes_without_embedding = session.query(Node).filter(Node.embedding.is_(None)).all()
    sys.stdout.write(f"Fetching embeddings for {len(nodes_without_embedding)} nodes...")

    for node in nodes_without_embedding:
        sys.stdout.write(".")
        sys.stdout.flush()
        if len(node.text) < 4000:
            # Fetch an embedding for the node
            res = openai.Embedding.create(
                input=node.text,
                model="text-embedding-ada-002",
            )
            embedding = res["data"][0]["embedding"]
            node.embedding = embedding
            session.add(node)
            session.commit()

            # Add a delay of 0.5 seconds to stay well within the rate limit of 150 per minute
            time.sleep(0.5)

    print("Done!")


def find_closest_nodes(session: Session, query: str):
    res = openai.Embedding.create(
        input=query,
        model="text-embedding-ada-002",
    )
    query_embedding = res["data"][0]["embedding"]

    match_count = 30
    similarity_threshold = 0.75
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
        select(Node)
        # .where(Node.embedding.l2_distance(query_embedding) <= distance_threshold)
        .order_by(Node.embedding.l2_distance(query_embedding)).limit(match_count)
    )

    # Define the distance expression
    distance_expression = Node.embedding.l2_distance(query_embedding)

    # Modify your query
    query = session.execute(
        select(Node)
        .add_columns(distance_expression.label("distance"))
        .where(Node.text_length < 1500)
        .order_by(distance_expression)
        .limit(match_count)
    )

    # Access the results
    for result in query:
        node = result[0]
        distance = result[1]
        print("Node ID:", colored(node.id, "green"))
        print("Node Distance:", colored(distance, "green"))
        print("Node Text Length:", colored(node.text_length, "green"))
        print(node.text)
        print("----------------------------------------")

    # query = None

    # # Look up the match_count nodes with an embedding closest to the query embedding
    # query = session.scalars(
    #     select(Node)
    #     .order_by(Node.embedding.l2_distance(query_embedding))
    #     .limit(match_count)
    # )

    # Execute the query and fetch the results
    closest_nodes = query.all()

    total_word_count = sum(len(node.text.split()) for node in closest_nodes)

    print(f"Total word count: {total_word_count}")

    # Print the results
    for node in closest_nodes:
        print(f"Node at distance: {node.embedding.l2_distance(query_embedding)}")
        print(colored(node.text, "green"))
        print("----------------------------------------")

    return closest_nodes


def get_first_completion(query: str, context: str):
    messages = [
        {
            "role": "system",
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
""",
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
    closest_nodes = find_closest_nodes(session, query)

    # Initialize the context string.

    context_string = ""

    # Define a separator between nodes.
    separator = (
        " "  # You can also use "\n" for newlines, or any other string as a separator.
    )

    # Iterate through the Section objects and append the text field to the context string.
    for node in closest_nodes:
        context_string += node.text + separator

    # Remove the trailing separator.
    context_string = context_string.rstrip(separator)

    # The pattern to match: <@ followed by a combination of uppercase letters and numbers, and then >
    pattern = r"<@[A-Z0-9]+>"

    # Substitute the pattern with an empty string
    stripped_query = re.sub(pattern, "", query)

    # Remove extra whitespace (if any)
    stripped_query = " ".join(stripped_query.split())

    return "YO"

    # return get_first_completion(stripped_query, context_string)
