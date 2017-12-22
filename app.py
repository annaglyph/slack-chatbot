import os
import time
from slackclient import SlackClient
import re
import random
from chatterbot import ChatBot
from datetime import datetime
import forecastio

DARKSKY_API_KEY = "754a52e2db50d325b4bdce9b0ea93364"
forecastio_api_key = "754a52e2db50d325b4bdce9b0ea93364"

lat = -31.967819
lng = 115.87718

forecast = forecastio.load_forecast(DARKSKY_API_KEY, lat, lng)

byHour = forecast.hourly()
print (byHour.summary)
print (byHour.icon)

# Uncomment the following lines to enable verbose logging
# import logging
# logging.basicConfig(level=logging.INFO)

# starterbot's ID as an environment variable
#SLACK_BOT_ID = os.environ.get("SLACK_BOT_ID")

# constants
#SLACK_BOT_TOKEN = 'xoxb-249135592198-YtX3rx2YGpIz3UJ10sAPVwvp' #eikonbot user
SLACK_BOT_TOKEN = 'xoxb-250664593921-l5Taz1QzdMbo9wwFbuygkL0T' #e-bot user (via custom integration)
#SLACK_BOT_TOKEN = 'xoxb-249135592198-bOftyviI7hGScYQFRHpubfdr'
#SLACK_BOT_ID = 'U7B3ZHE5U' #eikonbot user
SLACK_BOT_ID = 'U7CKJHFT3' #e-bot user

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
    database = "/Users/Rus/Development/Python/Projects/eikonbot/eikonbot_database_new.db",
    trainer = 'chatterbot.trainers.ChatterBotCorpusTrainer',
    forecastio_api_key = "754a52e2db50d325b4bdce9b0ea93364"
)

#chatbot.train('chatterbot.corpus.english')
chatbot.train('chatterbot.corpus.custom')

# instantiate Slack & Twilio clients
#slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
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
for key, value in userList.items():
	print (key, value)
			

def handle_command(command, channel, userID):
    """
        Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
    """
    
    '''
    for key, value in userList.items():
    	print key, value
    '''
    
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
    READ_WEBSOCKET_DELAY = 1 # 2 second delay between reading from firehose
    if slack_client.rtm_connect():
        print("Eikon Bot is connected and running!")
        while True:
            command, channel, userID = parse_slack_output(slack_client.rtm_read())
            if command and channel:
                handle_command(command, channel, userID)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")