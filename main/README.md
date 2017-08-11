# Main IRIS Communication module

This module handles recieiving, storing and forwarding of messages gathered by the bots

General concept is that the bots sends messages they recieve to the main module which stores them and notifies registered frontends that a message is available.
When the frontends recieve a message from the user they send them to the correct bot which posts the message in the appropriate channel.
All messages recieved and sent will be stored in a database for history purpouses