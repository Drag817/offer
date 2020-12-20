import logging
import urllib
from datetime import datetime
import io

from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.utils.emoji import emojize
from aiogram.types.message import ContentType
from aiogram.utils.markdown import italic, text, bold
from aiogram.types import InputMediaPhoto, ChatActions, CallbackQuery
from aiogram.types import InputFile
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher.filters.state import StatesGroup, State
from docx2pdf import convert

from config import TOKEN
from functions import parse, send_email
from docx_creater import offer_crate
import keyboards as kb


class Stage(StatesGroup):

    Q1 = State()
    Q2 = State()
    Q3 = State()
    Q4 = State()
    Q5 = State()


logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN, parse_mode=types.ParseMode.MARKDOWN)

dp = Dispatcher(bot, storage=MemoryStorage())
dp.middleware.setup(LoggingMiddleware())


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    await message.reply("Привет!\nЯ подготовлю КП!")


@dp.message_handler(commands=['help'])
async def process_help_command(message: types.Message):
    await message.reply("Отправь мне арткул товара")


@dp.message_handler(commands=['rm'])
async def process_rm_command(message: types.Message):
    await message.reply("Убираем шаблоны сообщений",
                        reply_markup=kb.ReplyKeyboardRemove())


@dp.message_handler(commands=['activate'])
async def process_start_command(message: types.Message):
    await message.reply("Давай создадим новый заказ",
                        reply_markup=kb.greet_kb1)


@dp.message_handler(Command('new_order'))
async def echo(message: types.Message):
    await message.answer('Введите артикулы товаров через пробел')
    await Stage.Q1.set()


@dp.message_handler(state=Stage.Q1)
async def process(message: types.Message, state: FSMContext):
    await bot.send_chat_action(message.from_user.id,
                               ChatActions.TYPING)

    art_list = message.text.split()
    for art in art_list:
        if art.isdigit() and len(art) % 6 == 0:
            continue
        else:
            await state.finish()
            return await message.answer('Неверно введены артикулы!')

    async with state.proxy() as data:
        try:
            for art in art_list:
                data['art_list'].append(art)
            print(data['art_list'])
        except KeyError:
            data['art_list'] = art_list
        data['current_art'] = art_list[0]
        data['message'] = message
        current_art = art_list[0]

    answer, images = parse(current_art)

    async with state.proxy() as data:
        data[f'article:{current_art}'] = current_art
        data[f'images:{current_art}'] = images
        data[f'count:{current_art}'] = 1
        data[f'price:{current_art}'] = 0

    count = 1
    price = 0
    answer += bold(f'\nКоличество: {count}\nЦена продажи: {price}р')

    async with state.proxy() as data:
        data[f'title:{current_art}'] = answer

    media = []

    for img in images:
        media.append(InputMediaPhoto(img))

    await bot.send_media_group(message.from_user.id,
                               media,
                               reply_to_message_id=message.message_id,
                               )

    await bot.send_message(message.from_user.id,
                           text=emojize(answer),
                           reply_markup=kb.inline_kb1,
                           )


@dp.callback_query_handler(text='count', state=Stage.Q1)
async def count(call: CallbackQuery):
    await call.message.answer('Введите количество:')
    await Stage.Q2.set()


@dp.message_handler(state=Stage.Q2)
async def count_edit(message: types.Message, state: FSMContext):
    count = message.text

    async with state.proxy() as data:
        current_art = data['current_art']
        answer = data[f'title:{current_art}']

    answer = answer.replace('Количество: 1', f'Количество: {count}')

    async with state.proxy() as data:
        data[f'count:{current_art}'] = count
        data[f'title:{current_art}'] = answer

    await bot.send_message(message.from_user.id,
                           text=emojize(answer),
                           )


@dp.callback_query_handler(text='price', state=Stage.Q1)
async def price1(call: CallbackQuery):
    await call.message.answer('Укажите цену:')
    await Stage.Q3.set()


@dp.callback_query_handler(text='price', state=Stage.Q2)
async def price2(call: CallbackQuery):
    await call.message.answer('Укажите цену:')
    await Stage.Q3.set()


@dp.message_handler(state=Stage.Q3)
async def price_edit(message: types.Message, state: FSMContext):
    price = message.text

    async with state.proxy() as data:
        current_art = data['current_art']
        answer = data[f'title:{current_art}']

    answer = answer.replace('Цена продажи: 0р', f'Цена продажи: {price}р')

    async with state.proxy() as data:
        data[f'price:{current_art}'] = price
        data[f'title:{current_art}'] = answer

    await bot.send_message(message.from_user.id,
                           text=emojize(answer),
                           )


