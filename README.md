# Neko-chan 

**A horrifying slack-bot that you should probably never use (for a multitude of reasons!)**

![version](https://img.shields.io/badge/version-v0.2.5-blue.svg)

### How to use it
You'll need a bot user key for your slack workspace, and you'll need the bot's user ID

You'll also need an API key for _your_ user account because the channel management for the 
bot are written so _incredibly_ not the way they should be done (but it was an interesting 
exercise in working around limitations I suppose)

You'll also need the User ID of the User whose API key ends up in this program because they will
(probably) be an admin for the bot and control things like whitelisting and unwhitelisting and adding
the bot to channels via the `channels.invite` api endpoint. The workspace I wrote this app for doesn't 
allow my account access to the `channels.kick` command so there's no ability for you to kick this 
bot form a channel - you can just sort of, _silence_ it I guess. who knows.

#### Whitelist and admin files
You'll need to create a `whitelist.txt` file and an `admins.txt` file - put your user's ID in the 
admins file and the channel id of the DMs channel in the whitelists file (at the very least)

### What is this for
Neko-chan is a lighthearted chat bot that also pulls images from the SFW collection at 
[nekos.life](http://nekos.life/). _There are no easter eggs in this project to allow for
someone to get an NSFW image from the API unless they modify the source._ This bot has no 
real purpose.

### Why does this exist
No good reason

### License
This bad boy is available to you all under an MIT license.
tl;dr - feel free do to whatever with this so long as you link to this project.

### This project caused me inexplicable pain and unrecoverable injury, who do I talk to?
email me at idontfeelsafe@computerscience.house and I'll promptly ignore you
