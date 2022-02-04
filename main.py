import logging  # импортируем модули для работы программы
import urllib

from aiogram import Bot, Dispatcher, executor, types # модуль aiogram для работы с api-telegram
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.utils.emoji import emojize
from aiogram.types.message import ContentType
from aiogram.utils.markdown import italic, text, bold, link
from aiogram.types import InputMediaPhoto, ChatActions, CallbackQuery
from aiogram.types import InputFile
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher.filters.state import StatesGroup, State
# from docx2pdf import convert # модуль для конвертирования в PDF

# импортирую ключи из файла конфигурации, а так же самописные модули
from config import TOKEN
from functions import send_email, take_list, orders_list, take_order, \
    order_job, new_order_job, items_to_excel, excel_to_dict, xml_from_edo, get_acc_info
from docx_creater import dict_to_word
import keyboards as kb

# создаю машину состояний через класс Stage
class Stage(StatesGroup):

    Q1 = State()
    Q2 = State()
    Q3 = State()
    Q4 = State()
    Q5 = State()
    Q6 = State()
    Q7 = State()

'''
Конечный автомат (Finite State Machine) — это математическая модель вычислений,
которая моделирует последовательную логику.
'''


logging.basicConfig(level=logging.INFO)

# Инициализирую объект бота
bot = Bot(token=TOKEN, parse_mode=types.ParseMode.MARKDOWN)

# Диспетчер необходим для обработки входящих обновлений из Telegram
dp = Dispatcher(bot, storage=MemoryStorage())
dp.middleware.setup(LoggingMiddleware())

# Планы для продакшена
# TODO: edit main message, not new message
# TODO: add "Bot is started" message to admin
# TODO: make try\except in handlers
# TODO: write reports (Exceptions) to admin

get_acc_info()

# Приветственное сообщение
@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    warn = get_acc_info()
    await bot.send_message(722639239, warn)


# Деактивация бота
@dp.message_handler(commands=['rm'])
async def process_rm_command(message: types.Message):
    await message.reply("Убираем шаблоны сообщений",
                        reply_markup=kb.ReplyKeyboardRemove())


# Активация бота
@dp.message_handler(commands=['activate'])
async def process_start_command(message: types.Message):
    await message.reply("...",
                        reply_markup=kb.greet_kb1)


# Начало работы с новым заказом
@dp.message_handler(Command('new_order')) # ловлю команду "new_order"
async def new_order_command(message: types.Message):
    await Stage.Q1.set() # перевожу себя в 1-е состояние
    await bot.send_message(message.from_user.id, # ответ бота
                           f"Введите токен доступа с {link('сайта', 'https://novosibirsk.e2e4online.ru/shop/custom/history/historyTable.faces')}")


@dp.message_handler(Command('excel_to_word')) # ловлю команду ""
async def new_order_command(message: types.Message):
    await Stage.Q4.set()
    await bot.send_message(message.from_user.id, 'Кидай расчетник!')


@dp.message_handler(Command('xml_from_edo')) # ловлю команду ""
async def new_order_command(message: types.Message):
    await Stage.Q7.set()
    await bot.send_message(message.from_user.id, 'Кидай XML-ку!')


@dp.message_handler(state=Stage.Q1) # ловлю сообщение от пользователя в 1-м состоянии
async def input_id(message: types.Message, state: FSMContext):
    # передаю в функцию "логический контекст" для вызова асинхронного хранилища
    if len(message.text) < 20: # проеврка длины ID сессии
        await bot.send_message(message.from_user.id,
                               'Всё еще жду идентификатор!')
    else:
        await bot.send_chat_action(message.from_user.id,  # "Бот печатает..."
                                   ChatActions.TYPING)

        async with state.proxy() as data: # вызываю асинхронное хранилище
            data['access_token'] = message.text # записываю ID сессии по ключу "session_id"
            data['consumer'] = '834623'


    consumer = '834623'
    take_list(consumer, message.text)  # передаю собранную инф-ю в свою ф-цию (1 этап)
    orders = orders_list()  # получаю список заказов (2 этап)

    orders_keyboard = types.InlineKeyboardMarkup()  # объявляю объект inline клавиатуры
    for order in orders:  # создаю кнопку на каждый заказ в цикле
        inline_btns = types.InlineKeyboardButton(
            f'Заказ {order} от {orders[order]["date"]} на сумму {orders[order]["cost"]}р.',
            callback_data=orders[order]["art"]
        )
        orders_keyboard.add(inline_btns)

    back_btn = types.InlineKeyboardButton('Назад', callback_data='back')  # Добавляю кнопку назад
    orders_keyboard.add(back_btn)

    async with state.proxy() as data:
        data['ord_kb'] = orders_keyboard

    await Stage.Q2.set()  # выставляю 2-е состояние

    await bot.send_message(message.from_user.id,
                           'Выберите заказ:',
                           reply_markup=orders_keyboard,
                           )

