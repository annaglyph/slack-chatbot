# Slack ChatBot

## Heroku

### Automated approach

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/anaglyph/slack-chatbot)

### Manual approach

#### Clone the repo

```
$ git clone git@github.com:anaglyph/slack-chatbot.git
$ cd slack-chatbot
```

#### Configure and deploy to Heroku

```
$ heroku create
$ heroku config:set \
    SLACK_BOT_ID= \
    SLACK_BOT_TOKEN= \
    DARKSKY_API_KEY= \
    FORECASTIO_API_KEY= \
    LAT= \
    LNG= \
    READ_WEBSOCKET_DELAY=
$ git push heroku master
```

## Docker

```
$ docker run -d \
    --name=slack-chatbot \
    -e SLACK_BOT_ID= \
    -e SLACK_BOT_TOKEN= \
    -e DARKSKY_API_KEY= \
    -e FORECASTIO_API_KEY= \
    -e LAT= \
    -e LNG= \
    -e READ_WEBSOCKET_DELAY=
    anaglyph/slack-chatbot
```
