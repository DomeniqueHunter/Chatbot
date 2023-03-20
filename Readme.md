# Chatbot

## Dependancies
I tested this bot on Linux. Raspbian (ARM) and Ubuntu (x86).
You need at least Python 3.6.9 with the packages requests websockets python-interface aiohttp

```bash
python3 -m pip install requests websockets python-interface aiohttp
```

## Install
To install the bot you need to checkout all the files. Put them in the direcory of your choice.
Go into the source folder (cd src/).
Create your config file through copying the example (cp config.json.example config.json).
Open the config with the editor of your choice and insert your _accoutname_ and the _account password_ and the _character_ the bot should use.
Start the Bot.
Join the chat and enter the channel where you want your bot.
Type /invite Botname and the bot will enter you channel.

## Docker Usage
If you want to use Docker, you just have to edit the config like in the Install Step. Then run ./build-container.sh to build the Docker Container.
If the Container is build, just run ist with ./run-container.sh


## Extensions
To extend the Bot, I recommend to write own plugins!
Documentatuon for this is an todo ;)