# Конструкция "with as":
#
# Не применяя:
#     file = open('file_path', 'w')
#     file.write('hello world !')
#     file.close()
#
# Применяя:
#     with open('file_path', 'w') as file:
#         file.write('hello world !')

        # await bot.send_message(message.from_user.id,
        #                        'Выберите профиль:',
        #                        reply_markup=kb.inline_kb1,
        #                        )


# @dp.callback_query_handler(state=Stage.Q1)
# async def choice_consumer(call: CallbackQuery, state: FSMContext):
#
#     # if call.data == 'fast-forward':
#     #     await Stage.Q4.set()
#     #     await bot.send_message(call.from_user.id,
#     #                            'Кидай расчетник!',
#     #                            )
#     #
#     # else:
#     await bot.send_chat_action(call.from_user.id, # "Бот печатает..."
#                                ChatActions.TYPING)
#
#     async with state.proxy() as data:
#         access_token = data['access_token']
#         data['consumer'] = '834623'
#
#     consumer = '834623'
#     take_list(consumer, access_token) # передаю собранную инф-ю в свою ф-цию (1 этап)
#     orders = orders_list() # получаю список заказов (2 этап)
#
#     orders_keyboard = types.InlineKeyboardMarkup() # объявляю объект inline клавиатуры
#     for order in orders: # создаю кнопку на каждый заказ в цикле
#         inline_btns = types.InlineKeyboardButton(
#             f'Заказ {order} от {orders[order]["date"]} на сумму {orders[order]["cost"]}р.',
#             callback_data=orders[order]["art"]
#         )
#         orders_keyboard.add(inline_btns)
#
#     back_btn = types.InlineKeyboardButton('Назад', callback_data='back') # Добавляю кнопку назад
#     orders_keyboard.add(back_btn)
#
#     async with state.proxy() as data:
#         data['ord_kb'] = orders_keyboard
#
#     await Stage.Q2.set() # выставляю 2-е состояние
#
#     await bot.send_message(call.from_user.id,
#                            'Выберите заказ:',
#                            reply_markup=orders_keyboard,
#                            )


@dp.callback_query_handler(state=Stage.Q2)
async def choice_order(call: CallbackQuery, state: FSMContext):
    await bot.send_chat_action(call.from_user.id,
                               ChatActions.TYPING)

    if call.data == 'back': # ... если была нажата кнопка назад
        await Stage.Q1.set()
        await bot.send_message(call.from_user.id,
                               'Выберите профиль:',
                               reply_markup=kb.inline_kb1,
                               )
    else:
        # достаю ID сессии на сайте и инф-ю о кабинете
        async with state.proxy() as data:
            access_token = data['access_token']
            consumer = data['consumer']

        order = call.data # получаю номер заказа
        take_order(consumer, access_token, order) # передаю в функцию парсинга заказа
        total_price = 0 # объявляю переменную итоговой стоимости

        if order != '1':
            answer = f'Заказ №{order}\n\n'
            items, articles = order_job() # получаю словарь с товарами и список артикулов товаров
        else:
            answer = f'Новый заказ\n\n'
            items, articles = new_order_job()

        async with state.proxy() as data:
            data['items'] = items # сохраняю словарь items в "словарь" data по ключу items

        print(items) # вывожу товары из заказа
        warn = False
        for item in items:
            art_link = f"https://novosibirsk.e2e4online.ru/shop/catalog/item/?id={items[item]['art']}"
            answer += f"{articles.index(item) + 1}. {items[item]['name'].split(',')[0]} - {items[item]['qty']}шт. - {items[item]['cost']}р. - "
            answer += f"{link(items[item]['art'], art_link)}\n"
            total_price += items[item]['cost'] * items[item]['qty']
            if items[item]['cost'] == 0:
                warn = '\n*ВНИМАНИЕ! - В ЗАКАЗЕ ЕСТЬ ТОВАР КОТОРЫЙ ОТСУТСТВУЕТ*'*10
                warn += f"\n\n{articles.index(item) + 1}. {items[item]['name'].split(',')[0]} - {link(items[item]['art'], art_link)}"

        answer += f"\nВсего наименований {len(items)} на сумму {total_price}руб."
        if warn:
            answer += f'\n\n{warn}'
        await Stage.Q3.set()
        await bot.send_message(call.from_user.id, text=answer, reply_markup=kb.inline_kb2)


