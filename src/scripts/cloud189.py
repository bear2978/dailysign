# -*- coding: utf-8 -*-
import base64
import re
import time
import requests
import rsa

name = "天翼云盘"
b64map = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"


def int2char(a):
    return list("0123456789abcdefghijklmnopqrstuvwxyz")[a]


def b64tohex(a):
    d = ""
    e = 0
    c = 0
    for i in range(len(a)):
        if list(a)[i] != "=":
            v = b64map.index(list(a)[i])
            if 0 == e:
                e = 1
                d += int2char(v >> 2)
                c = 3 & v
            elif 1 == e:
                e = 2
                d += int2char(c << 2 | v >> 4)
                c = 15 & v
            elif 2 == e:
                e = 3
                d += int2char(c)
                d += int2char(v >> 2)
                c = 3 & v
            else:
                e = 0
                d += int2char(c << 2 | v >> 4)
                d += int2char(15 & v)
    if e == 1:
        d += int2char(c << 2)
    return d


def rsa_encode(j_rsakey, string):
    rsa_key = f"-----BEGIN PUBLIC KEY-----\n{j_rsakey}\n-----END PUBLIC KEY-----"
    pubkey = rsa.PublicKey.load_pkcs1_openssl_pem(rsa_key.encode())
    result = b64tohex((base64.b64encode(rsa.encrypt(f"{string}".encode(), pubkey))).decode())
    return result


def login(session, username, password):
    url = "https://cloud.189.cn/api/portal/loginUrl.action?redirectURL=https://cloud.189.cn/web/redirect.html"
    token_url = "https://m.cLoud.189.cn/udb/udb_login.jsp?pageId=1&pageKey=default&clientType=wap&redirectURL=https://m.cloud.189.cn/zhuantil/2021/shakeLottery/index.html"
    res = session.get(url=token_url)
    pattern = r"https?://[^\s'\"]+"
    match = re.search(pattern, res.text)
    if match:
        url = match.group() + "&pageKey=normal&protocol=https"
    r = session.get(url=url)
    captchatoken = re.findall(r"captchaToken' value='(.+?)'", r.text)[0]
    lt = re.findall(r'lt = "(.+?)"', r.text)[0]
    returnurl = re.findall(r"returnUrl= '(.+?)'", r.text)[0]
    paramid = re.findall(r'paramId = "(.+?)"', r.text)[0]
    j_rsakey = re.findall(r'j_rsaKey" value="(\S+)"', r.text, re.M)[0]
    session.headers.update({"lt": lt})

    username = rsa_encode(j_rsakey, username)
    password = rsa_encode(j_rsakey, password)
    url = "https://open.e.189.cn/api/logbox/oauth2/loginSubmit.do"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:74.0) Gecko/20100101 Firefox/76.0",
        "Referer": "https://open.e.189.cn/",
    }
    data = {
        "appKey": "cloud",
        "accountType": "01",
        "userName": f"{{RSA}}{username}",
        "password": f"{{RSA}}{password}",
        "validateCode": "",
        "captchaToken": captchatoken,
        "returnUrl": returnurl,
        "mailSuffix": "@189.cn",
        "paramId": paramid,
    }
    r = session.post(url, data=data, headers=headers, timeout=5)
    if r.json()["result"] == 0:
        redirect_url = r.json()["toUrl"]
        session.get(url=redirect_url)
        return True
    else:
        return {"name": "登陆信息", "value": r.json()["msg"]}


def sign(session):
    rand = str(round(time.time() * 1000))
    surl = f"https://api.cloud.189.cn/mkt/userSign.action?rand={rand}&clientType=TELEANDROID&version=8.6.3&model=Redmi"
    url = "https://m.cloud.189.cn/v2/drawPrizeMarketDetails.action?taskId=TASK_SIGNIN&activityId=ACT_SIGNIN"
    url2 = "https://m.cloud.189.cn/v2/drawPrizeMarketDetails.action?taskId=TASK_SIGNIN_PHOTOS&activityId=ACT_SIGNIN"
    url3 = 'https://m.cloud.189.cn/v2/drawPrizeMarketDetails.action?taskId=TASK_2022_FLDFS_KJ&activityId=ACT_SIGNIN'
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 12; M2012K11AC Build/RKQ1.200826.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/90.0.4430.210 Mobile Safari/537.36 oppostore/201202 MIUI/V125 brand/Redmi model/M2012K11AC",
        "Referer": "https://m.cloud.189.cn/zhuanti/2016/sign/index.jsp?albumBackupOpened=1",
        "Host": "m.cloud.189.cn",
        "Accept-Encoding": "gzip, deflate",
    }
    response = session.get(url=surl, headers=headers)
    netdiskbonus = response.json().get("netdiskBonus")
    msg = []
    if response.json().get("isSign") == "false":
        msg.append({"name": "签到结果", "value": f"未签到，签到获得 {netdiskbonus}M 空间"})
    else:
        msg.append({"name": "签到结果", "value": f"已经签到过了，签到获得 {netdiskbonus}M 空间"})
    response = session.get(url=url, headers=headers)
    if "errorCode" in response.text:
        if response.json().get("errorCode") == "User_Not_Chance":
            description = "没有抽奖机会了"
        else:
            description = response.json().get("errorCode")
        msg.append({"name": "第一次抽", "value": description})
    else:
        description = response.json().get("description", "")
        if description in ["1", 1]:
            description = "50M空间"
        msg.append({"name": "第一次抽", "value": f"获得{description}"})
    response = session.get(url=url2, headers=headers)
    if "errorCode" in response.text:
        if response.json().get("errorCode") == "User_Not_Chance":
            description = "没有抽奖机会了"
        else:
            description = response.json().get("errorCode")
        msg.append({"name": "第二次抽", "value": description})
    else:
        description = response.json().get("description", "")
        if description in ["1", 1]:
            description = "50M空间"
        msg.append({"name": "第二次抽", "value": f"获得{description}"})
    response = session.get(url=url3, headers=headers)
    if "errorCode" in response.text:
        if response.json().get("errorCode") == "User_Not_Chance":
            description = "没有抽奖机会了"
        else:
            description = response.json().get("errorCode")
        msg.append({"name": "第三次抽", "value": description})
    else:
        description = response.json().get("description", "")
        if description in ["1", 1]:
            description = "50M空间"
        msg.append({"name": "第三次抽", "value": f"获得{description}"})
    return msg


def main(param):
    msg_list = []
    for account in param:
        try:
            cloud189_phone = account.get("phone", '')
            cloud189_password = account.get("password", '')
            session = requests.Session()
            flag = login(session=session, username=cloud189_phone, password=cloud189_password)
            if flag is True:
                sign_msg = sign(session=session)
            else:
                sign_msg = flag
            msg = [{"name": "帐号信息", "value": cloud189_phone[:3] + '****' + cloud189_phone[-4:]}] + sign_msg
            msg = "\n".join([f"{one.get('name')}: {one.get('value')}" for one in msg])
            msg_list.append(msg)
        except Exception as e:
            msg_list.append(f'执行任务出错:{str(e)}')
    return '\n'.join(msg_list)


if __name__ == "__main__":
    try:
        from dailysign.src.configs import config
        data = config.read_param('CLOUD189', 0)
    except Exception as e:
        import os, re, json
        data = re.split("&|\\n", os.getenv(os.path.basename(__file__).split(".")[0].upper()))
        data = [json.loads(item) for item in data]
    print(main(data))
