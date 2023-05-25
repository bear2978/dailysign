# -*-coding:utf-8-*-
import datetime
import requests

name = "阿里云盘"


# refresh_token需要定期更新，我们使用它来更新签到需要的access_token
# refresh_token获取教程：https://github.com/bighammer-link/Common-scripts/wiki/%E9%98%BF%E9%87%8C%E4%BA%91%E7%9B%98refresh_token%E8%8E%B7%E5%8F%96%E6%96%B9%E6%B3%95
# 签到函数
def daily_check(access_token, reward=True):
    content = []
    url = 'https://member.aliyundrive.com/v1/activity/sign_in_list?_rx-s=mobile'
    headers = {'Authorization': access_token, 'Content-Type': 'application/json'}
    result = requests.post(url=url, headers=headers, json={}).json()
    # print(result)
    if 'success' in result:
        sign_count = int(result['result']['signInCount'])
        today_sign_info = result['result']['signInLogs'][sign_count - 1]
        reward_msg = ""
        # 25 号后领取签到奖励
        day_num = int(datetime.date.today().strftime('%d'))
        if not reward and day_num >= 25:
            for i, info in enumerate(result['result']['signInLogs']):
                if not info['isReward'] and info['status'] == 'normal':
                    reward_msg += get_reward(access_token, info['day']) + "\n"
        else:
            reward_msg = get_reward(access_token, today_sign_info['day'])

        content.append('本月累计签到{}天'.format(result['result']['signInCount']))
        content.append(reward_msg)
    else:
        print('签到失败')
        content = '签到失败'
    return "\n".join(content)


# 领取某一天的签到奖励
def get_reward(access_token, day):
    url = 'https://member.aliyundrive.com/v1/activity/sign_in_reward?_rx-s=mobile'
    headers = {'Authorization': access_token, 'Content-Type': 'application/json'}
    res = requests.post(url=url, headers=headers, json={'signInDay': day}).json()
    # print(res)
    return f"领取第{day}天签到奖励成功: 获得{res['result']['name']}：{res['result']['description']}"


# 使用refresh_token更新access_token
def update_token(refresh_token):
    url = 'https://auth.aliyundrive.com/v2/account/token'
    _data = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token
    }
    response = requests.post(url=url, json=_data).json()
    if 'code' in response and response['code'] in ["InvalidParameter.RefreshToken", "RefreshTokenExpired"]:
        print('refresh_token 已过期或无效')
        return "refresh_token 已过期或无效"
    access_token = response['access_token']
    # print('获取的access_token为{}'.format(access_token))
    return access_token


def main(param):
    msg_list = []
    for account in param:
        refresh_token = account.get("refresh_token")
        reward = account.get("reward_now", True)
        access_token = update_token(refresh_token)
        content = ''
        if "无效" in access_token:
            content += f"{refresh_token}: {access_token}\n"
            continue
        # print('更新成功，开始进行签到')
        content += daily_check(access_token, reward)
        msg_list.append(content)
    return "\n".join(msg_list)


if __name__ == '__main__':
    try:
        from dailysign.src.configs import config
        data = config.read_param(__file__, 0)
    except Exception as e:
        import os, re, json
        data = re.split("&|\\n", os.getenv(os.path.basename(__file__).split(".")[0].upper()))
        data = [json.loads(item) for item in data]
    print(main(data))
