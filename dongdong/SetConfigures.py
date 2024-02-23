'''
@Project : 20240223-DongDong_Package 
@File : SetConfigures.py
@Author : 李成龙
@Date : 2024/2/23 18:29 
@Email : Chenglongli@cug.edu.cn
@Description : 
'''
import os

current_path = os.path.dirname(os.path.abspath(__file__))


def setconfigures(bark_token: str = None, teams_webhook: str = None, teams_user_mentions: [str] = [],
                  dingtalk_webhook: str = None, dingtalk_user_mentions: [str] = [], telegram_token: str = None,
                  telegram_chat_id: str = None, wechat_webhook: str = None, wechat_user_mentions: [str] = [],
                  wechat_user_mentions_mobile: [str] = []):
    str_keywords = {'bark_token': 1, 'teams_webhook': 2, 'dingtalk_webhook': 4, 'telegram_token': 6,
                    'telegram_chat_id': 7, 'wechat_webhook': 8}
    list_keywords = {'teams_user_mentions': 3, 'dingtalk_user_mentions': 5, 'wechat_user_mentions': 9,
                     'wechat_user_mentions_mobile': 10}
    with open(os.path.join(current_path, 'configure.py')) as f:
        configures = f.readlines()
    for name in str_keywords.keys():
        if eval(name):
            configures[str_keywords[name]] = f"{name} = '{eval(name)}'\n"
    for name in list_keywords.keys():
        if eval(name):
            string_list = ["'" + item + "'" for item in eval(name)]
            configures[list_keywords[name]] = f"{name} = [{', '.join(string_list)}]\n"
    with open(os.path.join(current_path, 'configure.py'), 'w') as f:
        f.writelines(configures)


if __name__ == '__main__':
    setconfigures(teams_webhook='1', teams_user_mentions=['12324', '5435', '6456', 'hjink'])
