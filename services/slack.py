import random

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from alchemy.database import get_db_session
from config import config
from services.openai import get_query_response

# Initialize your app with your token and signing secret
app = App(token=config["slack_bot_token"])


def get_random_response():
    responses = [
        "Starting my search for the best answer for you now! 🚀",
        "Initiating the process to find the most suitable response... 🌟",
        "Just starting to look for the right answer for your question... ⚙️",
        "Beginning to work on providing the most helpful answer for you... 🏃‍♂️",
        "Starting to process your request and gather the information you need... 🔍",
        "Now sorting through my knowledge to find the perfect response... 📚",
        "Initiating my search for the most accurate response for your query... 🎯",
        "Let me begin looking for the best fit for your question... 🧩",
        "Starting to fetch the most relevant information for your question... 🌐",
        "I'm on it! Just beginning to find the right response for you... ⌛",
        "Allow me a moment to start gathering the most accurate response... 🧠",
        "Beginning my search for the best answer for you now. Hang in there! 🕵️‍♂️",
        "Starting to work on your response! 🖌️",
        "Your answer is now in the works! I'll make sure it's helpful... ⚡",
        "Please wait as I start searching my database for the most appropriate response... 📖",
        "Stand by! Initiating the retrieval of the information you need... 📡",
        "Just starting to work on your request! Your answer will be ready soon... 🚧",
        "Initiating my search to ensure my response is accurate and helpful... 📊",
        "Beginning to look for the right answer for you now... 🧪",
        "Allow me a moment to start collecting the best response for your question... 🎁",
        "Kicking off my search for your answer now! 🏁",
        "Just starting to dig into your question... 🕳️",
        "Beginning my quest to find the perfect answer for you... 🗺️",
        "Now commencing the search for the most relevant response... 🔎",
        "Embarking on the journey to find the information you're looking for... 🧭",
        "Launching my search for the ideal response to your query... 🛫",
        "Starting to explore my knowledge base for your answer... 🏞️",
        "Initiating the hunt for the best response to your question... 🐾",
        "Setting off to discover the most accurate answer for you... ⛵",
        "Just beginning my investigation to find the ideal response... 🕵️",
        "Commencing the search for the most comprehensive reply... 🌄",
        "Now diving into the task of finding the best answer for you... 🏊",
        "Starting my mission to locate the most helpful response... 🚁",
        "Just initiating the process of uncovering the perfect reply... 🎢",
        "Ready, set, go! Looking for your answer now... 🚦",
        "Now beginning to navigate through my knowledge to find your answer... 🗺️",
        "Setting sail on my journey to find the information you need... ⛵",
        "Starting to probe my database for the right response... 🌌",
        "Now launching my search for the most suitable reply... 🚀",
        "Embarking on my mission to find the best answer for you... 🚂",
        "Initiating the expedition to discover your perfect response... 🏜️",
        "Commencing the quest for the ultimate answer to your question... 🏰",
        "Just starting to sift through my resources for your answer... 🏗️",
        "Now entering the search mode to find the best response... 🚪",
        "Initiating the operation to track down the ideal answer... 🎯",
        "Kicking off the process of finding the most relevant reply... ⚽",
        "Launching my investigation to uncover the right response... 🚀",
        "Beginning my search for the most fitting answer to your query... 🌠",
        "Ready to roll! Starting to look for your answer now... 🚴",
        "Jumping into action to find the best response for you... 🤸",
        "Setting out on my mission to uncover the perfect reply... 🚶‍♀️",
        "Now initiating the process of finding the most accurate response... 🕰️",
        "Just starting to assemble the best answer for you... 🧩",
        "Diving in to explore my knowledge and find your answer... 🐬",
        "Getting the ball rolling to locate the best response... 🎱",
        "Embarking on the adventure to discover your ideal answer... 🎢",
        "Ready to start the hunt for the perfect response to your question... 🔦",
        "Now delving into my database to find the most helpful reply... 🗄️",
        "Just starting my research to locate the right answer... 📚",
        "Gearing up to find the most suitable response for your query... 🚲",
        "Now turning the key to unlock the perfect answer for you... 🔑",
        "Beginning to search high and low for your ideal response... 🎈",
    ]
    return random.choice(responses)


# Listen for messages in the Slack channel
@app.event("app_mention")
def command_handler(body, say):
    print(f"got the event: {body}")
    # Extract the message text from the event payload
    query = body["event"]["text"]

    session = get_db_session().__next__()

    say(get_random_response())

    # You can add any additional filtering or conditions to respond to specific messages here.
    response = get_query_response(session, query)
    print(response)

    # Reply in Slack with the message.
    say(response)


def start_slack_bot():
    handler = SocketModeHandler(app, config["slack_app_token"])
    handler.start()
    handler.start()
