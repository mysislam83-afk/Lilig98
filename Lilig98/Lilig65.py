import tkinter as tk
from tkinter import ttk, messagebox
import random
import string
import json
import os
from datetime import datetime

class PasswordGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Random Password Generator")
        self.root.geometry("800x600")
        
        # Данные
        self.history = []
        self.load_history()
        
        # GUI
        self.setup_ui()
        self.update_history_table()
    
    def setup_ui(self):
        # Основной контейнер
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # === Настройки генерации ===
        settings_frame = ttk.LabelFrame(main_frame, text="⚙️ Настройки пароля", padding="10")
        settings_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Длина пароля
        ttk.Label(settings_frame, text="Длина пароля:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.length_var = tk.IntVar(value=12)
        self.length_scale = ttk.Scale(settings_frame, from_=4, to=32, orient=tk.HORIZONTAL, 
                                      variable=self.length_var, command=self.update_length_label)
        self.length_scale.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 10), pady=5)
        
        self.length_label = ttk.Label(settings_frame, text="12")
        self.length_label.grid(row=0, column=2, padx=(0, 10))
        
        # Чекбоксы
        self.use_uppercase = tk.BooleanVar(value=True)
        self.use_lowercase = tk.BooleanVar(value=True)
        self.use_digits = tk.BooleanVar(value=True)
        self.use_symbols = tk.BooleanVar(value=True)
        
        ttk.Checkbutton(settings_frame, text="Заглавные буквы (A-Z)", variable=self.use_uppercase).grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Checkbutton(settings_frame, text="Строчные буквы (a-z)", variable=self.use_lowercase).grid(row=1, column=1, sticky=tk.W, pady=5)
        ttk.Checkbutton(settings_frame, text="Цифры (0-9)", variable=self.use_digits).grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Checkbutton(settings_frame, text="Спецсимволы (!@#$%^&*)", variable=self.use_symbols).grid(row=2, column=1, sticky=tk.W, pady=5)
        
        settings_frame.columnconfigure(1, weight=1)
        
        # === Генерация пароля ===
        gen_frame = ttk.Frame(main_frame)
        gen_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(gen_frame, text="🔐 Сгенерировать пароль", command=self.generate_password).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(gen_frame, text="📋 Копировать", command=self.copy_to_clipboard).pack(side=tk.LEFT)
        
        # Отображение пароля
        self.password_var = tk.StringVar()
        self.password_entry = ttk.Entry(gen_frame, textvariable=self.password_var, font=("Courier", 12), width=30)
        self.password_entry.pack(side=tk.LEFT, padx=(10, 0), fill=tk.X, expand=True)
        
        # === Индикатор надёжности ===
        self.strength_label = ttk.Label(main_frame, text="", font=("Arial", 10))
        self.strength_label.pack(pady=(0, 10))
        
        # === История паролей ===
        history_frame = ttk.LabelFrame(main_frame, text="📜 История паролей", padding="10")
        history_frame.pack(fill=tk.BOTH, expand=True)
        
        # Таблица
        columns = ("Дата", "Пароль", "Длина", "Сложность")
        self.tree = ttk.Treeview(history_frame, columns=columns, show="headings", height=12)
        
        self.tree.heading("Дата", text="Дата создания")
        self.tree.heading("Пароль", text="Пароль")
        self.tree.heading("Длина", text="Длина")
        self.tree.heading("Сложность", text="Сложность")
        
        self.tree.column("Дата", width=150)
        self.tree.column("Пароль", width=250)
        self.tree.column("Длина", width=80)
        self.tree.column("Сложность", width=100)
        
        # Скроллбар
        scrollbar = ttk.Scrollbar(history_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Кнопки управления историей
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(btn_frame, text="🗑 Очистить историю", command=self.clear_history).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(btn_frame, text="💾 Сохранить историю", command=self.save_history).pack(side=tk.LEFT)
        
        # Статистика
        self.stats_label = ttk.Label(main_frame, text="", font=("Arial", 9))
        self.stats_label.pack(pady=(10, 0))
        self.update_stats()
    
    def update_length_label(self, event=None):
        """Обновление метки длины"""
        self.length_label.config(text=str(int(self.length_var.get())))
    
    def generate_password(self):
        """Генерация пароля"""
        length = int(self.length_var.get())
        
        # Проверка на минимальную/максимальную длину
        if length < 4:
            messagebox.showerror("Ошибка", "Минимальная длина пароля - 4 символа!")
            return
        if length > 32:
            messagebox.showerror("Ошибка", "Максимальная длина пароля - 32 символа!")
            return
        
        # Проверка, что выбран хотя бы один тип символов
        if not any([self.use_uppercase.get(), self.use_lowercase.get(), 
                   self.use_digits.get(), self.use_symbols.get()]):
            messagebox.showerror("Ошибка", "Выберите хотя бы один тип символов!")
            return
        
        # Формирование набора символов
        charset = ""
        if self.use_uppercase.get():
            charset += string.ascii_uppercase
        if self.use_lowercase.get():
            charset += string.ascii_lowercase
        if self.use_digits.get():
            charset += string.digits
        if self.use_symbols.get():
            charset += "!@#$%^&*()_+-=[]{}|;:,.<>?"
        
        # Генерация пароля
        password = ''.join(random.choice(charset) for _ in range(length))
        
        # Перемешивание для лучшей случайности
        password_list = list(password)
        random.shuffle(password_list)
        password = ''.join(password_list)
        
        # Отображение
        self.password_var.set(password)
        
        # Оценка сложности
        strength = self.check_strength(password)
        self.update_strength_indicator(strength)
        
        # Сохранение в историю
        self.add_to_history(password, length, strength)
        
        # Обновление таблицы
        self.update_history_table()
        self.update_stats()
    
    def check_strength(self, password):
        """Проверка сложности пароля"""
        score = 0
        length = len(password)
        
        # Длина
        if length >= 12:
            score += 2
        elif length >= 8:
            score += 1
        
        # Наличие разных типов символов
        if any(c.isupper() for c in password):
            score += 1
        if any(c.islower() for c in password):
            score += 1
        if any(c.isdigit() for c in password):
            score += 1
        if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            score += 2
        
        # Оценка
        if score >= 6:
            return "💪 Очень надёжный"
        elif score >= 4:
            return "✅ Надёжный"
        elif score >= 2:
            return "⚠️ Средний"
        else:
            return "❌ Слабый"
    
    def update_strength_indicator(self, strength):
        """Обновление индикатора надёжности"""
        colors = {
            "❌ Слабый": "red",
            "⚠️ Средний": "orange",
            "✅ Надёжный": "green",
            "💪 Очень надёжный": "darkgreen"
        }
        self.strength_label.config(text=f"Надёжность: {strength}", foreground=colors.get(strength, "black"))
    
    def add_to_history(self, password, length, strength):
        """Добавление пароля в историю"""
        self.history.insert(0, {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "password": password,
            "length": length,
            "strength": strength
        })
        
        # Ограничение истории (последние 100 паролей)
        if len(self.history) > 100:
            self.history = self.history[:100]
    
    def update_history_table(self):
        """Обновление таблицы истории"""
        # Очистка таблицы
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Добавление паролей
        for entry in self.history:
            # Маскируем пароль для отображения
            masked_pass = entry["password"][:4] + "*" * (len(entry["password"]) - 4) if len(entry["password"]) > 4 else "***"
            self.tree.insert("", 0, values=(
                entry["date"],
                masked_pass,
                entry["length"],
                entry["strength"]
            ))
    
    def copy_to_clipboard(self):
        """Копирование пароля в буфер обмена"""
        password = self.password_var.get()
        if password:
            self.root.clipboard_clear()
            self.root.clipboard_append(password)
            messagebox.showinfo("Успех", "Пароль скопирован в буфер обмена!")
        else:
            messagebox.showwarning("Внимание", "Сначала сгенерируйте пароль!")
    
    def load_history(self):
        """Загрузка истории из JSON"""
        if os.path.exists("passwords.json"):
            try:
                with open("passwords.json", "r", encoding="utf-8") as f:
                    self.history = json.load(f)
            except:
                self.history = []
    
    def save_history(self):
        """Сохранение истории в JSON"""
        try:
            with open("passwords.json", "w", encoding="utf-8") as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
            messagebox.showinfo("Успех", "История сохранена!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить историю: {e}")
    
    def clear_history(self):
        """Очистка истории"""
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите очистить всю историю?"):
            self.history = []
            self.update_history_table()
            self.update_stats()
            self.save_history()
            messagebox.showinfo("Успех", "История очищена!")
    
    def update_stats(self):
        """Обновление статистики"""
        total = len(self.history)
        avg_length = sum(p["length"] for p in self.history) / total if total > 0 else 0
        
        strong_count = sum(1 for p in self.history if "Очень надёжный" in p["strength"])
        
        stats_text = f"📊 Всего паролей: {total} | Средняя длина: {avg_length:.1f} | Надёжных: {strong_count}"
        self.stats_label.config(text=stats_text)
    
    def on_close(self):
        """Действия при закрытии"""
        self.save_history()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = PasswordGenerator(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()