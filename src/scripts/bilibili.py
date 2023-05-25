# -*- coding: utf-8 -*-
import os
import requests
from requests import utils

name = "哔哩哔哩"
# TODO 待测试，需要大会员账号测试领取福利


def get_nav(session):
    url = "https://api.bilibili.com/x/web-interface/nav"
    ret = session.get(url=url).json()
    uname = ret.get("data", {}).get("uname")
    uid = ret.get("data", {}).get("mid")
    is_login = ret.get("data", {}).get("isLogin")
    coin = ret.get("data", {}).get("money")
    vip_type = ret.get("data", {}).get("vipType")
    current_exp = ret.get("data", {}).get("level_info", {}).get("current_exp")
    return uname, uid, is_login, coin, vip_type, current_exp


def reward(session) -> dict:
    """取B站经验信息"""
    url = "https://api.bilibili.com/x/member/web/exp/reward"
    ret = session.get(url=url)
    return ret.json()


def live_sign(session) -> dict:
    """B站直播签到"""
    try:
        url = "https://api.live.bilibili.com/xlive/web-ucenter/v1/sign/DoSign"
        ret = session.get(url=url).json()
        if ret["code"] == 0:
            msg = f'签到成功，{ret["data"]["text"]}，特别信息:{ret["data"]["specialText"]}，本月已签到{ret["data"]["hadSignDays"]}天'
        elif ret["code"] == 1011040:
            msg = "今日已签到过,无法重复签到"
        else:
            msg = f'签到失败，信息为: {ret["message"]}'
    except Exception as e:
        msg = f"签到异常，原因为{str(e)}"
        print(msg)
    return msg


def manga_sign(session, platform="android") -> dict:
    """
    模拟B站漫画客户端签到
    """
    try:
        url = "https://manga.bilibili.com/twirp/activity.v1.Activity/ClockIn"
        post_data = {"platform": platform}
        ret = session.post(url=url, data=post_data).json()
        if ret["code"] == 0:
            msg = "签到成功"
        elif ret["msg"] == "clockin clockin is duplicate":
            msg = "今天已经签到过了"
        else:
            msg = f'签到失败，信息为({ret["msg"]})'
            print(msg)
    except Exception as e:
        msg = f"签到异常,原因为: {str(e)}"
        print(msg)
    return msg


def vip_privilege_receive(session, bili_jct, receive_type: int = 1) -> dict:
    """
    领取B站大会员权益
    receive_type int 权益类型，1为B币劵，2为优惠券
    """
    url = "https://api.bilibili.com/x/vip/privilege/receive"
    post_data = {"type": receive_type, "csrf": bili_jct}
    ret = session.post(url=url, data=post_data).json()
    return ret


def vip_manga_reward(session) -> dict:
    """获取漫画大会员福利"""
    url = "https://manga.bilibili.com/twirp/user.v1.User/GetVipReward"
    ret = session.post(url=url, json={"reason_id": 1}).json()
    return ret


def report_task(session, bili_jct, aid: int, cid: int, progres: int = 300) -> dict:
    """
    B站上报视频观看进度
    aid int 视频av号
    cid int 视频cid号
    progres int 观看秒数
    """
    url = "http://api.bilibili.com/x/v2/history/report"
    post_data = {"aid": aid, "cid": cid, "progres": progres, "csrf": bili_jct}
    ret = session.post(url=url, data=post_data).json()
    return ret


def share_task(session, bili_jct, aid) -> dict:
    """
    分享指定av号视频
    aid int 视频av号
    """
    url = "https://api.bilibili.com/x/web-interface/share/add"
    post_data = {"aid": aid, "csrf": bili_jct}
    ret = session.post(url=url, data=post_data).json()
    return ret


def get_followings(
    session, uid: int, pn: int = 1, ps: int = 50, order: str = "desc", order_type: str = "attention"
) -> dict:
    """
    获取指定用户关注的up主
    uid int 账户uid，默认为本账户，非登录账户只能获取20个*5页
    pn int 页码，默认第一页
    ps int 每页数量，默认50
    order str 排序方式，默认desc
    order_type 排序类型，默认attention
    """
    params = {
        "vmid": uid,
        "pn": pn,
        "ps": ps,
        "order": order,
        "order_type": order_type,
    }
    url = f"https://api.bilibili.com/x/relation/followings"
    ret = session.get(url=url, params=params).json()
    return ret


