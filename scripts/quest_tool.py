#!/usr/env python3
# -*- coding: utf-8 -*-
import json
import os
import sys

DEBUG = False
ALL_QUESTS_FILE = os.path.join(os.path.dirname(__file__), '../quest/poi.json')
SPLIT_QUESTS_DIR = os.path.join(os.path.dirname(__file__), '../quest')
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
    -p, --patch         # 默认模式 合并时采用patch模式
    -n, --no-patch      # 关闭patch模式，从新合成quest文件
    -s, --split         # 切割'{questsFile}'文件
    -c, --compression   # 压缩模式，不保留缩进(默认缩进2空格)
    -rm, --remove       # 删除所有小任务文件

使用 "python {file} --help" 查看帮助。
'''.format(directory=SPLIT_QUESTS_DIR, questsFile=ALL_QUESTS_FILE, file=os.path.basename(__file__)))


def loadQuests():
    with open(ALL_QUESTS_FILE, mode='r', encoding='utf-8') as f:
        quests = json.load(f)
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
    return


def mergeQuests(patch=True):
    if patch:
        quests = {quest['game_id']: quest for quest in loadQuests()}
    else:
        quests = dict()
    questFileList = loadQuestDir()

    for questFile in questFileList:
        filename = os.path.join(SPLIT_QUESTS_DIR, questFile)
        with open(filename, mode='r', encoding='utf-8') as f:
            quest = json.load(f)
        if 'game_id' not in quest:
            raise Exception('Missing attribute \'game_id\' ' + str(quest))
        quests[quest['game_id']] = quest

    questList = list(quests.values())
    with open(ALL_QUESTS_FILE, mode='w', encoding='utf-8') as f:
        json.dump(
            questList, f, indent=INDENT, ensure_ascii=False)
    return


def deleteQuests():
    questFileList = loadQuestDir()
    for file in questFileList:
        filename = os.path.join(SPLIT_QUESTS_DIR, file)
        try:
            os.remove(filename)
        except OSError:
            if DEBUG:
                print('删除失败 ' + filename)


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
        # --merge --no-patch
        if len(sys.argv) >= 2 and any(x == y for x in sys.argv[1:] for y in ['-n', '--no-patch']):
            print('正在从头合成任务文件...')
            mergeQuests(False)
            return
        # --merge --patch
        print('正在合并任务文件...')
        mergeQuests()
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
