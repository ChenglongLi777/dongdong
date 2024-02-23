'''
@Project : Kazumi 
@File : BarkNotificator.py
@Author : 李成龙
@Date : 2024/2/22 20:03 
@Email : Chenglongli@cug.edu.cn
@Description : 
'''
import functools
import os
import datetime
import socket
import traceback
import requests
from .configure import bark_token, DATE_FORMAT


class BarkNotificator:
    def __init__(self, token: str = None, taskname: str = None, sound: str = None):
        '''
        This class will configure the settings for bark notification.
        :param token: the bark token, you can get it from your bark app, https://api.day.app/yourtoken
        :param taskname: this variable is used to group messages, and pushes will be displayed in the notification center grouped by group
        :param sound: ringtone name, you can find them from your bark app

        You can set self.startmsg，self.completemsg and self.crashmsg to change the push information of the monitor, the format is as follows
        {
            'title': '',
            'body': '',
            'group': '',
            'level': None,
            'sound': self.sound,
        }
        '''
        if not token:
            token = bark_token
        self.url = 'https://api.day.app/' + token
        self.sound = sound
        self.taskname = taskname
        self.headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        self.startmsg = None
        self.completemsg = None
        self.crashmsg = None

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
                        message = self.startmsg
                    else:
                        message = {
                            'title': 'The script starts running 🎬',
                            'body': f'Machine name: {host_name}\nTask name: {self.taskname}\nStarting date: {start_time.strftime(DATE_FORMAT)}',
                            'group': self.taskname,
                            'level': None,
                            'sound': self.sound,
                        }
                    try:
                        requests.post(url=self.url, headers=self.headers, data=message)
                    except:
                        print('Unable to push message, please check network or configuration file')
                try:
                    value = func(*args, **kwargs)

                    if master_process:
                        end_time = datetime.datetime.now()
                        elapsed_time = end_time - start_time
                        if self.completemsg:
                            message = self.completemsg
                        else:
                            message = {
                                'title': 'The script is complete 🎉',
                                'body': f'Machine name: {host_name}\nTask name: {self.taskname}\nStarting date: {start_time.strftime(DATE_FORMAT)}\nEnd date: {end_time.strftime(DATE_FORMAT)}\nRunning duration: {str(elapsed_time)}',
                                'group': self.taskname,
                                'level': None,
                                'sound': self.sound,
                            }
                        try:
                            str_value = str(value)
                            message['body'] = message['body'] + f'\nMain call returned value: {str_value}'
                        except:
                            message['body'] = message[
                                                  'body'] + "\nMain call returned value: ERROR - Couldn't str the returned value."
                        try:
                            requests.post(url=self.url, headers=self.headers, data=message)
                        except:
                            print('Unable to push message, please check network or configuration file')

                    return value

                except Exception as ex:
                    end_time = datetime.datetime.now()
                    elapsed_time = end_time - start_time
                    if self.crashmsg:
                        message = self.crashmsg
                    else:
                        message = {
                            'title': 'The script has crashed ☠️',
                            'body': f'Machine name: {host_name}\nTask name: {self.taskname}\nStarting date: {start_time.strftime(DATE_FORMAT)}\nCrash date: {end_time.strftime(DATE_FORMAT)}\nCrashed running duration: {str(elapsed_time)}\n\nHere is the error:\n\n{ex}\n\n{traceback.format_exc()}',
                            'group': self.taskname,
                            'isArchive': '1',
                            'level': None,
                            'sound': self.sound,
                        }
                    try:
                        requests.post(url=self.url, headers=self.headers, data=message)
                    except:
                        print('Unable to push message, please check network or configuration file')
                    raise ex

            return wrapper_sender

        return decorator_sender

    def push(self, body: str, title: str = None, level: str = 'passive', isArchive=0):
        '''
        This function is used to push message to iPhone via Bark
        :param body: the message to push,str
        :param title: title of the push, if None, it will be set to taskname
        :param level: active: default value, the system will immediately light up the screen to display notifications; timeSensitive: time-sensitive notifications, you can display notifications in a focused state; passive: only add notifications to the notification list, will not light up the screen to remind
        :param isArchive: Pass 1 to save the push, pass the others to not save the push, not pass according to the app settings to decide whether to save or not
        :return:
        '''
        if not title:
            title = self.taskname
        message = {
            'title': title,
            'body': body,
            'group': self.taskname,
            'isArchive': str(isArchive),
            'level': level,
            'sound': self.sound,
        }
        try:
            requests.post(url=self.url, headers=self.headers, data=message)
        except:
            print('Unable to push message, please check network or configuration file')
