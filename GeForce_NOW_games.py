#!/usr/bin/env python

import argparse
import configparser
import json
import urllib.request
import steamapi


def get_json(url_json):
    with urllib.request.urlopen(url_json) as url:
        data = json.loads(url.read().decode())
    return data


def save_file(data, file_name):
    with open(file_name, 'w', encoding='utf8') as txt_file:
        for item in data:
            txt_file.write("%s\n" % item)


def generate_list(json_data):
    data = [game['title'] for game in json_data]
    return data


def connect(api_key, userurl):
    steamapi.core.APIConnection(api_key=api_key, validate_key=True)
    user = steamapi.user.SteamUser(userurl=userurl)
    games = user.games
    games_list = [game.name for game in games]
    return games_list


def get_common(geforce_game_list, steam_game_list):
    result = [game for game in steam_game_list if game in geforce_game_list]
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='GeForce-NOW-games',
        description='Generate a list of owned Steam games that work on '
                    'GeForce NOW platform.')
    parser.add_argument(
        'username', metavar='username', type=str,
        help='Steam username (urluser - present in the profile url)')
    parser.add_argument(
        'filename', metavar='filename', type=str,
        help='name of the output file - will be created or overwritten')
    args = parser.parse_args()

    config = configparser.ConfigParser()
    config.read('config.ini')
    key = config['STEAM']['ApiKey']

    geforce_url = \
        'https://static.nvidiagrid.net/supported-public-game-list/gfnpc.json'
    geforce_list = get_json(geforce_url)
    try:
        steam_list = connect(key, args.username)
    except steamapi.errors.APIException:
        print("Couldn't get the game list from Steam.")
        exit(1)
    game_list = generate_list(geforce_list)
    result_data = get_common(game_list, steam_list)
    save_file(result_data, args.filename)
