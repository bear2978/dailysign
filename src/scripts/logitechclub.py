# -*-coding:utf-8-*-
import time
import json
import random
import requests

name = "罗技粉丝俱乐部"
# 视频任务个数
VIDEO_TASK_NUM = 3

msg = []


# 封装通用请求
def send_request(url, auth, body=None, method="get"):
    host = url.replace('//', '/').split('/')[1]
    header = {
        "Host": host, "Connection": "keep-alive",
        "User-Agent": "Mozilla/5.0 (Linux; Android 12; M2012K11AC Build/RKQ1.200826.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/90.0.4430.210 Mobile Safari/537.36 oppostore/201202 MIUI/V125 brand/Redmi model/M2012K11AC",
        "Referer": "https://servicewechat.com/wx9be0a7d24db348e8/220/page-frame.html",
        "client_id": "LogitechFans", "Authorization": f"Bearer {auth}",
    }
    if body:
        header['Content-Type'] = 'application/json; charset=UTF-8'
        header['Content-Length'] = str(len(json.dumps(body)))

    if "post" == method.lower():
        res = requests.post(url=url, headers=header, data=json.dumps(body))
    else:
        res = requests.get(url=url, headers=header)
    # print(res.json())
    return res.json() if res.status_code == 200 else {}


# 分享任务
def share(auth):
    url = 'https://api.wincheers.net/api/services/app/crmAccount/GiftPoints'
    res = send_request(url=url, auth=auth, method='post')
    # print(res)
    if res['success']:
        msg.append(f"分享成功，每天首次分享可得50积分")
    else:
        msg.append(f"分享失败：{res['error']}")
    return res


# 观看视频
def watch_video(auth, social_id):
    url = f'https://api.wincheers.net/api/services/app/socialVideoOverLog/AddLog?SocialId={social_id}'
    res = send_request(url=url, auth=auth, method='post')
    # print(res)
    if res['success'] and res['result'] != 0:
        msg.append(f"完成观看视频任务成功，获得{res['result']}积分")
    elif res['error'] is not None:
        msg.append(f"观看视频失败：{res['error']}")
    return res


def main(param):
    for account in param:
        auth = account.get("cookie", "")
        # 登录
        url = 'https://api.wincheers.net/api/services/app/crmAccount/GetIsLogin'
        res = send_request(url=url, auth=auth, method='post')
        if res['success']:
            msg.append(f"昵称：{res['result']['name']}, 总积分：{res['result']['integral']}")
            is_sign_url = 'https://api.wincheers.net/api/services/app/signIn/IsSignDao'
            res = send_request(url=is_sign_url, auth=auth, method='post')
            if res['success']:
                info = str(res['result']).split("|")
                is_sign = info[0]
                sign_day = int(info[1])
                is_notice = info[2]
                integral = info[3]
                video_num = int(info[4])
                share_num = info[5]
                is_perfect = info[6]
                is_release = info[7]
                if 'ok' == is_sign:
                    msg.append(f"今日已签到，已连续签到{sign_day}天")
                else:
                    sign_url = 'https://api.wincheers.net/api/services/app/signIn/ContinuitySignIn'
                    res = send_request(url=sign_url, auth=auth, method='post')
                    if res['success']:
                        msg.append(f"签到成功，获得{res['result']}积分，已签到{(sign_day + 1)}天")
                    else:
                        msg.append(f"签到失败：{res['error']}")
                # 分享任务
                # if share_num == "0":
                #     share(auth)

                # 观看视频任务
                if video_num < VIDEO_TASK_NUM:
                    for i in range(VIDEO_TASK_NUM - video_num):
                        sid = int(random.random() * 10000) + 2000
                        res = watch_video(auth, sid)
                        time.sleep(random.randint(1, 4))
            msg.append("")
        else:
            msg.append(f"登录失败，CK失效:\n{res['error']}")
        # break
    return "\n".join(msg)


if __name__ == '__main__':
    try:
        from dailysign.src.configs import config
        data = config.read_param(__file__, 0)
    except Exception as e:
        import os, re, json
        data = re.split("&|\\n", os.getenv(os.path.basename(__file__).split(".")[0].upper()))
        data = [json.loads(item) for item in data]
    print(main(data))
