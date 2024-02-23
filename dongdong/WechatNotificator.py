'''
@Project : Kazumi 
@File : WechatNotificator.py
@Author : 李成龙
@Date : 2024/2/23 16:45 
@Email : Chenglongli@cug.edu.cn
@Description : 
'''
import functools
import os
import datetime
import socket
import traceback
import requests
from .configure import wechat_webhook, wechat_user_mentions, wechat_user_mentions_mobile, DATE_FORMAT


class WechatNotificator:
    def __init__(self, webhook: str = None, taskname=None, user_mentions: [str] = [], user_mentions_mobile: [str] = []):
        '''
        This class will configure the settings for wechat notification.
        :param webhook:
            The webhook URL to access your WeChat Work chatroom.
            Visit https://work.weixin.qq.com/api/doc/90000/90136/91770 for more details.
        :param taskname:
        :param user_mentions:
            Optional userids to notify (use '@all' for all group members).
            Visit https://work.weixin.qq.com/api/doc/90000/90136/91770 for more details.
        :param user_mentions_mobile:
            Optional user's phone numbers to notify (use '@all' for all group members).
            Visit https://work.weixin.qq.com/api/doc/90000/90136/91770 for more details.

        You can set self.startmsg，self.completemsg and self.crashmsg via a string list to change the push information of the monitor
        '''
        if not webhook:
            webhook = wechat_webhook
        if not user_mentions:
            user_mentions = wechat_user_mentions
        if not user_mentions_mobile:
            user_mentions_mobile = wechat_user_mentions_mobile
        self.webhook = webhook
        self.user_mentions = user_mentions
        self.user_mentions_mobile = user_mentions_mobile
        self.taskname = taskname
        self.startmsg = None
        self.completemsg = None
        self.crashmsg = None
        self.msg = {
            "msgtype": "text",
            "text": {
                "content": "",
                "mentioned_list": user_mentions,
                "mentioned_mobile_list": user_mentions_mobile
            }
        }

    def monitor(self):
        def decorator_sender(func):
            @functools.wraps(func)
            def wrapper_sender(*args, **kwargs):

                start_time = datetime.datetime.now()
                host_name = socket.gethostname()

                if 'RANK' in os.environ:
                    master_process = (int(os.environ['RANK']) == 0)
                    host_name += ' - RANK: %s' % os.environ['RANK']
                else:
                    master_process = True

                if master_process:
                    if self.startmsg:
                        contents = self.startmsg
                    else:
                        contents = ['The script starts running 🎬\n',
                                    f'Machine name: {host_name}\n',
                                    f'Task name: {self.taskname}\n',
                                    f'Starting date: {start_time.strftime(DATE_FORMAT)}']
                    self.msg['text']['content'] = '\n'.join(contents)
                    try:
                        requests.post(self.webhook, json=self.msg)
                    except:
                        print('Unable to push message, please check network or configuration file')
                try:
                    value = func(*args, **kwargs)

                    if master_process:
                        end_time = datetime.datetime.now()
                        elapsed_time = end_time - start_time
                        if self.completemsg:
                            contents = self.completemsg
                        else:
                            contents = ['The script is complete 🎉\n',
                                        f'Machine name: {host_name}\n',
                                        f'Task name: {self.taskname}\n',
                                        f'Starting date: {start_time.strftime(DATE_FORMAT)}\n',
                                        f'End date: {end_time.strftime(DATE_FORMAT)}\n'
                                        f'Running duration: {str(elapsed_time)}']
                        try:
                            str_value = str(value)
                            contents.append('\nMain call returned value: %s' % str_value)
                        except:
                            contents.append("\nMain call returned value: ERROR - Couldn't str the returned value.")
                        self.msg['text']['content'] = '\n'.join(contents)
                        try:
                            requests.post(self.webhook, json=self.msg)
                        except:
                            print('Unable to push message, please check network or configuration file')

                    return value

                except Exception as ex:
                    end_time = datetime.datetime.now()
                    elapsed_time = end_time - start_time
                    if self.crashmsg:
                        contents = self.crashmsg
                    else:
                        contents = ['The script has crashed ☠️\n',
                                    f'Machine name: {host_name}\n',
                                    f'Task name: {self.taskname}\n',
                                    f'Starting date: {start_time.strftime(DATE_FORMAT)}\n',
                                    f'Crash date: {end_time.strftime(DATE_FORMAT)}\n',
                                    f'Crashed running duration: {str(elapsed_time)}\n\n',
                                    f'Here is the error:\n\n{ex}\n\n',
                                    f'{traceback.format_exc()}']
                    self.msg['text']['content'] = '\n'.join(contents)
                    try:
                        requests.post(self.webhook, json=self.msg)
                    except:
                        print('Unable to push message, please check network or configuration file')
                    raise ex

            return wrapper_sender

        return decorator_sender

    def push(self, contents):
        '''
        This function is used to push message to wechat
        :param contents: the message to push,str
        :return:
        '''
        self.msg['text']['content'] = '\n'.join(contents)
        try:
            requests.post(self.webhook, json=self.msg)
        except:
            print('Unable to push message, please check network or configuration file')