def space_arc_search(
    session, uid: int, pn: int = 1, ps: int = 100, tid: int = 0, order: str = "pubdate", keyword: str = ""
) -> dict:
    """
    获取指定up主空间视频投稿信息
    uid int 账户uid，默认为本账户
    pn int 页码，默认第一页
    ps int 每页数量，默认50
    tid int 分区 默认为0(所有分区)
    order str 排序方式，默认pubdate
    keyword str 关键字，默认为空
    """
    params = {
        "mid": uid,
        "pn": pn,
        "ps": ps,
        "tid": tid,
        "order": order,
        "keyword": keyword,
    }
    url = f"https://api.bilibili.com/x/space/arc/search"
    ret = session.get(url=url, params=params)
    print(ret.text)
    data_list = [
        {"aid": one.get("aid"), "cid": 0, "title": one.get("title"), "owner": one.get("author")}
        for one in ret.get("data", {}).get("list", {}).get("vlist", [])
    ]
    return data_list


def elec_pay(session, bili_jct, uid: int, num: int = 50) -> dict:
    """
    用B币给up主充电
    uid int up主uid
    num int 充电电池数量
    """
    url = "https://api.bilibili.com/x/ugcpay/trade/elec/pay/quick"
    post_data = {"elec_num": num, "up_mid": uid, "otype": "up", "oid": uid, "csrf": bili_jct}
    ret = session.post(url=url, data=post_data).json()
    return ret


def coin_add(session, bili_jct, aid: int, num: int = 1, select_like: int = 1) -> dict:
    """
    给指定 av 号视频投币
    aid int 视频av号
    num int 投币数量
    select_like int 是否点赞
    """
    url = "https://api.bilibili.com/x/web-interface/coin/add"
    post_data = {
        "aid": aid,
        "multiply": num,
        "select_like": select_like,
        "cross_domain": "true",
        "csrf": bili_jct,
    }
    ret = session.post(url=url, data=post_data).json()
    return ret


def live_status(session) -> dict:
    """B站直播获取金银瓜子状态"""
    url = "https://api.live.bilibili.com/pay/v1/Exchange/getStatus"
    ret = session.get(url=url).json()
    data = ret.get("data")
    silver = data.get("silver", 0)
    gold = data.get("gold", 0)
    coin = data.get("coin", 0)
    msg = [
        {"name": "硬币数量", "value": coin},
        {"name": "金瓜子数", "value": gold},
        {"name": "银瓜子数", "value": silver},
    ]
    return msg


def get_region(session, rid=1, num=6) -> dict:
    """
    获取 B站分区视频信息
    rid int 分区号
    num int 获取视频数量
    """
    url = "https://api.bilibili.com/x/web-interface/dynamic/region?ps=" + str(num) + "&rid=" + str(rid)
    ret = session.get(url=url).json()
    data_list = [
        {
            "aid": one.get("aid"),
            "cid": one.get("cid"),
            "title": one.get("title"),
            "owner": one.get("owner", {}).get("name"),
        }
        for one in ret.get("data", {}).get("archives", [])
    ]
    return data_list


