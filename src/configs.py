# -*- coding: utf-8 -*-
import os
import json
import traceback
import importlib

__all__ = ['config']

# 通知列表
notice_map = {
    "BARK_URL": "",
    "COOLPUSHEMAIL": "",
    "COOLPUSHQQ": "",
    "COOLPUSHSKEY": "",
    "COOLPUSHWX": "",
    "DINGTALK_ACCESS_TOKEN": "",
    "DINGTALK_SECRET": "",
    "FSKEY": "",
    "PUSHPLUS_TOKEN": "",
    "PUSHPLUS_TOPIC": "",
    "QMSG_KEY": "",
    "QMSG_TYPE": "",
    "QYWX_AGENTID": "",
    "QYWX_CORPID": "",
    "QYWX_CORPSECRET": "",
    "QYWX_KEY": "",
    "QYWX_TOUSER": "",
    "QYWX_MEDIA_ID": "",
    "SCKEY": "",
    "SENDKEY": "",
    "TG_API_HOST": "",
    "TG_BOT_TOKEN": "",
    "TG_PROXY": "",
    "TG_USER_ID": "",
    "MERGE_PUSH": ""
}


def env2list(key):
    try:
        value = json.loads(os.getenv(key, []).strip()) if os.getenv(key) else []
        if isinstance(value, list):
            value = value
        else:
            value = []
    except Exception as e:
        print(e)
        value = []
    return value


def env2str(key):
    try:
        value = os.getenv(key, "") if os.getenv(key) else ""
        if isinstance(value, str):
            value = value.strip()
        elif isinstance(value, bool):
            value = value
        else:
            value = None
    except Exception as e:
        print(e)
        value = None
    return value


class Config:

    def __init__(self):
        self.cfg_path = ''
        self.data = None
        self._task_handler = {}
        self._load_config()
        self._init_task()

    # 初始化任务
    def _init_task(self):
        result = {}
        for script_name in os.listdir(os.path.join(os.path.dirname(__file__), "scripts")):
            if not script_name.endswith('.py') or script_name.startswith('__') or script_name.startswith('_'):
                continue
            task_name = script_name[:-3]
            try:
                if __package__:
                    task_module = importlib.import_module('.scripts.' + task_name, package=__package__)
                else:
                    task_module = importlib.import_module('.' + task_name, package="scripts")

                if task_module and hasattr(task_module, 'main'):
                    task_func = getattr(task_module, 'main')
                    alias_name = getattr(task_module, 'name') if hasattr(task_module, 'name') else task_name
                    result[task_name.upper()] = (alias_name, task_func)
                    # task_obj = task_class()
                    # print(task_class)
                    # task_obj.run()
                else:
                    # print(f'{task_module.__name__} has not attr {task_name}')
                    continue
            except Exception as e:
                print(f"{task_name} 任务加载失败\n{e}")
                traceback.format_exc()
        self._task_handler = result

    def _load_config(self):
        config_path = None
        config_path_list = []
        for one_path in [
            "config.json",
            "../config.json",
            "./config/config.json",
            "../config/config.json",
            "/config.json",
            "/ql/scripts/config.json",
        ]:
            _config_path = os.path.join(os.path.dirname(__file__), one_path)
            if os.path.exists(_config_path):
                config_path = os.path.normpath(_config_path)
                break
            config_path_list.append(os.path.normpath(os.path.dirname(_config_path)))
        if config_path:
            print("使用配置文件路径:", config_path)
            with open(config_path, "r", encoding="utf-8") as f:
                try:
                    self.data = json.load(f)
                except Exception as e:
                    print("json 格式错误，请务必到 https://www.sojson.com/ 网站检查 config.json 文件格式是否正确!")
                    print(str(e))
            self.cfg_path = config_path
        else:
            # 尝试读取青龙环境变量
            env_data = os.getenv("DAILY_SIGN")
            self.data = env_data if env_data else None
        if not self.data:
            print("未找到 DAILY_SIGN 环境变量和 config.json 配置文件 \n请先设置环境变量后再运行或在下方任意目录中添加「config.json」文件:\n" + "\n".join(config_path_list))

    @property
    def task_handler(self):
        return self._task_handler

    def get_check_info(self):
        result = {}
        if isinstance(self.data, dict):
            for one in self.data.keys():
                if one.upper() not in notice_map:
                    result[one.upper()] = self.data.get(one, [])
        else:
            for one in self.data.keys():
                if one.upper() not in notice_map:
                    result[one.upper()] = env2list(one)
        return result

    def get_notice_info(self):
        result = {}
        for one in notice_map.keys():
            if one in self.data:
                result[one.lower()] = self.data.get(one, None)
            else:
                result[one.lower()] = env2str(one)
        return result

    # 读取配置文件中的配置信息
    def read_param(self, key, index=None):
        # 处理传入的key值
        if os.path.isfile(key):
            key = os.path.basename(key)
        if key.__contains__('.'):
            key = key[:key.index('.')]
        result = self.data.get(str(key).upper(), [])
        if len(result):
            if index is None:
                return result
            elif index < len(result):
                return [result[index]]
            else:
                return []
        else:
            raise Exception(f'Key {key} not found in {self.cfg_path}!')


config = Config()
del Config

if __name__ == '__main__':
    print(config.read_param("MANUALTASK", 0))
    print(config.task_handler)
