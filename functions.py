import math # матем. модуль, для округления вверх
import os # модуль для работы с элементами ОС
import smtplib # модуль для работы с протоколом SMTP
from datetime import datetime
from email.mime.multipart import MIMEMultipart # подключаю модуль для создания объектов класса MIME
from lxml import etree
import json


# Создание объектов электронной почты и MIME

import requests # модуль для get и post запросов
import openpyxl # модуль для работы с excel (xls, xlsx)
from openpyxl.styles import Font
from bs4 import BeautifulSoup # модуль для обработки html кода
from aiogram.utils.markdown import bold

# Подключаю модули для работы с почтой
from email import encoders
from email.mime.base import MIMEBase
from email.mime.text import MIMEText

from config import TOKEN, EMAIL_PASS, BUH_LOGIN, BUH_PASS_HASH # импортирую пароль почты из файла конфиг-ии


def take_list(consumer, access_token): # объявляю функцию

    url_main = 'https://novosibirsk.e2e4online.ru/shop/custom/history/historyTable.faces'

    headers = {  # объявляю заголовки (выдаю себя за человека)
        'Accept': 'text/html, */*; q=0.01',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:93.0) Gecko/20100101 Firefox/93.0',
        'Cookie': f'access_token={access_token}'
    }

    params = { # объявляю параметры для POST запроса
        'new_customer_id': consumer,
        'customer_change': '1', # флаг "1" = True, для возможности выбора и смены клиента на сайте
    }

    req = requests.get(url_main, headers=headers, params=params)
    print(req)

    # Записываю ответ в html-файл
    with open('index.html', 'w', encoding='UTF-8') as file:
        file.write(req.text)


def take_order(consumer, access_token, order):
    url = f"https://novosibirsk.e2e4online.ru/shop/custom/requestOrderPanel.faces"

    headers = {  # объявляю заголовки (выдаю себя за человека)
        'Accept': 'text/html, */*; q=0.01',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:93.0) Gecko/20100101 Firefox/93.0',
        'Cookie': f'access_token={access_token}'
    }

    params = {
        'new_customer_id': consumer,
        'id': order,
        'customer_change': '1',
    }

    req = requests.post(url, headers=headers, params=params)
    # print(req.text)
    src = req.text

    with open('order.html', 'w', encoding='UTF-8') as file:
        file.write(src)


def orders_list():
    # Открываю html-файл и записываю его в переменную
    with open('index.html', encoding='UTF-8') as file:
        src = file.read()

    soup = BeautifulSoup(src, 'lxml') # создаю объект SOUP (lxml - движок обработки html\xml кода)
    data = soup.find_all("tr")[1:] # нахожу все теги <tr>, начиная со 2-го
    orders = {} # объявляю словарь, в который буду записывать результаты парсинга

    for el in data: # прохожу в цикле по всем <tr> элементам
        # Методом подбора, проерки и тестирования выявил необходимые условия обработки <tr> эл-в
        if el.find('a') and el.find('a').text != el and el.find('td', style="width:20%"):
            order = el.find('a').text # достаю значения <a> эл-в
            orders.update({ # обновляю словарь след. данными...
                order: {
                    'art': el.find('a').text, # по ключу 'art' записываю ID заказа
                    'date': el.find('td', style="width:20%").text, # ... дату
                    'cost': el.find('span', class_="costGB").text.replace( # ... стоимость
                        '\xa0', '')
                }
            })

            if order == 'Новый':
                orders.update({
                    order: {
                        'art': '1',
                        'date': el.find('td', style="width:20%").text,
                        'cost': el.find('span', class_="costGB").text.replace(
                            '\xa0', '')
                    }
                })
    print(orders) # вывожу полученный словарь в консоль
    return orders # возвращаю полученный словарь


def order_job():
    with open('order.html', encoding='UTF-8') as file:
        src = file.read()

    soup = BeautifulSoup(src, 'lxml')
    data = soup.find_all("tr", class_='gtm-row')
    items = {}
    articles = [] # объявляю список (в С++ это массив) артикулов

    for el in data: # ... цикл
        if el.find("a"):
            if el.find('a').text in articles: # если элемент есть в списке артикулов ...
                items[el.find('a').text]['qty'] += int( # добавляю количество к уже имеющемуся товару
                    el.find("span", class_="itemQty").text)
            else: # если товар новый ...
                articles.append(el.find('a').text) # добавляю артикул товара в списов артикулов
                items.update({ # обновляю словарь след. данными
                    el.find('a').text: {
                        'art': el.find('a').text, # артикул товара
                        'name': el.find('td', class_='taL').text, # наименование
                        'cost': float( # цена
                            el.find('span', class_='price').text.replace(
                                '\xa0', '')),
                        'qty': int(el.find("span", class_='itemQty').text), # количество
                    }
                })

    print(items, articles) # вывожу в консоль
    return items, articles # возвращаю словарь с товарами и список артикулов товаров


