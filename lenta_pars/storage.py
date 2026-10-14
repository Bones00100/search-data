import csv
import json
import os
from datetime import datetime


DATA_DIR = "data"

CSV_FILE = os.path.join(
    DATA_DIR,
    "prices.csv"
)

JSON_FILE = os.path.join(
    DATA_DIR,
    "prices.json"
)


def prepare_data_dir():
    os.makedirs(
        DATA_DIR,
        exist_ok=True
    )


def save_csv(products):
    """
    Сохраняет результаты в CSV.
    """

    prepare_data_dir()

    file_exists = os.path.exists(CSV_FILE)

    fieldnames = [
        "date",
        "store_id",
        "store_address",
        "category",
        "group",
        "item_id",
        "item",
        "price",
        "regular_price",
        "price_per_kg",
        "weight_g",
        "is_weight",
        "url"
    ]

    with open(
        CSV_FILE,
        "a",
        newline="",
        encoding="utf-8-sig"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        if not file_exists:
            writer.writeheader()

        writer.writerows(products)


def save_json(products):
    """
    Сохраняет результаты в JSON.
    """

    prepare_data_dir()

    existing = []

    if os.path.exists(JSON_FILE):

        try:

            with open(
                JSON_FILE,
                "r",
                encoding="utf-8"
            ) as file:

                existing = json.load(file)

                if not isinstance(existing, list):
                    existing = []

        except (json.JSONDecodeError, OSError):
            existing = []

    existing.extend(products)

    with open(
        JSON_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            existing,
            file,
            ensure_ascii=False,
            indent=2
        )


def save_results(products):
    """
    Сохраняет данные одновременно в CSV и JSON.
    """

    save_csv(products)
    save_json(products)

    print()
    print("Файлы сохранены:")
    print(f"CSV:  {CSV_FILE}")
    print(f"JSON: {JSON_FILE}")