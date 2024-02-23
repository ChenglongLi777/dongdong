'''
@Project : Kazumi 
@File : DesktopNotificator.py
@Author : 李成龙
@Date : 2024/2/23 15:58 
@Email : Chenglongli@cug.edu.cn
@Description : 
'''
import functools
import os
import datetime
import socket
import traceback
import platform
import subprocess
from .configure import DATE_FORMAT


class DesktopNotificator:
    def __init__(self, taskname=None, title='RingRingRing'):
        '''
        This class will configure the settings for desktop notification.
        :param taskname:
        :param title: title of the message
        '''
        self.taskname = taskname
        self.title = title
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
                        title = self.title
                        contents = self.startmsg
                    else:
                        title = 'The script starts running 🎬'
                        contents = [f'Machine name: {host_name}\n',
                                    f'Task name: {self.taskname}\n',
                                    f'Starting date: {start_time.strftime(DATE_FORMAT)}']
                    message = '\n'.join(contents)
                    try:
                        self.push(title, message)
                    except:
                        print('Unable to push message, please check network or configuration file')
                try:
                    value = func(*args, **kwargs)

                    if master_process:
                        end_time = datetime.datetime.now()
                        elapsed_time = end_time - start_time
                        if self.completemsg:
                            title = self.title
                            contents = self.completemsg
                        else:
                            title='The script is complete 🎉'
                            contents = [f'Machine name: {host_name}\n',
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
                        message = '\n'.join(contents)
                        try:
                            self.push(title, message)
                        except:
                            print('Unable to push message, please check network or configuration file')

                    return value

                except Exception as ex:
                    end_time = datetime.datetime.now()
                    elapsed_time = end_time - start_time
                    if self.crashmsg:
                        title = self.title
                        contents = self.crashmsg
                    else:
                        title='The script has crashed ☠️'
                        contents = [f'Machine name: {host_name}\n',
                                    f'Task name: {self.taskname}\n',
                                    f'Starting date: {start_time.strftime(DATE_FORMAT)}\n',
                                    f'Crash date: {end_time.strftime(DATE_FORMAT)}\n',
                                    f'Crashed running duration: {str(elapsed_time)}\n\n',
                                    f'Here is the error:\n\n{ex}\n\n',
                                    f'{traceback.format_exc()}']
                    message = '\n'.join(contents)
                    try:
                        self.push(title, message)
                    except:
                        print('Unable to push message, please check network or configuration file')
                    raise ex

            return wrapper_sender

        return decorator_sender

    def push(self, title, message):
        '''
        This function is used to push message to desktop
        :param title:
        :param message:
        :return:
        '''
        # Check the OS
        if platform.system() == "Darwin":
            subprocess.run(["sh", "-c", f"osascript -e 'display notification \"{message}\" with title \"{title}\"'"])

        elif platform.system() == "Linux":
            subprocess.run(["notify-send", title, message])

        elif platform.system() == "Windows":
            try:
                from win10toast import ToastNotifier
            except ImportError as err:
                print(
                    'Error: to use Windows Desktop Notifications, you need to install `win10toast` first. Please run `pip install win10toast==0.9`.')

            toaster = ToastNotifier()
            toaster.show_toast(title,
                               message,
                               icon_path=None,
                               duration=5)
