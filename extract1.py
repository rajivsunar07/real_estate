import asyncio
import aiohttp
import json
import os
from bs4 import BeautifulSoup


async def get_tasks(session, links):
    tasks = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36',
        'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjIxNzc0NTI3OTksImlhdCI6MTUxNjAyMjk5OSwiaXNzIjoiQmFzb2JhYXMgTmVwYWwiLCJuYmYiOjE1MTYwMjI5OTksImp0aSI6Ikd1ZXN0VG9rZW4iLCJzdWIiOjB9.QikmNgBYmqch5HREGFEpUs4Xk3x-zFfDg5mhYJO7jM8'
    }
    for link in links:
        tasks.append(session.get(link, headers=headers, ssl=False))
    return tasks

async def main(links):
    async with aiohttp.ClientSession() as session:
        tasks =  await get_tasks(session, links)

        responses = await asyncio.gather(*tasks)
        response_jsons = []
        for res in responses:
            json_res = await res.json()
            response_jsons.extend([json_res])
            
        with open('raw_data.json', 'w') as f:
            json.dump(response_jsons, f, indent=4)
    
base_link = 'https://basobaas.com/api/properties/buy?page={}'
max_page_num = 319
links = [base_link.format(i) for i in range(1, max_page_num + 1)]
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
asyncio.run(main(links))