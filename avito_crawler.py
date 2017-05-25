import lxml.html as html
from pymongo import MongoClient
import argparse
import logging
import pytils
import requests
import random
logging.basicConfig(level=logging.INFO)

sections = {'личные вещи': 'lichnye_veschi',
            'транспорт': 'transport',
            'для дома и дачи': 'dlya_doma_i_dachi',
            'бытовая электроника': 'bytovaya_elektronika',
            'xобби и отдых': 'hobbi_i_otdyh',
            'недвижимость': 'nedvizhimost',
            'работа': 'rabota',
            'услуги': 'uslugi',
            'животные': 'zhivotnye',
            'для бизнеса': 'dlya_biznesa'}

proxies = []


def main(section, area, query, item_count):

    random.seed()

    client = MongoClient()
    db = client['avito']
    db['avito_items'].drop()
    collection = db['avito_items']

    area = pytils.translit.translify(area)
    base_url = 'https://www.avito.ru'
    url = base_url + '/{area}/{section}'.format(area=area, section=sections[section])

    page_num = 1
    while item_count > 0:
        page = html.fromstring(requests.get(url,
                                            params={'p': page_num, 'q': query},
                                            proxies={'https': random.choice(proxies)},
                                            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
                                            ).text)

        page_num += 1
        items = page.find_class('item')
        item_count -= len(items)
        if len(items) == 0:
            break

        for item in items:

            num = item.get('id')[1:]
            name = item.find_class('item-description-title-link').pop().text_content().strip()
            link = base_url + item.find_class('item-description-title-link').pop().get('href')
            date = item.find_class('date').pop().text_content().strip()

            inner_page = html.fromstring(requests.get(link,
                                                      proxies={'https': random.choice(proxies)},
                                                      headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
                                                      ).text)
            params = inner_page.find_class('item-params')
            if len(params):
                params = params.pop().text_content().strip()
            else:
                params = ''

            description = inner_page.find_class('item-description')
            if len(description):
                description = description.pop().text_content().strip()
            else:
                description = ''

            address = inner_page.find_class('item-map-location')
            if len(address):
                address = address.pop().text_content().strip()
            else:
                address = ''

            photo = item.find_class('gallery-img-frame')
            if len(photo):
                photo = base_url + photo.pop().get('data-url')
            else:
                photo = ''

            product = {
                'id': num,
                'name': name,
                'link': link,
                'date': date,
                'photo': photo,
                'address': address,
                'params': params,
                'description': description
            }

            collection.insert_one(product)


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--area', type=str, default='челябинск',
                        help='город или область, в котором будет проводиться поиск')
    parser.add_argument('--section', type=str, default='',
                        help='раздел объявлений')
    parser.add_argument('--count', type=int, default=20,
                        help='количество объявлений')
    parser.add_argument('query', type=str,
                        help='поисковый запрос')
    options = parser.parse_args()

    if options.section.lower() not in sections and options.section != '':
        true_args = False
        print('Раздела \'{}\' не существует'.format(options.section))

    with open('proxies', 'r') as proxies_file:
        proxies = ['https://' + proxy.strip() for proxy in proxies_file]

    main(options.section, options.area, options.query, options.count)