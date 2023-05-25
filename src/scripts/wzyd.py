# -*-coding:utf-8-*-
import json
import traceback
import requests
from urllib import parse

name = "王者营地"
USER_AGENT = "Mozilla/5.0 (Linux; Android 10; MI 8 SE Build/QKQ1.190828.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/89.0.4389.72 MQQBrowser/6.2 TBS/045947 Mobile Safari/537.36;GameHelper; smobagamehelper; Brand: Xiaomi MI 8 SE$"


def get_header(cookie, role_id, timestamp, sig, msdk_token, msdk_encode_param):
    header = {
        "Host": "kohcamp.qq.com",
        "Origin": "https://camp.qq.com",
        "Referer": "https://kohcamp.qq.com",
        "Connection": "keep-alive",
        "Content-Type": "application/json",
        "X-Requested-With": "com.tencent.gamehelper.smoba",
        "User-Agent": USER_AGENT,
        "timestamp": timestamp,
        "userId": cookie.get("userId", ""),
        "algorithm": "v2",
        "openid": cookie.get("openId", ""),
        "encode": "2",
        "roleId": role_id,
        "cClientVersionName": cookie.get("cClientVersionName", "6.71.504"),
        "source": "smoba_zhushou",
        "msdkToken": msdk_token,
        "gameOpenid": cookie.get("gameOpenId"),
        "msdkEncodeParam": msdk_encode_param,
        "gameId": cookie.get("gameId", "20001"),
        "sig": sig,
        "appid": "1105200115",
        "noencrypt": "1",
        "version": "3.1.96a",
        # "Q-UA2": "QV=3&PL=ADR&PR=TRD&PP=com.tencent.gamehelper.smoba&PPVN=6.71.504&TBSVC=44136&CO=BK&COVC=045947&PB=GE&VE=GA&DE=PHONE&CHID=0&LCID=9422&MO= MI8SE &RL=1080*2028&OS=10&API=29",
        # "Q-GUID": "c9305f9371b3ccd42118556913b788cb",
        # "Q-header-ctrl": "3",
        # "Q-Auth": "31045b957cf33acf31e40be2f3e71c5217597676a9729f1b"
    }
    return header


# 签到
def sign(cookie, header):
    msg = f"帐号信息: {cookie.get('userId', '未知')}\n"
    try:
        data = {"cSystem": "android", "h5Get": 1, "roleId": cookie.get("gameRoleId")}
        sign_url = "https://kohcamp.qq.com/operation/action/signin"
        resp = requests.post(url=sign_url, headers=header, data=json.dumps(data)).json()
        # print(resp)
        if resp["returnCode"] == 0:
            msg += f"签到成功，已连续签到 {resp['data']['userTotalSign']} 天"
        else:
            msg += resp["returnMsg"]
    except:
        msg += "请求失败,请检查接口"
    return msg


# 任务列表
def get_task_list(cookie, header):
    task_list = []
    try:
        data = {"cSystem": "android", "h5Get": 1, "serverId": cookie.get("gameServerId"),
                "roleId": cookie.get("gameRoleId")}
        url = "https://kohcamp.qq.com/operation/action/tasklist"
        resp = requests.post(url=url, headers=header, data=json.dumps(data)).json()
        # print(resp)
        if resp["returnCode"] == 0:
            task_list = resp['data']['taskList']
    except Exception as e:
        print(f"获取任务列表失败: {e}")
    return task_list


# 完成任务
def do_task(cookie, header, task_list, msdk_token, access_token):
    msg = []
    task_ids = []
    try:
        # header['Content-Type'] = "application/x-www-form-urlencoded"
        for task in task_list:
            title = task['title']
            task_id = task['taskId']
            task_ids.append(task_id)
            # if '启动游戏' in title:
            #     if access_token == "":
            #         msg.append(f"{title}：未填写token，启动游戏失败")
            #     url = "https://ssl.kohsocialapp.qq.com:10001/play/gettaskconditiondata"
            #     data = f"type=2&token={access_token}&userId={cookie.get('userId')}"
            #     continue
            # elif '浏览资讯' in title:
            #     user_id, info_id = get_first_new(header)
            #     url = 'https://ssl.kohsocialapp.qq.com:10001/game/detailinfov3'
            #     data = f"iInfoId={info_id}&token={access_token}&userId={cookie.get('userId')}"
            # else:
            #     continue
            # print(f"-------------{title}---------------")
            # print(header)
            # print(data)
            # res = requests.post(url=url, headers=header, data=data).json()
            # print(res)
            # if res["returnCode"] == 0:
            #     msg.append(f"{title}：任务已完成")
            # else:
            #     msg.append(f"{title}：{res['returnMsg']}")
    except Exception as e:
        print(e)
        traceback.format_exc()
    return task_ids


# 获取第一条资讯
def get_first_new(header):
    data = {"page": 0, "channelId": 25818}
    news_url = "https://kohcamp.qq.com/info/listinfov2"
    resp = requests.post(url=news_url, data=json.dumps(data), headers=header).json()
    # print(resp)
    user_id, info_id = None, None
    if resp["returnCode"] != 0:
        return user_id, info_id
    news_list = resp["data"]['list']
    for news in news_list:
        try:
            if news.get("infoContent", {}) is None:
                continue
            info_id = news.get("infoContent", {}).get('infoId', '')
            user_id = news.get("infoContent", {}).get('user', {}).get('user', {}).get('user', {}).get('userId', '')
            if info_id and user_id:
                break
        except Exception as e:
            traceback.format_exc()
            print(e)
    return user_id, info_id


# 领取奖励
def reward_task(cookie, header, ids):
    msg = "【每日任务】："
    url = "https://kohcamp.qq.com/operation/action/rewardtask"
    data = {"cSystem": "android", "h5Get": 1, "taskIds": ids, "roleId": cookie.get("gameRoleId")}
    resp = requests.post(url=url, headers=header, data=json.dumps(data)).json()
    msg += "领取成功\n" if resp['returnCode'] == 0 else "领取失败\n"
    print(msg)
    return msg


def main(param):
    msg_list = []
    for account in param:
        msg = ""
        cookie = account.get("data")
        data = {k: v[0] for k, v in parse.parse_qs(cookie).items()}
        try:
            user_id = data.get("userId", "")
            role_id = account.get("roleId", "")
            timestamp = account.get("timestamp")
            sig = account.get("sig")
            msdk_token = account.get("msdkToken")
            msdk_encode_param = account.get("msdkEncodeParam")
            access_token = account.get("accessToken", "")
            header = get_header(data, role_id, timestamp, sig, msdk_token, msdk_encode_param)
            sign_msg = sign(data, header)
            msg += f"帐号信息: {user_id}\n签到结果: {sign_msg}\n"
            task_list = get_task_list(data, header)
            ids = do_task(data, header, task_list, msdk_token, access_token)
            # 领取奖励
            msg += reward_task(data, header, ids)
        except Exception as e:
            traceback.format_exc()
            print(f"获取用户信息失败: {e}")
            msg = "未获取到用户信息"
        msg_list.append(msg)
    return "\n".join(msg_list)


if __name__ == "__main__":
    try:
        from dailysign.src.configs import config
        args = config.read_param(__file__, 0)
    except Exception as e:
        import os, re, json
        args = re.split("&|\\n", os.getenv(os.path.basename(__file__).split(".")[0].upper()))
        args = [json.loads(item) for item in args]
    print(args)
    print(main(args))
