#!/usr/bin/env python3

import argparse
import configparser
import json
import urllib.request
from slugify import slugify
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
    data_list = []
    for game in json_data:
        data = dict()
        try:
            data['title'] = game['title']
        except TypeError:
            data['title'] = game.name
        try:
            data['slug'] = slugify(game['title'])
        except TypeError:
            data['slug'] = slugify(game.name)
        data_list.append(data)
    return data_list


def connect(api_key, userurl):
    steamapi.core.APIConnection(api_key=api_key, validate_key=True)
    user = steamapi.user.SteamUser(userurl=userurl)
    games = user.games
    games_list = generate_list(games)
    return games_list


def get_common(geforce_game_list, steam_game_list):
    geforce_slug_list = [game['slug'] for game in geforce_game_list]
    result = [game['title'] for game in steam_game_list
              if game['slug'] in geforce_slug_list]
    result.sort()
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
    geforce_url = config['GEFORCE']['JsonUrl']

    game_list = get_json(geforce_url)
    geforce_list = generate_list(game_list)

    try:
        steam_list = connect(key, args.username)
    except steamapi.errors.APIException:
        print("Couldn't get the game list from Steam.")
        input("Press Enter to exit...")
        exit(1)

    result_data = get_common(geforce_list, steam_list)
    save_file(result_data, args.filename)

    print("Done! :D")
    input("Press Enter to exit...")