def new_order_job():
    with open('order.html', encoding='UTF-8') as file:
        src = file.read()

    soup = BeautifulSoup(src, 'lxml')
    data = soup.find_all("tr", class_='gtm-row')
    items = {}
    articles = []

    for el in data:
        if el.find("a"):
            print(el.find('a').text)
            if el.find('a').text in articles:
                items[el.find('a').text]['qty'] += int(
                    el.find('input').get('data-prevval'))
            else:
                articles.append(el.find('a').text)
                if el.find('input'):
                    items.update({
                        el.find('a').text: {
                            'art': el.find('a').text,
                            'name': el.find('td', class_='taL').text,
                            'cost': float(el.find('input').get('data-price')),
                            'qty': int(el.find('input').get('data-prevval')),
                            }
                        })
                else:
                    items.update({
                        el.find('a').text: {
                            'art': el.find('a').text,
                            'name': f"{el.find('span').text.upper()} {el.find('td', class_='taL').text}",
                            'cost': 0,
                            'qty': 0
                        }
                    })

    # print(items)
    return items, articles


def items_to_excel(items, consumer):
    size = int(math.ceil(len(items) / 10.0)) * 10
    # подбираю размер болванки excel
    # округляю кол-во товаров в бОльшую сторону до десятков

    book = openpyxl.open(f'Расчетник{size}.xlsx') # открываю нужный по размеру документ
    sheet = book.active # выбираю активный лист

    # заношу нужные данные в нужные ячейки ...
    if consumer == '834623':
        sheet['C2'] = 'Да' # ... C2

    sheet['F2'] = 2000 # ... F2

    row = 5 # устанавливаю началньную 5-ую строку
    for item in items: # в цикле ...
        sheet[row][1].value = items[item]['name'] # заношу наименование товара из словаря
        sheet[row][1].font = Font(name='Times New Roman', size=12, bold=False)
        sheet[row][2].value = items[item]['qty'] # заношу кол-во товара из словаря
        sheet[row][2].font = Font(name='Times New Roman', size=12, bold=False)
        sheet[row][3].value = items[item]['cost'] # заношу цену товара из словаря
        sheet[row][3].font = Font(name='Times New Roman', size=12, bold=False)
        row += 1 # переключаюсь на след строку

    # date = datetime.today().strftime("%d_%m_%y")
    book.save(f'Расчетник.xlsx') # сохраняю excel
    book.close() # закрываю книгу


def excel_to_dict():
    book = openpyxl.open('Расчетник.xlsx', read_only=True, data_only=True) # Открываю книгу
    sheet = book.worksheets[1] # выбираю второй лист
    start = 3 # выставляю стартовое положение указателя строки
    data = {} # объявляю словарь для сбора данных
    counter = 0 # объявляю счетчик

    for row in range(start, sheet.max_row + 1): # цикл в диапазоне цифр от "start" до последней заполненной строки
        if sheet[row][1].value: # если строка заполнена ....
            data.update({ # обновляю словарь след. данными ...
                row-start: {
                    'num': sheet[row][0].value, # номер
                    'name': sheet[row][1].value, # наименование
                    'qty': sheet[row][2].value, # кол-во
                    'price': ('%.2f'%sheet[row][3].value).replace('.', ','), # цена
                    'cost': ('%.2f'%sheet[row][4].value).replace('.', ','), # стоимость
                }
            })
            counter += 1
        elif sheet[row][3].value == 'Итого:': # дойдя до конца ...
            total = row # сохранение "Всего наименований"

    data.update({ # сохранение в словарь:
        'total':{
            'name': sheet[total][3].value, # всего наименований ...
            'cost': ('%.2f'%sheet[total][4].value).replace('.', ','), # на сумму...
            'prop': sheet[total+1][4].value # прописью ...
        }
    })

    book.close()
    print(data)
    return data


def send_email(recipient):
    date = datetime.today().strftime("%d.%m.%y")

    filepath = 'КП.pdf' # выбирает файл на отправку
    filename = os.path.basename(filepath) # получает его системное имя
    part = MIMEBase('application', "octet-stream") # создание MIME объекта
    part.set_payload(open(filepath, "rb").read()) # побитово загружает файл в качестве полезной нагрузки в MIME объект
    encoders.encode_base64(part) # кодирует MIME объект в "base64"
    part.add_header('Content-Disposition', 'attachment', filename=filename) # добавляет заголовок к прикрепленному файлу

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
    msg.attach(MIMEText(body, 'plain')) # прикрепляем контейнер вложения письма
    msg.attach(part) # прикрепляем подготовленный MIME объект

    server.sendmail(email, recipient, msg.as_string())
    server.quit()


