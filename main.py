import tkinter as tk
from tkinter import ttk, messagebox, Canvas
import pyautogui
import threading
import time
import keyboard
import json
import os
from pynput import mouse

class AutoClicker:
    def __init__(self, root):
        self.root = root
        self.root.title("Vibe Click - Автокликер")
        self.root.geometry("1250x750")
        self.root.resizable(False, False)
        self.root.configure(bg="#f0f0f0")
        
        # Переменные
        self.is_clicking = False
        self.click_x = None
        self.click_y = None
        self.click_thread = None
        self.config_file = "vibe_click_config.json"
        self.action_chain = []  # Цепочка действий
        self.current_action_index = 0
        self.mouse_listener = None  # Для отслеживания кликов мыши
        self.waiting_for_click = False
        
        # Настройка безопасности pyautogui
        pyautogui.FAILSAFE = True
        
        self.create_widgets()
        self.load_settings()  # Загружаем настройки при старте
        
        # Горячие клавиши
        keyboard.add_hotkey('f6', self.toggle_clicking)  # Старт/стоп
        keyboard.add_hotkey('q', self.emergency_stop)    # Экстренная остановка
        
    def create_widgets(self):
        # Заголовок с градиентом (уменьшенный)
        title_frame = tk.Frame(self.root, bg="#2c3e50", height=45)
        title_frame.pack(fill="x")
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(
            title_frame, 
            text="Vibe Click - Автокликер",
            font=("Segoe UI", 16, "bold"),
            fg="white",
            bg="#2c3e50"
        )
        title_label.pack(pady=8)
        
        # Основной контент с отступами
        main_content = tk.Frame(self.root, bg="#f0f0f0")
        main_content.pack(fill="both", expand=True, padx=8, pady=5)
        
        # Основной канвас для блок-схемы (уменьшенный)
        canvas_frame = tk.Frame(main_content, bg="#ffffff", relief="solid", bd=1)
        canvas_frame.pack(pady=3)
        
        # Инструкция над схемой
        instruction_label = tk.Label(
            canvas_frame,
            text="📌 Выбери координаты → Добавь в цепочку → Запусти",
            font=("Segoe UI", 8),
            fg="#7f8c8d",
            bg="#ffffff",
            pady=3
        )
        instruction_label.pack(fill="x")
        
        canvas = Canvas(
            canvas_frame,
            width=700,
            height=120,
            bg="#ffffff",
            highlightthickness=0
        )
        canvas.pack(pady=5)
        
        # БЛОК 1: Выбор координат (слева)
        block1_x, block1_y = 80, 15
        block1_width, block1_height = 200, 90
        
        # Рисуем квадрат 1 с тенью
        canvas.create_rectangle(
            block1_x + 3, block1_y + 3,
            block1_x + block1_width + 3, block1_y + block1_height + 3,
            fill="#bdc3c7", outline="",
        )
        canvas.create_rectangle(
            block1_x, block1_y,
            block1_x + block1_width, block1_y + block1_height,
            fill="#3498db",
            outline="#2980b9",
            width=2
        )
        
        # Иконка и текст блока 1
        canvas.create_text(
            block1_x + block1_width // 2, block1_y + 25,
            text="📍",
            font=("Segoe UI", 20),
            fill="white"
        )
        canvas.create_text(
            block1_x + block1_width // 2, block1_y + 55,
            text="ШАГ 1",
            font=("Segoe UI", 10, "bold"),
            fill="white"
        )
        canvas.create_text(
            block1_x + block1_width // 2, block1_y + 72,
            text="Выбор координат",
            font=("Segoe UI", 9),
            fill="white"
        )
        
        # СТРЕЛКА между блоками (более толстая и красивая)
        arrow_start_x = block1_x + block1_width + 15
        arrow_end_x = 400
        arrow_y = block1_y + block1_height // 2
        
        # Рисуем стрелку
        canvas.create_line(
            arrow_start_x, arrow_y,
            arrow_end_x, arrow_y,
            arrow=tk.LAST,
            fill="#34495e",
            width=5,
            arrowshape=(16, 20, 6)
        )
        
        # БЛОК 2: Клик мышкой (справа)
        block2_x, block2_y = 420, 15
        block2_width, block2_height = 200, 90
        
        # Рисуем квадрат 2 с тенью
        canvas.create_rectangle(
            block2_x + 3, block2_y + 3,
            block2_x + block2_width + 3, block2_y + block2_height + 3,
            fill="#bdc3c7", outline="",
        )
        canvas.create_rectangle(
            block2_x, block2_y,
            block2_x + block2_width, block2_y + block2_height,
            fill="#e74c3c",
            outline="#c0392b",
            width=2
        )
        
        # Иконка и текст блока 2
        canvas.create_text(
            block2_x + block2_width // 2, block2_y + 25,
            text="▶️",
            font=("Segoe UI", 20),
            fill="white"
        )
        canvas.create_text(
            block2_x + block2_width // 2, block2_y + 55,
            text="ШАГ 2",
            font=("Segoe UI", 10, "bold"),
            fill="white"
        )
        canvas.create_text(
            block2_x + block2_width // 2, block2_y + 72,
            text="Запуск процесса",
            font=("Segoe UI", 9),
            fill="white"
        )
        
        # Кнопки под блоками (уменьшенные)
        buttons_frame = tk.Frame(main_content, bg="#f0f0f0")
        buttons_frame.pack(pady=5)
        
        # Кнопка для блока 1 (выбор координат)
        self.select_btn = tk.Button(
            buttons_frame,
            text="📍 Задать координаты",
            command=self.select_position,
            bg="#3498db",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            cursor="hand2",
            padx=15,
            pady=8,
            relief="flat",
            activebackground="#2980b9",
            activeforeground="white"
        )
        self.select_btn.grid(row=0, column=0, padx=8)
        
        # Кнопка для блока 2 (запуск кликов)
        self.start_stop_btn = tk.Button(
            buttons_frame,
            text="▶ Запустить процесс",
            command=self.toggle_clicking,
            bg="#27ae60",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            cursor="hand2",
            padx=15,
            pady=8,
            relief="flat",
            activebackground="#229954",
            activeforeground="white"
        )
        self.start_stop_btn.grid(row=0, column=1, padx=8)
        
        # Отображение координат (компактное)
        coord_display_frame = tk.Frame(main_content, bg="#ecf0f1", relief="solid", bd=1)
        coord_display_frame.pack(fill="x", pady=5)
        
        self.coord_label = tk.Label(
            coord_display_frame,
            text="Координаты: не заданы",
            font=("Segoe UI", 9, "bold"),
            bg="#ecf0f1",
            fg="#7f8c8d",
            pady=6
        )
        self.coord_label.pack()
        
        # СЕКЦИЯ ЦЕПОЧКИ ДЕЙСТВИЙ (компактная)
        chain_main_frame = tk.Frame(main_content, bg="#f0f0f0")
        chain_main_frame.pack(pady=3, fill="both", expand=True)
        
        # Заголовок цепочки (компактный)
        chain_title_frame = tk.Frame(chain_main_frame, bg="#ff9800", relief="flat", bd=0, height=30)
        chain_title_frame.pack(fill="x")
        chain_title_frame.pack_propagate(False)
        
        tk.Label(
            chain_title_frame,
            text="🔗 Цепочка действий",
            font=("Segoe UI", 10, "bold"),
            bg="#ff9800",
            fg="white"
        ).pack(pady=5)
        
        # Фрейм со списком и кнопками (компактный)
        chain_content_frame = tk.Frame(chain_main_frame, bg="#fff8e1", relief="solid", bd=1)
        chain_content_frame.pack(fill="both", expand=True)
        
        # Список действий с прокруткой (меньше)
        list_frame = tk.Frame(chain_content_frame, bg="#fff8e1")
        list_frame.pack(padx=5, pady=5, fill="both", expand=True)
        
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")
        
        self.chain_listbox = tk.Listbox(
            list_frame,
            font=("Consolas", 8),
            height=3,
            yscrollcommand=scrollbar.set,
            selectmode=tk.SINGLE,
            bg="#ffffff",
            fg="#2c3e50",
            selectbackground="#3498db",
            selectforeground="white",
            relief="solid",
            bd=1
        )
        self.chain_listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.chain_listbox.yview)
        
        # Поля ввода в одной строке
        input_row = tk.Frame(chain_content_frame, bg="#fff8e1")
        input_row.pack(pady=3)
        
        tk.Label(
            input_row,
            text="Название:",
            bg="#fff8e1",
            font=("Segoe UI", 8, "bold"),
            fg="#2c3e50"
        ).grid(row=0, column=0, padx=3)
        
        self.step_name_var = tk.StringVar(value="Шаг 1")
        step_name_entry = tk.Entry(
            input_row,
            textvariable=self.step_name_var,
            width=15,
            font=("Segoe UI", 8),
            relief="solid",
            bd=1
        )
        step_name_entry.grid(row=0, column=1, padx=3)
        
        tk.Label(
            input_row,
            text="Действие:",
            bg="#fff8e1",
            font=("Segoe UI", 8, "bold"),
            fg="#2c3e50"
        ).grid(row=0, column=2, padx=3)
        
        self.action_type = tk.StringVar(value="Клик левой")
        action_combo = ttk.Combobox(
            input_row,
            textvariable=self.action_type,
            values=["Клик левой", "Клик правой", "Клик средней", "Двойной клик"],
            state="readonly",
            width=13,
            font=("Segoe UI", 8)
        )
        action_combo.grid(row=0, column=3, padx=3)
        
        # Кнопки управления (компактные)
        buttons_row = tk.Frame(chain_content_frame, bg="#fff8e1")
        buttons_row.pack(pady=4)
        
        tk.Button(
            buttons_row,
            text="➕ Добавить",
            command=self.add_to_chain,
            bg="#4caf50",
            fg="white",
            font=("Segoe UI", 8, "bold"),
            cursor="hand2",
            padx=8,
            pady=4,
            relief="flat",
            activebackground="#45a049",
            activeforeground="white"
        ).grid(row=0, column=0, padx=3)
        
        tk.Button(
            buttons_row,
            text="❌ Удалить",
            command=self.remove_from_chain,
            bg="#f44336",
            fg="white",
            font=("Segoe UI", 8, "bold"),
            cursor="hand2",
            padx=8,
            pady=4,
            relief="flat",
            activebackground="#da190b",
            activeforeground="white"
        ).grid(row=0, column=1, padx=3)
        
        tk.Button(
            buttons_row,
            text="🗑️ Очистить",
            command=self.clear_chain,
            bg="#757575",
            fg="white",
            font=("Segoe UI", 8, "bold"),
            cursor="hand2",
            padx=8,
            pady=4,
            relief="flat",
            activebackground="#616161",
            activeforeground="white"
        ).grid(row=0, column=2, padx=3)
        
        # Настройки (компактные)
        settings_frame = tk.Frame(main_content, bg="#ffffff", relief="solid", bd=1)
        settings_frame.pack(pady=3, fill="x")
        
        settings_header = tk.Frame(settings_frame, bg="#34495e", height=25)
        settings_header.pack(fill="x")
        settings_header.pack_propagate(False)
        
        tk.Label(
            settings_header,
            text="⚙️ Настройки",
            font=("Segoe UI", 9, "bold"),
            bg="#34495e",
            fg="white"
        ).pack(pady=3)
        
        # Контент настроек (все в одной строке)
        settings_content = tk.Frame(settings_frame, bg="#ffffff")
        settings_content.pack(padx=5, pady=5)
        
        controls_frame = tk.Frame(settings_content, bg="#ffffff")
        controls_frame.pack()
        
        # Интервал
        tk.Label(
            controls_frame, 
            text="Интервал:",
            bg="#ffffff",
            font=("Segoe UI", 8, "bold"),
            fg="#2c3e50"
        ).grid(row=0, column=0, padx=3)
        
        self.interval_var = tk.DoubleVar(value=1.0)
        interval_spinbox = tk.Spinbox(
            controls_frame,
            from_=0.1,
            to=10.0,
            increment=0.1,
            textvariable=self.interval_var,
            width=8,
            font=("Segoe UI", 8),
            relief="solid",
            bd=1
        )
        interval_spinbox.grid(row=0, column=1, padx=3)
        
        # Кнопка мыши
        tk.Label(
            controls_frame,
            text="Кнопка:",
            bg="#ffffff",
            font=("Segoe UI", 8, "bold"),
            fg="#2c3e50"
        ).grid(row=0, column=2, padx=3)
        
        self.click_type = tk.StringVar(value="left")
        click_combo = ttk.Combobox(
            controls_frame,
            textvariable=self.click_type,
            values=["left", "right", "middle"],
            state="readonly",
            width=8,
            font=("Segoe UI", 8)
        )
        click_combo.grid(row=0, column=3, padx=3)
        
        # Кнопки сохранения и загрузки настроек
        save_btn = tk.Button(
            controls_frame,
            text="💾 Сохранить",
            command=self.save_settings,
            bg="#9b59b6",
            fg="white",
            font=("Segoe UI", 8, "bold"),
            cursor="hand2",
            padx=8,
            pady=4,
            relief="flat",
            activebackground="#8e44ad",
            activeforeground="white"
        )
        save_btn.grid(row=0, column=4, padx=3)
        
        load_btn = tk.Button(
            controls_frame,
            text="📂 Загрузить",
            command=self.load_settings_manual,
            bg="#3498db",
            fg="white",
            font=("Segoe UI", 8, "bold"),
            cursor="hand2",
            padx=8,
            pady=4,
            relief="flat",
            activebackground="#2980b9",
            activeforeground="white"
        )
        load_btn.grid(row=0, column=5, padx=3)
        
        # Статус (компактный)
        status_frame = tk.Frame(main_content, bg="#ecf0f1", relief="solid", bd=1, height=30)
        status_frame.pack(fill="x", pady=3)
        status_frame.pack_propagate(False)
        
        self.status_label = tk.Label(
            status_frame,
            text="⚫ Статус: Остановлено",
            font=("Segoe UI", 9, "bold"),
            fg="#95a5a6",
            bg="#ecf0f1"
        )
        self.status_label.pack(pady=6)
        
        # Панель с горячими клавишами (компактная)
        hotkeys_frame = tk.Frame(main_content, bg="#e8f5e9", relief="solid", bd=1)
        hotkeys_frame.pack(fill="x", pady=2)
        
        hotkeys_info = tk.Label(
            hotkeys_frame,
            text="⌨️ F6 - Старт/Стоп | Q - Остановка | Угол экрана - Экстренная остановка",
            font=("Segoe UI", 8, "bold"),
            bg="#e8f5e9",
            fg="#1b5e20"
        )
        hotkeys_info.pack(pady=3)
        
    def select_position(self):
        """Запуск процесса выбора позиции"""
        if self.waiting_for_click:
            messagebox.showinfo(
                "Информация",
                "Уже ожидается выбор позиции!"
            )
            return
        
        self.waiting_for_click = True
        self.select_btn.config(state="disabled", bg="#95a5a6", text="⏳ Ожидание клика...")
        
        messagebox.showinfo(
            "📍 Выбор позиции",
            "Наведите курсор на нужное место\nи нажмите ЛЕВУЮ кнопку мыши\n\n✅ Координаты будут запомнены!"
        )
        
        # Запускаем слушатель мыши
        def on_click(x, y, button, pressed):
            if pressed and button == mouse.Button.left and self.waiting_for_click:
                self.click_x, self.click_y = x, y
                self.root.after(0, lambda: self.coord_label.config(
                    text=f"✅ Координаты: X={self.click_x}, Y={self.click_y}",
                    fg="#27ae60"
                ))
                self.root.after(0, lambda: self.select_btn.config(
                    state="normal", 
                    bg="#3498db",
                    text="📍 Задать координаты"
                ))
                self.waiting_for_click = False
                # Останавливаем слушатель
                return False
        
        # Создаём и запускаем слушатель в отдельном потоке
        def start_listener():
            with mouse.Listener(on_click=on_click) as listener:
                listener.join()
        
        thread = threading.Thread(target=start_listener, daemon=True)
        thread.start()
        
    def toggle_clicking(self):
        """Переключение режима кликов"""
        if not self.is_clicking:
            # Если есть цепочка - используем её, иначе одиночный клик
            if len(self.action_chain) > 0:
                self.start_clicking()
            elif self.click_x is None or self.click_y is None:
                messagebox.showwarning(
                    "Внимание",
                    "Сначала выберите позицию для клика или создайте цепочку действий!"
                )
                return
            else:
                self.start_clicking()
        else:
            self.stop_clicking()
            
    def start_clicking(self):
        """Запуск автоматических кликов"""
        self.is_clicking = True
        self.start_stop_btn.config(
            text="⏸ Остановить процесс",
            bg="#e74c3c"
        )
        self.status_label.config(
            text="🟢 Статус: Работает",
            fg="#27ae60"
        )
        self.select_btn.config(state="disabled")
        
        # Запуск потока кликов
        self.click_thread = threading.Thread(target=self.clicking_loop, daemon=True)
        self.click_thread.start()
        
    def stop_clicking(self):
        """Остановка автоматических кликов"""
        self.is_clicking = False
        self.start_stop_btn.config(
            text="▶ Запустить процесс",
            bg="#27ae60"
        )
        self.status_label.config(
            text="⚫ Статус: Остановлено",
            fg="#95a5a6"
        )
        self.select_btn.config(state="normal")
        
    def clicking_loop(self):
        """Основной цикл кликов"""
        while self.is_clicking:
            try:
                # Если есть цепочка - выполняем её
                if len(self.action_chain) > 0:
                    for action in self.action_chain:
                        if not self.is_clicking:
                            break
                        
                        action_type = action.get('action_type', 'Клик левой')
                        x = action['x']
                        y = action['y']
                        button = action['button']
                        
                        # Выполняем действие в зависимости от типа
                        if action_type == "Двойной клик":
                            pyautogui.doubleClick(x, y, button=button)
                        else:
                            pyautogui.click(x, y, button=button)
                        
                        time.sleep(self.interval_var.get())
                else:
                    # Одиночный клик
                    pyautogui.click(
                        self.click_x, 
                        self.click_y, 
                        button=self.click_type.get()
                    )
                    time.sleep(self.interval_var.get())
            except pyautogui.FailSafeException:
                # Экстренная остановка при перемещении курсора в угол
                self.root.after(0, self.stop_clicking)
                self.root.after(0, lambda: messagebox.showinfo(
                    "Экстренная остановка",
                    "Клики остановлены (курсор в углу экрана)"
                ))
                break
            except Exception as e:
                self.root.after(0, self.stop_clicking)
                self.root.after(0, lambda: messagebox.showerror(
                    "Ошибка",
                    f"Произошла ошибка: {str(e)}"
                ))
                break
                
    def emergency_stop(self):
        """Экстренная остановка по нажатию Q"""
        if self.is_clicking:
            self.stop_clicking()
    
    def add_to_chain(self):
        """Добавление текущих координат в цепочку"""
        if self.click_x is None or self.click_y is None:
            messagebox.showwarning(
                "Внимание",
                "Сначала задайте координаты!\n\nНажмите '📍 Задать координаты' и выберите точку на экране."
            )
            return
        
        # Определяем кнопку мыши из типа действия
        action_type = self.action_type.get()
        if action_type == "Клик левой":
            button = "left"
        elif action_type == "Клик правой":
            button = "right"
        elif action_type == "Клик средней":
            button = "middle"
        elif action_type == "Двойной клик":
            button = "left"  # Для двойного клика используем левую
        else:
            button = "left"
        
        action = {
            'name': self.step_name_var.get(),
            'x': self.click_x,
            'y': self.click_y,
            'action_type': action_type,
            'button': button
        }
        
        self.action_chain.append(action)
        self.update_chain_display()
        
        # Автоматически увеличиваем номер шага
        current_name = self.step_name_var.get()
        if "Шаг" in current_name:
            try:
                parts = current_name.split()
                if len(parts) >= 2 and parts[-1].isdigit():
                    num = int(parts[-1]) + 1
                    self.step_name_var.set(f"Шаг {num}")
            except:
                pass
        
        messagebox.showinfo(
            "Успех",
            f"✅ Действие добавлено!\n\n'{action['name']}'\nВсего в цепочке: {len(self.action_chain)}"
        )
    
    def remove_from_chain(self):
        """Удаление выбранного действия из цепочки"""
        selection = self.chain_listbox.curselection()
        if not selection:
            messagebox.showwarning(
                "Внимание",
                "Выберите действие из списка для удаления!"
            )
            return
        
        index = selection[0]
        del self.action_chain[index]
        self.update_chain_display()
        
        messagebox.showinfo(
            "Удалено",
            f"❌ Действие удалено!\n\nОсталось в цепочке: {len(self.action_chain)}"
        )
    
    def clear_chain(self):
        """Очистка всей цепочки"""
        if len(self.action_chain) == 0:
            messagebox.showinfo(
                "Информация",
                "Цепочка уже пуста!"
            )
            return
        
        result = messagebox.askyesno(
            "Подтверждение",
            f"Удалить все {len(self.action_chain)} действий из цепочки?"
        )
        
        if result:
            self.action_chain.clear()
            self.update_chain_display()
            messagebox.showinfo(
                "Очищено",
                "🗑️ Вся цепочка очищена!"
            )
    
    def update_chain_display(self):
        """Обновление отображения цепочки"""
        self.chain_listbox.delete(0, tk.END)
        for i, action in enumerate(self.action_chain, 1):
            # Получаем иконку действия
            action_type = action.get('action_type', 'Клик левой')
            if action_type == "Клик левой":
                icon = "👆"
            elif action_type == "Клик правой":
                icon = "👉"
            elif action_type == "Клик средней":
                icon = "☝️"
            elif action_type == "Двойной клик":
                icon = "👆👆"
            else:
                icon = "🖱️"
            
            name = action.get('name', f'Шаг {i}')
            x = action['x']
            y = action['y']
            
            self.chain_listbox.insert(
                tk.END,
                f"{icon} {name} → X:{x}, Y:{y}"
            )
    
    def save_settings(self):
        """Сохранение настроек в файл"""
        settings = {
            "click_x": self.click_x,
            "click_y": self.click_y,
            "interval": self.interval_var.get(),
            "click_type": self.click_type.get(),
            "action_chain": self.action_chain  # Сохраняем цепочку действий
        }
        
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=4, ensure_ascii=False)
            
            chain_count = len(self.action_chain)
            chain_info = f"\n🔗 Цепочка: {chain_count} действий" if chain_count > 0 else "\n🔗 Цепочка: пусто"
            
            messagebox.showinfo(
                "Успех",
                f"✅ Настройки сохранены!\n\n"
                f"📁 Файл: {self.config_file}{chain_info}"
            )
        except Exception as e:
            messagebox.showerror(
                "Ошибка",
                f"Не удалось сохранить настройки:\n{str(e)}"
            )
    
    def load_settings(self):
        """Загрузка настроек из файла при старте"""
        if not os.path.exists(self.config_file):
            return
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                settings = json.load(f)
            
            # Загружаем координаты
            if settings.get("click_x") is not None and settings.get("click_y") is not None:
                self.click_x = settings["click_x"]
                self.click_y = settings["click_y"]
                self.coord_label.config(
                    text=f"✅ Координаты: X={self.click_x}, Y={self.click_y}",
                    fg="#27ae60"
                )
            
            # Загружаем интервал
            if settings.get("interval"):
                self.interval_var.set(settings["interval"])
            
            # Загружаем тип клика
            if settings.get("click_type"):
                self.click_type.set(settings["click_type"])
            
            # Загружаем цепочку действий
            if settings.get("action_chain"):
                self.action_chain = settings["action_chain"]
                self.update_chain_display()
                print(f"Загружена цепочка из {len(self.action_chain)} действий")
                
        except Exception as e:
            print(f"Ошибка загрузки настроек: {e}")
    
    def load_settings_manual(self):
        """Ручная загрузка настроек из файла"""
        if not os.path.exists(self.config_file):
            messagebox.showwarning(
                "Внимание",
                f"Файл настроек не найден!\n\n📁 {self.config_file}\n\nСначала сохраните настройки."
            )
            return
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                settings = json.load(f)
            
            # Загружаем координаты
            if settings.get("click_x") is not None and settings.get("click_y") is not None:
                self.click_x = settings["click_x"]
                self.click_y = settings["click_y"]
                self.coord_label.config(
                    text=f"✅ Координаты: X={self.click_x}, Y={self.click_y}",
                    fg="#27ae60"
                )
            
            # Загружаем интервал
            if settings.get("interval"):
                self.interval_var.set(settings["interval"])
            
            # Загружаем тип клика
            if settings.get("click_type"):
                self.click_type.set(settings["click_type"])
            
            # Загружаем цепочку действий
            chain_count = 0
            if settings.get("action_chain"):
                self.action_chain = settings["action_chain"]
                chain_count = len(self.action_chain)
                self.update_chain_display()
            
            chain_info = f"\n🔗 Цепочка: {chain_count} действий" if chain_count > 0 else "\n🔗 Цепочка: пусто"
            
            messagebox.showinfo(
                "Успех",
                f"✅ Настройки загружены!\n\n📁 Файл: {self.config_file}{chain_info}"
            )
                
        except Exception as e:
            messagebox.showerror(
                "Ошибка",
                f"Не удалось загрузить настройки:\n{str(e)}"
            )
                
    def on_closing(self):
        """Обработка закрытия окна"""
        self.is_clicking = False
        keyboard.unhook_all()
        self.root.destroy()

def main():
    root = tk.Tk()
    app = AutoClicker(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()

