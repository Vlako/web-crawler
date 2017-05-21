from vkapi import VKApi
from pymongo import MongoClient
import argparse
import logging
logging.basicConfig(level=logging.INFO)


def main(group_id, access_token):

    client = MongoClient()
    db = client['vk']
    collection = db['vk_users']

    vk = VKApi(access_token)
    users = vk.get_group_members(group_id)
    for i in vk.get_group_links_ids(group_id):
        users += vk.get_group_members(i)
    users = list({u['uid']: u for u in users}.values())

    for i, user in enumerate(users):
        user['groups'] = vk.get_user_groups(user['uid'])
        if 'city' in user:
            user['city'] = vk.get_city_name(user['city'])
        collection.insert_one(user)
        if i % 1000 == 0:
            logging.info('Количество сохранненых пользователей: '+str(i+1))

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('group_id', type=str,
                        help='идентификатор или короткое имя группы в VK')
    parser.add_argument('access_token', type=str,
                        help='ключ доступа VK')
    options = parser.parse_args()
    main(options.group_id, options.access_token)