def main(param):
    msg_list = []
    for account in param:
        cookie = account.get('cookie', '')
        bilibili_cookie = {item.split("=")[0]: item.split("=")[1] for item in cookie.split("; ")}
        bili_jct = bilibili_cookie.get("bili_jct")
        coin_num = account.get("coin_num", 0)
        coin_type = account.get("coin_type", 1)

        session = requests.session()
        requests.utils.add_dict_to_cookiejar(session.cookies, bilibili_cookie)
        session.headers.update(
            {
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.64",
                "Referer": "https://www.bilibili.com/",
                "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
                "Connection": "keep-alive",
            }
        )
        success_count = 0
        uname, uid, is_login, coin, vip_type, current_exp = get_nav(session=session)
        if is_login:
            manhua_msg = manga_sign(session=session)
            live_msg = live_sign(session=session)
            aid_list = get_region(session=session)
            reward_ret = reward(session=session)
            coins_av_count = reward_ret.get("data", {}).get("coins") // 10
            coin_num = coin_num - coins_av_count
            coin_num = coin_num if coin_num < coin else coin
            # if coin_type == 1 and coin_num:
            #     following_list = get_followings(session=session, uid=uid)
            #     for following in following_list.get("data", {}).get("list"):
            #         mid = following.get("mid")
            #         if mid:
            #             aid_list += space_arc_search(session=session, uid=mid)
            if coin_num > 0:
                for aid in aid_list[::-1]:
                    ret = coin_add(session=session, aid=aid.get("aid"), bili_jct=bili_jct)
                    if ret["code"] == 0:
                        coin_num -= 1
                        print(f'成功给{aid.get("title")}投一个币')
                        success_count += 1
                    elif ret["code"] == 34005:
                        print(f'投币{aid.get("title")}失败，原因为{ret["message"]}')
                        continue
                        # -104 硬币不够了 -111 csrf 失败 34005 投币达到上限
                    else:
                        print(f'投币{aid.get("title")}失败，原因为{ret["message"]}，跳过投币')
                        break
                    if coin_num <= 0:
                        break
                coin_msg = f"今日成功投币{success_count + coins_av_count}/{coin_num}个"
            else:
                coin_msg = f"今日成功投币{coins_av_count}/{coin_num}个"
            aid = aid_list[0].get("aid")
            cid = aid_list[0].get("cid")
            title = aid_list[0].get("title")
            report_ret = report_task(session=session, bili_jct=bili_jct, aid=aid, cid=cid)
            if report_ret.get("code") == 0:
                report_msg = f"观看《{title}》300秒"
            else:
                report_msg = f"任务失败"
                print(report_msg)
            share_ret = share_task(session=session, bili_jct=bili_jct, aid=aid)
            if share_ret.get("code") == 0:
                share_msg = f"分享《{title}》成功"
            else:
                share_msg = f"分享失败"
                print(share_msg)
            live_stats = live_status(session=session)
            uname, uid, is_login, new_coin, vip_type, new_current_exp = get_nav(session=session)
            reward_ret = reward(session=session)
            login = 1 if reward_ret.get("data", {}).get("login") else 0
            watch_av = 1 if reward_ret.get("data", {}).get("watch") else 0
            coins_av = 1 if reward_ret.get("data", {}).get("coins", 0) else 0
            share_av = 1 if reward_ret.get("data", {}).get("share") else 0
            today_exp = len([one for one in [login, watch_av, share_av] if one]) * 5
            today_exp += coins_av
            update_data = (28800 - new_current_exp) // (today_exp if today_exp else 1)
            msg = [
                      {"name": "帐号信息", "value": uname},
                      {"name": "漫画签到", "value": manhua_msg},
                      {"name": "直播签到", "value": live_msg},
                      {"name": "登陆任务", "value": "今日已登陆"},
                      {"name": "观看视频", "value": report_msg},
                      {"name": "分享任务", "value": share_msg},
                      {"name": "投币任务", "value": coin_msg},
                      {"name": "今日经验", "value": today_exp},
                      {"name": "当前经验", "value": new_current_exp},
                      {"name": "升级还需", "value": f"{update_data}天"},
                  ] + live_stats
            msg = "\n".join([f"{one.get('name')}: {one.get('value')}" for one in msg])
            msg_list.append(msg)
        else:
            msg_list.append('登陆信息失效，请重新登陆！')
        msg_list.append('')
        return '\n'.join(msg_list)


if __name__ == "__main__":
    try:
        from dailysign.src.configs import config
        data = config.read_param(__file__, 0)
    except Exception as e:
        import os, re, json
        data = re.split("&|\\n", os.getenv(os.path.basename(__file__).split(".")[0].upper()))
        data = [json.loads(item) for item in data]
    print(main(data))