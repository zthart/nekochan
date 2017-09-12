#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import random
import json
import time

from slackclient import SlackClient

VERSION = 'v0.1'

BOT_ID = '<YOUR BOTS ID>'
TOKEN = '<YOUR BOT USER API TOKEN>'
USER_TOKEN = '<AN API KEY ATTACHED TO YOUR USER FOR THE WORKSPACE YOU PLAN TO USE THIS BOT IN>'


AT_BOT = "<@{0}>".format(BOT_ID)

slack_client = SlackClient(TOKEN)

CAT_KAOMOJI = ['(=^-ω-^=)', '(=^ ◡ ^=)', '(´• ω •`)ﾉ', '(*≧ω≦*)', '(=⌒‿‿⌒=)', '/ᐠ｡ꞈ｡ᐟ❁ \∫']

# CREATE THESE FILES IN THIS DIRECTORY
# SHOULD BE NEWLINE-SEPARATED USER IDS IN THE ADMIN FILE
# AND NEWLINE-SEPARATED CHANNEL IDS IN THE WHITELIST FILE
# YOU SHOULD PROBABLY ADD THE CHANNEL ID OF THE DMS WITH THE BOT USER TO THE WHITELIST FIRST
WHITELIST_FILE = 'whitelist.txt'
ADMINS_FILE = 'admins.txt'

def get_lists():
    with open(WHITELIST_FILE, 'r') as wl_file:
        whitelist = wl_file.readlines()

    whitelist = [x.strip() for x in whitelist]

    with open(ADMINS_FILE, 'r') as a_file:
        admins = a_file.readlines()

    admins = [x.strip() for x in admins]

    return admins, whitelist

def whitelist_channel(channel):
    with open(WHITELIST_FILE, 'a') as wl_file:
        wl_file.write(channel+'\n')

def remove_from_whitelist(channel_to_remove):
    with open(WHITELIST_FILE, 'r') as wl_file:
        channels = wl_file.readlines()
    with open(WHITELIST_FILE, 'w') as wl_file:
        for channel in channels:
            if channel != channel_to_remove+'\n':
                wl_file.write(channel)

def parse_firehose(rtm_output):
    output_list = rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:

            if output and 'text' in output and AT_BOT in output['text']:
                print(json.dumps(output, indent=2))
                # return the response object
                return output

    return None

BLOCKING_FOR_CONFIRMATION = False
ON = None
BLOCK_FOR = None

def _determine_response(text, admin=False):
    global BLOCKING_FOR_CONFIRMATION
    global ON
    global BLOCK_FOR

    if admin:
        if BLOCKING_FOR_CONFIRMATION:
            if 'yes' in text:
                return 'confirm'
            else:
                BLOCKING_FOR_CONFIRMATION = False
                ON = None
                BLOCK_FOR = None
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
    else:
        return None



