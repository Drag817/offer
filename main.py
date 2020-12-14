import logging
import requests
from bs4 import BeautifulSoup
from aiogram import Bot, Dispatcher, executor, types
from aiogram.utils.emoji import emojize
from aiogram.utils.markdown import italic, text, code, bold
from aiogram.types import ParseMode, InputMediaPhoto

from api_token import token


logging.basicConfig(level=logging.INFO)


bot = Bot(token=token)
dp = Dispatcher(bot)


def parse(article):
    url = f"https://novosibirskshop.e2e4online.ru/shop/catalog/item/" \
          f"?id={article}"
    print(url)

    headers = {
        'accept': '*/*',
        'user - agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:83.0) '
                        'Gecko/20100101 Firefox/83.0',
    }

    req = requests.get(url, headers=headers)
    src = req.text

    with open('index.html', 'w', encoding='UTF-8') as file:
        file.write(src)

    with open('index.html', encoding='UTF-8') as file:
        src = file.read()

    soup = BeautifulSoup(src, 'lxml')

    product_title = (soup.find("div", class_='itemBlock').
                     find("h1").text.split('\n'))[0]
    print(product_title)

    product_price = soup.find("span", class_='price').text
    product_price = f"Закуп: {product_price}р."
    # print(product_price)

    answer = f"{product_title}\n\n{product_price}"

    imgs = soup.find_all("a", class_='fancybox-thumb')
    product_imgs = []

    for img in imgs[:3]:
        product_imgs.append(img.get('href'))

    print(product_imgs)
    return answer, product_imgs


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    await message.reply("Привет!\nЯ подготовлю КП!")


@dp.message_handler(commands=['help'])
async def process_help_command(message: types.Message):
    await message.reply("Отправь мне арткул товара")


@dp.message_handler()
async def echo(message: types.Message):
    if (message.text).isdigit():
        if len(message.text) % 6 == 0:
            article = message.text
            print(article)
            print(type(article))
            answer, imgs = parse(article)

            media = []

            media.append(
                InputMediaPhoto(types.InputFile.from_url(imgs[0]), answer))

            for img in imgs[1:]:
                media.append(InputMediaPhoto(img))

            await bot.send_media_group(message.from_user.id,
                                       media,
                                       reply_to_message_id=message.message_id,
                                       )
    else:
        message_text = text(
            emojize('Я не знаю, что с этим делать :astonished:'),
            italic('\nЯ просто напомню,'), 'что есть', '/help')
        await message.reply(message_text, parse_mode=ParseMode.MARKDOWN)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
