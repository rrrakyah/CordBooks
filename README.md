# CordBooks
### A bot to generate a Markov Chain for Discord

This bot, written in Python, fetches individual users messages histories and generates a random sentence.
#

### This bot has three functional commands:
``=fetch DAYS MESSAGES``

``=sus @SOMEONE/NICKNAME/NAME``

``=sussy ID``

``=info @SOMEONE/NICMANE/NAME


In order to be able to generate a text, you need to grow the database with a fetch, for example: ``=fetch 2 3000``.
This would fetch 3000 messages in the channel you sent the command in, starting from 2 days before today.


Once a user has enough entries in the database, you can do something like ``=sus kat`` or ``=sus @pie`` to generate a message based on their prior messages that have been fetched.

It is to be noted that ``$sus`` and ``$sussy`` are two diffrent commands and differ in their usage. ``$sussy`` uses an ID, incase someone has left the server, to generate their message. However this command isn't very functional and doesnt often work.
