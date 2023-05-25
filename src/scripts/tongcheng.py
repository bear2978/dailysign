# -*- coding = utf-8 -*-
import requests
import json, time
import traceback

# 手机抓包 任务界面下的请求将memberId与deviceId填入下面
name = '同城旅行'


# 登录
def sign(memberId, deviceId):
    msg = ''
    url = 'https://tcmobileapi.17usoft.com/platformsign/sign/signIndex'
    headers = {
        'Host': 'tcmobileapi.17usoft.com',
        'Content-Type': 'application/json;charset=utf-8',
        'Origin': 'https://appnew.ly.com',
        'Accept-Encoding': 'gzip,deflate,br',
        'Connection': 'keep-alive',
        'Accept': 'application/json,text/plain,*/*',
        'User-Agent': 'Mozilla/5.0(iPhone;CPUiPhoneOS13_4_1likeMacOSX)AppleWebKit/605.1.15(KHTML,likeGecko)Mobile/15E148TcTravel/10.2.0tctype/wk',
        'Referer': 'https://appnew.ly.com/sign/newsign/?abType=A&wvc6=1',
        'Content-Length': '151',
        'Accept-Language': 'zh-cn',
    }
    data = {"isReceive": 1,
            "memberId": memberId,
            "platId": 100,
            "reqFrom": "app",
            "regid": "",
            "deviceId": deviceId,
            # "jy_project_id": "tcwireless_net_activityplatform_new",
            # "jy_response": f"{time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))}9123b54215b913a0bd",
            # "jy_type": "sm"
    }
    response = requests.post(url=url, headers=headers, data=json.dumps(data)).json()
    # print(response)
    if response['statusCode'] == 0:
        continuedDays = response['data']['signInfo']['continuedDays']
        todayMileage = response['data']['signInfo']['todayMileage']
        if response['data']['signInfo']['addMile'] and response['data']['signInfo']['todayFirstSign']:
            # print(f'签到状态:签到成功，已连续签到{continuedDays}天，获取里程:{todayMileage}', flush=False)
            msg += f'签到状态:签到成功，已连续签到{continuedDays}天，获取里程:{todayMileage}\n'
        elif response['data']['signInfo']['addMile'] and not response['data']['signInfo']['todayFirstSign']:
            msg += f'签到状态:重复签到，已连续签到{continuedDays}天\n'
        else:
            # print(f'签到状态:签到失败，已连续签到{continuedDays}天', flush=False)
            msg += f'签到状态:签到失败，已连续签到{continuedDays}天\n'
        assets = response['data']['mileageBalance']
        # print(f'当前账号资产:{assets}里程')
        msg += f'当前账号资产:{assets}里程\n'
    else:
        # print('未知错误，请检查参数是否正确。', flush=False)
        msg += '未知错误，请检查参数是否正确。'
    return msg


# 查询可完成的每日任务
def query_today_task(memberId, deviceId):
    task_list = []
    url = "https://tcmobileapi.17usoft.com/platformsign/task/queryTaskList"
    headers = {
        'Host': 'tcmobileapi.17usoft.com',
        'Content-Type': 'application/json;charset=utf-8',
        'Origin': 'https://appnew.ly.com',
        'Accept-Encoding': 'gzip,deflate,br',
        'Connection': 'keep-alive',
        'Accept': 'application/json,text/plain,*/*',
        'User-Agent': 'Mozilla/5.0(iPhone;CPUiPhoneOS13_4_1likeMacOSX)AppleWebKit/605.1.15(KHTML,likeGecko)Mobile/15E148TcTravel/10.2.0tctype/wk',
        'Referer': 'https://appnew.ly.com/sign/newsign/?abType=A&wvc6=1',
        'Content-Length': '142',
        'Accept-Language': 'zh-cn',
    }
    data = {"taskType": 1002,
            "memberId": memberId,
            "platId": 100,
            "deviceId": deviceId,
            "reqFrom": "app"
            }

    response = requests.post(url=url, headers=headers, data=json.dumps(data)).json()
    if response['statusCode'] == 0:
        for task in response['data']['taskModelList']:
            detail = {}
            task_name = task['title']
            task_id = task['id']
            quantity = task['quantity']
            detail['task_name'] = task_name
            detail['task_id'] = task_id
            detail['quantity'] = quantity
            task_list.append(detail)
    return task_list


# 完成任务
def finish_today_task(memberId, task_list):
    msg = ''
    url = "https://tcmobileapi.17usoft.com/platformsign/task/commit"
    headers = {
        'Host': 'tcmobileapi.17usoft.com',
        'Content-Type': 'application/json;charset=utf-8',
        'Origin': 'https://appnew.ly.com',
        'Accept-Encoding': 'gzip,deflate,br',
        'Connection': 'keep-alive',
        'Accept': 'application/json,text/plain,*/*',
        'User-Agent': 'Mozilla/5.0(iPhone;CPUiPhoneOS13_4_1likeMacOSX)AppleWebKit/605.1.15(KHTML,likeGecko)Mobile/15E148TcTravel/10.2.0tctype/wk',
        'Referer': 'https://appnew.ly.com/sign/newsign/?abType=A&wvc6=1',
        'Content-Length': '88',
        'Accept-Language': 'zh-cn',
    }
    for detail in task_list:
        data = {"taskId": detail['task_id'],
                "memberId": memberId,
                "platId": 100,
                "reqFrom": "app"
                }
        res = requests.post(url=url, headers=headers, data=json.dumps(data)).json()
        msg += f"{detail['task_name']}:{res['message']},请手动领取奖励\n"
        time.sleep(1)
    return msg


