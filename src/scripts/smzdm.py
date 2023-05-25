# -*-coding:utf-8-*-
import re
import sys
import time
import random
import hashlib
import requests

name = "什么值得买"
# 抽奖任务
LOTTERY_TASK = {"生活频道转盘抽奖": "A6X1veWE2O", "会员中心转盘抽奖": "ljX8qVlEA7"}
# 这里填短期抽奖，expire代表过期时间
OTHER_TASK = [{"值得买才是618活动": "OP28eJ7EW7", "expire": "2023-06-18"}]
TOKEN = None


def get_token(ck):
    global TOKEN
    if TOKEN:
        return TOKEN
    url = 'https://user-api.smzdm.com/robot/token'
    timestamp = int(round(time.time() * 1000))
    headers = {
        'Host': 'user-api.smzdm.com',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Cookie': ck,
        'User-Agent': 'smzdm_android_V10.4.1 rv:841 (22021211RC;Android12;zh)smzdmapp',
    }
    data = {
        "f": "android",
        "v": "10.4.1",
        "weixin": 1,
        "time": timestamp,
        "sign": hashlib.md5(bytes(f'f=android&time={timestamp}&v=10.4.1&weixin=1&key=apr1$AwP!wRRT$gJ/q.X24poeBInlUJC',
                                  encoding='utf-8')).hexdigest().upper()
    }
    res = requests.post(url=url, headers=headers, data=data).json()
    if res:
        TOKEN = res['data']['token']
        return TOKEN
    else:
        print("获取 token 失败\n")
        sys.exit(0)


def send_request(url, header, method="get", data=None):
    timestamp = int(round(time.time() * 1000))
    _header = {
        "Accept": '*/*',
        'Accept-Language': 'zh-Hans-CN;q=1',
        'Accept-Encoding': 'gzip',
        'Host': url.replace('//', '/').split('/')[1],
        'x-requested-with': 'com.smzdm.client.android',
        'User-Agent': 'smzdm_android_V10.4.1 rv:841 (22021211RC;Android12;zh)smzdmapp',
    }
    _header = dict(_header, **header)

    token = get_token(header.get("cookie"))
    _data = {
        "f": "android",
        "v": "10.4.1",
        "sk": "ierkM0OZZbsuBKLoAgQ6OJneLMXBQXmzX+LXkNTuKch8Ui2jGlahuFyWIzBiDq/L",
        "weixin": 1,
        "time": timestamp,
        "token": token,
        "sign": hashlib.md5(bytes(
            f'f=android&sk=ierkM0OZZbsuBKLoAgQ6OJneLMXBQXmzX+LXkNTuKch8Ui2jGlahuFyWIzBiDq/L&time={timestamp}&token={token}&v=10.4.1&weixin=1&key=apr1$AwP!wRRT$gJ/q.X24poeBInlUJC',
            encoding='utf-8')).hexdigest().upper()
    }

    if data is not None:
        _data = dict(_data, **data)
    # print(_header)
    # print(_data)
    if method == "get":
        return requests.get(url, headers=_header)
    return requests.post(url, headers=_header, data=_data)


def sign(cookie):
    url = 'https://user-api.smzdm.com/checkin'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'cookie': cookie,
    }
    res = send_request(url=url, header=headers, method="post").json()
    return f"{res['error_msg']}，已连续签到{res['data']['daily_num']}天"


def draw(cookie):
    msg = []
    activity_draw = LOTTERY_TASK
    header = {"cookie": cookie}
    # 获取生活频道转盘抽奖ID
    res = send_request(url="https://m.smzdm.com/zhuanti/life/choujiang/", header=header)
    # print(res.text)
    # 从响应中拿到 lottery_activity_id
    lottery_activity_id = re.findall('name="lottery_activity_id" value="(.*?)"', res.text)
    if lottery_activity_id:
        activity_draw.update({'生活频道转盘抽奖': lottery_activity_id[0]})
    # 获取会员中心转盘抽奖ID
    res = send_request(url="https://m.smzdm.com/topic/zhyzhuanpan/cjzp/", header=header)
    # print(res.text)
    hash_id = re.findall('\\\\"hashId\\\\":\\\\"(.*?)\\\\"', res.text)
    if hash_id:
        activity_draw.update({'会员中心转盘抽奖': hash_id[0]})
    # 处理短期活动
    for task in OTHER_TASK:
        # 设置活动结束日期
        end_time = time.mktime(time.strptime(task.get("expire", "2023-05-23") + " 23:59:59", "%Y-%m-%d %H:%M:%S"))
        if int(time.time()) <= end_time:
            del task['expire']
            activity_draw.update(task)
    # print(activity_draw)
    # 抽奖
    header['Referer'] = 'https://m.smzdm.com/'
    for act_name, activity_id in activity_draw.items():
        activity_url = f"https://zhiyou.smzdm.com/user/lottery/jsonp_draw?active_id={activity_id}"
        res = send_request(url=activity_url, header=header, method="post").json()
        msg.append(f"【{act_name}】：{res['error_msg']}")
        time.sleep(random.uniform(1, 3))
    return "\n".join(msg)


def main(param):
    msg_list = []
    for account in param:
        cookie = account.get("cookie", "")
        msg_list.append(sign(cookie))
        msg_list.append(draw(cookie))
    return '\n'.join(msg_list)


if __name__ == "__main__":
    try:
        from dailysign.src.configs import config
        data = config.read_param('SMZDM', 0)
    except Exception as e:
        import os, re, json
        data = re.split("&|\\n", os.getenv(os.path.basename(__file__).split(".")[0].upper()))
        data = [json.loads(item) for item in data]
    print(main(data))
