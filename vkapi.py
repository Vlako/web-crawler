import requests
import re
from functools import lru_cache


class VKApi:

    def __init__(self, access_token):
        self.access_token = access_token

    def get_group_members(self, group_id):
        params = {'group_id': group_id,
                  'offset': 0,
                  'access_token': self.access_token,
                  'fields': 'sex, bdate, city, country, lists, domain, has_mobile, contacts, connections, site, education, universities, schools, can_post, can_see_all_posts, can_see_audio, can_write_private_message, status, common_count, relation, relatives, home_town',
                  'version': '5.64'}

        user_count = requests.get('https://api.vk.com/method/groups.getMembers',
                                  params={'group_id': group_id,
                                          'version': '5.64',
                                          'access_token': self.access_token
                                          }).json()['response']['count']

        users = []
        for offset in range(user_count // 1000 + 1):
            params['offset'] = offset * 1000
            users += requests.get('https://api.vk.com/method/groups.getMembers',
                                  params=params).json()['response']['users']
        return users

    def get_group_links_ids(self, group_id):
        for link in requests.get('https://api.vk.com/method/groups.getById',
                                 params={'group_id': group_id,
                                         'version': '5.64',
                                         'fields': 'links',
                                         'access_token': self.access_token
                                         }).json()['response'][0]['links']:
            if link['url'].startswith('https://vk.com/'):
                if re.match('club\d+', link['url'].replace('https://vk.com/', '')):
                    link['url'] = link['url'].replace('https://vk.com/', '').replace('club', '')
                yield link['url'].replace('https://vk.com/', '')

    def get_user_groups(self, user_id):
        try:
            return requests.get('https://api.vk.com/method/groups.get',
                                params={'user_id': user_id,
                                        'version': '5.64',
                                        'access_token': self.access_token
                                        }).json()['response']
        except:
            return []

    @lru_cache(None)
    def get_city_name(self, city_id):
        city = requests.get('https://api.vk.com/method/database.getCitiesById',
                            params={'city_ids': city_id,
                                    'version': '5.64'
                                    }).json()['response']
        if len(city):
            return city[0]['name']
        else:
            return ''
