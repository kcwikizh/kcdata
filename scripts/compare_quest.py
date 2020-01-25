#!/usr/bin/env python3
import os
from collections import OrderedDict
import urllib.request
import urllib.parse
import json
import re


'''
"101": {
    "code": "A1",
    "name": "はじめての「編成」！",
    "desc": "2隻以上の艦で編成される「艦隊」を編成せよ！",
    "memo": "[獲]駆逐艦白雪",
    // "hash": 12345678
},
'''
KC3_QUESTS_DATA_URL = 'https://raw.githubusercontent.com/KC3Kai/kc3-translations/master/data/jp/quests.json'
# https://zh.kcwiki.org/api.php?action=query&format=json&prop=revisions&titles=任务/期间限定任务&rvprop=content
KCWIKI_LIMITED_QUESTS_URL = 'https://zh.kcwiki.org/api.php?action=query&format=json&prop=revisions&rvprop=content&titles=' + \
    urllib.parse.quote('任务/期间限定任务')
LOCAL = False  # load KC3 data from local
KCWIKI_QUESTS_DATA_FILE = os.path.join(
    os.path.dirname(__file__), '../quest/poi.json')
DEBUG = False

if DEBUG:
    log = print
else:
    def log(*a): pass  # do nothing


def printHelp():
    print('''Compare Kcdata Quests with KC3 Quests data.''')


def loadJsonFromUrl(url: str) -> OrderedDict:
    req = urllib.request.Request(url)
    # parsing response
    r = urllib.request.urlopen(req).read()
    return json.loads(r.decode('utf-8', 'ignore'), object_pairs_hook=OrderedDict)


def loadJson(filename: str) -> OrderedDict:
    with open(filename, mode='r', encoding='utf-8') as f:
        quests = json.load(f, object_pairs_hook=OrderedDict)
    return quests


def loadTimeLimitedWikiText() -> list:
    req = urllib.request.Request(KCWIKI_LIMITED_QUESTS_URL)
    # parsing response
    r = urllib.request.urlopen(req).read()
    data = json.loads(r.decode('utf-8'))
    wikiText = data['query']['pages']['19739']['revisions'][0]['*']
    # {{任务表| type =出击| 编号 =MB01| 前置 =Bd2
    reg = '^{{任务表| type =\w+ | 编号 =\s*(\w+)'
    quests = re.findall(reg, wikiText)
    return quests


def formatKc3Data(kc3Data):
    '''
    remove invaild data
    '''
    del kc3Data['eof']
    newData = kc3Data.copy()
    cnt = 0

    log('Remove multiplexing data:')
    for key in kc3Data:
        if not key.isdigit():
            data = kc3Data[key]
            log(key, data['code'], data['name'])
            del newData[key]
            cnt += 1

    kc3Data = newData.copy()
    print('Loading Kcwiki Time Limited Quests WikiText...')
    limitedQuest = set(loadTimeLimitedWikiText())
    log()
    log('Remove time limited data:')
    for key in kc3Data:
        data = kc3Data[key]
        if data['code'] in limitedQuest:
            log(key, data['code'], data['name'])
            del newData[key]
            cnt += 1

    kc3Data = newData.copy()
    log()
    log('Remove 期間限定 data:')
    for key in kc3Data:
        data = kc3Data[key]
        if '期間限定' in data.get('memo', ''):
            log(key, data['code'], data['name'])
            del newData[key]
            cnt += 1

    log('Removed', cnt, 'invaild quest')
    return newData


def analysis(json):
    cnt = 0
    for key in json:
        data = json[key]
        cnt += 1
        print(key, data['code'], data['name'])

    print('Total Number:', cnt)


def compare(json1, json2):
    cnt = 0

    print('Missing Quests:')
    for key in json1:
        if key not in json2:
            data = json1[key]
            print(key, data['code'], data['name'])
            cnt += 1

    print()
    print('Different Quests:')
    for key in json1:
        if key not in json2:
            continue

        data1 = json1[key]
        data2 = json2[key]

        def formatCode(code):  # remove prefix 0
            return re.sub('([a-zA-Z])0([0-9]$)', r'\1\2', code)

        if formatCode(data1['code']) != formatCode(data2['code']):
            print(key, data1['code'], data1['name'],
                  data2['code'], data2['name'])
            cnt += 1

    print()
    print('Total number', cnt)


def main():
    global KC3_QUESTS_DATA_URL, LOCAL, KCWIKI_QUESTS_DATA_FILE

    print('Loading KC3 quest data file...')
    if LOCAL:
        kc3Data = loadJson(os.path.join(
            os.path.dirname(__file__), './quests.json'))
    else:
        kc3Data = loadJsonFromUrl(KC3_QUESTS_DATA_URL)
    kc3Data = formatKc3Data(kc3Data)

    kcwikiData = {
        str(quest['game_id']): {
            'code': quest['wiki_id'],
            'name': quest['name'],
            'desc': quest['detail']
        }
        for quest in loadJson(KCWIKI_QUESTS_DATA_FILE)
    }
    # analysis(kc3Data)
    # analysis(kcwikiData)
    print()
    print('-------- Compare kc3 with kcwiki --------')
    compare(kc3Data, kcwikiData)
    # print()
    # print('-------- Compare kcwiki with kc3 --------')
    # compare(kcwikiData, kc3Data)


if __name__ == "__main__":
    main()
