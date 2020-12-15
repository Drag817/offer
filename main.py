import logging

from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.utils.emoji import emojize
from aiogram.types.message import ContentType
from aiogram.utils.markdown import italic, text, bold
from aiogram.types import InputMediaPhoto, ChatActions, CallbackQuery
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher.filters.state import StatesGroup, State

from config import TOKEN
from functions import parse
import keyboards as kb


class Stage(StatesGroup):

    Q1 = State()
    Q2 = State()
    Q3 = State()


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


# @dp.message_handler(commands=["geophone"])
# async def geophone(message):
#     # Эти параметры для клавиатуры необязательны, просто для удобства
#     keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
#     button_phone = types.KeyboardButton(text="Отправить номер телефона",
#                                         request_contact=True)
#     button_geo = types.KeyboardButton(text="Отправить местоположение",
#                                       request_location=True)
#     keyboard.add(button_phone, button_geo)
#     await bot.send_message(message.chat.id,
#                            "Отправь мне свой номер телефона или поделись "
#                            "местоположением, жалкий человечишка!",
#                            reply_markup=keyboard)


# @dp.message_handler(commands=['1'])
# async def process_command_1(message: types.Message):
#     await message.reply("Первая инлайн кнопка", reply_markup=kb.inline_kb1)


# @dp.callback_query_handler(lambda c: c.data == 'count')
# async def process_callback_button1(callback_query: types.CallbackQuery):
#     await bot.answer_callback_query(callback_query.id)
#     await bot.send_message(callback_query.from_user.id,
#                            'Нажата первая кнопка!')


# @dp.callback_query_handler(lambda c: c.data and c.data.startswith('btn'))
# async def process_callback_kb1btn1(callback_query: types.CallbackQuery):
#     code = callback_query.data[-1]
#     if code.isdigit():
#         code = int(code)
#     if code == 2:
#         await bot.answer_callback_query(callback_query.id,
#                                         text='Нажата вторая кнопка')
#     elif code == 5:
#         await bot.answer_callback_query(
#             callback_query.id,
#             text='Нажата кнопка с номером 5.\n'
#                  'А этот текст может быть длиной до 200 символов 😉',
#             show_alert=True)
#     else:
#         await bot.answer_callback_query(callback_query.id)
#     await bot.send_message(callback_query.from_user.id,
#                            f'Нажата инлайн кнопка! code={code}')


# @dp.message_handler(commands=['2'])
# async def process_command_2(message: types.Message):
#     await message.reply("Отправляю все возможные кнопки",
#                         reply_markup=kb.inline_kb_full)


@dp.message_handler(Command('new_order'))
async def echo(message: types.Message):
    await message.answer('Введите артикулы товаров через пробел')

    await Stage.Q1.set()


@dp.message_handler(state=Stage.Q1)
async def process(message: types.Message, state: FSMContext):
    art_list = message.text.split()
    for art in art_list:
        print(art)
        if art.isdigit() and len(art) % 6 == 0:
            continue
        else:
            await state.finish()
            return await message.answer('Неверно введены артикулы!')

    async with state.proxy() as data:
        data['art_list'] = art_list
        data['current_art'] = art_list[0]
        data['message'] = message
        current_art = art_list[0]

        # async with state.proxy() as data:
        #     art_list = data['art_list']

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

    await bot.send_chat_action(message.from_user.id,
                               ChatActions.TYPING)

    await bot.send_media_group(message.from_user.id,
                               media,
                               reply_to_message_id=message.message_id,
                               )

    await bot.send_message(message.from_user.id,
                           text=emojize(answer),
                           reply_markup=kb.inline_kb1,
                           )


@dp.callback_query_handler(text='count', state=Stage.Q1)
async def count(call: CallbackQuery, state: FSMContext):
    print(call.message.text)

    async with state.proxy() as data:
        print(data['current_art'])
        current_art = data['current_art']
        print(data[f'title:{current_art}'])

    await call.message.answer('Введите количество:')
    await Stage.Q2.set()


@dp.message_handler(state=Stage.Q2)
async def count_edit(message: types.Message, state: FSMContext):
    count = message.text

    async with state.proxy() as data:
        current_art = data['current_art']
        art_list = data['art_list']
        answer = data[f'title:{current_art}']

    answer = answer.replace('Количество: 1', f'Количество: {count}')

    async with state.proxy() as data:
        data[f'count:{current_art}'] = count
        data[f'title:{current_art}'] = answer

    await bot.send_message(message.from_user.id,
                           text=emojize(answer),
                           )


@dp.callback_query_handler(text='price', state=Stage.Q1)
async def price1(call: CallbackQuery, state: FSMContext):
    await call.message.answer('Укажите цену:')
    await Stage.Q3.set()


@dp.callback_query_handler(text='price', state=Stage.Q2)
async def price2(call: CallbackQuery, state: FSMContext):
    await call.message.answer('Укажите цену:')
    await Stage.Q3.set()


@dp.message_handler(state=Stage.Q3)
async def price_edit(message: types.Message, state: FSMContext):
    price = message.text

    async with state.proxy() as data:
        current_art = data['current_art']
        art_list = data['art_list']
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
        index = art_list.index(current_art)
        # TODO: тут будет try-except
        current_art = data['current_art'] = art_list[index + 1]

        message = data['message']

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

    await bot.send_chat_action(message.from_user.id,
                               ChatActions.TYPING)

    await bot.send_media_group(message.from_user.id,
                               media,
                               reply_to_message_id=message.message_id,
                               )

    await bot.send_message(message.from_user.id,
                           text=emojize(answer),
                           reply_markup=kb.inline_kb1,
                           )


@dp.message_handler(content_types=ContentType.ANY)
async def default(message: types.Message):
    # if message.text.isdigit():
    #     if len(message.text) % 6 == 0:
    #         answer, images = parse(message.text)
    #
    #         count = 1
    #         price = 0
    #         answer += bold(f'\nКоличество: {count}\nЦена продажи: {price}р')
    #
    #         media = []
    #
    #         for img in images:
    #             media.append(InputMediaPhoto(img))
    #
    #         await bot.send_chat_action(message.from_user.id,
    #                                    ChatActions.TYPING)
    #
    #         await bot.send_media_group(message.from_user.id,
    #                                    media,
    #                                    reply_to_message_id=message.message_id,
    #                                    )
    #
    #         await bot.send_message(message.from_user.id,
    #                                text=emojize(answer),
    #                                reply_to_message_id=-1,
    #                                reply_markup=kb.inline_kb1,
    #                                )
    # else:
    message_text = text(
        emojize('Я не знаю, что с этим делать :astonished:'),
        italic('\nЯ просто напомню,'), 'что есть', '/help')
    await message.reply(message_text)


if __name__ == '__main__':
    executor.start_polling(dp)
