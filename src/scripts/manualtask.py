# -*- coding: utf8 -*-
name = '手动签到任务'


def main(param):
    msg = ''
    for item in param:
        msg += f"{item.get('name', '')}&nbsp;<a href='{item.get('href', '')}'>立即签到</a>\n"
    return msg


if __name__ == '__main__':
    try:
        from dailysign.src.configs import config
        data = config.read_param("MANUALTASK", 0)
    except Exception as e:
        import os, re, json
        data = re.split("&|\\n", os.getenv(os.path.basename(__file__).split(".")[0].upper()))
        data = [json.loads(item) for item in data]
    print(main(data))
