from datetime import datetime

from scraper import (
    get_meat_products,
    get_price,
    get_regular_price,
    get_weight_grams,
    get_price_per_kg,
    get_regular_price_per_kg,
    get_product_url
)

from storage import save_results


STORE_ID = "0291"

STORE_ADDRESS = "ул. Бибиревская 10 к.2"

CATEGORY = "мясо"


def detect_group(name):
    """
    Определяет группу товара по названию.
    """

    text = name.lower()

    # Фарш
    if "фарш" in text:
        return "фарш"

    # Консервы
    if any(word in text for word in [
        "тушенка",
        "тушёнка",
        "консервы",
        "закуска мясная",
        "мясо перепела"
    ]):
        return "консервы"

    # Субпродукты
    if any(word in text for word in [
        "печень",
        "сердце",
        "сердечки",
        "желудок",
        "желудки",
        "легкое",
        "лёгкое",
        "язык"
    ]):
        return "субпродукты"

    # Полуфабрикаты
    if any(word in text for word in [
        "котлет",
        "биточ",
        "шницель",
        "колбаски",
        "полуфабрикат"
    ]):
        return "полуфабрикаты"

    # Шашлык
    if "шашлык" in text:
        return "шашлык"

    # Свинина
    if any(word in text for word in [
        "свини",
        "свин",
        "бекон",
        "свиной",
        "свиная"
    ]):
        return "свинина"

    # Говядина
    if any(word in text for word in [
        "говядин",
        "говяж",
        "теля"
    ]):
        return "говядина"

    # Индейка
    if "индеек" in text or "индейк" in text:
        return "индейка"

    # Курица
    if any(word in text for word in [
        "курин",
        "куриц",
        "цыплен",
        "бройлер"
    ]):
        return "курица"

    # Утка
    if any(word in text for word in [
        "утк",
        "утен"
    ]):
        return "утка"

    # Кролик
    if "кролик" in text:
        return "кролик"

    # Баранина
    if any(word in text for word in [
        "баранин",
        "ягнен"
    ]):
        return "баранина"

    return "другое"


def main():

    print("=" * 70)
    print("СБОР ЦЕН НА МЯСО — ЛЕНТА")
    print("=" * 70)

    print()
    print("Магазин: Лента")
    print(f"Магазин ID: {STORE_ID}")
    print(f"Адрес: {STORE_ADDRESS}")
    print(f"Категория: {CATEGORY}")

    print()
    print("Получаем товары через API...")
    print("Между запросами будет пауза.")

    items = get_meat_products()

    if not items:

        print()
        print("Товары не получены.")
        return

    current_date = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    results = []

    print()
    print("=" * 70)
    print("ОБРАБОТКА ТОВАРОВ")
    print("=" * 70)

    for item in items:

        name = item.get(
            "name",
            "Без названия"
        )

        group = detect_group(
            name
        )

        price = get_price(
            item
        )

        regular_price = get_regular_price(
            item
        )

        weight_g = get_weight_grams(
            item
        )

        price_per_kg = get_price_per_kg(
            item
        )

        regular_price_per_kg = (
            get_regular_price_per_kg(
                item
            )
        )

        result = {
            "date": current_date,

            "store_id": STORE_ID,

            "store_address": STORE_ADDRESS,

            "category": CATEGORY,

            "group": group,

            "item_id": item.get(
                "id"
            ),

            "item": name,

            "price": price,

            "regular_price": regular_price,

            "price_per_kg": price_per_kg,

            "weight_g": weight_g,

            "is_weight": item.get(
                "isWeight",
                False
            ),

            "url": get_product_url(
                item
            )
        }

        results.append(
            result
        )

        print(
            f"{group:16} | "
            f"{name[:55]:55} | "
            f"{price_per_kg} ₽/кг"
        )

    save_results(
        results
    )

    print()
    print("=" * 70)
    print(
        f"Собрано товаров: {len(results)}"
    )
    print("=" * 70)


if __name__ == "__main__":
    main()