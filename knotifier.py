#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
 Authors:
   yifengyou <842056007@qq.com>
"""
import sys
import glob
import os
import random
import re
import shutil
import subprocess
import sys
import argparse
import time

# Github仓库的API接口
import requests

GITHUB_LINUIX_REPOURL = "https://api.github.com/repos/torvalds/linux/commits"
CONFIG = "/etc/knotifier.config"
# 上次获取的commit的哈希值
LAST_SHA = None


def check_python_version():
    current_python = sys.version_info[0]
    if current_python == 3:
        return
    else:
        raise Exception('Invalid python version requested: %d' % current_python)


def handle_config(args):
    pass


def handle_run(args):
    global GITHUB_LINUIX_REPOURL
    # 发送请求，获取最新的commit列表
    response = requests.get(GITHUB_LINUIX_REPOURL)
    # 检查响应状态码
    if response.status_code == 200:
        # 解析响应数据为JSON格式
        data = response.json()
        # 获取最新的commit的哈希值
        new_sha = data[0]["sha"]

        print("New commit detected!")
        print(f"SHA: {new_sha}")
        print(f"Author: {data[0]['commit']['author']['name']}")
        print(f"Date: {data[0]['commit']['author']['date']}")
        print(f"Message: {data[0]['commit']['message']}")
        print(f"URL: {data[0]['html_url']}")

def main():
    global DEBUG, CURRENT_VERSION
    check_python_version()

    # 顶层解析
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("-v", "--version", action="store_true",
                        help="show program's version number and exit")
    parser.add_argument("-h", "--help", action="store_true",
                        help="show this help message and exit")
    subparsers = parser.add_subparsers()

    # 定义base命令用于集成
    parent_parser = argparse.ArgumentParser(add_help=False, description="knotifier - a tool for kernel development")
    parent_parser.add_argument("-V", "--verbose", default=None, action="store_true", help="show verbose output")
    parent_parser.add_argument("-w", "--workdir", default=None, help="setup workdir")
    parent_parser.add_argument('-l', '--log', default=None, help="log file path")
    parent_parser.add_argument('-d', '--debug', default=None, action="store_true", help="enable debug output")

    # 添加子命令 init
    parser_config = subparsers.add_parser('config', parents=[parent_parser])
    parser_config.add_argument("-s", "--show", default=None, action="store_true",
                               help="show all config")
    parser_config.set_defaults(func=handle_config)

    # 添加子命令 run
    parser_run = subparsers.add_parser('run', parents=[parent_parser])
    parser_run.add_argument('-n', '--name', help="setup vm name")
    parser_run.set_defaults(func=handle_run)

    # 开始解析命令
    args = parser.parse_args()

    # 解析命令后解析配置文件，合并两者
    if os.path.isfile(CONFIG):
        print("load config file %s" % CONFIG)
        with open(CONFIG, 'r', encoding='utf8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                match = re.match(r'(\w+)\s*=\s*([\w/.-]+)', line)
                if match:
                    key = match.group(1)
                    value = match.group(2)
                    # 如果命令行没有定义key，则使用配置中的KV
                    if not hasattr(args, key):
                        setattr(args, key, value)
                    # 如果命令行未打开选项，但配置中打开，则使用配置中的KV
                    if getattr(args, key) is None:
                        setattr(args, key, value)

    # 参数解析后开始具备debug output能力
    if hasattr(args, "debug") and args.debug is not None:
        DEBUG = True
        print("Enable debug output")
        print("Parser and config:")
        for key, value in vars(args).items():
            print("  %s = %s" % (key, value))

    if args.version:
        print("knotifier %s" % CURRENT_VERSION)
        sys.exit(0)
    elif args.help or len(sys.argv) < 2:
        parser.print_help()
        sys.exit(0)
    else:
        args.func(args)


if __name__ == "__main__":
    main()
