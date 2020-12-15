from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton

new_order_btn = KeyboardButton('/new_order')

# greet_kb = ReplyKeyboardMarkup()
# greet_kb.add(button_hi)

greet_kb1 = ReplyKeyboardMarkup(resize_keyboard=True,).add(new_order_btn)

# inline_btn_1 = InlineKeyboardButton('Изменить кол-во', callback_data='count')
# inline_btn_2 = InlineKeyboardButton('Изменить цену', callback_data='price')
#
# inline_kb1 = InlineKeyboardMarkup(row_width=2)
# inline_kb1.row(inline_btn_1, inline_btn_2)

inline_kb1 = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text='Изменить кол-во',
                                 callback_data='count'),
            InlineKeyboardButton(text='Указть цену',
                                 callback_data='price'),
        ],
        [
            InlineKeyboardButton(text='Продолжить ✅',
                                 callback_data='continue'),
        ],
    ]
)


# inline_kb_full = InlineKeyboardMarkup(row_width=2).add(inline_btn_1)
# inline_kb_full.add(InlineKeyboardButton('Вторая кнопка',
# callback_data='btn2'))
# inline_btn_3 = InlineKeyboardButton('кнопка 3', callback_data='btn3')
# inline_btn_4 = InlineKeyboardButton('кнопка 4', callback_data='btn4')
# inline_btn_5 = InlineKeyboardButton('кнопка 5', callback_data='btn5')
# inline_kb_full.add(inline_btn_3, inline_btn_4, inline_btn_5)
# inline_kb_full.row(inline_btn_3, inline_btn_4, inline_btn_5)
# inline_kb_full.insert(InlineKeyboardButton("query=''",
# switch_inline_query=''))
# inline_kb_full.insert(InlineKeyboardButton("query='qwerty'",
# switch_inline_query='qwerty'))
# inline_kb_full.insert(InlineKeyboardButton("Inline в этом же чате",
# switch_inline_query_current_chat='wasd'))
# inline_kb_full.add(InlineKeyboardButton('Уроки aiogram',
# url='https://surik00.gitbooks.io/aiogram-lessons/content/'))
