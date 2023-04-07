import aiohttp
import asyncio
import platform
import sys
from datetime import datetime, timedelta
import json



API_URL = 'https://api.privatbank.ua/p24api/exchange_rates?date='

CURRENCIES = ['USD', 'EUR']


async def reguest(date):
    url = API_URL + date.strftime('%d.%m.%Y')
    print(url)
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    return result
                else:
                    print("Error status: {resp.status} for {url}")
        except aiohttp.ClientConnectorError as err:
            print(f'Connection error: {url}', str(err))
            return None

async def data_interval(days):
    result = []
    for i in range(days):
        date = datetime.now() - timedelta(days=i)
        data = await reguest(date)
        if data is not None:
            result.append(data)
    return result


async def main(days):
    data = await data_interval(days)
    result = []
    for d in data:
        item = {}
        for rate in d['exchangeRate']:
            item['date'] = d['date']
            if rate['currency'] in CURRENCIES:
                if 'saleRate' in rate and 'purchaseRate' in rate:
                    item[rate['currency']] = {'sale': rate['saleRate'], 'purchase': rate['purchaseRate']}
                else:
                    continue
        result_item = {item['date']: {}}
        for currency in CURRENCIES:
            if currency in item:
                result_item[item['date']][currency] = {
                    'sale': item[currency]['sale'],
                    'purchase': item[currency]['purchase']
                }
        result.append(result_item)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    if len(sys.argv) > 1:
        days = int(sys.argv[1])
    else:
        days = 1
    try:
        if platform.system() == 'Windows':
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        if days > 10:
            print('You can get exchange rates for no more than 10 days')
            sys.exit(1)
    except ValueError:
        print('Please enter the required period between 1 and 10 days')
        sys.exit(1)
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main(days))

