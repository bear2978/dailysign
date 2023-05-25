# -*- coding: utf-8 -*-
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
try:
    from src.main import sign_in
except Exception as e:
    print(e)


def main_handler(event, context):
    sign_in()


# 本地测试
if __name__ == '__main__':
    # print(sys.path)
    sign_in()
