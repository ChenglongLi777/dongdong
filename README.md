# dongdong

This package is used to push messages when your python script is running or when it crashes during the process with three additional lines of code. This package reference [knickknack](https://github.com/huggingface/knockknock).

When running large scripts, such as training deep learning models, we often don't know how long it will take to finish. If you're running on a server, you may need to log in from time to time to check the status of the run, and you'll waste a lot of time if something goes wrong while the script is running. Therefore, it is important to have scripts that automatically notify you when they finish running or stop with an error. What's more, it would be nice to be able to push the training results for each epoch.

The package can monitor the running status of the script. Notifications will be pushed when the script starts running, ends and stops with an error. The return value (if any) and error information will also be included in the notification information.

## Installation

Install with `pip`.

```bash
pip install knockknock
```

This code has only been tested with Python >= 3.6.

## Usage

There are currently *five* ways to push notifications: Bark, Desktop, DingTalk, Teams and WeChat.

### Configuration

You can use the Set Configures function to set `bark_token, teams_webhook, teams_user_mentions, dingtalk_webhook, dingtalk_user_mentions, telegram_token, telegram_chat_id, wechat_webhook, wechat_user_mentions and wechat_user_mentions_mobile`. You don’t need to provide the corresponding variables next time.

```python
from dongdong import setconfigures

bark_token=''
setconfigures(bark_token=bark_token)
```

### Bark

This service can only be used for iOS devices as Bark is iOS only. Get the Key in Bark as bark_token.

![image-20240224175836304](/Volumes/Data/OneDrive - Kazumi/Project/20240223-DongDong_Package/assets/image-20240224175836304.png)

```python
from dongdong import BarkNotificator

bark = BarkNotificator(taskname='test_monitor')

@bark.monitor()
def test_monitor():
    print('start')
    time.sleep(5)
    
def test_push():
    for i in range(1, 21):
        bark.push(title=f'Epoch[{str(i).zfill(2)}/20]',
                  body=f' Train loss: {0.0001}, Val loss: {0.0000}', isArchive=1)
```

![CleanShot 2024-02-24 at 19.53.49](/assets/CleanShot 2024-02-24 at 19.53.49-8775737-8775743-8775753-8775759.gif)

If you want to push your message when the script starts running, ends or stops with an error, you can set `startmsg`, `complete` or `crashmsg` attribute.

```python
bark.startmsg={
            'title': '',
            'body': '',
            'group': '',
            'level': None,
            'sound': self.sound,
        }
```

For `push` function, you can set `level` to set push interruption level:

- active: default value, the system will immediately light up the screen to display notifications
- timeSensitive: time-sensitive notifications, you can display notifications in a focused state
- Passive: only add notifications to the notification list, will not light up the screen to remind

### DingTalk

Similarly, you can also use DingTalk to get notifications. Given DingTalk chatroom robot's webhook url and secret/keywords(at least one of them are set when creating a chatroom robot), your notifications will be sent to reach any one in that chatroom.

```python
from dongdong import DingTalkNotificator

dingtalk = DingTalkNotificator(taskname='test')

@dingtalk.monitor()
def test_monitor():
    print('start')
    time.sleep(5)

def test_push():
    for i in range(1, 11):
        message = [
            f'Epoch[{str(i).zfill(2)}/20] Train loss: {0.0001}, Val loss: {0.0000}'
        ]
        dingtalk.push(message, isAtAll=False)
```

You can set  `startmsg`,  `complete` or `crashmsg` attribute via a string list to change the push information of the monitor.

```python
dingtalk.startmsg=[
  'This is the title',
  'You can push anything you want'
]
```

### Teams

You can also use Microsoft Teams to get notifications. Given your Team channel [webhook URL](https://docs.microsoft.com/en-us/microsoftteams/platform/concepts/connectors/connectors-using), your notifications will be sent to reach any one in that channel.

```python
from dongdong import TeamsNotificator

teams = TeamsNotificator(taskname='test')

@teams.monitor()
def test_monitor():
    print('start')
    time.sleep(5)

def test_push():
    for i in range(1, 21):
        message = [
            f'Epoch[{str(i).zfill(2)}/20] Train loss: {0.0001}, Val loss: {0.0000}'
        ]
        teams.push(message)
```

You can set  `startmsg`,  `complete` or `crashmsg` attribute via a string list to change the push information of the monitor.

```python
teams.startmsg=[
  'This is the title',
  'You can push anything you want'
]
```

### WeChat

You can also use WeChat to get notifications. Given WeChat Work chatroom robot's webhook url, your notifications will be sent to reach anyone in that chatroom.

You can also use Microsoft Teams to get notifications. Given your Team channel [webhook URL](https://docs.microsoft.com/en-us/microsoftteams/platform/concepts/connectors/connectors-using), your notifications will be sent to reach any one in that channel.

```python
from dongdong import WechatNotificator

wechat = TeamsNotificator(taskname='test')

@wechat.monitor()
def test_monitor():
    print('start')
    time.sleep(5)

def test_push():
    for i in range(1, 21):
        message = [
            f'Epoch[{str(i).zfill(2)}/20] Train loss: {0.0001}, Val loss: {0.0000}'
        ]
        wechat.push(message)
```

You can set  `startmsg`,  `complete` or `crashmsg` attribute via a string list to change the push information of the monitor.

```python
wechat.startmsg=[
  'This is the title',
  'You can push anything you want'
]
```

