import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime

class WeatherDiary:
    def __init__(self, root):
        self.root = root
        self.root.title("Weather Diary - Дневник погоды")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        
        # Файл для хранения записей
        self.data_file = "weather_data.json"
        self.entries = self.load_entries()
        
        # Переменные для фильтрации
        self.filter_active = False
        self.filtered_entries = []
        
        # Создание интерфейса
        self.create_widgets()
        
        # Обновление отображения
        self.update_display()
        
    def create_widgets(self):
        # Основной контейнер с прокруткой
        main_canvas = tk.Canvas(self.root)
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=main_canvas.yview)
        self.scrollable_frame = ttk.Frame(main_canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        )
        
        main_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        main_canvas.configure(yscrollcommand=scrollbar.set)
        
        # Панель ввода новой записи
        input_frame = ttk.LabelFrame(self.scrollable_frame, text="Добавить новую запись", padding="10")
        input_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Дата
        date_frame = ttk.Frame(input_frame)
        date_frame.pack(fill=tk.X, pady=5)
        ttk.Label(date_frame, text="Дата (ГГГГ-ММ-ДД):", width=20).pack(side=tk.LEFT)
        self.date_entry = ttk.Entry(date_frame, width=30)
        self.date_entry.pack(side=tk.LEFT, padx=(10, 0))
        ttk.Label(date_frame, text="Пример: 2024-01-15", foreground="gray").pack(side=tk.LEFT, padx=(10, 0))
        
        # Температура
        temp_frame = ttk.Frame(input_frame)
        temp_frame.pack(fill=tk.X, pady=5)
        ttk.Label(temp_frame, text="Температура (°C):", width=20).pack(side=tk.LEFT)
        self.temp_entry = ttk.Entry(temp_frame, width=30)
        self.temp_entry.pack(side=tk.LEFT, padx=(10, 0))
        
        # Описание погоды
        desc_frame = ttk.Frame(input_frame)
        desc_frame.pack(fill=tk.X, pady=5)
        ttk.Label(desc_frame, text="Описание погоды:", width=20).pack(side=tk.LEFT)
        self.desc_entry = ttk.Entry(desc_frame, width=50)
        self.desc_entry.pack(side=tk.LEFT, padx=(10, 0))
        
        # Осадки
        precip_frame = ttk.Frame(input_frame)
        precip_frame.pack(fill=tk.X, pady=5)
        ttk.Label(precip_frame, text="Осадки:", width=20).pack(side=tk.LEFT)
        self.precip_var = tk.BooleanVar()
        ttk.Checkbutton(precip_frame, text="Да", variable=self.precip_var).pack(side=tk.LEFT, padx=(10, 0))
        
        # Кнопка добавления
        button_frame = ttk.Frame(input_frame)
        button_frame.pack(pady=10)
        ttk.Button(button_frame, text="➕ Добавить запись", command=self.add_entry).pack()
        
        # Панель фильтрации
        filter_frame = ttk.LabelFrame(self.scrollable_frame, text="Фильтрация записей", padding="10")
        filter_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Фильтр по дате
        date_filter_frame = ttk.Frame(filter_frame)
        date_filter_frame.pack(fill=tk.X, pady=5)
        ttk.Label(date_filter_frame, text="Фильтр по дате:", width=15).pack(side=tk.LEFT)
        self.filter_date_entry = ttk.Entry(date_filter_frame, width=20)
        self.filter_date_entry.pack(side=tk.LEFT, padx=(10, 0))
        ttk.Button(date_filter_frame, text="Применить", 
                  command=lambda: self.apply_filters()).pack(side=tk.LEFT, padx=(10, 0))
        ttk.Button(date_filter_frame, text="Очистить", 
                  command=lambda: self.clear_filter_date()).pack(side=tk.LEFT, padx=(5, 0))
        ttk.Label(date_filter_frame, text="Формат: ГГГГ-ММ-ДД", foreground="gray").pack(side=tk.LEFT, padx=(10, 0))
        
        # Фильтр по температуре
        temp_filter_frame = ttk.Frame(filter_frame)
        temp_filter_frame.pack(fill=tk.X, pady=5)
        ttk.Label(temp_filter_frame, text="Фильтр по температуре:", width=15).pack(side=tk.LEFT)
        
        self.temp_filter_var = tk.StringVar(value="all")
        ttk.Radiobutton(temp_filter_frame, text="Все", variable=self.temp_filter_var, 
                       value="all", command=self.apply_filters).pack(side=tk.LEFT, padx=(10, 0))
        ttk.Radiobutton(temp_filter_frame, text="Выше +10°C", variable=self.temp_filter_var, 
                       value="above_10", command=self.apply_filters).pack(side=tk.LEFT, padx=(10, 0))
        ttk.Radiobutton(temp_filter_frame, text="Ниже или равно +10°C", variable=self.temp_filter_var, 
                       value="below_10", command=self.apply_filters).pack(side=tk.LEFT, padx=(10, 0))
        
        # Кнопка сброса всех фильтров
        ttk.Button(filter_frame, text="❌ Сбросить все фильтры", 
                  command=self.reset_filters).pack(pady=10)
        
        # Таблица записей
        entries_frame = ttk.LabelFrame(self.scrollable_frame, text="Записи о погоде", padding="10")
        entries_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Создание таблицы
        columns = ("Дата", "Температура", "Описание", "Осадки")
        self.tree = ttk.Treeview(entries_frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.tree.heading(col, text=col)
            if col == "Описание":
                self.tree.column(col, width=300)
            elif col == "Дата":
                self.tree.column(col, width=120)
            elif col == "Температура":
                self.tree.column(col, width=100)
            else:
                self.tree.column(col, width=80)
        
        # Скроллбар для таблицы
        tree_scrollbar = ttk.Scrollbar(entries_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=tree_scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Кнопки управления записями
        control_frame = ttk.Frame(entries_frame)
        control_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(control_frame, text="🗑 Удалить выбранную запись", 
                  command=self.delete_entry).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="✏ Редактировать выбранную запись", 
                  command=self.edit_entry).pack(side=tk.LEFT, padx=5)
        
        # Панель статистики
        stats_frame = ttk.LabelFrame(self.scrollable_frame, text="Статистика", padding="10")
        stats_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.stats_label = ttk.Label(stats_frame, text="")
        self.stats_label.pack()
        
        # Упаковка основного контейнера
        main_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Привязка колесика мыши для прокрутки
        def _on_mousewheel(event):
            main_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        main_canvas.bind("<MouseWheel>", _on_mousewheel)
        
    def validate_date(self, date_str):
        """Проверка корректности формата даты"""
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False
    
    def add_entry(self):
        """Добавление новой записи"""
        date = self.date_entry.get().strip()
        temp = self.temp_entry.get().strip()
        description = self.desc_entry.get().strip()
        precipitation = self.precip_var.get()
        
        # Валидация ввода
        if not date:
            messagebox.showwarning("Ошибка ввода", "Поле 'Дата' не может быть пустым!")
            return
        
        if not self.validate_date(date):
            messagebox.showwarning("Ошибка ввода", 
                                 "Неверный формат даты!\nИспользуйте формат: ГГГГ-ММ-ДД\nПример: 2024-01-15")
            return
        
        if not temp:
            messagebox.showwarning("Ошибка ввода", "Поле 'Температура' не может быть пустым!")
            return
        
        try:
            temp_float = float(temp)
        except ValueError:
            messagebox.showwarning("Ошибка ввода", "Температура должна быть числом!")
            return
        
        if not description:
            messagebox.showwarning("Ошибка ввода", "Поле 'Описание погоды' не может быть пустым!")
            return
        
        # Создание записи
        entry = {
            "date": date,
            "temperature": temp_float,
            "description": description,
            "precipitation": "Да" if precipitation else "Нет"
        }
        
        self.entries.append(entry)
        # Сортировка по дате
        self.entries.sort(key=lambda x: x["date"])
        self.save_entries()
        self.reset_filters()
        self.clear_input_fields()
        messagebox.showinfo("Успех", "Запись успешно добавлена!")
        
    def delete_entry(self):
        """Удаление выбранной записи"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Нет выбора", "Пожалуйста, выберите запись для удаления")
            return
        
        # Получение данных выбранной записи
        item = self.tree.item(selected[0])
        values = item['values']
        
        # Поиск и удаление записи
        display_entries = self.filtered_entries if self.filter_active else self.entries
        entry_to_delete = None
        for entry in display_entries:
            if (entry["date"] == values[0] and 
                entry["temperature"] == float(values[1]) and 
                entry["description"] == values[2]):
                entry_to_delete = entry
                break
        
        if entry_to_delete and entry_to_delete in self.entries:
            self.entries.remove(entry_to_delete)
            self.save_entries()
            self.reset_filters()
            messagebox.showinfo("Успех", "Запись успешно удалена!")
        
    def edit_entry(self):
        """Редактирование выбранной записи"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Нет выбора", "Пожалуйста, выберите запись для редактирования")
            return
        
        # Получение данных выбранной записи
        item = self.tree.item(selected[0])
        values = item['values']
        
        # Заполнение полей ввода
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, values[0])
        self.temp_entry.delete(0, tk.END)
        self.temp_entry.insert(0, str(values[1]))
        self.desc_entry.delete(0, tk.END)
        self.desc_entry.insert(0, values[2])
        self.precip_var.set(values[3] == "Да")
        
        # Удаление старой записи
        display_entries = self.filtered_entries if self.filter_active else self.entries
        for entry in display_entries:
            if (entry["date"] == values[0] and 
                entry["temperature"] == float(values[1]) and 
                entry["description"] == values[2]):
                if entry in self.entries:
                    self.entries.remove(entry)
                    break
        
        self.save_entries()
        messagebox.showinfo("Информация", "Теперь вы можете отредактировать запись и нажать 'Добавить запись'")
        
    def apply_filters(self):
        """Применение фильтров"""
        self.filtered_entries = self.entries.copy()
        self.filter_active = True
        
        # Фильтр по дате
        filter_date = self.filter_date_entry.get().strip()
        if filter_date:
            if self.validate_date(filter_date):
                self.filtered_entries = [e for e in self.filtered_entries if e["date"] == filter_date]
            else:
                messagebox.showwarning("Ошибка фильтра", "Неверный формат даты в фильтре!")
                return
        
        # Фильтр по температуре
        temp_filter = self.temp_filter_var.get()
        if temp_filter == "above_10":
            self.filtered_entries = [e for e in self.filtered_entries if e["temperature"] > 10]
        elif temp_filter == "below_10":
            self.filtered_entries = [e for e in self.filtered_entries if e["temperature"] <= 10]
        
        self.update_display()
        self.update_statistics()
        
    def clear_filter_date(self):
        """Очистка фильтра по дате"""
        self.filter_date_entry.delete(0, tk.END)
        self.apply_filters()
        
    def reset_filters(self):
        """Сброс всех фильтров"""
        self.filter_date_entry.delete(0, tk.END)
        self.temp_filter_var.set("all")
        self.filter_active = False
        self.filtered_entries = []
        self.update_display()
        self.update_statistics()
        
    def update_display(self):
        """Обновление отображения таблицы"""
        # Очистка таблицы
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Заполнение таблицы
        display_entries = self.filtered_entries if self.filter_active else self.entries
        
        for entry in display_entries:
            self.tree.insert("", tk.END, values=(
                entry["date"],
                f"{entry['temperature']:.1f}",
                entry["description"],
                entry["precipitation"]
            ))
            
    def update_statistics(self):
        """Обновление статистики"""
        display_entries = self.filtered_entries if self.filter_active else self.entries
        
        if not display_entries:
            self.stats_label.config(text="Нет записей для отображения")
            return
        
        total = len(display_entries)
        avg_temp = sum(e["temperature"] for e in display_entries) / total
        min_temp = min(e["temperature"] for e in display_entries)
        max_temp = max(e["temperature"] for e in display_entries)
        rainy_days = sum(1 for e in display_entries if e["precipitation"] == "Да")
        
        filter_text = " (с учетом фильтров)" if self.filter_active else ""
        
        stats_text = (f"📊 Статистика{filter_text}: "
                     f"Всего записей: {total} | "
                     f"Средняя температура: {avg_temp:.1f}°C | "
                     f"Мин. температура: {min_temp:.1f}°C | "
                     f"Макс. температура: {max_temp:.1f}°C | "
                     f"Дней с осадками: {rainy_days}")
        
        self.stats_label.config(text=stats_text)
        
    def clear_input_fields(self):
        """Очистка полей ввода"""
        self.date_entry.delete(0, tk.END)
        self.temp_entry.delete(0, tk.END)
        self.desc_entry.delete(0, tk.END)
        self.precip_var.set(False)
        
    def load_entries(self):
        """Загрузка записей из JSON файла"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def save_entries(self):
        """Сохранение записей в JSON файл"""
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.entries, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherDiary(root)
    root.mainloop()
