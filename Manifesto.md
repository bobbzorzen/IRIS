# Manifesto
## This document should describe the general idea and technologies involved in this project(Mostly for development/notes purpouses)

### Technologies used
The general communication between modules like bot -> main should be socket based as standard.
Perhaps a more passive approach could be created by making the main module a giant rest api which bots and frontends poll constantly

The main module will be/is written in Python or Node.js... Depends on what seems easiest when it comes to socket communication.
The bots should be written in whatever language best suits the client at hand, hangout and skype bot will be written in node.js whilst IRC bot will be written i Python


### General idea of the product
I'm thinking that bots should be completely independant and that they should be startable from the frontends by sending commands to the main which by running a predefined commandline specified by each bot which starts the bot and lets it establish a connection with main and sends startup confirmation to frontend
