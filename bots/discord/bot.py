import paho.mqtt.client as mqtt
import logging
import time
logger = logging.getLogger(__name__)


class DiscordBot:
    def __init__(self, connect_callback, message_callback):
        """ Constructor """
        self.on_message_callback = message_callback
        self.on_connect_callback = connect_callback


    def setup(self, configuration):
        """ Setup function"""
        logger.info(' '.join(["Attempting a connect to:",
                     configuration['mqtt']['broker'],
                     str(configuration['mqtt']['port'])]))
        self.loaded_configuration = configuration
        self.is_initial_connect = True
        self.mqtt_client = mqtt.Client(configuration['mqtt']['client_id'])
        self.mqtt_client.username_pw_set(configuration['mqtt']['user'], configuration['mqtt']['password'])
        self.mqtt_client.on_connect = self.__on_connect
        self.mqtt_client.on_message = self.__on_message
        self.mqtt_client.connect(configuration['mqtt']['broker'],
                                 configuration['mqtt']['port'],
                                 60)
        self.delay = configuration['communication_delay']
        self.bot_topic = configuration['mqtt']['bot_topic']

    def update_loop(self):
        """ Updates the mqtt loop - checking for messages """
        logger.debug("Loop Tick!")
        time.sleep(self.delay/1000)
        rc = self.mqtt_client.loop()
        if rc is not 0:
            logger.error("No connection!")
            self.mqtt_client.reconnect()

    def subscribe(self, topic):
        """ subscribe to a topic """
        self.mqtt_client.subscribe(topic)

    def publish(self, message, topic=None):
        """ publish message """
        if topic is None:
            topic = self.bot_topic
        print(message)
        (result, mid) = self.mqtt_client.publish(topic, message)

        if result is not 0:
            logger.debug("Failed to publish message with topic:" + topic)
            return False

        else:
            logger.debug("Message sent with topic:" + topic)
            return True

    def __on_message(self, client, obj, message):
        """ When message is recieved from broker """
        logger.debug("Message received")
        if self.on_message_callback is not None:
            self.on_message_callback(str(message.topic), str(message.payload))
        else:
            logger.error("Define a valid on_message_callback_function!")

    def __publish_connect_message(self):
        """ Publish a greetings message on connect """
        logger.debug("Connect successfull")
        self.publish("Greetings from Discord Bot", topic=self.bot_topic)

    def __on_connect(self, client, userdata, flags, rc):
        """ Called when client connects to broker """
        logger.debug("Connected with rc code: " + str(rc))
        if rc == 0:
            if self.is_initial_connect:
                self.__publish_connect_message()
                self.is_initial_connect = False
            self.on_connect_callback()
        else:
            logger.error("Failed to connect to mqtt broker: " + str(rc))

    def get_configuration(self):
        """ Return the loaded configuration json as dict """
        return self.loaded_configuration
