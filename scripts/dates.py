import re
from datetime import datetime


def convert_dates(text, default_year="2023"):
    patterns = [
        (
            r"(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})",
            "%m/%d/%Y",
        ),  # MM/DD/YYYY or MM-DD-YYYY
        (
            r"(\d{1,2}) (?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)[a-z]* (\d{4})",
            "%d %B %Y",
        ),  # DD Month YYYY
        (
            r"(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)[a-z]* (\d{1,2})(?:st|nd|rd|th)?[ ,]*",
            "%B %d",
        ),  # Month DD
    ]

    def replace_date(match):
        for pattern, date_format in patterns:
            try:
                date_obj = datetime.strptime(match.group(), date_format)
                if len(date_format) == 6:  # Month DD format
                    return date_obj.replace(year=int(default_year)).strftime("%Y-%m-%d")
                else:
                    return date_obj.strftime("%Y-%m-%d")
            except ValueError:
                pass
        return match.group()

    for pattern, _ in patterns:
        text = re.sub(pattern, replace_date, text, flags=re.IGNORECASE)

    return text


# Sample text containing dates in different formats
sample_text = "Summarise the standup update from February 28th."

# Convert dates in the sample text
converted_text = convert_dates(sample_text)

print(converted_text)
