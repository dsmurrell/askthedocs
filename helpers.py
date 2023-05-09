import hashlib
import json
import re

import spacy
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from rich import print as rprint
from rich.syntax import Syntax

# # Make sure to download required NLTK data
# nltk.download("punkt")
# nltk.download("stopwords")
# nltk.download("wordnet")

# need to run "python -m spacy download en_core_web_sm" first
# Load the spaCy English model
nlp = spacy.load("en_core_web_sm")


def compute_hash(data):
    if isinstance(data, dict):
        data = json.dumps(data, sort_keys=True)
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def pretty_print_dict(d):
    json_string = json.dumps(d, sort_keys=True, indent=4)
    syntax_colored_json = Syntax(
        json_string, "json", theme="solarized-dark", line_numbers=False
    )
    rprint(syntax_colored_json)


def preprocess_text(text, remove_stopwords=True, lemmatize=True):
    # Remove URLs
    text = re.sub(r"http\S+|www\S+|https\S+", "", text, flags=re.MULTILINE)

    # Remove lines with specific patterns
    # remove this type of pattern [//]: # (child_page is not supported)
    text = re.sub(r"\[//\]:\s*#\s*\([^)]*\)", "", text)
    # remove image links
    text = re.sub(r"!\[[^\]]*\]\([^\)]*\)", "", text)

    # Replace filenames with their human-readable part
    text = re.sub(r"\[([^\]]+)\]\([a-zA-Z0-9]+_([^\)]+)\)", r"\1", text)

    # Remove special characters, but keep digits and certain characters like '-', '/'
    text = re.sub(r"[^a-zA-Z0-9\s\-\/]+", "", text)

    # Remove newline characters and other whitespaces
    text = text.replace("\n", " ").replace("\r", " ").replace("\t", " ")

    # Tokenization
    tokens = word_tokenize(text)

    # Lowercase tokens with the first letter capitalized and the rest lowercase
    tokens = [token.lower() if token.istitle() else token for token in tokens]

    # Remove stopwords (optional)
    if remove_stopwords:
        stop_words = set(stopwords.words("english"))
        tokens = [token for token in tokens if token.lower() not in stop_words]

    # Lemmatization (optional)
    if lemmatize:
        lemmatizer = WordNetLemmatizer()
        tokens = [lemmatizer.lemmatize(token) for token in tokens]

    # Join tokens back into a single string
    preprocessed_text = " ".join(tokens)

    return preprocessed_text


def remove_html_tags(text):
    # Remove HTML tags using regex
    html_pattern = r"<[^>]+>"
    text = re.sub(html_pattern, "", text)
    return text


# def clean_text(text):
#     # Remove lines with specific patterns
#     # remove this type of pattern [//]: # (child_page is not supported)
#     text = re.sub(r"\[//\]:\s*#\s*\([^)]*\)", "", text)
#     # remove image links
#     text = re.sub(r"!\[[^\]]*\]\([^\)]*\)", "", text)

#     return text


# def clean_text(text):
#     # Remove lines with specific patterns
#     # remove this type of pattern [//]: # (child_page is not supported)
#     text = re.sub(r"\[//\]:\s*#\s*\([^)]*\)", "", text)

#     # remove image links
#     text = re.sub(r"!\[[^\]]*\]\([^\)]*\)", "", text)

#     # Simplify links: ([https://example.com](https://example.com)) => (https://example.com)
#     text = re.sub(r"\[([^\]]*?)(\([^\)]+\))\]\([^\)]+\)", r"\1\2", text)

#     # Remove special characters and extra spaces
#     text = re.sub(r"[�*|]", "", text)
#     text = re.sub(r"\s{2,}", " ", text)

#     # Remove extra newlines
#     text = re.sub(r"\n{3,}", "\n\n", text)

#     return text


# def clean_text(text):
#     # Remove lines with specific patterns
#     # remove this type of pattern [//]: # (child_page is not supported)
#     text = re.sub(r"\[//\]:\s*#\s*\([^)]*\)", "", text)

#     # remove image links
#     text = re.sub(r"!\[[^\]]*\]\([^\)]*\)", "", text)