def handle_command(data, admins, channels):
    global BLOCKING_FOR_CONFIRMATION
    global ON
    global BLOCK_FOR

    calling_user_id = data['user']
    user = slack_client.api_call('users.info', user=calling_user_id)
    text = ('parse: '+ data['text'].split(AT_BOT)[0] + data['text'].split(AT_BOT)[1]).lower()
    channel = data['channel']

    is_admin = False

    if calling_user_id in admins:
        is_admin = True

    if channel not in channels:
        print('Neko-chan isn\'t allowed in this channel') 
        return

    print('checking response code for text:\n{0}'.format(text))
    response_code = _determine_response(text, admin=is_admin)

    print('got response code: \'{0}\''.format(response_code))

    # print('User Data:\n' + json.dumps(user, indent=2))

    if user['user']['profile']['first_name'] == '':
        name = user['user']['real_name']
    else:
        try:
            name = user['user']['profile']['first_name'].split(' ')[1]
        except:
            name = user['user']['real_name']

    response = None

    if is_admin:
        if response_code == 'join':
            target_channel_name = '#{0}'.format(text.split('|')[1].split('>')[0])
            print('Channel name:\t' + target_channel_name)
            target_channel_id = text.split('#')[1].split('|')[0].upper()
            print('Channel id:\t' + target_channel_id)

            params = {
                'token': USER_TOKEN,
                'channel': target_channel_id,
                'user': BOT_ID
            }

            slack_response = requests.post('https://slack.com/api/channels.invite', data=params)

            print(json.dumps(slack_response.json(), indent=2))

            if slack_response.json()['ok']:
                whitelist_channel(target_channel_id)
                response = 'Okay {0}-chan! You got it!!! (=^ ◡ ^=)'.format(name)
            elif slack_response.json()['error'] == 'already_in_channel':
                if target_channel_id not in channels:
                    response = 'I\'m not allowed to speak in {0}, {1}-chan... Should we change that?'.format(target_channel_name, name)
                    BLOCKING_FOR_CONFIRMATION = True
                    ON = 'whitelist'
                    BLOCK_FOR = target_channel_id
                else:
                    response = 'I\'m already in {0}, {1}-chan! No need to add me again („ಡωಡ„)'.format(target_channel_name, name)
            else:
                response = 'Sorry {0}-chan... I couldn\'t join that channel ｡ﾟ(｡ﾉωヽ｡)ﾟ｡'.format(name)
        elif response_code == 'leave':
            target_channel_name = '#{0}'.format(text.split('|')[1].split('>')[0])
            target_channel_id = text.split('#')[1].split('|')[0].upper()
            print('Channel Name:\t{0}\nChannel ID:\t{1}'.format(target_channel_name, target_channel_id))
            remove_from_whitelist(target_channel_id)
            response = 'Unfortunately I can\'t _leave_ channels {0}-chan, but I\'ll keep quiet in {1} for now!'.format(name, '<#{0}|{1}>'.format(target_channel_id, target_channel_name.split('#')[1]))
        elif response_code == 'confirm':
            if ON is 'whitelist':
                slack_response = slack_client.api_call('channels.info', channel=BLOCK_FOR)
                target_channel_name = slack_response['channel']['name']
                whitelist_channel(BLOCK_FOR)
                BLOCKING_FOR_CONFIRMATION = False
                ON = None
                BLOCK_FOR = None
                response = 'Alright {0}-chan! I\'ll pipe up again in #{1} starting now!'.format(name, target_channel_name)

    if response is None:
        if response_code == 'greet':
            response = "Hi!!!!!!! (=^-ω-^=) (´• ω •`)ﾉ\nHow's your day going {0}-chan?".format(name)
        elif response_code == 'nyaa':
            response = 'nyaaa~ {0}'.format(CAT_KAOMOJI[random.randint(0, 4)])
        elif response_code == 'image':
            api_response = requests.get('http://nekos.life/api/neko')
            response = 'Here you go {0}-chan!!!\n{1}'.format(name, api_response.json()['neko'])
        elif response_code == 'lewd' or response_code == 'hand':
            response = 'Th-that\'s l-l-lewd {0}-chan (⁄ ⁄•⁄ω⁄•⁄ ⁄) '.format(name)
        elif response_code == 'waifu-neg':
            response = 'Hmf (＃￣ω￣)... I was told that that _I_ was best-girl'
        elif response_code == 'waifu-pos':
            response = 'Y-you really think so {0}-chan?! (´• ω •`) ♡♡♡'.format(name)
        else:
            response = 'I\'m not sure what you mean {0}-chan ┐(\'ω`;)┌'.format(name)

    slack_client.api_call("chat.postMessage", channel=channel, text=response, as_user=True)


if __name__ == '__main__':
    admin_list, channel_list = get_lists()

    print('Nekochan {0} running with Admins:\n{1}\nWhitelist:\n{2}'.format(VERSION, admin_list, channel_list))

    if slack_client.rtm_connect():
        print('Neko-chan connected and running! (*≧ω≦*)')
        while True:
            mention = parse_firehose(slack_client.rtm_read())

            if mention:
                admin_list, channel_list = get_lists()
                handle_command(mention, admin_list, channel_list)

            time.sleep(1)
    else:
        print('Oh no!!! Couldn\'t connect to slack ｡･ﾟﾟ*(>д<)*ﾟﾟ･｡')


