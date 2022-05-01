from typing import Dict, Any, Optional, Union

import requests
from bs4 import BeautifulSoup

from .serializers import ProductStateSerializer


def get_product(code: int) -> Optional[
    Dict[str, Union[Optional[str], Any]]]:
    url = f'https://www.wildberries.ru/catalog/{code}/detail.aspx'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    try:
        brand = soup.find('h1', class_='same-part-kt__header').text.split('/')[
            0].replace(u'\xa0', '').strip()
        name = soup.find('h1', class_='same-part-kt__header').text.split('/')[
            1].replace(u'\xa0', '').strip()
        current_price = soup.find('span',
                                  class_='price-block__final-price').text.replace(
            u'\xa0', '').strip()[:-1]
        try:
            old_price = soup.find(
                class_='price-block__old-price').text.replace(u'\xa0', '')[:-1]
        except AttributeError:
            old_price = None
        supplier = requests.get(
            f"https://wbx-content-v2.wbstatic.net/sellers/{code}.json").json()[
            'supplierName']
        product_state = {
            "product_name": name,
            "current_price": current_price,
            "old_price": old_price,
            "brand": brand,
            "supplier": supplier,
        }
    except:
        product_state = None
    return product_state


def save_state(code: int, code_id: int) -> Dict[str, int]:
    try:
        data = get_product(code)
        data['code'] = code_id
    except ValueError as error:
        raise error
    serializer = ProductStateSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return serializer.data
