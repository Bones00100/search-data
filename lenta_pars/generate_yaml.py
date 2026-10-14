import csv
import os
import yaml


INPUT_FILE = "data/prices.csv"
OUTPUT_FILE = "config/products.yaml"


def load_products():
    products = []

    with open(
        INPUT_FILE,
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:
            products.append(row)

    return products


def generate_yaml(products):
    config = {
        "store": "Лента",
        "store_id": "0291",
        "store_address": "ул. Бибиревская 10 к.2",
        "category": "мясо",
        "products": {}
    }

    for product in products:

        group = product["group"]

        if group not in config["products"]:
            config["products"][group] = []

        item = {
            "id": int(product["item_id"]),
            "name": product["item"],
            "url": product["url"]
        }

        config["products"][group].append(item)

    return config


def save_yaml(config):
    os.makedirs(
        "config",
        exist_ok=True
    )

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        yaml.dump(
            config,
            file,
            allow_unicode=True,
            sort_keys=False,
            default_flow_style=False
        )


def main():

    print("=" * 60)
    print("СОЗДАНИЕ products.yaml")
    print("=" * 60)

    if not os.path.exists(INPUT_FILE):

        print()
        print(f"Ошибка: файл не найден:")
        print(INPUT_FILE)

        return

    products = load_products()

    print()
    print(
        f"Загружено товаров: {len(products)}"
    )

    config = generate_yaml(
        products
    )

    save_yaml(
        config
    )

    print()
    print("Группы товаров:")

    for group, items in config["products"].items():

        print(
            f"  {group}: {len(items)}"
        )

    print()
    print("=" * 60)

    print(
        f"Файл создан: {OUTPUT_FILE}"
    )

    print("=" * 60)


if __name__ == "__main__":
    main()