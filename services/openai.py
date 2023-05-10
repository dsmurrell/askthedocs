import re
import sys
import time

import openai
from sqlalchemy import and_, select
from sqlalchemy.orm import Session
from termcolor import colored

from alchemy.models import Node, Question
from config import config
from helpers import preprocess_text

openai.api_key = config["openai_key"]


def fetch_and_save_embeddings(session: Session):
    # Select nodes without an embedding
    nodes_without_embedding = session.query(Node).filter(Node.embedding.is_(None)).all()
    sys.stdout.write(f"Fetching embeddings for {len(nodes_without_embedding)} nodes...")

    for i, node in enumerate(nodes_without_embedding):
        sys.stdout.write(".")
        sys.stdout.flush()
        if i % 100 == 0:
            print(i)
        if len(node.text) < 8000:
            # Fetch an embedding for the node
            res = openai.Embedding.create(
                input=node.text_processed,
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
    print("Original Query:", colored(query, "red"))
    processed_query = preprocess_text(query)
    print("Processed Query:", colored(processed_query, "blue"))

    res = openai.Embedding.create(
        input=processed_query,
        model="text-embedding-ada-002",
    )
    query_embedding = res["data"][0]["embedding"]

    match_count = 8
    similarity_threshold = (
        0.75  # try and use a similarity threshold of 0.75 in the query
    )

    query = session.scalars(
        select(Node)
        .order_by(Node.embedding.l2_distance(query_embedding))
        .limit(match_count)
    )

    # Define the distance expression
    distance_expression = Node.embedding.l2_distance(query_embedding)

    # Modify your query
    query = session.execute(
        select(Node)
        .add_columns(distance_expression.label("distance"))
        .where(and_(Node.text_length < 7700, Node.text_length > 300))
        .order_by(distance_expression)
        .limit(match_count)
    )

    # Execute the query and store the results in a variable
    query_results = query.all()

    # Access the results
    for result in query_results:
        node = result[0]
        distance = result[1]
        print("Node text_processed:", colored(node.text_processed, "blue"))
        print("Document URL:", colored(node.document.url, "green"))
        print("Node Distance:", colored(distance, "green"))
        print("Node Text Length:", colored(node.text_length, "green"))
        print("Node Text Cleaned:", colored(node.text_cleaned, "yellow"))
        print("----------------------------------------")

    # Execute the query and fetch the results
    closest_nodes = [node for (node, _) in query_results]

    total_word_count = sum(len(node.text.split()) for node in closest_nodes)

    print(f"Total word count: {total_word_count}")

    return closest_nodes


def get_first_completion(query: str, context: str):
    messages = [
        {
            "role": "system",
            "content": """You are a very enthusiastic Sano Genetics representative who loves to help people!""",
        },
        {
            "role": "user",
            "content": f"""Given the following sections from the Sano Genetics documentation, answer the question using only that information. If you are unsure and the answer is not explicitly written in the documentation, say "Sorry, don't know how to help with that."

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


def get_second_completion(query: str, context: str):
    messages = [
        {
            "role": "system",
            "content": """You are a very enthusiastic Sano Genetics representative who loves quote the sections that will help people the most.""",
        },
        {
            "role": "user",
            "content": f"""Given the following sections from the Sano Genetics documentation, respond strictly in the format [x, y] where these are the number of the sections that help answer the question the most. A program will use the answer... so make sure to adhere strictly to the format [x, y] where x and y are section numbers from 1 to 10. Only provide the two most useful section numbers.

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


def replace_date_completion(query: str):
    messages = [
        {
            "role": "system",
            "content": """You are a date finder and converter.""",
        },
        {
            "role": "user",
            "content": f"""In the question below, can you find any dates and replace them with the format YYYY-MM-DD. If the year isn't specified assume that it is 2023. The respond with the exact same question but with the dates replaced with the format YYYY-MM-DD. Question follows:

{query}
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


def get_query_response(session: Session, query_string: str, username: str, type: str):
    # The pattern to match: <@ followed by a combination of uppercase letters and numbers, and then >
    pattern = r"<@[A-Z0-9]+>"

    # Search for the pattern and extract it
    matched_pattern = re.search(pattern, query_string)

    matched_username = None
    if matched_pattern:
        matched_username = matched_pattern.group(0)
        # Substitute the pattern with an empty string
        stripped_query = re.sub(pattern, "", query_string)
    else:
        stripped_query = query_string
        print("No pattern found in the query string.")

    # Remove extra whitespace (if any)
    stripped_query = " ".join(stripped_query.split())

    # stripped_query = replace_date_completion(stripped_query)

    closest_nodes = find_closest_nodes(session, stripped_query)

    # Initialize the context string.

    context_string = ""

    # Define a separator between nodes.
    separator = (
        " "  # You can also use "\n" for newlines, or any other string as a separator.
    )

    # Iterate through the Section objects and append the text field to the context string.
    for i, node in enumerate(closest_nodes):
        context_string += f"{i+1}> {node.text_cleaned} \n\n"

    # Remove the trailing separator.
    context_string = context_string.rstrip(separator)

    print("Context String:", colored(context_string, "yellow"))

    first_completion = get_first_completion(stripped_query, context_string)

    useful_urls_string = ""
    second_completion = ""
    try:
        second_completion = get_second_completion(stripped_query, context_string)

        # Remove the brackets and split the string by commas
        numbers_str = second_completion.strip("[]").split(",")

        # Convert the list of strings into a list of integers
        vector_of_ints = [int(number.strip()) for number in numbers_str]

        useful_urls = []
        for num in vector_of_ints:
            useful_urls.append(closest_nodes[num - 1].document.url)
        for url in set(useful_urls):
            url = url.replace("-", "")
            useful_urls_string += f"https://www.notion.so/sanogenetics/{url}" + "\n"

        if "sorry" not in first_completion.lower():
            first_completion += "\n\n" + "Source:\n" + useful_urls_string

    except:
        pass

    question = Question(
        username=matched_username,
        body_username=username,
        method=type,
        platform="slack",
        query_string=query_string,
        stripped_query=stripped_query,
        context_string=context_string,
        first_completion=first_completion,
        second_completion=second_completion,
        useful_urls_string=useful_urls_string,
    )
    session.add(question)
    session.commit()
    return first_completion
