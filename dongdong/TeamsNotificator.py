'''
@Project : Kazumi 
@File : TeamsNotificator.py
@Author : 李成龙
@Date : 2024/2/23 10:11 
@Email : Chenglongli@cug.edu.cn
@Description : 
'''
import functools
import os
import datetime
import socket
import json
import traceback
import requests
from .configure import teams_user_mentions, teams_webhook, DATE_FORMAT


class TeamsNotificator:
    def __init__(self, webhook: str = None, taskname=None, user_mentions: [str] = []):
        if not webhook:
            webhook = teams_webhook
        if not user_mentions:
            user_mentions = teams_user_mentions
        self.webhook = webhook
        self.taskname = taskname
        self.user_mentions = user_mentions
        self.startmsg = None
        self.completemsg = None
        self.crashmsg = None
        self.dump = {
            "username": "dongdong",
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
                    contents.append(' '.join(self.user_mentions))
                    self.dump['text'] = '\n'.join(contents)
                    try:
                        requests.post(self.webhook, json.dumps(self.dump))
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
                        contents.append(' '.join(self.user_mentions))
                        self.dump['text'] = '\n'.join(contents)
                        try:
                            requests.post(self.webhook, json.dumps(self.dump))
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
                    contents.append(' '.join(self.user_mentions))
                    self.dump['text'] = '\n'.join(contents)
                    try:
                        requests.post(self.webhook, json.dumps(self.dump))
                    except:
                        print('Unable to push message, please check network or configuration file')
                    raise ex

            return wrapper_sender

        return decorator_sender

    def push(self, contents):
        contents.append(' '.join(self.user_mentions))
        self.dump['text'] = '\n'.join(contents)
        try:
            requests.post(self.webhook, json.dumps(self.dump))
        except:
            print('Unable to push message, please check network or configuration file')
