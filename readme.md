<p align="center">
    <br><strong><font size=50>每日签到集合</font></strong>
    <br>基于 Sitoi/DailyCheckIn 项目修改的每日签到脚本
    <br>支持多账号使用
</p>

## 特别声明

- 本仓库发布的脚本及其中涉及的任何解锁和解密分析脚本，仅用于测试和学习研究，禁止用于商业用途，不能保证其合法性，准确性，完整性和有效性，请根据情况自行判断。
- 本项目内所有资源文件，禁止任何公众号、自媒体进行任何形式的转载、发布。
- 本人对任何脚本问题概不负责，包括但不限于由任何脚本错误导致的任何损失或损害。
- 间接使用脚本的任何用户，包括但不限于建立VPS或在某些行为违反国家/地区法律或相关法规的情况下进行传播, 本人对于由此引起的任何隐私泄漏或其他后果概不负责。
- 请勿将本仓库的任何内容用于商业或非法目的，否则后果自负。
- 如果任何单位或个人认为该项目的脚本可能涉嫌侵犯其权利，则应及时通知并提供身份证明，所有权证明，我们将在收到认证文件后删除相关脚本。
- 任何以任何方式查看此项目的人或直接或间接使用该项目的任何脚本的使用者都应仔细阅读此声明。本人保留随时更改或补充此免责声明的权利。一旦使用并复制了任何相关脚本或Script项目的规则，则视为您已接受此免责声明。
**您必须在下载后的24小时内从计算机或手机中完全删除以上内容**
> ***您使用或者复制了本仓库且本人制作的任何脚本，则视为 `已接受` 此声明，请仔细阅读***

## 环境要求
> python >= 3.7

> 安装依赖 `pip install requests rsa`

## 签到列表
| 终端 | 任务名称 | 名称 | Cookie 时长 | 备注 |
| --- | --- | --- | --- | --- |
| WEB | AILIYUN | https://www.aliyundrive.com/drive | 不定期更新 | 每日签到 |
| WEB | BILIBILI | https://www.bilibili.com/ | 待测试 | 直播签到，漫画签到，每日经验任务，自动投币，银瓜子换硬币等功能 |
| WEB | CLOUD189 | https://cloud.189.cn/ | 永久 | 每日签到 +3次抽奖获得空间奖励 |
|  WX | LOGITECHCLUB | 罗技粉丝俱乐部 | 不定期更新 | 每日签到，看视频积分奖励 |
|  -  | MANUALTASK | 手动任务 | 永久 | 抓签到跳转链接，手动签到 |
| APP | MIMOTION | 小米运动 | 永久 | 每日小米运动刷步数 |
| WEB | SMZDM | https://www.smzdm.com/ | 永久 | 签到，抽奖获得碎银子 |
| APP | TONGCHENG | 同程旅行 | 永久 | 做每日任务获得里程。 |
| APP | WZYG | 王者营地 | 不定期更新 | 每日签到，领取奖励 |


## 阿里云盘refresh_token获取方法

一、进入到阿里云盘官网并且成功登录 https://www.aliyundrive.com/drive
法1
按F12，进入开发者工具模式，在顶上菜单栏点 Application ，然后在左边菜单找到 Local storage 下面的 https://www.aliyundrive.com/ 这个域名，点到这个域名会看到有一个 token 选项，再点 token ，就找到 refresh_token 了

![](https://user-images.githubusercontent.com/21276183/220014474-42db9b98-887e-4ad4-a1d4-6eb6993b850a.png)

法2
自动获取: 登录阿里云盘后，按F12，进入开发者工具模式，控制台粘贴 JSON.parse(localStorage.token).refresh_token
![](https://github.com/mrabit/aliyundriveDailyCheck/raw/master/assets/refresh_token_1.png)


## 更新日志
- 2023-05-23
    * 修复【天翼云盘】不能登录
    * 修复【阿里云盘】签到不领取奖励
  
## 支付宝红包
![](https://github.com/bear2978/dailysign/blob/main/image_20230525115518.jpg)