@dp.callback_query_handler(text='continue', state=Stage.Q3)
async def next_prod(call: CallbackQuery, state: FSMContext):
    await call.answer('Ищу следующий товар...')

    async with state.proxy() as data:
        current_art = data['current_art']
        art_list = data['art_list']
        message = data['message']
        index = art_list.index(current_art)
        try:
            current_art = data['current_art'] = art_list[index + 1]
        except IndexError:
            return await bot.send_message(message.from_user.id,
                                          text='Артикулы обработаны. '
                                               'Вы можете:',
                                          reply_markup=kb.inline_finalize,)

    await bot.send_chat_action(message.from_user.id,
                               ChatActions.TYPING)

    await Stage.Q1.set()

    answer, images = parse(current_art)

    async with state.proxy() as data:
        data[f'article:{current_art}'] = current_art
        data[f'images:{current_art}'] = images
        data[f'count:{current_art}'] = 1
        data[f'price:{current_art}'] = 0

    count = 1
    price = 0
    answer += bold(f'\nКоличество: {count}\nЦена продажи: {price}р')

    async with state.proxy() as data:
        data[f'title:{current_art}'] = answer

    media = []

    for img in images:
        media.append(InputMediaPhoto(img))

    await bot.send_media_group(message.from_user.id,
                               media,
                               reply_to_message_id=message.message_id,
                               )

    await bot.send_message(message.from_user.id,
                           text=emojize(answer),
                           reply_markup=kb.inline_kb1,
                           )


@dp.callback_query_handler(text='add', state=Stage.Q3)
async def again(call: CallbackQuery):
    await call.message.answer('Введите артикулы товаров через пробел')
    await Stage.Q1.set()


@dp.callback_query_handler(text='create', state=Stage.Q3)
async def offer_docx(call: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        message = data['message']

    await bot.send_chat_action(message.from_user.id,
                               ChatActions.UPLOAD_DOCUMENT)

    order = {}
    async with state.proxy() as data:
        order.update(data)
        message = data['message']

    date = datetime.today().strftime("%d.%m.%y")
    offer_crate(order)

    msg = 'Прверьте, пожалуйста, документ. Если всё в порядке - ' \
          'Нажмите "В PDF". По необходимости, Вы можете отредактировать' \
          'документ и прислать его сюда!'

    await Stage.Q4.set()
    await bot.send_document(message.from_user.id,
                            InputFile(f'КП_от_{date}.docx'))

    await bot.send_message(message.from_user.id,
                           text=msg,
                           reply_markup=kb.pdf,
                           )


@dp.callback_query_handler(text='convert', state=Stage.Q4)
async def docx_to_pdf_inline(call: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        message = data['message']

    await bot.send_chat_action(message.from_user.id,
                               ChatActions.RECORD_AUDIO)

    date = datetime.today().strftime("%d.%m.%y")
    convert(f'КП_от_{date}.docx')

    await call.message.answer('Введите почту получателя')
    await Stage.Q5.set()


@dp.message_handler(content_types=ContentType.DOCUMENT, state=Stage.Q4)
async def docx_to_pdf_file(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        message = data['message']

    await bot.send_chat_action(message.from_user.id,
                               ChatActions.RECORD_AUDIO)

    date = datetime.today().strftime("%d.%m.%y")

    document_id = msg.document.file_id
    file_info = await bot.get_file(document_id)
    fi = file_info.file_path
    name = f'КП_от_{date}.docx'
    urllib.request.urlretrieve(
        f'https://api.telegram.org/file/bot{TOKEN}/{fi}', f'./{name}')

    convert(name)

    await bot.send_message(message.from_user.id,
                           text='Введите почту получателя',
                           )
    await Stage.Q5.set()


@dp.message_handler(state=Stage.Q5)
async def price_edit(message: types.Message, state: FSMContext):
    recipient = message.text
    send_email(recipient)

    await state.finish()

    await bot.send_message(message.from_user.id,
                           text='Благодарю за работу!',
                           )


@dp.message_handler(content_types=ContentType.ANY)
async def default(message: types.Message):
    message_text = text(
        emojize('Я не знаю, что с этим делать :astonished:'),
        italic('\nЯ просто напомню,'), 'что есть', '/help')
    await message.reply(message_text)


if __name__ == '__main__':
    executor.start_polling(dp)
