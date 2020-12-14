import logging
import requests
from bs4 import BeautifulSoup
from aiogram import Bot, Dispatcher, executor, types

from api_token import token


logging.basicConfig(level=logging.INFO)


bot = Bot(token=token)
dp = Dispatcher(bot)


def parse(article):
    url = f"https://novosibirskshop.e2e4online.ru/shop/catalog/xmlPrice.faces?search={article}"
    print(url)

    headers = {
        'accept': '*/*',
        'user - agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:83.0) Gecko/20100101 Firefox/83.0',
    }

    req = requests.get(url, headers=headers)
    src = req.text

    with open('index.html', 'w', encoding='UTF-8') as file:
        file.write(src)

    with open('index.html', encoding='UTF-8') as file:
        src = file.read()

    soup = BeautifulSoup(src, 'lxml')
    product_title = soup.find("name").get('value')
    print(product_title)

    return product_title


@dp.message_handler()
async def echo(message: types.Message):
    if (message.text).isdigit():
        if len(message.text) % 6 == 0:
            article = message.text
            print(article)
            print(type(article))
            answer = parse(article)
            await message.answer(str(answer))
    else:
        await message.answer('Нет, Валера, не так...')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
