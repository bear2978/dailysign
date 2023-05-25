# -*- coding: utf-8 -*-
import os
import sys
import time
import traceback
import argparse
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, wait
try:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    from dailysign.src.configs import config
    from dailysign.src.__version__ import VERSION
    from dailysign.src.util.message import push_message
except ImportError as e:
    print(e)
    sys.exit(0)


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--include", nargs="+", help="任务执行包含的任务列表")
    parser.add_argument("--exclude", nargs="+", help="任务执行排除的任务列表")
    return parser.parse_args()


def check_config():
    try:
        notice_info = config.get_notice_info()
        _check_info = config.get_check_info()
        task_handler = config.task_handler
        args = parse_arguments()
        include = args.include
        exclude = args.exclude
        if not include:
            include = list(task_handler.keys())
        else:
            include = [one for one in include if one.upper() in task_handler.keys()]
        if not exclude:
            exclude = []
        else:
            exclude = [one for one in exclude if one.upper() in task_handler.keys()]
        task_list = list(set(include) - set(exclude))
        check_info = {}
        # 配置文件中的信息
        for one_check, check_data in _check_info.items():
            if one_check not in task_list:
                continue
            check_info[one_check] = check_data
        # scripts 目录下的脚本
        for one_check, check_tuple in task_handler.items():
            if one_check in exclude:
                continue
            elif one_check in _check_info.keys():
                _check_list = list()
                for check_item in _check_info.get(one_check, []):
                    # 过滤模板配置
                    if "xxx" not in str(check_item) and "多账号" not in str(check_item):
                        _check_list.append(check_item)
                check_info[one_check] = _check_list
            else:
                task_name, task = check_tuple
                if task.__code__.co_argcount == 0:
                    check_info[one_check] = []
        return notice_info, check_info
    except Exception as ex:
        traceback.format_exc(ex)
        return False, False


def sign_in():
    start_time = time.time()
    utc_time = (datetime.utcnow() + timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")
    print(f"当前时间: {utc_time}\n当前版本: {VERSION}")

    notice_info, check_info = check_config()
    if check_info:
        task_name_str = "\n".join(
            [f"「{one.upper()}」账号数 : {len(value)}" for one, value in check_info.items()]
        )
        print(f"\n---------- 本次执行签到任务如下 ----------\n{task_name_str}\n")
        # return
        content_list = []
        thread_pool = ThreadPoolExecutor()
        pool_task_list = {}
        for one_check, check_list in check_info.items():
            task_name, task = config.task_handler.get(one_check.upper())
            print(f"----------提交任务「{task_name}」到线程池执行----------")
            # 无参直接调用，有参使用json文件参数
            if check_list:
                # 将任务提交到线程池执行
                item_task = thread_pool.submit(task, check_list)
            else:
                item_task = thread_pool.submit(task)
            pool_task_list[task_name] = item_task
        # 等待线程池执行完成
        wait(pool_task_list.values())
        for name, task in pool_task_list.items():
            try:
                res = task.result()
            except Exception as ex:
                print(ex)
                res = f"执行出错"
            content_list.append(f"「{name}」\n{res}")
        print("\n\n")

        content_list.append(
            f"开始时间: {utc_time}\n"
            f"任务用时: {'%.2f' % (time.time() - start_time)} 秒\n"
            f"当前版本: {VERSION}\n"
        )
        print('---------- push_message ----------')
        print('\n'.join(content_list))
        push_message(content_list=content_list, notice_info=notice_info)
        return 0


if __name__ == '__main__':
    sign_in()
