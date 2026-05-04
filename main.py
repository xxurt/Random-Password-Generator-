import tkinter as tk
from tkinter import ttk, messagebox
import random
import string
import json
import os
from datetime import datetime

# Файл для хранения истории
HISTORY_FILE = "history.json"

class PasswordGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Random Password Generator")
        self.root.geometry("650x500")
        self.root.resizable(False, False)

        # Переменные
        self.length_var = tk.IntVar(value=12)
        self.use_digits = tk.BooleanVar(value=True)
        self.use_letters = tk.BooleanVar(value=True)
        self.use_symbols = tk.BooleanVar(value=False)

        # Загрузка истории
        self.history = self.load_history()

        # Создание интерфейса
        self.create_widgets()
        self.update_history_table()

    def create_widgets(self):
        # Рамка для настроек
        settings_frame = ttk.LabelFrame(self.root, text="Настройки пароля", padding=10)
        settings_frame.pack(fill="x", padx=10, pady=5)

        # Ползунок длины пароля
        ttk.Label(settings_frame, text="Длина пароля:").grid(row=0, column=0, sticky="w")
        self.length_scale = ttk.Scale(settings_frame, from_=4, to=32, variable=self.length_var, orient="horizontal")
        self.length_scale.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.length_label = ttk.Label(settings_frame, text="12")
        self.length_label.grid(row=0, column=2, padx=5)
        self.length_var.trace_add("write", lambda *args: self.length_label.config(text=str(self.length_var.get())))

        # Чекбоксы
        ttk.Checkbutton(settings_frame, text="Цифры (0-9)", variable=self.use_digits).grid(row=1, column=0, sticky="w")
        ttk.Checkbutton(settings_frame, text="Буквы (A-Z, a-z)", variable=self.use_letters).grid(row=1, column=1, sticky="w")
        ttk.Checkbutton(settings_frame, text="Спецсимволы (!@#$%^&*)", variable=self.use_symbols).grid(row=1, column=2, sticky="w")

        # Кнопка генерации
        self.generate_btn = ttk.Button(settings_frame, text="Сгенерировать пароль", command=self.generate_password)
        self.generate_btn.grid(row=2, column=0, columnspan=3, pady=10)

        # Рамка для отображения пароля
        display_frame = ttk.LabelFrame(self.root, text="Сгенерированный пароль", padding=10)
        display_frame.pack(fill="x", padx=10, pady=5)

        self.password_var = tk.StringVar()
        self.password_entry = ttk.Entry(display_frame, textvariable=self.password_var, font=("Courier", 12), state="readonly")
        self.password_entry.pack(fill="x", padx=5, pady=5)

        # Рамка для истории
        history_frame = ttk.LabelFrame(self.root, text="История паролей", padding=10)
        history_frame.pack(fill="both", expand=True, padx=10, pady=5)

        columns = ("timestamp", "length", "charset", "password")
        self.history_tree = ttk.Treeview(history_frame, columns=columns, show="headings")
        self.history_tree.heading("timestamp", text="Дата/время")
        self.history_tree.heading("length", text="Длина")
        self.history_tree.heading("charset", text="Набор символов")
        self.history_tree.heading("password", text="Пароль")
        self.history_tree.column("timestamp", width=140)
        self.history_tree.column("length", width=60)
        self.history_tree.column("charset", width=120)
        self.history_tree.column("password", width=280)

        scrollbar = ttk.Scrollbar(history_frame, orient="vertical", command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=scrollbar.set)
        self.history_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Кнопка очистки истории
        clear_btn = ttk.Button(history_frame, text="Очистить историю", command=self.clear_history)
        clear_btn.pack(pady=5)

    def generate_password(self):
        length = self.length_var.get()

        # Проверка минимальной/максимальной длины
        if length < 4:
            messagebox.showerror("Ошибка", "Минимальная длина пароля — 4 символа")
            return
        if length > 32:
            messagebox.showerror("Ошибка", "Максимальная длина пароля — 32 символа")
            return

        # Проверка, что выбран хотя бы один набор символов
        if not (self.use_digits.get() or self.use_letters.get() or self.use_symbols.get()):
            messagebox.showerror("Ошибка", "Выберите хотя бы один тип символов")
            return

        # Формирование набора символов
        chars = ""
        charset_desc = []
        if self.use_digits.get():
            chars += string.digits
            charset_desc.append("цифры")
        if self.use_letters.get():
            chars += string.ascii_letters
            charset_desc.append("буквы")
        if self.use_symbols.get():
            chars += "!@#$%^&*"
            charset_desc.append("спецсимволы")

        # Генерация пароля
        password = ''.join(random.choice(chars) for _ in range(length))

        # Отображение
        self.password_var.set(password)

        # Сохранение в историю
        record = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "length": length,
            "charset": ", ".join(charset_desc),
            "password": password
        }
        self.history.insert(0, record)
        self.save_history()
        self.update_history_table()

    def update_history_table(self):
        # Очистка таблицы
        for row in self.history_tree.get_children():
            self.history_tree.delete(row)

        # Добавление записей
        for record in self.history:
            self.history_tree.insert("", "end", values=(
                record["timestamp"],
                record["length"],
                record["charset"],
                record["password"]
            ))

    def save_history(self):
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(self.history, f, ensure_ascii=False, indent=2)

    def load_history(self):
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def clear_history(self):
        self.history = []
        self.save_history()
        self.update_history_table()
        self.password_var.set("")
        messagebox.showinfo("История", "История очищена")

if __name__ == "__main__":
    root = tk.Tk()
    app = PasswordGenerator(root)
    root.mainloop()