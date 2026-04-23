import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
import os
from datetime import datetime

class GitHubUserFinder:
    def __init__(self, root):
        self.root = root
        self.root.title("GitHub User Finder")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Файл для хранения избранных
        self.favorites_file = "favorites.json"
        self.favorites = self.load_favorites()
        
        # Создание интерфейса
        self.create_widgets()
        
        # Привязка событий
        self.search_entry.bind("<Return>", lambda event: self.search_users())
        
    def create_widgets(self):
        # Верхняя панель поиска
        search_frame = ttk.Frame(self.root, padding="10")
        search_frame.pack(fill=tk.X)
        
        ttk.Label(search_frame, text="Поиск пользователя GitHub:").pack(side=tk.LEFT, padx=(0, 10))
        self.search_entry = ttk.Entry(search_frame, width=40)
        self.search_entry.pack(side=tk.LEFT, padx=(0, 10))
        
        self.search_button = ttk.Button(search_frame, text="Найти", command=self.search_users)
        self.search_button.pack(side=tk.LEFT)
        
        # Панель вкладок
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Вкладка результатов поиска
        self.results_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.results_frame, text="Результаты поиска")
        
        # Таблица результатов
        columns = ("Логин", "ID", "Тип", "Ссылка")
        self.results_tree = ttk.Treeview(self.results_frame, columns=columns, show="headings")
        
        for col in columns:
            self.results_tree.heading(col, text=col)
            self.results_tree.column(col, width=150)
        
        scrollbar = ttk.Scrollbar(self.results_frame, orient=tk.VERTICAL, command=self.results_tree.yview)
        self.results_tree.configure(yscrollcommand=scrollbar.set)
        
        self.results_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Кнопка добавления в избранное
        button_frame = ttk.Frame(self.results_frame)
        button_frame.pack(fill=tk.X, pady=5)
        
        self.add_fav_button = ttk.Button(button_frame, text="Добавить выбранного в избранное", 
                                        command=self.add_to_favorites)
        self.add_fav_button.pack()
        
        # Вкладка избранного
        self.favorites_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.favorites_frame, text="Избранное")
        
        # Таблица избранного
        fav_columns = ("Логин", "ID", "Дата добавления")
        self.favorites_tree = ttk.Treeview(self.favorites_frame, columns=fav_columns, show="headings")
        
        for col in fav_columns:
            self.favorites_tree.heading(col, text=col)
            self.favorites_tree.column(col, width=150)
        
        fav_scrollbar = ttk.Scrollbar(self.favorites_frame, orient=tk.VERTICAL, command=self.favorites_tree.yview)
        self.favorites_tree.configure(yscrollcommand=fav_scrollbar.set)
        
        self.favorites_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        fav_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Кнопка удаления из избранного
        fav_button_frame = ttk.Frame(self.favorites_frame)
        fav_button_frame.pack(fill=tk.X, pady=5)
        
        self.remove_fav_button = ttk.Button(fav_button_frame, text="Удалить выбранного из избранного",
                                           command=self.remove_from_favorites)
        self.remove_fav_button.pack()
        
        # Обновление списка избранного
        self.update_favorites_display()
        
    def load_favorites(self):
        """Загрузка избранных пользователей из JSON файла"""
        if os.path.exists(self.favorites_file):
            try:
                with open(self.favorites_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def save_favorites(self):
        """Сохранение избранных пользователей в JSON файл"""
        with open(self.favorites_file, 'w', encoding='utf-8') as f:
            json.dump(self.favorites, f, ensure_ascii=False, indent=2)
    
    def search_users(self):
        """Поиск пользователей через GitHub API"""
        username = self.search_entry.get().strip()
        
        # Проверка корректности ввода
        if not username:
            messagebox.showwarning("Ошибка ввода", "Поле поиска не может быть пустым!")
            return
        
        try:
            # Запрос к GitHub API для поиска пользователей
            url = f"https://api.github.com/search/users?q={username}&per_page=30"
            response = requests.get(url)
            
            if response.status_code == 200:
                data = response.json()
                users = data.get('items', [])
                
                # Очистка таблицы
                for item in self.results_tree.get_children():
                    self.results_tree.delete(item)
                
                # Заполнение таблицы результатами
                if users:
                    for user in users:
                        self.results_tree.insert("", tk.END, values=(
                            user['login'],
                            user['id'],
                            user['type'],
                            user['html_url']
                        ))
                else:
                    messagebox.showinfo("Результаты поиска", "Пользователи не найдены")
            else:
                messagebox.showerror("Ошибка API", f"Ошибка при запросе к API: {response.status_code}")
                
        except requests.RequestException as e:
            messagebox.showerror("Ошибка соединения", f"Не удалось подключиться к GitHub API: {str(e)}")
    
    def add_to_favorites(self):
        """Добавление выбранного пользователя в избранное"""
        selected = self.results_tree.selection()
        if not selected:
            messagebox.showwarning("Нет выбора", "Пожалуйста, выберите пользователя из результатов поиска")
            return
        
        # Получение данных выбранного пользователя
        item = self.results_tree.item(selected[0])
        values = item['values']
        
        user_data = {
            'login': values[0],
            'id': values[1],
            'type': values[2],
            'html_url': values[3],
            'date_added': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Проверка, не добавлен ли уже пользователь
        if any(fav['id'] == user_data['id'] for fav in self.favorites):
            messagebox.showinfo("Информация", f"Пользователь {values[0]} уже в избранном")
            return
        
        self.favorites.append(user_data)
        self.save_favorites()
        self.update_favorites_display()
        messagebox.showinfo("Успех", f"Пользователь {values[0]} добавлен в избранное")
    
    def remove_from_favorites(self):
        """Удаление выбранного пользователя из избранного"""
        selected = self.favorites_tree.selection()
        if not selected:
            messagebox.showwarning("Нет выбора", "Пожалуйста, выберите пользователя из избранного")
            return
        
        item = self.favorites_tree.item(selected[0])
        values = item['values']
        
        # Удаление по логину
        self.favorites = [fav for fav in self.favorites if fav['login'] != values[0]]
        self.save_favorites()
        self.update_favorites_display()
        messagebox.showinfo("Успех", f"Пользователь {values[0]} удалён из избранного")
    
    def update_favorites_display(self):
        """Обновление отображения списка избранного"""
        # Очистка таблицы
        for item in self.favorites_tree.get_children():
            self.favorites_tree.delete(item)
        
        # Заполнение таблицы
        for fav in self.favorites:
            self.favorites_tree.insert("", tk.END, values=(
                fav['login'],
                fav['id'],
                fav['date_added']
            ))

if __name__ == "__main__":
    root = tk.Tk()
    app = GitHubUserFinder(root)
    root.mainloop()
