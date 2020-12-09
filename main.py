import logging

from aiogram import Bot, Dispatcher, executor, types


logging.basicConfig(level=logging.INFO)


bot = Bot(token='1160713030:AAF2luS9Rof5f9YRnihjKOAIN4PGfv3wuH4')
dp = Dispatcher(bot)


@dp.message_handler()
async def echo(message: types.Message):
    await message.answer(message.text)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
