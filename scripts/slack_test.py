import sys
from pathlib import Path

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

sys.path.append(str(Path(__file__).resolve().parent.parent))

from config import config

# Initialize your app with your token and signing secret
app = App(token=config["slack_bot_token"])


# Listen for messages in the Slack channel
@app.event("app_mention")
def command_handler(body, say):
    print(f"got the event: {body}")
    # Extract the message text from the event payload
    body["event"]["text"]

    # You can add any additional filtering or conditions to respond to specific messages here.

    # Reply with "That's great!"
    say("That's great!")


if __name__ == "__main__":
    # Set up the SocketModeHandler with your bot's token
    handler = SocketModeHandler(app, config["slack_app_token"])
    handler.start()
