import os
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart

import requests
from bs4 import BeautifulSoup
from aiogram.utils.markdown import bold

from email import encoders
from email.mime.base import MIMEBase
from email.mime.text import MIMEText

from config import EMAIL_PASS


def parse(article):
    url = f"https://novosibirskshop.e2e4online.ru/shop/catalog/item/" \
          f"?id={article}"

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

    try:
        price = soup.find("span", class_='price').text
        product_price = f"Закуп: {price}р"
    except AttributeError:
        product_price = "Нет в продаже"

    answer = f"{product_title}\n\n{bold(product_price)}"

    images = soup.find_all("a", class_='fancybox-thumb')
    product_images = []

    for img in images[:3]:
        product_images.append(img.get('href'))

    return answer, product_images


def send_email(recipient):
    date = datetime.today().strftime("%d.%m.%y")

    filepath = f'КП_от_{date}.pdf'
    filename = os.path.basename(filepath)
    part = MIMEBase('application', "octet-stream")
    part.set_payload(open(filepath, "rb").read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', 'attachment', filename=filename)

    email = "pyscript@yandex.ru"
    server = smtplib.SMTP("smtp.yandex.ru", 587)
    server.set_debuglevel(1)
    server.ehlo()
    server.starttls()
    server.login(email, EMAIL_PASS)

    msg = MIMEMultipart()

    msg['From'] = email
    msg['To'] = recipient
    msg['Subject'] = f'Коммерческое предложение от {date}'
    body = 'Актуальное коммерческое предложение во вложении.\n' \
           'При открытии вложения с мобильного устройства, ' \
           'рекомендуется сначала скачать его.'
    msg.attach(MIMEText(body, 'plain'))
    msg.attach(part)

    server.sendmail(email, recipient, msg.as_string())
    server.quit()
