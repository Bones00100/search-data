import re
import time
import requests


API_URL = "https://integration.api.lenta.com/catalog/v1/items"

STORE_ID = "0291"
CATEGORY_ID = 136

REQUEST_LIMIT = 100

# Пауза между запросами к API
REQUEST_DELAY = 3


def get_meat_products():
    """
    Получает все товары категории "Мясо"
    из магазина Лента с ID 0291.
    """

    all_items = []
    offset = 0

    session = requests.Session()

    while True:

        params = {
            "stores": STORE_ID,
            "channel": "lo",
            "retailBrand": "lo",
            "categoryId": CATEGORY_ID,
            "limit": REQUEST_LIMIT,
            "offset": offset
        }

        print()
        print("-" * 60)
        print(f"Запрос товаров: offset={offset}")
        print("-" * 60)

        try:

            response = session.get(
                API_URL,
                params=params,
                timeout=30
            )

            print(f"HTTP: {response.status_code}")

            response.raise_for_status()

            data = response.json()

        except requests.RequestException as error:

            print(f"Ошибка запроса: {error}")
            print("Ждём 10 секунд и пробуем снова...")

            time.sleep(10)

            continue

        items = data.get(
            "items",
            []
        )

        total = data.get(
            "total",
            0
        )

        print(
            f"Всего доступно: {total}"
        )

        print(
            f"Получено сейчас: {len(items)}"
        )

        if not items:
            break

        all_items.extend(items)

        print(
            f"Всего собрано: {len(all_items)}"
        )

        # Последняя страница
        if len(items) < REQUEST_LIMIT:
            break

        offset += REQUEST_LIMIT

        if offset >= total:
            break

        print(
            f"Пауза {REQUEST_DELAY} секунд..."
        )

        time.sleep(REQUEST_DELAY)

    print()
    print("=" * 60)
    print(
        f"ИТОГО СОБРАНО ТОВАРОВ: {len(all_items)}"
    )
    print("=" * 60)

    return all_items


def get_weight_grams(item):
    """
    Получает вес товара в граммах.

    Сначала пытаемся получить вес из API.
    Если API его не дал, ищем вес в названии.
    """

    weight = item.get(
        "weight",
        {}
    )

    api_weight = weight.get(
        "net"
    )

    try:

        if api_weight is not None:

            api_weight = float(
                api_weight
            )

            if api_weight > 0:
                return api_weight

    except (TypeError, ValueError):
        pass

    # Если API не дал вес,
    # ищем его в названии товара.

    name = item.get(
        "name",
        ""
    )

    if not name:
        return None

    # Например:
    # 450г
    # 300 г
    # 1 кг
    # 1,2 кг

    gram_match = re.search(
        r"(\d+(?:[.,]\d+)?)\s*г(?:р)?\b",
        name,
        re.IGNORECASE
    )

    if gram_match:

        value = gram_match.group(1)

        value = value.replace(
            ",",
            "."
        )

        try:
            return float(value)
        except ValueError:
            pass

    kg_match = re.search(
        r"(\d+(?:[.,]\d+)?)\s*кг\b",
        name,
        re.IGNORECASE
    )

    if kg_match:

        value = kg_match.group(1)

        value = value.replace(
            ",",
            "."
        )

        try:

            return float(value) * 1000

        except ValueError:
            pass

    return None


def get_price(item):
    """
    Возвращает текущую цену товара в рублях.
    """

    prices = item.get(
        "prices",
        {}
    )

    price = prices.get(
        "price"
    )

    if price is None:
        return None

    try:

        return round(
            float(price) / 100,
            2
        )

    except (TypeError, ValueError):

        return None


def get_regular_price(item):
    """
    Возвращает обычную цену товара в рублях.
    """

    prices = item.get(
        "prices",
        {}
    )

    price = prices.get(
        "priceRegular"
    )

    if price is None:
        return None

    try:

        return round(
            float(price) / 100,
            2
        )

    except (TypeError, ValueError):

        return None


def get_price_per_kg(item):
    """
    Рассчитывает цену товара за 1 кг.

    Для весового товара API уже предоставляет
    цену за килограмм.

    Для фасованного товара рассчитываем:
    
    цена упаковки / вес упаковки * 1000
    """

    price = get_price(item)

    if price is None:
        return None

    is_weight = item.get(
        "isWeight",
        False
    )

    # Весовой товар.
    # API уже отдаёт цену за кг.
    if is_weight:

        return round(
            price,
            2
        )

    # Фасованный товар.
    weight_g = get_weight_grams(
        item
    )

    if not weight_g or weight_g <= 0:
        return None

    price_per_kg = (
        price / weight_g
    ) * 1000

    return round(
        price_per_kg,
        2
    )


def get_regular_price_per_kg(item):
    """
    Рассчитывает обычную цену товара за кг.
    """

    price = get_regular_price(
        item
    )

    if price is None:
        return None

    is_weight = item.get(
        "isWeight",
        False
    )

    if is_weight:

        return round(
            price,
            2
        )

    weight_g = get_weight_grams(
        item
    )

    if not weight_g or weight_g <= 0:
        return None

    price_per_kg = (
        price / weight_g
    ) * 1000

    return round(
        price_per_kg,
        2
    )


def get_product_url(item):
    """
    Формирует ссылку на страницу товара.
    """

    slug = item.get(
        "slug"
    )

    product_id = item.get(
        "id"
    )

    if not slug:
        return ""

    if product_id:

        return (
            "https://lenta.com/product/"
            f"{slug}-{product_id}/"
        )

    return (
        "https://lenta.com/product/"
        f"{slug}/"
    )