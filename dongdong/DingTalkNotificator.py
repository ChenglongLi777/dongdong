'''
@Project : Kazumi 
@File : DingTalkNotificator.py
@Author : 李成龙
@Date : 2024/2/23 14:57 
@Email : Chenglongli@cug.edu.cn
@Description : 
'''
import functools
import os
import datetime
import socket
import hmac
import base64
import urllib
import hashlib
import traceback
import requests
from .configure import dingtalk_webhook, dingtalk_user_mentions, DATE_FORMAT


class DingTalkNotificator:
    def __init__(self, webhook: str = None, taskname=None, user_mentions: [str] = [], secret: str = '',
                 keywords: [str] = []):
        '''
        This class will configure the settings for dingtalk notification.
        :param webhook: str
            The webhook URL to access your DingTalk chatroom.
            Visit https://ding-doc.dingtalk.com/doc#/serverapi2/qf2nxq for more details.
        :param taskname:
        :param user_mentions:
            Optional users phone number to notify.
            Visit https://ding-doc.dingtalk.com/doc#/serverapi2/qf2nxq for more details.
        :param secret:
            DingTalk chatroom robot are set with at least one of those three security methods
            (ip / keyword / secret), the chatroom will only accect messages that:
                are from authorized ips set by user (ip),
                contain any keyword set by user (keyword),
                are posted through a encrypting way (secret).
            Vist https://ding-doc.dingtalk.com/doc#/serverapi2/qf2nxq from more details.
        :param keywords: see `secret`

        You can set self.startmsg，self.completemsg and self.crashmsg via a string list to change the push information of the monitor
        '''
        if not webhook:
            webhook = dingtalk_webhook
        if not user_mentions:
            user_mentions = dingtalk_user_mentions
        self.webhook = webhook
        self.user_mentions = user_mentions
        self.secret = secret
        self.keywords = keywords
        self.taskname = taskname
        self.startmsg = None
        self.completemsg = None
        self.crashmsg = None
        self.msg = {
            "msgtype": "text",
            "text": {
                "content": ""
            },
            "at": {
                "atMobiles": user_mentions,
                "isAtAll": True
            }
        }

    def _construct_encrypted_url(self):
        '''
        Visit https://ding-doc.dingtalk.com/doc#/serverapi2/qf2nxq for details
        '''
        timestamp = round(datetime.datetime.now().timestamp() * 1000)
        secret_enc = self.secret.encode('utf-8')
        string_to_sign = '{}\n{}'.format(timestamp, self.secret)
        string_to_sign_enc = string_to_sign.encode('utf-8')
        hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
        sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
        encrypted_url = self.webhook + '&timestamp={}'.format(timestamp) \
                        + '&sign={}'.format(sign)
        return encrypted_url

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
                    contents.extend(['@{}'.format(i) for i in self.user_mentions])
                    contents.extend(self.keywords)
                    self.msg['text']['content'] = '\n'.join(contents)
                    try:
                        if self.secret:
                            postto = self._construct_encrypted_url()
                            requests.post(postto, json=self.msg)
                        else:
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
                            contents.append(
                                '\nMain call returned value: %s' % str_value)
                        except:
                            contents.append("\nMain call returned value: ERROR - Couldn't str the returned value.")
                        contents.extend(['@{}'.format(i) for i in self.user_mentions])
                        contents.extend(self.keywords)
                        self.msg['text']['content'] = '\n'.join(contents)
                        try:
                            if self.secret:
                                postto = self._construct_encrypted_url()
                                requests.post(postto, json=self.msg)
                            else:
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
                    contents.extend(['@{}'.format(i) for i in self.user_mentions])
                    contents.extend(self.keywords)
                    self.msg['text']['content'] = '\n'.join(contents)
                    try:
                        if self.secret:
                            postto = self._construct_encrypted_url()
                            requests.post(postto, json=self.msg)
                        else:
                            requests.post(self.webhook, json=self.msg)
                    except:
                        print('Unable to push message, please check network or configuration file')
                    raise ex

            return wrapper_sender

        return decorator_sender

    def push(self, contents, isAtAll=False):
        '''
        This function is used to push message to dingtalk
        :param contents: the message to push,str
        :param isAtAll:
        :return:
        '''
        contents.extend(['@{}'.format(i) for i in self.user_mentions])
        contents.extend(self.keywords)
        self.msg['text']['content'] = '\n'.join(contents)
        self.msg['at']['isAtAll'] = isAtAll
        try:
            if self.secret:
                postto = self._construct_encrypted_url()
                requests.post(postto, json=self.msg)
            else:
                requests.post(self.webhook, json=self.msg)
        except:
            print('Unable to push message, please check network or configuration file')
