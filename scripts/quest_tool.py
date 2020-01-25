#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import json
import re
from collections import OrderedDict

DEBUG = False
ALL_QUESTS_FILE = os.path.join(os.path.dirname(__file__), '../quest/poi.json')
SPLIT_QUESTS_DIR = os.path.join(os.path.dirname(__file__), '../quest')
README_FILE = os.path.join(os.path.dirname(__file__), '../quest/README.md')
INDENT = 2  # 缩进


def printHelp():
    print('''kcwiki任务切割/合并脚本

切割/合并'{directory}'目录下的quest小文件，所有操作均为覆写模式!!!使用前请保存git并确认参数正确!!!

用法:
    python {file} [param]
常用指令:
    python {file} -m # 合并quest小文件
    python {file} -s # 切割quest大文件

参数:
    -m, --merge         # 将'{directory}'目录下的任务小文件，合并为'{questsFile}'
    -n, --no-patch      # 默认模式 重新合成quest文件
    -p, --patch         # 合并时采用修补模式，在旧quest基础上更新
    -s, --split         # 切割'{questsFile}'文件
    -c, --compression   # 压缩模式，不保留缩进(默认缩进2空格)
    -rm, --remove       # 删除所有小任务文件
    --no-update-readme  # 不更新README文件

使用 "python {file} --help" 查看帮助。
'''.format(directory=SPLIT_QUESTS_DIR, questsFile=ALL_QUESTS_FILE, file=os.path.basename(__file__)))


def loadQuests():
    with open(ALL_QUESTS_FILE, mode='r', encoding='utf-8') as f:
        quests = json.load(f, object_pairs_hook=OrderedDict)
    return quests


def loadQuestDir():
    questFileList = list(filter(lambda filename: filename.split('.')[
        0].isdigit(), os.listdir(SPLIT_QUESTS_DIR)))
    if DEBUG:
        print('任务文件列表 ', questFileList)
    return questFileList


def splitQuests():
    quests = loadQuests()
    if DEBUG:
        print('任务数量 ' + str(len(quests)))
    for quest in quests:
        if 'game_id' not in quest:
            raise Exception('Missing attribute \'game_id\' ' + str(quest))
        with open(os.path.join(SPLIT_QUESTS_DIR, str(quest['game_id']) + '.json'), mode='w', encoding='utf-8') as f:
            json.dump(
                quest, f, indent=INDENT, ensure_ascii=False)
            f.write('\n')
    return


def mergeQuests(patch=False):
    if patch:
        quests = {quest['game_id']: quest for quest in loadQuests()}
    else:
        quests = dict()
    questFileList = loadQuestDir()

    for questFile in questFileList:
        filename = os.path.join(SPLIT_QUESTS_DIR, questFile)
        with open(filename, mode='r', encoding='utf-8') as f:
            try:
                quest = json.load(f, object_pairs_hook=OrderedDict)
            except Exception as e:
                print('json解析错误 ', filename, e)
        if 'game_id' not in quest:
            raise Exception('Missing attribute \'game_id\' ' + str(quest))
        quests[quest['game_id']] = quest

    questList = list(quests.values())
    with open(ALL_QUESTS_FILE, mode='w', encoding='utf-8') as f:
        json.dump(
            questList, f, indent=INDENT, ensure_ascii=False)
    return questList


def deleteQuests():
    questFileList = loadQuestDir()
    for file in questFileList:
        filename = os.path.join(SPLIT_QUESTS_DIR, file)
        try:
            os.remove(filename)
        except OSError:
            print('删除失败 ' + filename)


def updateReadme(questList):
    header = '# 任务列表\n\n'
    s = '\n'.join(
        list(
            map(
                lambda quest: '- {gameId} [{wikiId}](https://zh.kcwiki.org/wiki/任务#{wikiId}) {name}'.format(
                    gameId=quest.get('game_id'),
                    wikiId=re.sub(
                        '([a-zA-Z])0([0-9]$)',
                        r'\1\2', quest.get('wiki_id')
                    ),
                    name=quest.get('name')),
                questList)
        )
    )
    with open(README_FILE, mode='w', encoding='utf-8') as f:
        f.write(header)
        f.write(s)
        f.write('\n')


def main():
    # --help
    if len(sys.argv) >= 2 and any(x == y for x in sys.argv[1:] for y in ['h', 'help', '-h', '--help']):
        printHelp()
        return
    # --debug
    if len(sys.argv) >= 2 and any(x == y for x in sys.argv[1:] for y in ['-d', '--debug']):
        global DEBUG
        DEBUG = True
        print('debug mode')
    # --compression
    if len(sys.argv) >= 2 and any(x == y for x in sys.argv[1:] for y in ['-c', '--compression']):
        global INDENT
        INDENT = 0
    # --merge
    if len(sys.argv) >= 2 and any(x == y for x in sys.argv[1:] for y in ['-m', '--merge']):
        # --merge --patch
        questList = None
        if len(sys.argv) >= 2 and any(x == y for x in sys.argv[1:] for y in ['-p', '--patch']):
            print('正在修补合成任务文件...')
            questList = mergeQuests(True)
        else:
            # --merge --no-patch
            print('正在重新生成任务文件...')
            questList = mergeQuests()
        if '--no-update-readme' in sys.argv[1:]:
            print('正在更新README')
            return
        updateReadme(questList)
        return
    # --split
    if len(sys.argv) >= 2 and any(x == y for x in sys.argv[1:] for y in ['-s', '--split']):
        print('正在切割任务文件...')
        splitQuests()
        return
    # --remove
    if len(sys.argv) >= 2 and any(x == y for x in sys.argv[1:] for y in ['-rm', '--remove']):
        print('正在删除任务文件...')
        deleteQuests()
        return
    printHelp()


if __name__ == '__main__':
    main()
