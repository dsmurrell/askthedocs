import hashlib
import json
import re

from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from rich import print as rprint
from rich.syntax import Syntax

# # Make sure to download required NLTK data
# nltk.download("punkt")
# nltk.download("stopwords")
# nltk.download("wordnet")


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
    # Lowercase
    text = text.lower()

    # Remove special characters and digits
    text = re.sub(r"[^a-z\s]+", "", text)

    # Remove newline characters and other whitespaces
    text = text.replace("\n", " ").replace("\r", " ").replace("\t", " ")

    # Tokenization
    tokens = word_tokenize(text)

    # Remove stopwords (optional)
    if remove_stopwords:
        stop_words = set(stopwords.words("english"))
        tokens = [token for token in tokens if token not in stop_words]

    # Lemmatization (optional)
    if lemmatize:
        lemmatizer = WordNetLemmatizer()
        tokens = [lemmatizer.lemmatize(token) for token in tokens]

    # Join tokens back into a single string
    preprocessed_text = " ".join(tokens)

    return preprocessed_text


# # Example usage
# text = "This is an example text with newline characters,\n numbers like 123, and special characters like @#$%^&*()."
# preprocessed_tokens = preprocess_text(text)
# print(preprocessed_tokens)

def remove_html_tags(text):
    # Remove HTML tags using regex
    html_pattern = r"<[^>]+>"
    text = re.sub(html_pattern, "", text)
    return text

def clean_no_html_text(text):
    # Remove newline characters and other whitespaces
    text = text.replace("\n", " ").replace("\r", " ").replace("\t", " ")

    # Remove excessive whitespace
    text = re.sub(r"\s+", " ", text).strip()

    return text


# # Example usage
# context = "This is an example of context text\nwith newline characters, extra spaces,    and other whitespaces.\n"
# prepared_context = clean_no_html_text(context)
# print(prepared_context)