#     # Simplify links: ([https://example.com](https://example.com)) => (https://example.com)
#     text = re.sub(r"\[\s*(https?:\/\/[^\s\]]+)\s*\]\(\s*\1\s*\)", r"(\1)", text)

#     # Remove special characters and extra spaces
#     text = re.sub(r"[�*|]", "", text)
#     text = re.sub(r"\s{2,}", " ", text)

#     # Remove extra newlines
#     text = re.sub(r"\n{3,}", "\n\n", text)

#     return text


# def clean_text(text):
#     # Remove lines with specific patterns
#     # remove this type of pattern [//]: # (child_page is not supported)
#     text = re.sub(r"\[//\]:\s*#\s*\([^)]*\)", "", text)

#     # remove image links
#     text = re.sub(r"!\[[^\]]*\]\([^\)]*\)", "", text)

#     # Simplify links: ([https://example.com](https://example.com)) => (https://example.com)
#     text = re.sub(r"\[\s*((?:https?:\/\/)[^\s\]]+)\s*\]\(\s*\1\s*\)", r"(\1)", text)

#     # Remove special characters and extra spaces
#     text = re.sub(r"[�*|]", "", text)
#     text = re.sub(r"\s{2,}", " ", text)

#     # Remove extra newlines
#     text = re.sub(r"\n{3,}", "\n\n", text)

#     return text

# import re


# # WORKING REASONABLY
# def clean_text(text):
#     # Remove lines with specific patterns
#     # remove this type of pattern [//]: # (child_page is not supported)
#     text = re.sub(r"\[//\]:\s*#\s*\([^)]*\)", "", text)

#     # remove image links
#     text = re.sub(r"!\[[^\]]*\]\([^\)]*\)", "", text)

#     # Simplify links: ([https://example.com](https://example.com)) => (https://example.com)
#     text = re.sub(
#         r"\[?\[\s*((?:https?:\/\/)[^\s\]]+?)\s*\]\(?\s*\1\s*\)?", r"(\1)", text
#     )

#     # Remove special characters and extra spaces
#     text = re.sub(r"[�*|]", "", text)
#     text = re.sub(r"\s{2,}", " ", text)

#     # Remove extra newlines
#     text = re.sub(r"\n{3,}", "\n\n", text)

#     return text


# import re


# def clean_text(text):
#     # Remove lines with specific patterns
#     # remove this type of pattern [//]: # (child_page is not supported)
#     text = re.sub(r"\[//\]:\s*#\s*\([^)]*\)", "", text)

#     # remove image links
#     text = re.sub(r"!\[[^\]]*\]\([^\)]*\)", "", text)

#     # Simplify links: ([https://example.com](https://example.com)) => (https://example.com)
#     text = re.sub(
#         r"\[?\[?\s*((?:https?:\/\/)[^\s\]]+?)\s*\]\]?\(?\s*\1\s*\)?", r"(\1)", text
#     )

#     # Remove special characters and extra spaces
#     text = re.sub(r"[�*|]", "", text)
#     text = re.sub(r"\s{2,}", " ", text)

#     # Remove extra newlines
#     text = re.sub(r"\n{3,}", "\n\n", text)

#     return text


# trying a test PR

import re


def clean_text(text):
    # Remove lines with specific patterns
    # remove this type of pattern [//]: # (child_page is not supported)
    text = re.sub(r"\[//\]:\s*#\s*\([^)]*\)", "", text)

    # remove image links
    text = re.sub(r"!\[[^\]]*\]\([^\)]*\)", "", text)

    # Simplify links: ([https://example.com](https://example.com)) => (https://example.com)
    text = re.sub(
        r"\[?\[\s*((?:https?:\/\/)[^\s\]]+?)\s*\]\(?\s*\1\s*\)?", r"(\1)", text
    )

    # Remove extra parentheses and brackets around links:
    # ((https://example.com)) => (https://example.com)
    # ([https://example.com]) => (https://example.com)
    # ((https://example.com)]) => (https://example.com)
    text = re.sub(r"\({1,2}\[?([^\)]+)\]?\){1,2}", r"(\1)", text)

    # Remove special characters and extra spaces
    text = re.sub(r"[�*|]", "", text)
    text = re.sub(r"\s{2,}", " ", text)

    # Remove extra newlines
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text
