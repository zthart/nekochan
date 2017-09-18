#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import random
import sys
import time

import requests
from slackclient import SlackClient

VERSION = 'v0.2'


class Nekochan():
    def __init__(self, bot_token, user_token):
        """A Silly chatbot without a point

        Args:
            bot_token (str): The Bot's API Token
            user_token (str): A User's API token for inviting the bot to channels

        Attributes:
            self.bot_token (str): The Bot's API Token
            self.user_token (str): A User's API token for inviting the bot to channels
            self.slack_client (SlackClient): The SlackClient object used to communicate with the API
            self.bot_id (str): The Bot's user ID
            self.at_bot (str): the coded string that replaces the '@botname' text in message objects
            self.whitelist_file (str): Path to the whitelist.txt file
            self.admins_file (str): Path to the admins.txt file
            self.kaomoji_list (:obj:`list`): A list of cute kaomoji!
            self.whitelist (:obj:`list`): The list of channel ID's the bot is allowed to speak in
            self.admins (:obj:`list`): The list of User IDs of the bot's admins
            self.blocking_for_admin (bool): determines whether the bot is expecting specific input from an admin
            self.blocking_issue (str): A string keyword for the specific blocking scenario
            self.blocking_data (str): The ID of a slack object to act on to resolve the blocking scenario
        """
        self.bot_token = bot_token
        self.user_token = user_token

        self.slack_client = SlackClient(self.bot_token)

        self.bot_id = self._retrieve_bot_id(self.slack_client)

        if self.bot_id is None:
            print('There was a problem getting my Bot ID! ( : ౦ ‸ ౦ : )')
            sys.exit(1)

        self.at_bot = '<@{0}>'.format(self.bot_id)

        self.whitelist_file = 'whitelist.txt'
        self.admins_file = 'admins.txt'

        self.kaomoji_list = [
            '(=^-ω-^=)',
            '(=^ ◡ ^=)',
            '(´• ω •`)ﾉ',
            '(*≧ω≦*)',
            '(=⌒‿‿⌒=)',
            '/ᐠ｡ꞈ｡ᐟ❁ \∫'
        ]

        self.whitelist = self._retrieve_whitelist()
        self.admins = self._retrieve_admins()

        self.blocking_for_admin = False
        self.blocking_issue = None
        self.blocking_data = None

    def _reset_block(self):
        self.blocking_for_admin = False
        self.blocking_issue = None
        self.blocking_data = None

    def _set_block(self, issue, data):
        self.blocking_for_admin = True
        self.blocking_issue = issue
        self.blocking_data = data

    @staticmethod
    def _retrieve_bot_id(slack_client):
        """Helper function to get bot ID

        This function uses a `SlackClient` object to retrieve a list of all users in the current workspace, and then 
        looks for a string match of its own name in order to store the ID assigned to it

        Args:
            slack_client (:obj:`SlackClient`): The SlackClient object through which to request all user info

        Returns:
            The (str) ID of the bot user if found, `None` otherwise
        """
        slack_response = slack_client.api_call('users.list')
        if slack_response['ok']:
            users = slack_response['members']
            for user in users:
                if 'name' in user and user['name'] == 'neko-chan':
                    return user['id']

        return None

    def _get_kaomoji(self):
        """Return a random kaomoji from the list of available kaomoji

        Returns:
            A random kaomoji (str) from the list of available kaomoji
        """
        return self.kaomoji_list[random.randint(0,len(self.kaomoji_list)-1)]

    def _retrieve_whitelist(self):
        """Get a list of the channel IDs of the channels in the whitelist

        Channels in the whitelist can be posted to - this list is not necessarily the same as a list of all channels 
        in which the bot is present. The bot may be in many channels outside of these, but only mentions in channels 
        in this list will be processed for a response

        Returns:
            A :obj:`list` of the slack channel IDs of the channels in which the bot is allowed to respond to mentions.
        """
        with open(self.whitelist_file, 'r') as w:
            whitelist = w.readlines()

        return [x.strip() for x in whitelist]

    def update_whitelist(self):
        """Update the whitelist content by re-reading the whitelist file
        """
        self.whitelist = self._retrieve_whitelist()

    def _retrieve_admins(self):
        """Get a list of the admins in the admins.txt file

        Returns:
            A :obj:`list` of the slack User IDs of the users with admin priveleges - not necessarily the same as a 
            list of admin level users in the workspace.
        """
        with open(self.admins_file, 'r') as a:
            admins = a.readlines()

        return [x.strip() for x in admins]

    def update_admins(self):
        """Update the admin list content by re-reading the admins file
        """
        self.admins = self._retrieve_admins()

    def _whitelist_channel(self, channel_id):
        """Add a channel's ID to the whitelist

        Args:
            channel_id (str): The ID of the channel to add to the whitelist
        """
        with open(self.whitelist_file, 'a') as w:
            w.write(channel_id.upper() + '\n')

        self.update_whitelist()

    def _add_admin(self, user_id):
        """Add a user's ID to the admin list

        Args:
            user_id (str): The ID of the user to add to the admin list
        """
        with open(self.admins_file, 'a') as a:
            a.write(user_id.upper() + '\n')

        self.update_admins()

    def _unwhitelist_channel(self, channel_id):
        """Remove a channel ID from the whitelist

        Args:
            channel_id (str): The channel ID to remove from the whitelist

        Returns:
            The channel ID (str) of the channel that was removed, `None` if no channel was removed
        """
        removed = None
        with open(self.whitelist_file, 'r') as w:
            channels = w.readlines()
        with open(self.whitelist_file, 'w') as w:
            for channel in channels:
                if channel != channel_id.upper()+'\n':
                    w.write(channel)
                else:
                    removed = channel
        self.update_whitelist()
        return removed

    def _remove_admin(self, user_id):
        """Removed a user ID fromt the admin list

        Args:
            user_id (str): The user ID to remove from the whitelist

        Returns:
            The user ID (str) of the user that was removed, `None` if no user was removed
        """
        removed = None
        with open(self.admins_file, 'r') as a:
            admins = a.readlines()
        with open(self.admins_file, 'w') as a:
            for admin in admins:
                if admin != user_id.upper()+'\n':
                    a.write(admin)
                else:
                    removed = admin
        self.update_admins()
        return removed

    def _response_switch(self, text, admin=False):
        """if/else ladder that filters on keywords in the mentioning user's message

        Args:
            text (str): The message as returned by the slack API
            admin (bool): True if the user whose message we're processing is on the bot's admin list

        Returns:
            a (str) response code if a known keyword is found, `None` otherwise
        """
        if admin:
            if self.blocking_for_admin:
                if 'yes' in text:
                    return 'confirm'
                else:
                    self._reset_block()
            if 'join' in text:
                return 'join'
            elif 'kick' in text or 'leave' in text:
                return 'leave'

        if 'sound' in text or 'noise' in text or 'say' in text or 'meow' in text or 'speak' in text:
            return 'nyaa'
        elif ' hi' in text or 'hello' in text:
            return 'greet'
        elif 'friend' in text or 'friends' in text or 'neko' in text or text.strip() == 'parse:':
            return 'image'
        elif 'lewd' in text or 'lewds' in text or 'fuck' in text:
            return 'lewd'
        elif 'hold hands' in text or 'handholding' in text:
            return 'hand'
        elif 'waifu' in text or 'best' in text:
            if 'are' in text or 'you' and 're' in text:
                if 'not' not in text:
                    return 'waifu-pos'
            return 'waifu-neg'
        elif 'tell' in text or 'whisper' in text:
            return 'whisper'
        else:
            return None

    def _parse_firehose(self, rtm_output):
        """Read through the most recent firehose output for mentions

        Args:
            rtm_output (:obj:`list`): a list of output from the slack rtm api

        Returns:
            dict: Message objects from the output with bot mentions
        """
        if rtm_output and len(rtm_output) > 0:
            for output in rtm_output:
                if output and 'text' in output and self.at_bot in output['text']:
                    print(json.dumps(output, indent=2))
                    return output

    def _retrieve_name(self, user, is_id=False):
        """Helper function to return first or real name, based on availability

        Args:
            user (:obj:`dict`): The json user object returned by the slack api

        Returns:
            str: Either the first name or real name of the given user
        """
        if is_id:
            user_object = self.slack_client.api_call('users.info', user=user)

        else:
            user_object = user

        if user_object['user']['profile']['first_name'] == '':
            return user_object['user']['real_name']
        else:
            try:
                return user_object['user']['profile']['first_name'].split(' ')[1]
            except:
                return user_object['user']['real_name']

    def _handle_whisper(self, message, sending_user, target_user):
        """ Create a whisper message json object, and send it to the specified user in their DMs with Neko-Chan

        Args:
            message (str): The actual text of the message
            sending_user (str): The plain text username of the person who requested the whisper
            target_user (str): The slack user ID of the user to send the message to

        Returns:
            str: The response to print out to the requesting user
        """
        target_user_name = self._retrieve_name(target_user, is_id=True)
        channel_object = self.slack_client.api_call('im.open', user=target_user)
        channel_id = channel_object['channel']['id']

        message_json = {
            'text': 'Hey there {0}-chan! {1}-chan asked me to send you this message:'.format(target_user_name,
                                                                                             sending_user),
            'attachments': [
                {
                    'fallback': 'Message from {0}-chan'.format(sending_user),
                    'color': '#a0319e',
                    'author_name': sending_user,
                    'text': message,
                    'footer': 'Delivered with ♡ by Neko-chan!'
                }
            ]
        }

        post_response = self.slack_client.api_call('chat.postEphemeral',
                                                   channel=channel_id,
                                                   text=message_json['text'],
                                                   user=target_user,
                                                   as_user=True,
                                                   attachments=message_json['attachments'],
                                                   )
        print(json.dumps(post_response, indent=2))
        return 'Okay {0}-chan - I sent them your message!'.format(sending_user)

    def _handle_join(self, text, name):
        """Determine the response for a join request

        Args:
            text (str): The text of the message including the join command
            name (str): The name of the user requesting the join

        Returns:
            str: The bot's response to the join request
        """
        target_channel_name = text.split('|')[1].split('>')[0]
        target_channel_id = text.split('#')[1].split('|')[0].upper()

        channel_mention = '<#{0}|{1}>'.format(target_channel_id, target_channel_name)

        params = {
            'token': self.user_token,
            'channel': target_channel_id,
            'user': self.bot_id
        }

        slack_response = requests.post('https://slack.com/api/channels.invite', data=params).json()

        if slack_response['ok']:
            self._whitelist_channel(target_channel_id)
            return 'Okay {0}-chan! You got it!!! (=^ ◡ ^=)'.format(name)
        elif slack_response['error'] == 'already_in_channel':
            if target_channel_id not in self.whitelist:
                self._set_block('whitelist', target_channel_id)
                return 'I\'m not allowed to speak in {0}, {1}-chan... Should we change that?'.format(channel_mention,
                                                                                                     name)
            else:
                return 'I\'m already in {0}, {1}-chan! No need to add me again („ಡωಡ„)'.format(channel_mention, name)
        else:
            return 'Sorry {0}-chan... I couldn\'t join that channel... ｡ﾟ(｡ﾉωヽ｡)ﾟ｡'.format(name)

    def _handle_command(self, data):
        """The main logic for the bot

        Takes in the data from the firehose that contains a mention of the bot, retrieves user and other info from the
        message and sends the output to the `_response_switch()` function to determine the proper response. Makes the
        call to the slack api to actually respond to commands.

        Args:
            data (:obj:`dict`): The output from the firehose that contains a bot mention

        """
        calling_user_id = data['user']
        user_object = self.slack_client.api_call('users.info', user=calling_user_id)
        text = ('parse: ' + data['text'].split(self.at_bot)[0] + data['text'].split(self.at_bot)[1]).lower()
        channel = data['channel']

        is_admin = calling_user_id in self.admins

        if channel not in self.whitelist:
            print('Neko-chan isn\'t allowed in this channel')
            return

        print('checking response code for text:\n{0}'.format(text))
        response_code = self._response_switch(text, admin=is_admin)

        print('got response code:{0}'.format(response_code))

        name = self._retrieve_name(user_object)

        response = None

        if is_admin:
            if response_code == 'join':
                response = self._handle_join(text, name)
            elif response_code == 'leave':
                target_channel_name = text.split('|')[1].split('>')[0]
                target_channel_id = text.split('#')[1].split('|')[0].upper()

                channel_mention = '<#{0}|{1}>'.format(target_channel_id, target_channel_name)

                self._unwhitelist_channel(target_channel_id)

                response = 'Unfortunately I can\'t _leave_ channels {0}-chan, but I\'ll keep quiet ' \
                           'in {1} for now!'.format(name, channel_mention)
            elif response_code == 'confirm':
                if self.blocking_issue is 'whitelist':
                    slack_response = self.slack_client.api_call('channels.info', channel=self.blocking_data)
                    target_channel_name = slack_response['channel']['name']
                    target_channel_id = slack_response['channel']['id']

                    channel_mention = '<#{0}|{1}>'.format(target_channel_id, target_channel_name)

                    self._whitelist_channel(self.blocking_data)
                    self._reset_block()

                    response = 'Alright {0}-chan! I\'ll pipe up again in {1} starting now!'.format(name,
                                                                                                   channel_mention)

        if response is None:
            if response_code == 'greet':
                response = "Hi!!!!!!! (=^-ω-^=) (´• ω •`)ﾉ\nHow's your day going {0}-chan?".format(name)
            elif response_code == 'nyaa':
                response = 'nyaaa~ {0}'.format(self._get_kaomoji())
            elif response_code == 'image':
                api_response = requests.get('http://nekos.life/api/neko')
                response = 'Here you go {0}-chan!!!\n{1}'.format(name, api_response.json()['neko'])
            elif response_code == 'lewd' or response_code == 'hand':
                response = 'Th-that\'s l-l-lewd {0}-chan (⁄ ⁄•⁄ω⁄•⁄ ⁄) '.format(name)
            elif response_code == 'waifu-neg':
                response = 'Hmf (＃￣ω￣)... I was told that that _I_ was best-girl'
            elif response_code == 'waifu-pos':
                response = 'Y-you really think so {0}-chan?! (´• ω •`) ♡♡♡'.format(name)
            elif response_code == 'whisper':
                target_user = text.split('<@')[1].split('>')[0].upper()
                response = self._handle_whisper(data['text'], name, target_user)
            else:
                response = 'I\'m not sure what you mean {0}-chan ┐(\'ω`;)┌'.format(name)

        self.slack_client.api_call('chat.postMessage', channel=channel, text=response)

    def run(self):
        """Main execution loop for the bot

        The loop will attempt to reconnect to slack 3 times before exiting
        """
        retries = 3
        while retries >= 0:
            if self.slack_client.rtm_connect():
                print('Neko-chan connected and running! (*≧ω≦*)')
                while True:
                    mention = self._parse_firehose(self.slack_client.rtm_read())

                    if mention:
                        self._handle_command(mention)

                    time.sleep(0.5)
            else:
                if retries is not 0:
                    print('Oh no!!! Couldn\'t connect to slack ｡･ﾟﾟ*(>д<)*ﾟﾟ･｡\nRetrying {0} more times...'.format(retries))
                    retries -= 1
                else:
                    print('I wasn\'t able to reach slack ( ╥ω╥ ), you should try again later...')
                    sys.exit(1)

if __name__ == '__main__':
    # Create the Nekochan object
    # Replace these placeholders with your keys!
    nekochan = Nekochan('<bot_token>',
                        '<user_token>')

    # print some general info
    print('Nekochan {0} starting up!\nAdmins: {1}\nWhitelist: {2}'.format(VERSION,
                                                                          nekochan.admins,
                                                                          nekochan.whitelist))

    # Start!
    nekochan.run()