def xml_from_edo():
    tree = etree.parse('Документ.xml')
    root = tree.getroot()

    data = {}
    for child1 in root:
        if child1.tag == 'Документ':
            data.update(document=child1.attrib['ПоФактХЖ'],
                        doc_name=child1.attrib['НаимДокОпр'],
                        date=child1.attrib['ДатаИнфПр'],
                        agent=child1.attrib['НаимЭконСубСост'],
                        items=[])
            for sub in child1:
                if sub.tag == 'ТаблСчФакт':
                    for child2 in sub:
                        if child2.tag == 'СведТов':
                            item = dict(num=child2.attrib['НомСтр'],
                                         name=child2.attrib['НаимТов'],
                                         qty=child2.attrib['КолТов'],
                                         price=child2.attrib['ЦенаТов'],
                                         cost=child2.attrib['СтТовУчНал'])
                            data['items'].append(item)
                        elif child2.tag == 'ВсегоОпл':
                            data.update(total=child2.attrib['СтТовУчНалВсего'])
    return data


def get_acc_info():
    url_login = 'https://oauth.moedelo.org/Login?redirect_uri=https%3a%2f%2fwww.moedelo.org%2fFinances%3f_companyId%3d9389184&_companyId='
    url_main = 'https://restapi.moedelo.org/Finances/Money/Table/MultiCurrency?_=1629617901706&_companyId=9389184&budgetaryType&closingDocumentsCondition=0&count=1000&direction&endDate=&kontragentId&kontragentType&offset=0&operationType=&patentId&provideInTax&query=&sortColumn=1&sortType=2&sourceId=0&sourceType=0&startDate=&sum&sumCondition&sumFrom&sumTo&taxationSystemType&workerId'

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko)  Safari/537.36',
        'Connection': 'keep-alive',
    }

    payload = {
        "Login": BUH_LOGIN,
        "Password": BUH_PASS_HASH
        }

    client = requests.session()
    auth_me = client.post(url_login, headers=headers, data=payload)
    cookies = auth_me.cookies.get_dict()
    paymants = client.get(url_main, cookies=cookies)

    local_time = datetime.now()
    index = math.ceil(local_time.month / 3) - 1

    quarters = [['01', '02', '03'],
                ['04', '05', '06'],
                ['07', '08', '09'],
                ['10', '11', '12']]

    total_earn = 0
    total_earn_in_past = 0
    quarter_earn = 0
    total_spent = 0
    for el in json.loads(paymants.text)['data']['Operations']:
        if el['OperationType'] != 16:
            total_spent += el['Sum']
        else:
            if int(el['Date'][:4]) < local_time.year:
                total_earn_in_past += el['Sum']
            if el['Date'][:4] == f'{local_time.year}':
                total_earn += el['Sum']
            if el['Date'][5:7] in quarters[index] and el['Date'][:4] == f'{local_time.year}':
                quarter_earn += el['Sum']

    avg_month = int(quarter_earn/3)
    answer_index = math.floor(avg_month/250000)

    buh_fees = [7200, 14400, 23400, 34200]

    data = 'Здравствуйте, Максим Олегович!\n' \
           f'Среднемесячный оборот за текущий квартал составляет {avg_month}руб и '

    if answer_index > 0:
        buh_fee = buh_fees[answer_index - 1]
        data += f'превышает лимит {int(answer_index) * 250}т.р., будьте готовы к доплате в размере {buh_fee}р.'
    else:
        buh_fee = 0
        data += 'не превышает лимит по тарифному плану.'

    profit = (total_earn + total_earn_in_past) - total_spent - buh_fee - (quarter_earn * 0.06) - (total_earn * 0.01)
    # print(f'profit [{profit}] = total_earn [{total_earn}] - total_spent [{total_spent}] - buh_fee [{buh_fee}] - (quarter_earn * 0.06) [{quarter_earn * 0.06}] - (total_earn * 0.01) [{total_earn * 0.01}]')
    profit = profit - (profit * 0.1)
    # profit *= 0.9
    print(int(profit))

    data += f'\nСумма налога за текущий квартал составляет {int(quarter_earn * 0.06)}р.\n'

    if int(total_earn) >= 300000:
        data += f'Общая сумма надбавочного налога за год составляет {int((total_earn - 300000) * 0.01)}р.\n'

    requests.post(f'https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id=722639239&text={data}')

