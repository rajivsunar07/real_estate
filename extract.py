import json
import requests
from bs4 import BeautifulSoup
import asyncio
import aiohttp

last_page = 42
buy_links = []
for page_num in range(1, last_page+1):
    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'
    }
    res = BeautifulSoup(requests.get("https://gharsansarnepal.com/buy-properties-in-nepal?page={}".format(page_num), headers=headers).content, 'html.parser')
    link = [x.find('a')['href'] for x in res.find_all('div', {'class': 'explore-item-title'})]
    buy_links.extend(link)

rent_links = []
last_page = 4
for page_num in range(1, last_page+1):
    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'
    }
    res = BeautifulSoup(requests.get("https://gharsansarnepal.com/gharsansar/nepal/rent?page={}".format(page_num)).content, 'html.parser')
    rent_links.extend([x.find('a')['href'] for x in res.find_all('div', {'class': 'explore-item-title'})])

links  = {'buy_links': list(set(buy_links)), 'rent_links': list(set(rent_links))}
with open('links.json', 'w') as f:
    json.dump(links, f, indent=4)

def get_data(soup): 

    price = soup.find('div', {"class": "banner-sub-title"}).find("h4").text
    location = soup.find('div', {'class': 'overview-sub-title'}).find('h5').text
    overview_details = soup.find('div', {'class': 'overview-details'})
    
    try:
        features = [x.text.strip() for x in overview_details.find('input', {'value': 'FEATURES'}).parent.find_next('ul').find_all('li')]
    except AttributeError:
        features = []

    try:
        property_description = [(x.find('input')['value'], x.text.strip()) if x.find('input') != None else ('Other', x.text.strip()) for x in overview_details.find('input', {'value': 'Property details'}).parent.find_all_next('p')] 
    except:
        property_description = []

    amenities = [x.text.strip() for x in soup.find('div', {'class': 'amenities'}).find_all('p')]

    try:
        map_location = soup.find('div', {'class': 'map-field'}).find('iframe')['src']
    except:
        map_location = []

    try:
        property_details = [(x.text.replace('\n', '').split(":")[0].strip(), x.text.replace('\n', '').split(":")[1].strip()) for x in soup.find("span", string="Property details").findNext("div").find("ul").find_all("li")]
    except:
        property_details = []

    data = {
        'price': price,
        'location': location,
        'features': features,
        'property_description': dict(property_description),
        'amenities': amenities,
        'map_location': map_location,
        'property_details': dict(property_details)
    }

    return data

async def get_tasks(session, links):
    tasks = []
    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'
    }
    for link in links:
        tasks.append(session.get(link, ssl=False, headers=headers))
    return tasks

async def get_session(links, output_file_name):
    async with aiohttp.ClientSession() as session:
        tasks = await get_tasks(session, links)

        responses = await asyncio.gather(*tasks)
        for res in responses:
            try:
                res_text = await res.text()
                soup = BeautifulSoup(res_text, 'html.parser')
                id = str(res.url).split('/')[-1]

                data =  get_data(soup)
                
                with open(output_file_name, 'r') as f:
                    output_data = json.load(f)       
                output_data[id] = data
                with open(output_file_name, 'w') as f:
                    json.dump(output_data, f, indent=4)
            except UnicodeDecodeError:
                print(UnicodeDecodeError, res.url)
                continue
            

with open('links.json', 'r') as f:
    links = json.load(f)

buy_links = links['buy_links']
output_file_name = 'buy_property_data.json'
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
asyncio.run(get_session(buy_links, output_file_name))

rent_links = links['rent_links']
output_file_name = 'rent_property_data.json'
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
asyncio.run(get_session(rent_links, output_file_name))
