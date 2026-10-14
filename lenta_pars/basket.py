import csv
import os
from collections import defaultdict


INPUT_FILE = "data/prices.csv"

# МРОТ Москвы на 2026 год
MOSCOW_MROT = 39730.00

# 1/4 МРОТ
TARGET = MOSCOW_MROT / 4

# Допустимый диапазон ±5%
MIN_TOTAL = TARGET * 0.95
MAX_TOTAL = TARGET * 1.05


def load_products():
    """
    Загружает товары из CSV.
    """

    products = []

    with open(
        INPUT_FILE,
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:

            try:
                price = float(
                    row["price"]
                )
            except (ValueError, TypeError):
                continue

            if price <= 0:
                continue

            row["price"] = price

            products.append(row)

    return products


def get_cheapest_by_group(products):
    """
    Выбирает самый дешёвый товар
    из каждой группы.
    """

    groups = defaultdict(list)

    for product in products:

        group = product["group"]

        groups[group].append(
            product
        )

    cheapest = []

    for group, items in groups.items():

        item = min(
            items,
            key=lambda x: x["price"]
        )

        cheapest.append(
            item
        )

    return cheapest


def add_unique_products(products, selected):
    """
    Добавляет товары, стараясь максимально
    приблизиться к целевой сумме.
    """

    selected_ids = {
        item["item_id"]
        for item in selected
    }

    total = sum(
        item["price"]
        for item in selected
    )

    while total < TARGET:

        remaining = [
            item
            for item in products
            if item["item_id"] not in selected_ids
            and total + item["price"] <= MAX_TOTAL
        ]

        if not remaining:
            break

        # Ищем товар, который максимально
        # приблизит нас к целевой сумме.
        item = min(
            remaining,
            key=lambda x: abs(
                TARGET -
                (total + x["price"])
            )
        )

        selected.append(
            item
        )

        selected_ids.add(
            item["item_id"]
        )

        total += item["price"]

        if MIN_TOTAL <= total <= MAX_TOTAL:
            # Если уже попали в диапазон,
            # проверяем, можно ли сделать ещё ближе.
            break

    return selected


def improve_basket(products, selected):
    """
    Пытается улучшить итоговую сумму,
    заменяя дорогие/дешёвые позиции.
    """

    total = sum(
        item["price"]
        for item in selected
    )

    if MIN_TOTAL <= total <= MAX_TOTAL:
        return selected

    selected_ids = {
        item["item_id"]
        for item in selected
    }

    while total < MIN_TOTAL:

        candidates = [
            item
            for item in products
            if item["item_id"] not in selected_ids
            and total + item["price"] <= MAX_TOTAL
        ]

        if not candidates:
            break

        item = min(
            candidates,
            key=lambda x: abs(
                TARGET -
                (total + x["price"])
            )
        )

        selected.append(
            item
        )

        selected_ids.add(
            item["item_id"]
        )

        total += item["price"]

    return selected


def print_basket(basket):
    """
    Выводит готовую корзину.
    """

    print()
    print("=" * 100)
    print("ПРОДУКТОВАЯ КОРЗИНА")
    print("=" * 100)

    total = 0

    for number, item in enumerate(
        basket,
        start=1
    ):

        price = item["price"]

        total += price

        print(
            f"{number:3}. "
            f"{item['group']:18} | "
            f"{price:8.2f} ₽ | "
            f"{item['item']}"
        )

    print("-" * 100)

    print(
        f"Итого:              {total:.2f} ₽"
    )

    print(
        f"Цель:               {TARGET:.2f} ₽"
    )

    print(
        f"Допустимый диапазон:"
        f" {MIN_TOTAL:.2f} - {MAX_TOTAL:.2f} ₽"
    )

    difference = total - TARGET

    print(
        f"Отклонение:         {difference:+.2f} ₽"
    )

    if MIN_TOTAL <= total <= MAX_TOTAL:

        print(
            "Статус:             КОРЗИНА В ДОПУСТИМОМ ДИАПАЗОНЕ"
        )

    else:

        print(
            "Статус:             НЕ ПОПАЛА В ДИАПАЗОН"
        )

    print("=" * 100)

def save_basket(basket):
    """
    Сохраняет сформированную корзину в CSV.
    """

    output_file = "data/basket.csv"

    total = sum(
        item["price"]
        for item in basket
    )

    with open(
        output_file,
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as file:

        writer = csv.writer(
            file
        )

        writer.writerow([
            "group",
            "item_id",
            "item",
            "price",
            "price_per_kg",
            "weight_g",
            "url"
        ])

        for item in basket:

            writer.writerow([
                item["group"],
                item["item_id"],
                item["item"],
                item["price"],
                item["price_per_kg"],
                item["weight_g"],
                item["url"]
            ])

        writer.writerow([])

        writer.writerow([
            "ИТОГО",
            "",
            "",
            total,
            "",
            "",
            ""
        ])

    print()
    print(
        f"Корзина сохранена: {output_file}"
    )

def main():

    print("=" * 70)
    print("РАСЧЁТ ПРОДУКТОВОЙ КОРЗИНЫ")
    print("=" * 70)

    if not os.path.exists(INPUT_FILE):

        print()
        print(
            f"Файл не найден: {INPUT_FILE}"
        )

        return

    products = load_products()

    print()
    print(
        f"Загружено товаров: {len(products)}"
    )

    print(
        f"МРОТ Москвы: {MOSCOW_MROT:.2f} ₽"
    )

    print(
        f"1/4 МРОТ: {TARGET:.2f} ₽"
    )

    print(
        f"Допустимый диапазон:"
        f" {MIN_TOTAL:.2f} - {MAX_TOTAL:.2f} ₽"
    )

    # Сначала берём по одному самому дешёвому
    # товару из каждой группы.
    selected = get_cheapest_by_group(
        products
    )

    print()
    print(
        f"Выбрано разных групп: {len(selected)}"
    )

    # Затем постепенно заполняем корзину.
    selected = add_unique_products(
        products,
        selected
    )

    # Дополнительное улучшение.
    selected = improve_basket(
        products,
        selected
    )

    print_basket(
        selected
    )
    
    save_basket(
    selected
)


if __name__ == "__main__":
    main()