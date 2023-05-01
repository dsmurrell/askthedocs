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
    text = re.sub(r"\[//\]:\s*#\s*\([^)]*\)", "", text)
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


# def preprocess_text(text, remove_stopwords=True, lemmatize=True, use_ner=True):
#     # Replace URLs
#     text = re.sub(r"http\S+|www\S+|https\S+", "", text, flags=re.MULTILINE)

#     # Apply Named Entity Recognition (NER) to preserve capitalization
#     if use_ner:
#         doc = nlp(text)
#         preserved_tokens = []

#         for token in doc:
#             if token.ent_type_ in {
#                 "ORG",
#                 "GPE",
#                 "NORP",
#             }:  # organizations, geopolitical entities, and nationalities
#                 preserved_tokens.append(token.text)
#             else:
#                 preserved_tokens.append(token.text.lower())

#         text = " ".join(preserved_tokens)

#     # Remove special characters, but keep digits and certain characters like '-', '/'
#     text = re.sub(r"[^a-zA-Z0-9\s\-\/]+", "", text)

#     # Remove newline characters and other whitespaces
#     text = text.replace("\n", " ").replace("\r", " ").replace("\t", " ")

#     # Tokenization
#     tokens = word_tokenize(text)

#     # Remove stopwords (optional)
#     if remove_stopwords:
#         stop_words = set(stopwords.words("english"))
#         tokens = [token for token in tokens if token not in stop_words]

#     # Lemmatization (optional)
#     if lemmatize:
#         lemmatizer = WordNetLemmatizer()
#         tokens = [lemmatizer.lemmatize(token) for token in tokens]

#     # Join tokens back into a single string
#     preprocessed_text = " ".join(tokens)

#     return preprocessed_text


# def preprocess_text(text, remove_stopwords=True, lemmatize=True):
#     # Lowercase
#     text = text.lower()

#     # Remove URLs
#     text = re.sub(r"http\S+|www\S+|https\S+", "", text, flags=re.MULTILINE)

#     # Remove special characters and digits
#     text = re.sub(r"[^a-z\s]+", "", text)

#     # Remove newline characters and other whitespaces
#     text = text.replace("\n", " ").replace("\r", " ").replace("\t", " ")

#     # Tokenization
#     tokens = word_tokenize(text)

#     # Remove stopwords (optional)
#     if remove_stopwords:
#         stop_words = set(stopwords.words("english"))
#         tokens = [token for token in tokens if token not in stop_words]

#     # Lemmatization (optional)
#     if lemmatize:
#         lemmatizer = WordNetLemmatizer()
#         tokens = [lemmatizer.lemmatize(token) for token in tokens]

#     # Join tokens back into a single string
#     preprocessed_text = " ".join(tokens)

#     return preprocessed_text


# def preprocess_text(text, remove_stopwords=True, lemmatize=True):
#     # Lowercase
#     text = text.lower()

#     # Remove special characters and digits
#     text = re.sub(r"[^a-z\s]+", "", text)

#     # Remove newline characters and other whitespaces
#     text = text.replace("\n", " ").replace("\r", " ").replace("\t", " ")

#     # Tokenization
#     tokens = word_tokenize(text)

#     # Remove stopwords (optional)
#     if remove_stopwords:
#         stop_words = set(stopwords.words("english"))
#         tokens = [token for token in tokens if token not in stop_words]

#     # Lemmatization (optional)
#     if lemmatize:
#         lemmatizer = WordNetLemmatizer()
#         tokens = [lemmatizer.lemmatize(token) for token in tokens]

#     # Join tokens back into a single string
#     preprocessed_text = " ".join(tokens)

#     return preprocessed_text


def remove_html_tags(text):
    # Remove HTML tags using regex
    html_pattern = r"<[^>]+>"
    text = re.sub(html_pattern, "", text)
    return text


# def clean_no_html_text(text):
#     # Remove newline characters and other whitespaces
#     text = text.replace("\n", " ").replace("\r", " ").replace("\t", " ")

#     # Remove excessive whitespace
#     text = re.sub(r"\s+", " ", text).strip()

#     return text
