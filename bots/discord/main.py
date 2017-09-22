from bot import DiscordBot
import logging
import hashlib
import os
import utils

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

discord_bot = None

def loop():
    """ Loop function """
    # Update mqtt loop
    discord_bot.update_loop()

    discord_bot.publish("Hello!")
    discord_bot.publish("Hello!", topic="/hangout/calle/jonte/")




def on_message(topic, message):
    ''' Function called on message received'''
    logger.debug("Botty got something!")
    logger.debug("".join([topic, " : ", message]))


def on_connect():
    """ On connect function. Called when connected to broker """
    logger.debug("Botty is connected!")


def main():
    global discord_bot
    discord_bot = DiscordBot(on_connect, on_message)

    config_path = os.path.realpath(os.path.join(os.path.dirname(__file__),
                                                'configuration.json'))
    configuration = utils.fetch_json_file_as_dict(config_path)
    discord_bot.setup(configuration)
    discord_bot.subscribe("/hangouts/#")

    while True:
        loop()

if __name__ == "__main__":
    main()
