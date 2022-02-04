from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton


new_order_btn = KeyboardButton('/new_order')
excel_to_word = KeyboardButton('/excel_to_word')
xml_from_edo = KeyboardButton('/xml_from_edo')

greet_kb1 = ReplyKeyboardMarkup(resize_keyboard=True,).row(new_order_btn, excel_to_word)

inline_kb1 = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text='Физ лицо',
                                 callback_data='621378')
        ],
        [
            InlineKeyboardButton(text='ИП Холостенко',
                                 callback_data='834623'),
        ],
        # [
        #     InlineKeyboardButton(text='Расчетник в КП',
        #                          callback_data='fast-forward'),
        # ],
    ]
)


inline_kb2 = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text='Отправить данные в Расчетник',
                                 callback_data='to_excel')
        ],
        [
            InlineKeyboardButton(text='Назад',
                                 callback_data='back'),
        ],
    ]
)


inline_finalize = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text='Добавить товары',
                                 callback_data='add'),
        ],
        [
            InlineKeyboardButton(text='Сформировать КП ✅',
                                 callback_data='create'),
        ],
    ]
)

pdf = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text='В PDF ✅',
                                 callback_data='convert'),
        ],
    ]
)
