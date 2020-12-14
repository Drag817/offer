import requests
from bs4 import BeautifulSoup


def parse(article):
    url = f"https://novosibirskshop.e2e4online.ru/shop/catalog/item/" \
          f"?id={article}"
    # print(url)

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
    product_title = f"{product_title} [ссылка]({url})"
    # print(product_title)

    try:
        product_price = soup.find("span", class_='price').text
        product_price = f"Закуп: {product_price}р"
    except AttributeError:
        product_price = "Нет в продаже"
    # print(product_price)

    answer = f"{product_title}\n\n{product_price}"

    imgs = soup.find_all("a", class_='fancybox-thumb')
    product_imgs = []

    for img in imgs[:3]:
        product_imgs.append(img.get('href'))

    # print(product_imgs)
    return answer, product_imgs
