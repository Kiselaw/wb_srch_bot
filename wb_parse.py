import asyncio
from asyncio import Task
from urllib.parse import parse_qs, quote

import aiohttp
import nest_asyncio

nest_asyncio.apply()


def parse(vendor_code: str, product_name: str) -> list[tuple[str, int]]:
    """
    Парcер данных с wildberries.ru.
    """
    result = []

    async def get_data(session, url: str) -> None:
        """
        Поиск товара.
        """
        response = await session.get(url)
        data = await response.json(content_type=None)
        if not data:
            return
        found = False
        place = None
        for product in data['data']['products']:
            if product['id'] == int(vendor_code):
                found = True
            if found is True:
                place = data['data']['products'].index(product)
                break
        if place is not None:
            page = parse_qs(url)['page'][0]
            # Вообще нумерация элементов с 0, но так лучше восприятие
            # для пользователя взаимодействующего с ботом.
            result.append((page, place + 1))
        return

    async def tasks_creator() -> None:
        """
        Создание задач.
        """
        urls = [
            ('https://search.wb.ru/exactmatch/ru/common/v4/search?appType=1'
             '&couponsGeo=12,7,3,6,5,18,21'
             '&curr=rub&dest=-1216601,-337422,-1114193,-1123298'
             '&emp=0&lang=ru&locale=ru&page={0}&pricemarginCoeff=1.0'
             '&query={1}&reg=1'
             '&regions=80,64,83,4,38,33,70,82,69,68,86,30,40,48,1,22,66,31'
             '&resultset=catalog&sort=popular'
             '&spp=34&sppFixGeo=4'
             '&suppressSpellcheck=false'
             ).format(page, quote(product_name)) for page in range(1, 101)
        ]
        async with aiohttp.ClientSession() as session:
            tasks: list[Task] = []
            for url in urls:
                task = asyncio.create_task(get_data(session, url))
                tasks.append(task)
            await asyncio.gather(*tasks)
    asyncio.run(tasks_creator())
    return result