@dp.callback_query_handler(state=Stage.Q3)
async def order_to_excel(call: CallbackQuery, state: FSMContext):

    if call.data == 'back':
        async with state.proxy() as data:
            orders_keyboard = data['ord_kb']
        await Stage.Q2.set()
        await bot.send_message(call.from_user.id,
                               'Выберите заказ:',
                               reply_markup=orders_keyboard,
                               )
    else:

        await bot.send_chat_action(call.from_user.id, # "Бот отправляет документ..."
                                   ChatActions.UPLOAD_DOCUMENT)

        async with state.proxy() as data:
            items = data['items']
            consumer = data['consumer']

        items_to_excel(items, consumer) # переношу товары из заказа в excel книгу

        await Stage.Q4.set()
        await bot.send_document(call.from_user.id, # бот присылает заполненный excel
                                InputFile(f'Расчетник.xlsx'))

        await bot.send_message(call.from_user.id,
                               'Проверьте Расчетник и отправьте мне отредактированную версию')


@dp.message_handler(content_types=ContentType.DOCUMENT, state=Stage.Q4)
async def excel_to_word(msg: types.Message, state: FSMContext):

    await bot.send_chat_action(msg.from_user.id,
                               ChatActions.UPLOAD_DOCUMENT)

    # Бот получает excel документ
    document_id = msg.document.file_id # создаю объект ID документа
    file_info = await bot.get_file(document_id) # получаю объект информации по ID документа
    fi = file_info.file_path # получаю объект документа
    name = 'Расчетник.xlsx' # ввожу имя документа, при сохранении
    urllib.request.urlretrieve( # скачиваю документ с указанными параметрами
        f'https://api.telegram.org/file/bot{TOKEN}/{fi}', f'./{name}')

    data = excel_to_dict() # создаю словарь из excel документа
    dict_to_word(data) # передаю словарь в функцию для формирования Коммерческого предложения

    await bot.send_document(msg.from_user.id, # бот отправляет документ на проверку\редактирование
                            InputFile('КП.docx'))


    await bot.send_message(msg.from_user.id,
                           text=f'Благодарю за работу!',
                           )
    await state.finish()


@dp.message_handler(content_types=ContentType.DOCUMENT, state=Stage.Q5)
async def word_to_pdf(msg: types.Message):

    await bot.send_chat_action(msg.from_user.id,
                               ChatActions.UPLOAD_DOCUMENT)

    document_id = msg.document.file_id
    file_info = await bot.get_file(document_id)
    fi = file_info.file_path
    name = 'КП.docx'
    urllib.request.urlretrieve(
        f'https://api.telegram.org/file/bot{TOKEN}/{fi}', f'./{name}')

    # convert(name) # конвертирует отредактированный документ в PDF

    await bot.send_document(msg.from_user.id, # присылает PDF на проверку
                            InputFile('КП.pdf'))
    await msg.answer('Введите почту получателя')
    await Stage.Q6.set()


@dp.message_handler(state=Stage.Q6)
async def send_to_client(message: types.Message, state: FSMContext):
    recipient = message.text # получает почту получателя
    send_email(recipient) # передает получателя в функцию для отправки письма

    await state.finish() # выходит из машины состояний
    await bot.send_message(message.from_user.id,
                           text='Письмо отправлено!\nБлагодарю!',
                           )


@dp.message_handler(content_types=ContentType.DOCUMENT, state=Stage.Q7)
async def parse_xml(msg: types.Message, state: FSMContext):
    await bot.send_chat_action(msg.from_user.id,
                               ChatActions.TYPING)

    # Бот получает xml документ
    document_id = msg.document.file_id # создаю объект ID документа
    file_info = await bot.get_file(document_id) # получаю объект информации по ID документа
    fi = file_info.file_path # получаю объект документа
    name = 'Документ.xml' # ввожу имя документа, при сохранении
    urllib.request.urlretrieve( # скачиваю документ с указанными параметрами
        f'https://api.telegram.org/file/bot{TOKEN}/{fi}', f'./{name}')

    data = xml_from_edo() # создаю словарь для ответа бота
    answer = f"{data['doc_name']} от {data['date']}\n\n" \
             f"Контрагент: {data['agent']}\n\n"

    for el in data['items']:
        item = f"{el['num']}. {el['name']} - {el['qty']}шт. по {round(float(el['price'])*1.2, 2)}р. = {el['cost']}р.\n"
        answer += item

    answer += f"\n Итого наименований {len(data['items'])}шт. на сумму {data['total']}р."

    await bot.send_message(msg.from_user.id, answer)
    await state.finish()


# Заглушка
@dp.message_handler(content_types=ContentType.ANY, state=[Stage.Q1, Stage.Q2, Stage.Q3, Stage.Q4, Stage.Q5])
async def default(message: types.Message):
    message_text = text(
        emojize('Я не знаю, что с этим делать :astonished:'),
        italic('\nЯ просто напомню,'), 'что есть', '/help')
    await message.reply(message_text)

# Запуск бота
if __name__ == '__main__':
    executor.start_polling(dp)
