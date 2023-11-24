from dadata import Dadata
import sqlite3
from httpx import HTTPStatusError


def create_database():
    db = sqlite3.connect("Dadata.db")
    cursor = db.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS settings
    (id INTEGER PRIMARY KEY, 
    base_url TEXT DEFAULT 'https://suggestions.dadata.ru/suggestions/api/4_1/rs/suggest/address', 
    api_key TEXT,
    language TEXT DEFAULT "ru")""")
    db.commit()
    db.close()


def checking_api_key():
    db = sqlite3.connect("Dadata.db")
    cursor = db.cursor()
    cursor.execute("SELECT api_key FROM settings WHERE id = 1")
    secret_key_list = cursor.fetchone()
    if secret_key_list is None:
        api_new = input("При первом запуске программы, необходимо установить уникальный для каждого пользователя ПО API"
                        " ключ,\nпо которому будет происходить соединение. Чтобы его получить, нужно зарегестрироваться"
                        " на сервисе.\nСсылка:https://dadata.ru/profile/#info\nПосле необходимые данные будут доступны "
                        "в Вашем личном кабинете\nНапишите, пожалуйста, ключ: ")
        cursor.execute("INSERT INTO settings (api_key) VALUES (?)", (api_new,))
        db.commit()
    db.close()


def update_settings(choice):
    db = sqlite3.connect("Dadata.db")
    cursor = db.cursor()
    if choice == "1":
        print(cursor.fetchall())
        new_base_url = input("Введите базовый URL к сервису dadata: ")
        cursor.execute("UPDATE settings SET base_url = ? WHERE id = 1", (new_base_url,))
    elif choice == "2":
        new_api_key = input("Введите API ключ для сервиса dadata: ")
        cursor.execute("UPDATE settings SET api_key = ? WHERE id = 1", (new_api_key,))
    elif choice == "3":
        new_language = input("Выберите язык ответа от dadata (en/ru): ")
        if new_language.lower() == "en" or new_language.lower() == "ru":
            cursor.execute("UPDATE settings SET language = ? WHERE id = 1", (new_language,))
        else:
            print("Неверный формат языка. Пожалуйста, попробуйте еще раз.")
    else:
        print("Неверный ввод, попробуйте снова")
    db.commit()
    db.close()


def get_address_suggestions(address):
    db = sqlite3.connect("Dadata.db")
    cursor = db.cursor()
    try:
        cursor.execute("SELECT api_key, language from settings WHERE id = 1")
        secret_key_list = cursor.fetchone()
        secret_key, language = secret_key_list
        with Dadata(token=secret_key) as dadata:
            address_variants = dadata.suggest(name="address", query=address, count=7, language=language)
            if len(address_variants) > 0:
                number = 1
                for variant in address_variants:
                    print(f"{number}. {variant['unrestricted_value']}")
                    number += 1
                num_of_address = int(
                    input("\nПожалуйтса, введите порядковый номер нужного адреса ( без точки ).\nНомер: "))
                if 1 <= num_of_address < number:
                    lat = address_variants[num_of_address - 1]["data"]["geo_lat"]
                    lon = address_variants[num_of_address - 1]["data"]["geo_lon"]
                    if lat is None and lon is None:
                        print("Упс, по всей видимости мы не знаем координаты интересующего Вас адреса.")
                    else:
                        print(f"Широта: {lat}, Долгота:{lon}")
                else:
                    print("Вы ввели неправильный порядковый номер.")
            else:
                print("Похоже по ващему запросу ничего не нашлось. Пожалуйста, попробуйте еще раз.")
    except (HTTPStatusError, UnicodeError, ValueError):
        print("Возможно Вы ввели API ключ с ошибкой. ( Можно указать новый в настройках ). Если ошибка возникла при "
              "вводе номера нужного адреса, то Вы ввели буквы вместо чисел))")
    db.close()


def print_menu_settings():
    print("\n" * 2)
    print("1. Установить базовый URL к сервису dadata")
    print("2. Установить новый API ключ для сервиса dadata")
    print("3. Установить язык ответа от сервиса")
    print("4. Выйти")


def menu_settings():
    print_menu_settings()
    choice = input("Выберите пункт меню: ")
    if choice == "1":
        update_settings(choice)
    elif choice == "2":
        update_settings(choice)
    elif choice == "3":
        update_settings(choice)
    elif choice == "4":
        return
    else:
        print("Некорректный выбор. Пожалуйста, попробуйте еще раз. Ожидается ответ в формате '1'.")


def print_menu():
    print("\n----------------------")
    print("|1. Указать настройки|")
    print("|2. Ввести адрес     |")
    print("|3. Выход            |\n----------------------")


def main():
    create_database()
    checking_api_key()
    while True:
        print_menu()
        option = input("Выберите пункт меню: ")
        if option == "1":
            menu_settings()
        elif option == "2":
            address = input("Введите, пожалуйста, адрес: ")
            get_address_suggestions(address)
        elif option == "3":
            print("Хорошего дня! :)")
            break
        else:
            print("Некорректный выбор. Пожалуйста, попробуйте еще раз. Ожидается ответ в формате '1'.")


if __name__ == "__main__":
    main()
