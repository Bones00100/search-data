import requests

BASE_URL = "https://integration.api.lenta.com"

STORE_ID = "0291"
CHANNEL = "lo"


def get_products(category_id):
    url = f"{BASE_URL}/catalog/v1/items"

    params = {
        "stores": STORE_ID,
        "channel": CHANNEL,
        "retailBrand": "lo",
        "categoryId": category_id,
        "limit": 100,
        "offset": 0
    }

    headers = {
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(
        url,
        headers=headers,
        params=params,
        timeout=30
    )

    print()
    print("URL:")
    print(response.url)

    print()
    print("STATUS:", response.status_code)

    if response.status_code != 200:
        print()
        print("ОТВЕТ:")
        print(response.text[:5000])
        return None

    return response.json()


def main():
    print("=" * 70)
    print("ТЕСТ ПАРАМЕТРА categoryId")
    print("=" * 70)

    # Категория товара из нашего предыдущего результата:
    # 136 = птица
    category_id = 136

    data = get_products(category_id)

    if data is None:
        return

    items = data.get("items", [])

    print()
    print("=" * 70)
    print(f"НАЙДЕНО ТОВАРОВ: {len(items)}")
    print("=" * 70)

    for i, item in enumerate(items, 1):
        prices = item.get("prices", {})
        weight = item.get("weight", {})

        print(f"{i}. {item.get('name')}")
        print(f"   ID: {item.get('id')}")
        print(f"   categoryId: {item.get('categoryId')}")
        print(f"   Цена: {prices.get('price', 0) / 100:.2f} ₽")
        print(f"   Цена обычная: {prices.get('priceRegular', 0) / 100:.2f} ₽")
        print(f"   Вес: {weight.get('net')} г")
        print(f"   Весовой: {item.get('isWeight')}")
        print()


if __name__ == "__main__":
    main()