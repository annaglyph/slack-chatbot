import os
import time
from slackclient import SlackClient
import re
import random
from chatterbot import ChatBot
from datetime import datetime
import forecastio
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
logger.addHandler(ch)

# Constants
READ_WEBSOCKET_DELAY = os.environ.get("READ_WEBSOCKET_DELAY") # delay between reading from firehose

# Slack API 
SLACK_BOT_ID = os.environ.get("SLACK_BOT_ID")
SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")

# Weather service API key and target location
FORECASTIO_API_KEY = os.getenv('FORECASTIO_API_KEY')
DARKSKY_API_KEY = os.getenv('DARKSKY_API_KEY')
LAT = os.getenv('LAT')
LNG = os.getenv('LNG')

forecast = forecastio.load_forecast(DARKSKY_API_KEY, LAT, LNG)

byHour = forecast.hourly()
logger.info('Forecast Summary: {}'.format(byHour.summary))

AT_BOT = "<@" + SLACK_BOT_ID + ">"

# Create a new instance of a ChatBot
chatbot = ChatBot(
    "Ebot",
    storage_adapter="chatterbot.storage.SQLStorageAdapter",
    logic_adapters=[
        "chatterbot.logic.MathematicalEvaluation",
        'chatterbot_weather.WeatherLogicAdapter',
        # "chatterbot.logic.TimeLogicAdapter",
        "chatterbot.logic.BestMatch"
    ],
    database = "database.db",
    trainer = 'chatterbot.trainers.ChatterBotCorpusTrainer',
    forecastio_api_key = FORECASTIO_API_KEY
)

#chatbot.train('chatterbot.corpus.english')
chatbot.train('chatterbot.corpus.custom')

# instantiate Slack & Twilio clients
slack_client = SlackClient(SLACK_BOT_TOKEN)

userList = {}
api_call = slack_client.api_call("users.list")
if api_call.get('ok'):
    # retrieve all users
    users = api_call.get('members')
    for user in users:
    	userCode = '{0}'.format(user.get('id'))
    	try:
    		if user['profile']['display_name'] != '':
    			userList[userCode] = '%s' % user['profile']['display_name']
    		else:
    			userList[userCode] = '%s' % user['real_name']
    	except KeyError:
    		pass
			

def handle_command(command, channel, userID):
    """
        Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
    """
    
    attachments = None
    userName = userList[userID]
    response = '%s' % chatbot.get_response(command)
    	
    slack_client.api_call("chat.postMessage", channel=channel, text=response, attachments=attachments, as_user=True)


def parse_slack_output(slack_rtm_output):
    """
        The Slack Real Time Messaging API is an events firehose.
        this parsing function returns None unless a message is
        directed at the Bot, based on its ID.
    """
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output and AT_BOT in output['text']:
                # return text after the @ mention, whitespace removed
                return output['text'].split(AT_BOT)[1].strip().lower(), \
                       output['channel'], \
                       output['user']
    return None, None, None


if __name__ == "__main__":
    READ_WEBSOCKET_DELAY = 2 # 2 second delay between reading from firehose
    if slack_client.rtm_connect():
        print("Slack-ChatBot is connected and running!")
        while True:
            command, channel, userID = parse_slack_output(slack_client.rtm_read())
            if command and channel:
                handle_command(command, channel, userID)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")