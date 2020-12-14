import logging

from aiogram import Bot, Dispatcher, executor, types
from aiogram.utils.emoji import emojize
from aiogram.types.message import ContentType
from aiogram.utils.markdown import italic, text
from aiogram.types import InputMediaPhoto, ChatActions


from config import TOKEN
from functions import parse
import keyboards as kb


logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN, parse_mode=types.ParseMode.MARKDOWN)
dp = Dispatcher(bot)


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


@dp.message_handler(commands=["geophone"])
async def geophone(message):
    # Эти параметры для клавиатуры необязательны, просто для удобства
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    button_phone = types.KeyboardButton(text="Отправить номер телефона",
                                        request_contact=True)
    button_geo = types.KeyboardButton(text="Отправить местоположение",
                                      request_location=True)
    keyboard.add(button_phone, button_geo)
    await bot.send_message(message.chat.id,
                           "Отправь мне свой номер телефона или поделись "
                           "местоположением, жалкий человечишка!",
                           reply_markup=keyboard)


@dp.message_handler(commands=['1'])
async def process_command_1(message: types.Message):
    await message.reply("Первая инлайн кнопка", reply_markup=kb.inline_kb1)


@dp.callback_query_handler(lambda c: c.data == 'count')
async def process_callback_button1(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id,
                           'Нажата первая кнопка!')


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


@dp.message_handler(content_types=ContentType.ANY)
async def echo(message: types.Message):
    if message.text == 'Новый заказ':
        await message.reply('Введи артикул товара (через пробел)')
    elif message.text.isdigit():
        if len(message.text) % 6 == 0:
            answer, images = parse(message.text)

            media = [InputMediaPhoto(images[0],
                                     answer)]

            for img in images[1:]:
                media.append(InputMediaPhoto(img))

            await bot.send_chat_action(message.from_user.id,
                                       ChatActions.TYPING)

            await bot.send_media_group(message.from_user.id,
                                       media,
                                       reply_to_message_id=message.message_id,
                                       )

            await message.reply('Цена, кол-во?',
                                reply_markup=kb.inline_kb1,
                                )
    else:
        message_text = text(
            emojize('Я не знаю, что с этим делать :astonished:'),
            italic('\nЯ просто напомню,'), 'что есть', '/help')
        await message.reply(message_text)


if __name__ == '__main__':
    executor.start_polling(dp)
