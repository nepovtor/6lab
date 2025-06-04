import sqlite3
import datetime

DB_NAME = 'store.db'


def connect_db():
    return sqlite3.connect(DB_NAME)


def init_db():
    conn = connect_db()
    c = conn.cursor()
    c.execute(
        """CREATE TABLE IF NOT EXISTS items(
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            quantity INTEGER NOT NULL,
            release_year INTEGER NOT NULL
        )"""
    )
    conn.commit()
    conn.close()


def input_int(prompt: str) -> int:
    while True:
        try:
            value = int(input(prompt))
            return value
        except ValueError:
            print("Пожалуйста, введите целое число.")


def input_float(prompt: str) -> float:
    while True:
        try:
            value = float(input(prompt))
            return value
        except ValueError:
            print("Пожалуйста, введите число.")


def input_year(prompt: str) -> int:
    current_year = datetime.datetime.now().year
    while True:
        year = input_int(prompt)
        if 1900 <= year <= current_year:
            return year
        print("Введите корректный год (от 1900 до {0}).".format(current_year))


def add_item():
    conn = connect_db()
    c = conn.cursor()
    item_id = input_int("ID товара: ")
    c.execute("SELECT id FROM items WHERE id=?", (item_id,))
    if c.fetchone():
        print("Товар с таким ID уже существует.")
        conn.close()
        return
    name = input("Название: ")
    price = input_float("Стоимость: ")
    quantity = input_int("Количество: ")
    release_year = input_year("Год выпуска: ")
    c.execute("INSERT INTO items(id, name, price, quantity, release_year) VALUES (?, ?, ?, ?, ?)",
              (item_id, name, price, quantity, release_year))
    conn.commit()
    conn.close()
    print("Товар добавлен.")
def list_items():
    conn = connect_db()
    c = conn.cursor()
    for row in c.execute("SELECT * FROM items"):
        print(row)
    conn.close()


def delete_item():
    conn = connect_db()
    c = conn.cursor()
    item_id = input_int("ID товара для удаления: ")
    c.execute("DELETE FROM items WHERE id=?", (item_id,))
    if c.rowcount == 0:
        print("Товар не найден.")
    else:
        conn.commit()
        print("Товар удалён.")
    conn.close()


def update_item():
    conn = connect_db()
    c = conn.cursor()
    item_id = input_int("ID товара для обновления: ")
    c.execute("SELECT * FROM items WHERE id=?", (item_id,))
    if not c.fetchone():
        print("Товар не найден.")
        conn.close()
        return
    name = input("Новое название: ")
    price = input_float("Новая стоимость: ")
    quantity = input_int("Новое количество: ")
    release_year = input_year("Новый год выпуска: ")
    c.execute("UPDATE items SET name=?, price=?, quantity=?, release_year=? WHERE id=?",
              (name, price, quantity, release_year, item_id))
    conn.commit()
    conn.close()
    print("Товар обновлён.")


def menu():
    actions = {
        '1': ("Добавить товар", add_item),
        '2': ("Показать все", list_items),
        '3': ("Удалить товар", delete_item),
        '4': ("Обновить товар", update_item),
        '0': ("Выход", None),
    }
    while True:
        for k, (desc, _) in actions.items():
            print(f"{k}. {desc}")
        choice = input("Выберите действие: ")
        action = actions.get(choice)
        if not action:
            print("Неверный выбор.")
            continue
        if choice == '0':
            break
        action[1]()


if __name__ == '__main__':
    init_db()
    menu()