# 领取奖励
def receive_rewards(memberId, task_list):
    msg = ''
    url = 'https://tcmobileapi.17usoft.com/platformsign/task/receive'
    headers = {
        'Host': 'tcmobileapi.17usoft.com',
        'Content-Type': 'application/json;charset=utf-8',
        'Origin': 'https://appnew.ly.com',
        'Accept-Encoding': 'gzip,deflate,br',
        'Connection': 'keep-alive',
        'Accept': 'application/json,text/plain,*/*',
        'User-Agent': 'Mozilla/5.0(iPhone;CPUiPhoneOS13_4_1likeMacOSX)AppleWebKit/605.1.15(KHTML,likeGecko)Mobile/15E148TcTravel/10.2.0tctype/wk',
        'Referer': 'https://appnew.ly.com/sign/newsign/?abType=A&wvc6=1',
        'Content-Length': '401',
        'Accept-Language': 'zh-cn',
    }
    for detail in task_list:
        data = {"taskId": detail['task_id'],
                "memberId": memberId,
                "reqFrom": "app",
                "token": "",
                "platId": 100
                }
        response = requests.post(url=url, headers=headers, data=json.dumps(data)).json()
        if str(response['statusCode']) == "0":
            task_name = detail['task_name']
            quantity = detail['quantity']
            msg += f'{task_name}:奖励{quantity}里程\n'
        elif str(response['statusCode']) == "4":
            task_name = detail['task_name']
            msg += f'{task_name}:已经领取过奖励\n'
        else:
            task_name = detail['task_name']
            msg += f'{task_name}:奖励领取失败，请手动领取\n'
        time.sleep(1)
    return msg


# 提交每日抽奖任务
def luck_draw_task(task_headers, push_text):
    task_list = [{"task_id": "mat573637986101694464",
                  "task_name": "浏览商城首页15秒",
                  "task_type": "3"}
    ]
    url = 'https://wx.17u.cn/wcrewardshopapiv2/tasks/commitTask'
    headers = task_headers
    for task in task_list:
        task_id = task['task_id']
        task_name = task['task_name']
        task_type = task['task_type']
        data = {
            "unionId": "unionId",
            "access_token": "undefined",
            "osType": task_type,
            "taskNo": task_id
        }
        response = requests.post(url=url, headers=headers, data=json.dumps(data)).json()['resultInfo']
        print(response)
        time.sleep(16)
        frequency = receive_draw_task(task_headers, task)
        print(f'任务:[{task_name}]{response}   获得{frequency}次抽奖机会')
        push_text = push_text + f'任务:[{task_name}]{response}   获得{frequency}次抽奖机会\n'
    return push_text


# 领取每日任务奖励
def receive_draw_task(task_headers, task):
    url = 'https://wx.17u.cn/wcrewardshopapiv2/tasks/reward/receive'
    headers = task_headers
    data = {"unionId": "unionId",
            "access_token": "undefined",
            "osType": 1,
            "taskNo": task['task_id']}
    response = requests.post(url=url, headers=headers, data=json.dumps(data)).json()
    return response['data']['receiveRewardTimes']


# 查询每日抽奖次数
def query_draw_number(task_headers):
    url = 'https://wx.17u.cn/wcrewardshopapiv2/roulette/getAwardTimes'
    headers = task_headers
    data = {
      "secToken": "undefined",
      "osType": 0,
      "access_token": "undefined",
      "unionId": "unionId"
    }
    response = requests.post(url=url, headers=headers, data=json.dumps(data)).json()
    draw_number = response["data"]["numberOfCanUse"]
    if response["data"]["freeFlag"]:
        draw_number = draw_number + 1
    print(f'共有{draw_number}次抽奖次数')
    return draw_number


# 抽奖
def luck_draw(task_headers, number):
    msg = ''
    url = 'https://wx.17u.cn/wcrewardshopapiv2/roulette/lottery'
    headers = task_headers
    data = {"unionId": "unionId",
            "access_token": "undefined",
            "secToken": "undefined",
            "osType": 1,
            "onceFlag": "true",
            "hostFakeUid": "",
            "playId": "ENZ9mWYH7UA+EOfapCSPCQ==",
            "nickName": "尊敬的会员",
            "taskNo": ""
            }
    for i in range(number):
        response = requests.post(url=url, headers=headers, data=json.dumps(data)).json()
        print(response)
        prizeTitle = response['data'][0]['prizeTitle']
        msg = f'第{i+1}次抽奖，获得[{prizeTitle}]\n'
    return msg


def main(param):
    push_text = ''
    for item in param:
        try:
            memberId = item.get('memberId', '')
            deviceId = item.get('deviceId', '')
            task_headers = item.get('headers', '')
            # try:
            #     push_text += sign(memberId, deviceId)
            # except Exception as e:
            #     print(f'签到出错：{e}')
            #     push_text += f'签到出错\n'

            try:
                task_list = query_today_task(memberId, deviceId)
                finish_today_task(memberId, task_list)
                push_text += receive_rewards(memberId, task_list)
            except Exception as e:
                print(f'每日任务出错：{traceback.format_exc()}')
                push_text += f'每日任务出错:{str(e)}\n'

            if task_headers:
                try:
                    push_text += luck_draw(task_headers, query_draw_number(task_headers))
                    # push_text += luck_draw(task_headers, 1)
                except Exception as e:
                    print(f'抽奖出错：{e}')
                    push_text += f'抽奖出错\n'
            push_text += '\n'
        except Exception as e:
            print(f'执行任务出错：{e}')
            push_text += f'执行任务出错\n'
    return push_text


if __name__ == '__main__':
    try:
        from dailysign.src.configs import config
        data = config.read_param('TONGCHENG', 0)
    except Exception as e:
        import os, re, json
        data = re.split("&|\\n", os.getenv(os.path.basename(__file__).split(".")[0].upper()))
        data = [json.loads(item) for item in data]
    print(main(data))
