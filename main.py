import tkinter as tk
from tkinter import ttk, messagebox, Canvas
import pyautogui
import threading
import time
import keyboard
import json
import os
from pynput import mouse
import math

class Block:
    """Базовый класс для блоков"""
    def __init__(self, canvas, x, y, block_type, block_id):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.type = block_type  # 'coordinate' or 'click'
        self.id = block_id
        self.shapes = []  # Список ID элементов canvas
        self.text_ids = []
        self.data = {}
        self.connections_out = []  # Исходящие связи
        self.connections_in = []   # Входящие связи
        
    def draw(self):
        """Отрисовка блока"""
        pass
    
    def move(self, dx, dy):
        """Перемещение блока"""
        self.x += dx
        self.y += dy
        for shape_id in self.shapes + self.text_ids:
            self.canvas.move(shape_id, dx, dy)
        
    def contains_point(self, x, y):
        """Проверка попадания точки в блок"""
        return False
    
    def delete(self):
        """Удаление блока"""
        for shape_id in self.shapes + self.text_ids:
            self.canvas.delete(shape_id)

class CoordinateBlock(Block):
    """Блок координат (квадрат)"""
    SIZE = 80
    
    def __init__(self, canvas, x, y, block_id):
        super().__init__(canvas, x, y, 'coordinate', block_id)
        self.data = {'x': None, 'y': None}
        self.draw()
    
    def draw(self):
        """Отрисовка квадрата"""
        # Тень
        shadow = self.canvas.create_rectangle(
            self.x + 3, self.y + 3,
            self.x + self.SIZE + 3, self.y + self.SIZE + 3,
            fill="#bdc3c7", outline=""
        )
        self.shapes.append(shadow)
        
        # Основной квадрат
        rect = self.canvas.create_rectangle(
            self.x, self.y,
            self.x + self.SIZE, self.y + self.SIZE,
            fill="#3498db",
            outline="#2980b9",
            width=3,
            tags=f"block_{self.id}"
        )
        self.shapes.append(rect)
        
        # Иконка
        icon = self.canvas.create_text(
            self.x + self.SIZE // 2, self.y + 20,
            text="📍",
            font=("Segoe UI", 16),
            fill="white",
            tags=f"block_{self.id}"
        )
        self.text_ids.append(icon)
        
        # Текст
        text = self.canvas.create_text(
            self.x + self.SIZE // 2, self.y + 45,
            text="Координата",
            font=("Segoe UI", 8, "bold"),
            fill="white",
            tags=f"block_{self.id}"
        )
        self.text_ids.append(text)
        
        # Координаты
        self.coord_text = self.canvas.create_text(
            self.x + self.SIZE // 2, self.y + 65,
            text="Не задано",
            font=("Segoe UI", 7),
            fill="white",
            tags=f"block_{self.id}"
        )
        self.text_ids.append(self.coord_text)
    
    def update_coordinates(self, x, y):
        """Обновление координат"""
        self.data['x'] = x
        self.data['y'] = y
        self.canvas.itemconfig(self.coord_text, text=f"X:{x}\nY:{y}")
    
    def contains_point(self, x, y):
        """Проверка попадания точки в квадрат"""
        return (self.x <= x <= self.x + self.SIZE and 
                self.y <= y <= self.y + self.SIZE)

class ClickBlock(Block):
    """Блок клика (треугольник)"""
    SIZE = 80
    
    def __init__(self, canvas, x, y, block_id, click_type='left'):
        super().__init__(canvas, x, y, 'click', block_id)
        self.data = {'click_type': click_type}
        self.draw()
    
    def draw(self):
        """Отрисовка треугольника"""
        # Цвета в зависимости от типа клика
        colors = {
            'left': ("#27ae60", "#229954"),
            'right': ("#e74c3c", "#c0392b"),
            'middle': ("#f39c12", "#e67e22")
        }
        fill_color, outline_color = colors.get(self.data['click_type'], colors['left'])
        
        # Вершины треугольника (указывает вниз)
        points = [
            self.x + self.SIZE // 2, self.y,  # Верхняя вершина
            self.x, self.y + self.SIZE,       # Нижняя левая
            self.x + self.SIZE, self.y + self.SIZE  # Нижняя правая
        ]
        
        # Тень
        shadow_points = [p + 3 for p in points]
        shadow = self.canvas.create_polygon(
            shadow_points,
            fill="#bdc3c7", outline=""
        )
        self.shapes.append(shadow)
        
        # Основной треугольник
        triangle = self.canvas.create_polygon(
            points,
            fill=fill_color,
            outline=outline_color,
            width=3,
            tags=f"block_{self.id}"
        )
        self.shapes.append(triangle)
        
        # Иконка
        icons = {'left': "👆", 'right': "👉", 'middle': "☝️"}
        icon = self.canvas.create_text(
            self.x + self.SIZE // 2, self.y + 25,
            text=icons.get(self.data['click_type'], "🖱️"),
            font=("Segoe UI", 16),
            fill="white",
            tags=f"block_{self.id}"
        )
        self.text_ids.append(icon)
        
        # Текст
        labels = {'left': "Левый", 'right': "Правый", 'middle': "Средний"}
        text = self.canvas.create_text(
            self.x + self.SIZE // 2, self.y + 50,
            text=f"{labels.get(self.data['click_type'], 'Клик')}",
            font=("Segoe UI", 8, "bold"),
            fill="white",
            tags=f"block_{self.id}"
        )
        self.text_ids.append(text)
        
        click_text = self.canvas.create_text(
            self.x + self.SIZE // 2, self.y + 65,
            text="клик",
            font=("Segoe UI", 7),
            fill="white",
            tags=f"block_{self.id}"
        )
        self.text_ids.append(click_text)
    
    def contains_point(self, x, y):
        """Проверка попадания точки в треугольник"""
        # Упрощенная проверка - используем прямоугольник вокруг треугольника
        return (self.x <= x <= self.x + self.SIZE and 
                self.y <= y <= self.y + self.SIZE)

class Connection:
    """Соединение между блоками"""
    def __init__(self, canvas, from_block, to_block, delay=0.0):
        self.canvas = canvas
        self.from_block = from_block
        self.to_block = to_block
        self.delay = delay  # Задержка на переходе
        self.line_id = None
        self.arrow_id = None
        self.text_id = None
        self.delay_circle_id = None  # ID желтого круга с задержкой
        self.draw()
    
    def draw(self):
        """Отрисовка стрелки"""
        # Центры блоков (учитываем разные типы блоков)
        if hasattr(self.from_block, 'SIZE'):
            x1 = self.from_block.x + self.from_block.SIZE // 2
            y1 = self.from_block.y + self.from_block.SIZE // 2
        else:  # GroupBlock с WIDTH и HEIGHT
            x1 = self.from_block.x + self.from_block.WIDTH // 2
            y1 = self.from_block.y + self.from_block.HEIGHT // 2
        
        if hasattr(self.to_block, 'SIZE'):
            x2 = self.to_block.x + self.to_block.SIZE // 2
            y2 = self.to_block.y + self.to_block.SIZE // 2
        else:  # GroupBlock с WIDTH и HEIGHT
            x2 = self.to_block.x + self.to_block.WIDTH // 2
            y2 = self.to_block.y + self.to_block.HEIGHT // 2
        
        # Рисуем линию
        self.line_id = self.canvas.create_line(
            x1, y1, x2, y2,
            arrow=tk.LAST,
            fill="#34495e",
            width=3,
            arrowshape=(12, 15, 5),
            tags="connection"
        )
        
        # Опускаем на задний план
        self.canvas.tag_lower("connection")
        
        # Если есть задержка - показываем её на стрелке
        if self.delay > 0:
            mid_x = (x1 + x2) // 2
            mid_y = (y1 + y2) // 2
            
            # Фон для текста
            self.delay_circle_id = self.canvas.create_oval(
                mid_x - 15, mid_y - 15,
                mid_x + 15, mid_y + 15,
                fill="#ff9800",
                outline="#f57c00",
                width=2,
                tags="connection"
            )
            
            # Текст с временем
            self.text_id = self.canvas.create_text(
                mid_x, mid_y,
                text=f"{self.delay}s",
                font=("Segoe UI", 8, "bold"),
                fill="white",
                tags="connection"
            )
    
    def update(self):
        """Обновление позиции стрелки"""
        if self.line_id:
            self.canvas.delete(self.line_id)
        if self.text_id:
            self.canvas.delete(self.text_id)
        if self.delay_circle_id:
            self.canvas.delete(self.delay_circle_id)
        self.draw()
    
    def delete(self):
        """Удаление соединения"""
        if self.line_id:
            self.canvas.delete(self.line_id)
        if self.text_id:
            self.canvas.delete(self.text_id)
        if self.delay_circle_id:
            self.canvas.delete(self.delay_circle_id)
    
    def contains_point(self, x, y, tolerance=10):
        """Проверка попадания точки на линию"""
        # Получаем координаты линии
        if hasattr(self.from_block, 'SIZE'):
            x1 = self.from_block.x + self.from_block.SIZE // 2
            y1 = self.from_block.y + self.from_block.SIZE // 2
        else:
            x1 = self.from_block.x + self.from_block.WIDTH // 2
            y1 = self.from_block.y + self.from_block.HEIGHT // 2
        
        if hasattr(self.to_block, 'SIZE'):
            x2 = self.to_block.x + self.to_block.SIZE // 2
            y2 = self.to_block.y + self.to_block.SIZE // 2
        else:
            x2 = self.to_block.x + self.to_block.WIDTH // 2
            y2 = self.to_block.y + self.to_block.HEIGHT // 2
        
        # Расстояние от точки до линии
        line_len = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        if line_len == 0:
            return False
        
        # Расстояние от точки до линии через векторное произведение
        distance = abs((y2 - y1) * x - (x2 - x1) * y + x2 * y1 - y2 * x1) / line_len
        
        # Проверяем что точка находится между началом и концом линии
        dot_product = ((x - x1) * (x2 - x1) + (y - y1) * (y2 - y1)) / (line_len ** 2)
        
        return distance <= tolerance and 0 <= dot_product <= 1

class DelayBlock(Block):
    """Блок задержки (зеленый круг)"""
    SIZE = 80
    
    def __init__(self, canvas, x, y, block_id, delay=1.0):
        super().__init__(canvas, x, y, 'delay', block_id)
        self.data = {'delay': delay}
        self.draw()
    
    def draw(self):
        """Отрисовка зеленого круга"""
        radius = self.SIZE // 2
        center_x = self.x + radius
        center_y = self.y + radius
        
        # Тень
        shadow = self.canvas.create_oval(
            self.x + 3, self.y + 3,
            self.x + self.SIZE + 3, self.y + self.SIZE + 3,
            fill="#bdc3c7", outline=""
        )
        self.shapes.append(shadow)
        
        # Основной круг
        circle = self.canvas.create_oval(
            self.x, self.y,
            self.x + self.SIZE, self.y + self.SIZE,
            fill="#27ae60",
            outline="#229954",
            width=3,
            tags=f"block_{self.id}"
        )
        self.shapes.append(circle)
        
        # Иконка
        icon = self.canvas.create_text(
            center_x, center_y - 15,
            text="⏱️",
            font=("Segoe UI", 16),
            fill="white",
            tags=f"block_{self.id}"
        )
        self.text_ids.append(icon)
        
        # Текст
        text = self.canvas.create_text(
            center_x, center_y + 5,
            text="Задержка",
            font=("Segoe UI", 8, "bold"),
            fill="white",
            tags=f"block_{self.id}"
        )
        self.text_ids.append(text)
        
        # Значение задержки
        self.delay_text = self.canvas.create_text(
            center_x, center_y + 20,
            text=f"{self.data['delay']} сек",
            font=("Segoe UI", 7),
            fill="white",
            tags=f"block_{self.id}"
        )
        self.text_ids.append(self.delay_text)
    
    def update_delay(self, delay):
        """Обновление задержки"""
        self.data['delay'] = delay
        center_x = self.x + self.SIZE // 2
        center_y = self.y + self.SIZE // 2
        self.canvas.itemconfig(self.delay_text, text=f"{delay} сек")
    
    def contains_point(self, x, y):
        """Проверка попадания точки в круг"""
        radius = self.SIZE // 2
        center_x = self.x + radius
        center_y = self.y + radius
        distance = math.sqrt((x - center_x)**2 + (y - center_y)**2)
        return distance <= radius

class RepeatBlock(Block):
    """Блок повторений (синий круг)"""
    SIZE = 80
    
    def __init__(self, canvas, x, y, block_id, repeat_count=1):
        super().__init__(canvas, x, y, 'repeat', block_id)
        self.data = {'repeat_count': repeat_count}
        self.draw()
    
    def draw(self):
        """Отрисовка синего круга"""
        radius = self.SIZE // 2
        center_x = self.x + radius
        center_y = self.y + radius
        
        # Тень
        shadow = self.canvas.create_oval(
            self.x + 3, self.y + 3,
            self.x + self.SIZE + 3, self.y + self.SIZE + 3,
            fill="#bdc3c7", outline=""
        )
        self.shapes.append(shadow)
        
        # Основной круг
        circle = self.canvas.create_oval(
            self.x, self.y,
            self.x + self.SIZE, self.y + self.SIZE,
            fill="#3498db",
            outline="#2980b9",
            width=3,
            tags=f"block_{self.id}"
        )
        self.shapes.append(circle)
        
        # Иконка
        icon = self.canvas.create_text(
            center_x, center_y - 15,
            text="🔄",
            font=("Segoe UI", 16),
            fill="white",
            tags=f"block_{self.id}"
        )
        self.text_ids.append(icon)
        
        # Текст
        text = self.canvas.create_text(
            center_x, center_y + 5,
            text="Повторить",
            font=("Segoe UI", 8, "bold"),
            fill="white",
            tags=f"block_{self.id}"
        )
        self.text_ids.append(text)
        
        # Количество повторов
        self.repeat_text = self.canvas.create_text(
            center_x, center_y + 20,
            text=f"{self.data['repeat_count']}x",
            font=("Segoe UI", 7),
            fill="white",
            tags=f"block_{self.id}"
        )
        self.text_ids.append(self.repeat_text)
    
    def update_repeat_count(self, count):
        """Обновление количества повторов"""
        self.data['repeat_count'] = count
        center_x = self.x + self.SIZE // 2
        center_y = self.y + self.SIZE // 2
        self.canvas.itemconfig(self.repeat_text, text=f"{count}x")
    
    def contains_point(self, x, y):
        """Проверка попадания точки в круг"""
        radius = self.SIZE // 2
        center_x = self.x + radius
        center_y = self.y + radius
        distance = math.sqrt((x - center_x)**2 + (y - center_y)**2)
        return distance <= radius

class GroupBlock(Block):
    """Блок группы/подпроцесса (прямоугольник с пунктиром)"""
    WIDTH = 150
    HEIGHT = 100
    
    def __init__(self, canvas, x, y, block_id, group_type='start'):
        super().__init__(canvas, x, y, 'group', block_id)
        self.data = {'group_type': group_type, 'name': 'Группа'}
        self.draw()
    
    def draw(self):
        """Отрисовка прямоугольника группы"""
        # Цвет в зависимости от типа
        if self.data['group_type'] == 'start':
            fill_color = "#9b59b6"
            outline_color = "#8e44ad"
            icon = "▶"
            label = "Начало группы"
        else:
            fill_color = "#e67e22"
            outline_color = "#d35400"
            icon = "◀"
            label = "Конец группы"
        
        # Тень
        shadow = self.canvas.create_rectangle(
            self.x + 3, self.y + 3,
            self.x + self.WIDTH + 3, self.y + self.HEIGHT + 3,
            fill="#bdc3c7", outline=""
        )
        self.shapes.append(shadow)
        
        # Основной прямоугольник с пунктиром
        rect = self.canvas.create_rectangle(
            self.x, self.y,
            self.x + self.WIDTH, self.y + self.HEIGHT,
            fill=fill_color,
            outline=outline_color,
            width=3,
            dash=(5, 3),
            tags=f"block_{self.id}"
        )
        self.shapes.append(rect)
        
        # Иконка
        icon_text = self.canvas.create_text(
            self.x + self.WIDTH // 2, self.y + 25,
            text=icon,
            font=("Segoe UI", 20, "bold"),
            fill="white",
            tags=f"block_{self.id}"
        )
        self.text_ids.append(icon_text)
        
        # Текст
        text = self.canvas.create_text(
            self.x + self.WIDTH // 2, self.y + 55,
            text=label,
            font=("Segoe UI", 9, "bold"),
            fill="white",
            tags=f"block_{self.id}"
        )
        self.text_ids.append(text)
        
        # Название группы
        self.name_text = self.canvas.create_text(
            self.x + self.WIDTH // 2, self.y + 75,
            text=self.data['name'],
            font=("Segoe UI", 8),
            fill="white",
            tags=f"block_{self.id}"
        )
        self.text_ids.append(self.name_text)
    
    def update_name(self, name):
        """Обновление названия группы"""
        self.data['name'] = name
        self.canvas.itemconfig(self.name_text, text=name)
    
    def contains_point(self, x, y):
        """Проверка попадания точки в прямоугольник"""
        return (self.x <= x <= self.x + self.WIDTH and 
                self.y <= y <= self.y + self.HEIGHT)

class KeyboardInputBlock(Block):
    """Блок ввода текста с клавиатуры (ромб)"""
    SIZE = 90
    
    def __init__(self, canvas, x, y, block_id, text='', press_enter=True):
        super().__init__(canvas, x, y, 'keyboard_input', block_id)
        self.data = {'text': text, 'press_enter': press_enter}
        self.draw()
    
    def draw(self):
        """Отрисовка ромба"""
        # Координаты ромба
        center_x = self.x + self.SIZE // 2
        center_y = self.y + self.SIZE // 2
        
        points = [
            center_x, self.y,                    # Верхняя вершина
            self.x + self.SIZE, center_y,        # Правая вершина
            center_x, self.y + self.SIZE,        # Нижняя вершина
            self.x, center_y                     # Левая вершина
        ]
        
        # Тень
        shadow_points = [p + 3 if i % 2 == 0 else p + 3 for i, p in enumerate(points)]
        shadow = self.canvas.create_polygon(
            shadow_points,
            fill="#bdc3c7", outline=""
        )
        self.shapes.append(shadow)
        
        # Основной ромб
        diamond = self.canvas.create_polygon(
            points,
            fill="#16a085",
            outline="#138d75",
            width=3,
            tags=f"block_{self.id}"
        )
        self.shapes.append(diamond)
        
        # Иконка
        icon = self.canvas.create_text(
            center_x, center_y - 15,
            text="⌨️",
            font=("Segoe UI", 14),
            fill="white",
            tags=f"block_{self.id}"
        )
        self.text_ids.append(icon)
        
        # Текст
        text_label = self.canvas.create_text(
            center_x, center_y + 5,
            text="Ввод",
            font=("Segoe UI", 8, "bold"),
            fill="white",
            tags=f"block_{self.id}"
        )
        self.text_ids.append(text_label)
        
        # Отображение текста (сокращённое)
        display_text = self.data['text'][:8] + "..." if len(self.data['text']) > 8 else self.data['text']
        if not display_text:
            display_text = "(пусто)"
        
        self.text_display = self.canvas.create_text(
            center_x, center_y + 20,
            text=display_text,
            font=("Segoe UI", 6),
            fill="white",
            tags=f"block_{self.id}"
        )
        self.text_ids.append(self.text_display)
    
    def update_text(self, text, press_enter):
        """Обновление текста"""
        self.data['text'] = text
        self.data['press_enter'] = press_enter
        
        display_text = text[:8] + "..." if len(text) > 8 else text
        if not display_text:
            display_text = "(пусто)"
        
        self.canvas.itemconfig(self.text_display, text=display_text)
    
    def contains_point(self, x, y):
        """Проверка попадания точки в ромб"""
        center_x = self.x + self.SIZE // 2
        center_y = self.y + self.SIZE // 2
        
        # Упрощенная проверка - используем квадрат вокруг ромба
        return (self.x <= x <= self.x + self.SIZE and 
                self.y <= y <= self.y + self.SIZE)

class FlowEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("BPMN FlowClick Studio")
        self.root.geometry("1600x900")
        self.root.configure(bg="#ecf0f1")
        
        # Переменные
        self.blocks = []
        self.connections = []
        self.next_block_id = 1
        self.selected_block = None
        self.drag_data = {"x": 0, "y": 0, "block": None}
        self.connection_mode = False
        self.connection_start_block = None
        self.is_running = False
        self.config_file = "vibe_click_config.json"
        self.batch_coordinate_mode = False
        self.batch_coord_blocks = []
        self.batch_coord_index = 0
        self.current_code = "" 
        self.current_edited_block = None
        self.current_edited_connection = None  # Текущее редактируемое соединение
        
        # Настройка pyautogui
        pyautogui.FAILSAFE = True
        
        self.create_widgets()
        
        # Горячие клавиши
        keyboard.add_hotkey('ctrl', self.start_coordinate_selection, suppress=False)
        keyboard.add_hotkey('f6', self.toggle_execution)
        keyboard.add_hotkey('q', self.emergency_stop)
        
    def create_widgets(self):
        # Заголовок
        title_frame = tk.Frame(self.root, bg="#2c3e50", height=50)
        title_frame.pack(fill="x")
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(
            title_frame,
            text="🎯 FlowClick Studio",
            font=("Segoe UI", 18, "bold"),
            fg="white",
            bg="#2c3e50"
        )
        title_label.pack(pady=10)
        
        # Панель инструментов
        toolbar_frame = tk.Frame(self.root, bg="#34495e", height=120)
        toolbar_frame.pack(fill="x")
        toolbar_frame.pack_propagate(False)
        
        toolbar_content = tk.Frame(toolbar_frame, bg="#34495e")
        toolbar_content.pack(pady=10)
        
        # ПЕРВЫЙ РЯД - Блоки действий
        row1 = tk.Frame(toolbar_content, bg="#34495e")
        row1.pack(pady=2)
        
        # Кнопки добавления блоков
        tk.Label(
            row1,
            text="Добавить блок:",
            bg="#34495e",
            fg="white",
            font=("Segoe UI", 10, "bold")
        ).grid(row=0, column=0, padx=10)
        
        tk.Button(
            row1,
            text="📍 Координата",
            command=self.add_coordinate_block,
            bg="#3498db",
            fg="white",
            font=("Segoe UI", 9, "bold"),
            cursor="hand2",
            padx=10,
            pady=5,
            relief="flat"
        ).grid(row=0, column=1, padx=5)
        
        tk.Button(
            row1,
            text="👆 Левый клик",
            command=lambda: self.add_click_block('left'),
            bg="#27ae60",
            fg="white",
            font=("Segoe UI", 9, "bold"),
            cursor="hand2",
            padx=10,
            pady=5,
            relief="flat"
        ).grid(row=0, column=2, padx=5)
        
        tk.Button(
            row1,
            text="👉 Правый клик",
            command=lambda: self.add_click_block('right'),
            bg="#e74c3c",
            fg="white",
            font=("Segoe UI", 9, "bold"),
            cursor="hand2",
            padx=10,
            pady=5,
            relief="flat"
        ).grid(row=0, column=3, padx=5)
        
        tk.Button(
            row1,
            text="☝️ Средний клик",
            command=lambda: self.add_click_block('middle'),
            bg="#f39c12",
            fg="white",
            font=("Segoe UI", 9, "bold"),
            cursor="hand2",
            padx=10,
            pady=5,
            relief="flat"
        ).grid(row=0, column=4, padx=5)
        
        tk.Button(
            row1,
            text="⌨️ Ввод текста",
            command=self.add_keyboard_input_block,
            bg="#16a085",
            fg="white",
            font=("Segoe UI", 9, "bold"),
            cursor="hand2",
            padx=10,
            pady=5,
            relief="flat"
        ).grid(row=0, column=5, padx=5)
        
        # Разделитель
        ttk.Separator(row1, orient="vertical").grid(row=0, column=6, padx=15, sticky="ns")
        
        # Кнопка пакетного задания координат
        self.batch_coord_btn = tk.Button(
            row1,
            text="🎯 Задать все координаты",
            command=self.start_batch_coordinate_mode,
            bg="#9b59b6",
            fg="white",
            font=("Segoe UI", 9, "bold"),
            cursor="hand2",
            padx=10,
            pady=5,
            relief="flat"
        )
        self.batch_coord_btn.grid(row=0, column=7, padx=5)
        
        # Разделитель
        ttk.Separator(row1, orient="vertical").grid(row=0, column=8, padx=15, sticky="ns")
        
        # Кнопка соединения
        self.connect_btn = tk.Button(
            row1,
            text="🔗 Соединить",
            command=self.toggle_connection_mode,
            bg="#9b59b6",
            fg="white",
            font=("Segoe UI", 9, "bold"),
            cursor="hand2",
            padx=10,
            pady=5,
            relief="flat"
        )
        self.connect_btn.grid(row=0, column=9, padx=5)
        
        # ВТОРОЙ РЯД - Управляющие блоки и действия
        row2 = tk.Frame(toolbar_content, bg="#34495e")
        row2.pack(pady=2)
        
        tk.Label(
            row2,
            text="Управление:",
            bg="#34495e",
            fg="white",
            font=("Segoe UI", 10, "bold")
        ).grid(row=0, column=0, padx=10)
        
        tk.Button(
            row2,
            text="🔄 Повторить (раз)",
            command=self.add_repeat_block,
            bg="#3498db",
            fg="white",
            font=("Segoe UI", 9, "bold"),
            cursor="hand2",
            padx=10,
            pady=5,
            relief="flat"
        ).grid(row=0, column=1, padx=5)
        
        tk.Button(
            row2,
            text="⏱️ Задержка (сек)",
            command=self.add_delay_block,
            bg="#27ae60",
            fg="white",
            font=("Segoe UI", 9, "bold"),
            cursor="hand2",
            padx=10,
            pady=5,
            relief="flat"
        ).grid(row=0, column=2, padx=5)
        
        tk.Button(
            row2,
            text="▶ Начало группы",
            command=lambda: self.add_group_block('start'),
            bg="#9b59b6",
            fg="white",
            font=("Segoe UI", 9, "bold"),
            cursor="hand2",
            padx=10,
            pady=5,
            relief="flat"
        ).grid(row=0, column=3, padx=5)
        
        tk.Button(
            row2,
            text="◀ Конец группы",
            command=lambda: self.add_group_block('end'),
            bg="#e67e22",
            fg="white",
            font=("Segoe UI", 9, "bold"),
            cursor="hand2",
            padx=10,
            pady=5,
            relief="flat"
        ).grid(row=0, column=4, padx=5)
        
        # Разделитель
        ttk.Separator(row2, orient="vertical").grid(row=0, column=5, padx=15, sticky="ns")
        
        # Кнопки управления
        self.run_btn = tk.Button(
            row2,
            text="▶ Запустить",
            command=self.toggle_execution,
            bg="#27ae60",
            fg="white",
            font=("Segoe UI", 9, "bold"),
            cursor="hand2",
            padx=15,
            pady=5,
            relief="flat"
        )
        self.run_btn.grid(row=0, column=6, padx=5)
        
        tk.Button(
            row2,
            text="🗑️ Очистить",
            command=self.clear_canvas,
            bg="#95a5a6",
            fg="white",
            font=("Segoe UI", 9, "bold"),
            cursor="hand2",
            padx=10,
            pady=5,
            relief="flat"
        ).grid(row=0, column=7, padx=5)
        
        tk.Button(
            row2,
            text="💾 Сохранить",
            command=self.save_flow,
            bg="#3498db",
            fg="white",
            font=("Segoe UI", 9, "bold"),
            cursor="hand2",
            padx=10,
            pady=5,
            relief="flat"
        ).grid(row=0, column=8, padx=5)
        
        tk.Button(
            row2,
            text="📂 Загрузить",
            command=self.load_flow,
            bg="#3498db",
            fg="white",
            font=("Segoe UI", 9, "bold"),
            cursor="hand2",
            padx=10,
            pady=5,
            relief="flat"
        ).grid(row=0, column=9, padx=5)
        
        tk.Button(
            row2,
            text="🐍 Экспорт в Python",
            command=self.export_to_python,
            bg="#f39c12",
            fg="white",
            font=("Segoe UI", 9, "bold"),
            cursor="hand2",
            padx=10,
            pady=5,
            relief="flat"
        ).grid(row=0, column=10, padx=5)
        
        # Основной контейнер для Canvas и правой панели
        main_container = tk.Frame(self.root, bg="#2c3e50")
        main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Canvas слева
        canvas_frame = tk.Frame(main_container, bg="#ffffff", relief="solid", bd=2)
        canvas_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        self.canvas = Canvas(
            canvas_frame,
            bg="#ffffff",
            highlightthickness=0
        )
        self.canvas.pack(fill="both", expand=True)
        
        # Правая панель для кода
        self.code_panel_frame = tk.Frame(main_container, bg="#2c3e50", width=400, relief="solid", bd=2)
        self.code_panel_frame.pack(side="right", fill="both", padx=(5, 0))
        self.code_panel_frame.pack_propagate(False)
        
        # Заголовок панели кода
        code_header = tk.Frame(self.code_panel_frame, bg="#34495e", height=40)
        code_header.pack(fill="x")
        code_header.pack_propagate(False)
        
        tk.Label(
            code_header,
            text="🐍 Python код блока",
            font=("Segoe UI", 10, "bold"),
            fg="white",
            bg="#34495e"
        ).pack(pady=10)
        
        # Текстовое поле для кода
        code_text_frame = tk.Frame(self.code_panel_frame, bg="#1e1e1e")
        code_text_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Скроллбар
        code_scrollbar = tk.Scrollbar(code_text_frame)
        code_scrollbar.pack(side="right", fill="y")
        
        # Текстовое поле с подсветкой синтаксиса (редактируемое!)
        self.code_text = tk.Text(
            code_text_frame,
            font=("Consolas", 9),
            bg="#1e1e1e",
            fg="#d4d4d4",
            insertbackground="white",
            selectbackground="#264f78",
            wrap="word",
            yscrollcommand=code_scrollbar.set,
            padx=10,
            pady=10
        )
        self.code_text.pack(side="left", fill="both", expand=True)
        code_scrollbar.config(command=self.code_text.yview)
        
        # Начальное сообщение
        self.code_text.insert("1.0", "# Выберите блок, чтобы увидеть его Python код\n# Select a block to see its Python code")
        
        # Кнопки управления кодом
        button_frame = tk.Frame(self.code_panel_frame, bg="#34495e", height=80)
        button_frame.pack(fill="x")
        button_frame.pack_propagate(False)
        
        tk.Button(
            button_frame,
            text="✅ Применить изменения",
            command=self.apply_code_changes,
            bg="#e67e22",
            fg="white",
            font=("Segoe UI", 9, "bold"),
            cursor="hand2",
            padx=10,
            pady=5,
            relief="flat"
        ).pack(pady=5)
        
        # Кнопка копирования кода
        copy_btn_frame = tk.Frame(self.code_panel_frame, bg="#34495e", height=40)
        copy_btn_frame.pack(fill="x")
        copy_btn_frame.pack_propagate(False)
        
        tk.Button(
            copy_btn_frame,
            text="📋 Копировать код",
            command=self.copy_code_to_clipboard,
            bg="#27ae60",
            fg="white",
            font=("Segoe UI", 9, "bold"),
            cursor="hand2",
            padx=10,
            pady=5,
            relief="flat"
        ).pack(pady=5)
        
        # Сетка на canvas
        self.draw_grid()
        
        # Статус бар
        status_frame = tk.Frame(self.root, bg="#34495e", height=35)
        status_frame.pack(fill="x")
        status_frame.pack_propagate(False)
        
        self.status_label = tk.Label(
            status_frame,
            text="⚫ Готов | Ctrl - выбор координат | Двойной клик на квадрат - захват координат | F6 - запуск | Q - остановка",
            font=("Segoe UI", 9),
            fg="white",
            bg="#34495e"
        )
        self.status_label.pack(pady=8)
        
        # Привязки событий
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<Double-Button-1>", self.on_canvas_double_click)
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_release)
        self.canvas.bind("<Button-3>", self.on_right_click)  # Правый клик для удаления
        
        # Загрузка сохраненного потока
        self.load_flow_silent()
    
    def draw_grid(self):
        """Рисование сетки на canvas"""
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        
        if width <= 1:
            width = 1200
        if height <= 1:
            height = 700
        
        # Вертикальные линии
        for i in range(0, width, 40):
            self.canvas.create_line(i, 0, i, height, fill="#ecf0f1", tags="grid")
        
        # Горизонтальные линии
        for i in range(0, height, 40):
            self.canvas.create_line(0, i, width, i, fill="#ecf0f1", tags="grid")
        
        self.canvas.tag_lower("grid")
    
    def add_coordinate_block(self):
        """Добавление блока координат"""
        block = CoordinateBlock(self.canvas, 100 + len(self.blocks) * 20, 100 + len(self.blocks) * 20, self.next_block_id)
        self.blocks.append(block)
        self.next_block_id += 1
        self.status_label.config(text=f"✅ Добавлен блок координат #{block.id}")
    
    def add_click_block(self, click_type):
        """Добавление блока клика"""
        block = ClickBlock(self.canvas, 300 + len(self.blocks) * 20, 100 + len(self.blocks) * 20, self.next_block_id, click_type)
        self.blocks.append(block)
        self.next_block_id += 1
        labels = {'left': 'левый', 'right': 'правый', 'middle': 'средний'}
        self.status_label.config(text=f"✅ Добавлен блок {labels[click_type]} клик #{block.id}")
    
    def add_repeat_block(self):
        """Добавление блока повторений"""
        # Диалог для ввода количества повторов
        dialog = tk.Toplevel(self.root)
        dialog.title("Количество повторов")
        dialog.geometry("300x150")
        dialog.configure(bg="#ecf0f1")
        dialog.transient(self.root)
        dialog.grab_set()
        
        tk.Label(
            dialog,
            text="Сколько раз повторить?",
            font=("Segoe UI", 11, "bold"),
            bg="#ecf0f1"
        ).pack(pady=15)
        
        repeat_var = tk.IntVar(value=5)
        spinbox = tk.Spinbox(
            dialog,
            from_=1,
            to=1000,
            textvariable=repeat_var,
            width=10,
            font=("Segoe UI", 11)
        )
        spinbox.pack(pady=10)
        spinbox.focus()
        
        def on_ok():
            count = repeat_var.get()
            block = RepeatBlock(self.canvas, 100 + len(self.blocks) * 20, 200 + len(self.blocks) * 20, self.next_block_id, count)
            self.blocks.append(block)
            self.next_block_id += 1
            self.status_label.config(text=f"✅ Добавлен блок повторений ({count}x) #{block.id}")
            dialog.destroy()
        
        tk.Button(
            dialog,
            text="✅ Добавить",
            command=on_ok,
            bg="#27ae60",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            cursor="hand2",
            padx=20,
            pady=5
        ).pack(pady=10)
    
    def add_delay_block(self):
        """Добавление блока задержки"""
        # Диалог для ввода времени задержки
        dialog = tk.Toplevel(self.root)
        dialog.title("Задержка")
        dialog.geometry("300x150")
        dialog.configure(bg="#ecf0f1")
        dialog.transient(self.root)
        dialog.grab_set()
        
        tk.Label(
            dialog,
            text="Задержка в секундах:",
            font=("Segoe UI", 11, "bold"),
            bg="#ecf0f1"
        ).pack(pady=15)
        
        delay_var = tk.DoubleVar(value=1.0)
        spinbox = tk.Spinbox(
            dialog,
            from_=0.1,
            to=60.0,
            increment=0.1,
            textvariable=delay_var,
            width=10,
            font=("Segoe UI", 11)
        )
        spinbox.pack(pady=10)
        spinbox.focus()
        
        def on_ok():
            delay = delay_var.get()
            block = DelayBlock(self.canvas, 300 + len(self.blocks) * 20, 200 + len(self.blocks) * 20, self.next_block_id, delay)
            self.blocks.append(block)
            self.next_block_id += 1
            self.status_label.config(text=f"✅ Добавлен блок задержки ({delay} сек) #{block.id}")
            dialog.destroy()
        
        tk.Button(
            dialog,
            text="✅ Добавить",
            command=on_ok,
            bg="#27ae60",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            cursor="hand2",
            padx=20,
            pady=5
        ).pack(pady=10)
    
    def add_group_block(self, group_type):
        """Добавление блока группы"""
        block = GroupBlock(self.canvas, 100 + len(self.blocks) * 20, 150 + len(self.blocks) * 20, self.next_block_id, group_type)
        self.blocks.append(block)
        self.next_block_id += 1
        label = "начало" if group_type == 'start' else "конец"
        self.status_label.config(text=f"✅ Добавлен блок {label} группы #{block.id}")
    
    def add_keyboard_input_block(self):
        """Добавление блока ввода текста"""
        # Диалог для ввода текста
        dialog = tk.Toplevel(self.root)
        dialog.title("Ввод текста с клавиатуры")
        dialog.geometry("400x200")
        dialog.configure(bg="#ecf0f1")
        dialog.transient(self.root)
        dialog.grab_set()
        
        tk.Label(
            dialog,
            text="Текст для ввода:",
            font=("Segoe UI", 11, "bold"),
            bg="#ecf0f1"
        ).pack(pady=10)
        
        text_var = tk.StringVar(value="")
        entry = tk.Entry(
            dialog,
            textvariable=text_var,
            width=35,
            font=("Segoe UI", 11)
        )
        entry.pack(pady=10)
        entry.focus()
        
        # Checkbox для нажатия Enter
        enter_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            dialog,
            text="Нажать Enter после ввода",
            variable=enter_var,
            font=("Segoe UI", 10),
            bg="#ecf0f1"
        ).pack(pady=10)
        
        def on_ok():
            text = text_var.get()
            press_enter = enter_var.get()
            block = KeyboardInputBlock(self.canvas, 200 + len(self.blocks) * 20, 100 + len(self.blocks) * 20, self.next_block_id, text, press_enter)
            self.blocks.append(block)
            self.next_block_id += 1
            self.status_label.config(text=f"✅ Добавлен блок ввода текста #{block.id}")
            dialog.destroy()
        
        tk.Button(
            dialog,
            text="✅ Добавить",
            command=on_ok,
            bg="#27ae60",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            cursor="hand2",
            padx=20,
            pady=5
        ).pack(pady=10)
    
    def start_coordinate_selection(self):
        """Захват координат по Ctrl - одним нажатием"""
        # Если в режиме пакетного задания координат
        if self.batch_coordinate_mode:
            self.capture_next_batch_coordinate()
            return
        
        # Проверяем есть ли выбранный блок координат
        if self.selected_block and isinstance(self.selected_block, CoordinateBlock):
            # Сразу получаем текущие координаты курсора
            x, y = pyautogui.position()
            self.selected_block.update_coordinates(x, y)
            self.status_label.config(text=f"✅ Координаты установлены: X={x}, Y={y} для блока #{self.selected_block.id}")
        else:
            self.status_label.config(text="⚠️ Сначала выберите блок координат (кликните на синий квадрат 📍)")
    
    def on_canvas_double_click(self, event):
        """Двойной клик - быстрый захват координат или редактирование параметров"""
        # Сначала проверяем клик по соединению (стрелке)
        clicked_connection = self.get_connection_at_position(event.x, event.y)
        if clicked_connection:
            # Редактирование задержки на соединении
            dialog = tk.Toplevel(self.root)
            dialog.title("Задержка на переходе")
            dialog.geometry("300x150")
            dialog.configure(bg="#ecf0f1")
            dialog.transient(self.root)
            dialog.grab_set()
            
            tk.Label(
                dialog,
                text="Задержка (секунды):",
                font=("Segoe UI", 11, "bold"),
                bg="#ecf0f1"
            ).pack(pady=15)
            
            delay_var = tk.DoubleVar(value=clicked_connection.delay)
            spinbox = tk.Spinbox(
                dialog,
                from_=0.0,
                to=60.0,
                increment=0.1,
                textvariable=delay_var,
                width=10,
                font=("Segoe UI", 11)
            )
            spinbox.pack(pady=10)
            spinbox.focus()
            
            def on_ok():
                clicked_connection.delay = delay_var.get()
                clicked_connection.update()
                self.status_label.config(text=f"✅ Задержка установлена: {delay_var.get()} сек")
                dialog.destroy()
            
            tk.Button(
                dialog,
                text="✅ Сохранить",
                command=on_ok,
                bg="#27ae60",
                fg="white",
                font=("Segoe UI", 10, "bold"),
                cursor="hand2",
                padx=20,
                pady=5
            ).pack(pady=10)
            return
        
        # Проверяем клик по блокам
        clicked_block = self.get_block_at_position(event.x, event.y)
        
        if clicked_block and isinstance(clicked_block, CoordinateBlock):
            # Диалог с выбором: автозахват или ручной ввод
            dialog = tk.Toplevel(self.root)
            dialog.title(f"Редактировать координаты #{clicked_block.id}")
            dialog.geometry("400x250")
            dialog.configure(bg="#ecf0f1")
            dialog.transient(self.root)
            dialog.grab_set()
            
            tk.Label(
                dialog,
                text="Способ установки координат:",
                font=("Segoe UI", 12, "bold"),
                bg="#ecf0f1"
            ).pack(pady=15)
            
            # Кнопка автозахвата
            def auto_capture():
                x, y = pyautogui.position()
                clicked_block.update_coordinates(x, y)
                self.selected_block = clicked_block
                self.status_label.config(text=f"✅ Автозахват! Координаты: X={x}, Y={y} для блока #{clicked_block.id}")
                # Обновляем панель кода
                self.update_code_panel(clicked_block)
                dialog.destroy()
            
            tk.Button(
                dialog,
                text="📍 Автозахват (текущая позиция мыши)",
                command=auto_capture,
                bg="#3498db",
                fg="white",
                font=("Segoe UI", 10, "bold"),
                cursor="hand2",
                padx=20,
                pady=10
            ).pack(pady=5)
            
            # Разделитель
            tk.Label(
                dialog,
                text="или введите вручную:",
                font=("Segoe UI", 9),
                bg="#ecf0f1",
                fg="#7f8c8d"
            ).pack(pady=5)
            
            # Фрейм для ручного ввода
            manual_frame = tk.Frame(dialog, bg="#ecf0f1")
            manual_frame.pack(pady=10)
            
            current_x = clicked_block.data.get('x', 0)
            current_y = clicked_block.data.get('y', 0)
            
            tk.Label(
                manual_frame,
                text="X:",
                font=("Segoe UI", 10, "bold"),
                bg="#ecf0f1"
            ).grid(row=0, column=0, padx=5)
            
            x_var = tk.IntVar(value=current_x if current_x is not None else 0)
            x_entry = tk.Spinbox(
                manual_frame,
                from_=0,
                to=5000,
                textvariable=x_var,
                width=10,
                font=("Segoe UI", 10)
            )
            x_entry.grid(row=0, column=1, padx=5)
            
            tk.Label(
                manual_frame,
                text="Y:",
                font=("Segoe UI", 10, "bold"),
                bg="#ecf0f1"
            ).grid(row=0, column=2, padx=5)
            
            y_var = tk.IntVar(value=current_y if current_y is not None else 0)
            y_entry = tk.Spinbox(
                manual_frame,
                from_=0,
                to=5000,
                textvariable=y_var,
                width=10,
                font=("Segoe UI", 10)
            )
            y_entry.grid(row=0, column=3, padx=5)
            
            def manual_ok():
                clicked_block.update_coordinates(x_var.get(), y_var.get())
                self.selected_block = clicked_block
                self.status_label.config(text=f"✅ Координаты установлены: X={x_var.get()}, Y={y_var.get()} для блока #{clicked_block.id}")
                # Обновляем панель кода
                self.update_code_panel(clicked_block)
                dialog.destroy()
            
            tk.Button(
                dialog,
                text="✅ Сохранить",
                command=manual_ok,
                bg="#27ae60",
                fg="white",
                font=("Segoe UI", 10, "bold"),
                cursor="hand2",
                padx=20,
                pady=5
            ).pack(pady=10)
        
        elif clicked_block and isinstance(clicked_block, RepeatBlock):
            # Редактирование количества повторов
            dialog = tk.Toplevel(self.root)
            dialog.title(f"Редактировать блок #{clicked_block.id}")
            dialog.geometry("300x150")
            dialog.configure(bg="#ecf0f1")
            dialog.transient(self.root)
            dialog.grab_set()
            
            tk.Label(
                dialog,
                text="Сколько раз повторить?",
                font=("Segoe UI", 11, "bold"),
                bg="#ecf0f1"
            ).pack(pady=15)
            
            repeat_var = tk.IntVar(value=clicked_block.data['repeat_count'])
            spinbox = tk.Spinbox(
                dialog,
                from_=1,
                to=1000,
                textvariable=repeat_var,
                width=10,
                font=("Segoe UI", 11)
            )
            spinbox.pack(pady=10)
            spinbox.select_range(0, tk.END)
            spinbox.focus()
            
            def on_ok():
                clicked_block.update_repeat_count(repeat_var.get())
                self.status_label.config(text=f"✅ Блок #{clicked_block.id} обновлен: {repeat_var.get()} повторов")
                # Обновляем панель кода
                self.update_code_panel(clicked_block)
                dialog.destroy()
            
            tk.Button(
                dialog,
                text="✅ Сохранить",
                command=on_ok,
                bg="#27ae60",
                fg="white",
                font=("Segoe UI", 10, "bold"),
                cursor="hand2",
                padx=20,
                pady=5
            ).pack(pady=10)
        
        elif clicked_block and isinstance(clicked_block, DelayBlock):
            # Редактирование задержки
            dialog = tk.Toplevel(self.root)
            dialog.title(f"Редактировать блок #{clicked_block.id}")
            dialog.geometry("300x150")
            dialog.configure(bg="#ecf0f1")
            dialog.transient(self.root)
            dialog.grab_set()
            
            tk.Label(
                dialog,
                text="Задержка в секундах:",
                font=("Segoe UI", 11, "bold"),
                bg="#ecf0f1"
            ).pack(pady=15)
            
            delay_var = tk.DoubleVar(value=clicked_block.data['delay'])
            spinbox = tk.Spinbox(
                dialog,
                from_=0.1,
                to=60.0,
                increment=0.1,
                textvariable=delay_var,
                width=10,
                font=("Segoe UI", 11)
            )
            spinbox.pack(pady=10)
            spinbox.select_range(0, tk.END)
            spinbox.focus()
            
            def on_ok():
                clicked_block.update_delay(delay_var.get())
                self.status_label.config(text=f"✅ Блок #{clicked_block.id} обновлен: {delay_var.get()} сек")
                # Обновляем панель кода
                self.update_code_panel(clicked_block)
                dialog.destroy()
            
            tk.Button(
                dialog,
                text="✅ Сохранить",
                command=on_ok,
                bg="#27ae60",
                fg="white",
                font=("Segoe UI", 10, "bold"),
                cursor="hand2",
                padx=20,
                pady=5
            ).pack(pady=10)
        
        elif clicked_block and isinstance(clicked_block, GroupBlock):
            # Редактирование названия группы
            dialog = tk.Toplevel(self.root)
            dialog.title(f"Редактировать группу #{clicked_block.id}")
            dialog.geometry("350x150")
            dialog.configure(bg="#ecf0f1")
            dialog.transient(self.root)
            dialog.grab_set()
            
            tk.Label(
                dialog,
                text="Название группы:",
                font=("Segoe UI", 11, "bold"),
                bg="#ecf0f1"
            ).pack(pady=15)
            
            name_var = tk.StringVar(value=clicked_block.data['name'])
            entry = tk.Entry(
                dialog,
                textvariable=name_var,
                width=25,
                font=("Segoe UI", 11)
            )
            entry.pack(pady=10)
            entry.select_range(0, tk.END)
            entry.focus()
            
            def on_ok():
                clicked_block.update_name(name_var.get())
                self.status_label.config(text=f"✅ Группа #{clicked_block.id} переименована: {name_var.get()}")
                # Обновляем панель кода
                self.update_code_panel(clicked_block)
                dialog.destroy()
            
            tk.Button(
                dialog,
                text="✅ Сохранить",
                command=on_ok,
                bg="#27ae60",
                fg="white",
                font=("Segoe UI", 10, "bold"),
                cursor="hand2",
                padx=20,
                pady=5
            ).pack(pady=10)
        
        elif clicked_block and isinstance(clicked_block, KeyboardInputBlock):
            # Редактирование текста для ввода
            dialog = tk.Toplevel(self.root)
            dialog.title(f"Редактировать блок #{clicked_block.id}")
            dialog.geometry("500x300")
            dialog.configure(bg="#ecf0f1")
            dialog.transient(self.root)
            dialog.grab_set()
            
            tk.Label(
                dialog,
                text="Текст для ввода:",
                font=("Segoe UI", 11, "bold"),
                bg="#ecf0f1"
            ).pack(pady=10)
            
            # Используем Text виджет для многострочного ввода
            text_frame = tk.Frame(dialog, bg="#ecf0f1")
            text_frame.pack(pady=5, padx=20, fill="both", expand=True)
            
            text_scrollbar = tk.Scrollbar(text_frame)
            text_scrollbar.pack(side="right", fill="y")
            
            text_widget = tk.Text(
                text_frame,
                width=50,
                height=8,
                font=("Segoe UI", 10),
                wrap="word",
                yscrollcommand=text_scrollbar.set
            )
            text_widget.pack(side="left", fill="both", expand=True)
            text_scrollbar.config(command=text_widget.yview)
            
            # Вставляем текущий текст
            text_widget.insert("1.0", clicked_block.data['text'])
            text_widget.focus()
            
            # Checkbox для нажатия Enter
            enter_var = tk.BooleanVar(value=clicked_block.data['press_enter'])
            tk.Checkbutton(
                dialog,
                text="✅ Нажать Enter после ввода",
                variable=enter_var,
                font=("Segoe UI", 10),
                bg="#ecf0f1"
            ).pack(pady=10)
            
            def on_ok():
                new_text = text_widget.get("1.0", "end-1c")  # Получаем весь текст
                clicked_block.update_text(new_text, enter_var.get())
                self.status_label.config(text=f"✅ Блок #{clicked_block.id} обновлен")
                # Обновляем панель кода
                self.update_code_panel(clicked_block)
                dialog.destroy()
            
            tk.Button(
                dialog,
                text="✅ Сохранить",
                command=on_ok,
                bg="#27ae60",
                fg="white",
                font=("Segoe UI", 10, "bold"),
                cursor="hand2",
                padx=20,
                pady=5
            ).pack(pady=10)
    
    def start_batch_coordinate_mode(self):
        """Запуск режима пакетного задания координат"""
        # Если уже в режиме - отменяем
        if self.batch_coordinate_mode:
            self.batch_coordinate_mode = False
            self.batch_coord_btn.config(bg="#9b59b6", text="🎯 Задать все координаты")
            self.status_label.config(text="❌ Режим пакетного задания отменен")
            self.batch_coord_blocks = []
            self.batch_coord_index = 0
            return
        
        # Находим все блоки координат без заданных координат
        coord_blocks = [b for b in self.blocks if isinstance(b, CoordinateBlock)]
        
        if not coord_blocks:
            messagebox.showinfo("Информация", "Нет блоков координат! Добавьте блоки 📍 Координата")
            return
        
        # Фильтруем только блоки без координат или берем все
        empty_blocks = [b for b in coord_blocks if b.data['x'] is None or b.data['y'] is None]
        
        if not empty_blocks:
            # Если все заданы, предлагаем переназначить все
            result = messagebox.askyesno(
                "Все координаты заданы",
                f"Все {len(coord_blocks)} блоков уже имеют координаты.\n\nПереназначить все координаты заново?"
            )
            if result:
                self.batch_coord_blocks = coord_blocks
            else:
                return
        else:
            self.batch_coord_blocks = empty_blocks
        
        self.batch_coord_index = 0
        self.batch_coordinate_mode = True
        
        # Меняем внешний вид кнопки
        self.batch_coord_btn.config(bg="#e74c3c", text="❌ Отменить режим")
        
        # Выделяем первый блок
        self.selected_block = self.batch_coord_blocks[0]
        self.highlight_current_batch_block()
        
        messagebox.showinfo(
            "Режим пакетного задания",
            f"📍 Будет задано {len(self.batch_coord_blocks)} координат\n\n"
            f"Для каждого блока:\n"
            f"1. Наведите курсор куда нужно\n"
            f"2. Нажмите Ctrl\n\n"
            f"Начинаем с блока #{self.batch_coord_blocks[0].id}"
        )
    
    def highlight_current_batch_block(self):
        """Подсветка текущего блока в пакетном режиме"""
        if self.batch_coord_index < len(self.batch_coord_blocks):
            current_block = self.batch_coord_blocks[self.batch_coord_index]
        self.status_label.config(
                text=f"🎯 Режим пакетного задания | Блок {self.batch_coord_index + 1}/{len(self.batch_coord_blocks)} (#{current_block.id}) | Наведите курсор и нажмите Ctrl"
            )
    
    def capture_next_batch_coordinate(self):
        """Захват координат для следующего блока в пакетном режиме"""
        if self.batch_coord_index < len(self.batch_coord_blocks):
            current_block = self.batch_coord_blocks[self.batch_coord_index]
            x, y = pyautogui.position()
            current_block.update_coordinates(x, y)
            
            self.batch_coord_index += 1
            
            # Проверяем, есть ли еще блоки
            if self.batch_coord_index < len(self.batch_coord_blocks):
                self.selected_block = self.batch_coord_blocks[self.batch_coord_index]
                self.highlight_current_batch_block()
            else:
                # Закончили
                self.finish_batch_coordinate_mode()
    
    def finish_batch_coordinate_mode(self):
        """Завершение режима пакетного задания"""
        self.batch_coordinate_mode = False
        self.batch_coord_btn.config(bg="#9b59b6", text="🎯 Задать все координаты")
        messagebox.showinfo(
            "Готово!",
            f"✅ Все координаты заданы!\n\n"
            f"Задано блоков: {len(self.batch_coord_blocks)}"
        )
        self.status_label.config(text="✅ Пакетное задание координат завершено!")
        self.batch_coord_blocks = []
        self.batch_coord_index = 0
    
    def toggle_connection_mode(self):
        """Переключение режима соединения"""
        self.connection_mode = not self.connection_mode
        if self.connection_mode:
            self.connect_btn.config(bg="#e74c3c", text="🔗 Режим соединения")
            self.status_label.config(text="🔗 Выберите первый блок, затем второй для соединения")
            self.connection_start_block = None
        else:
            self.connect_btn.config(bg="#9b59b6", text="🔗 Соединить")
            self.status_label.config(text="⚫ Режим соединения выключен")
            self.connection_start_block = None
    
    def on_canvas_click(self, event):
        """Клик на canvas"""
        # Проверяем режим соединения
        if self.connection_mode:
            clicked_block = self.get_block_at_position(event.x, event.y)
            if clicked_block:
                if self.connection_start_block is None:
                    self.connection_start_block = clicked_block
                    self.status_label.config(text=f"🔗 Выбран блок #{clicked_block.id}, выберите второй блок")
                else:
                    # Создаем соединение
                    if self.connection_start_block != clicked_block:
                        connection = Connection(self.canvas, self.connection_start_block, clicked_block)
                        self.connections.append(connection)
                        self.connection_start_block.connections_out.append(clicked_block)
                        clicked_block.connections_in.append(self.connection_start_block)
                        self.status_label.config(text=f"✅ Соединение создано: #{self.connection_start_block.id} → #{clicked_block.id}")
                    self.connection_start_block = None
                    self.connection_mode = False
                    self.connect_btn.config(bg="#9b59b6", text="🔗 Соединить")
            return
        

        clicked_connection = self.get_connection_at_position(event.x, event.y)
        if clicked_connection:
            self.update_code_panel_connection(clicked_connection)
            self.status_label.config(text=f"🔗 Выбрано соединение: #{clicked_connection.from_block.id} → #{clicked_connection.to_block.id}")
            return
        
        # Обычный режим - выбор блока
        clicked_block = self.get_block_at_position(event.x, event.y)
        if clicked_block:
            self.selected_block = clicked_block
            self.drag_data["x"] = event.x
            self.drag_data["y"] = event.y
            self.drag_data["block"] = clicked_block
            
            block_type = "Координата" if isinstance(clicked_block, CoordinateBlock) else "Клик"
            self.status_label.config(text=f"📌 Выбран блок #{clicked_block.id} ({block_type})")
            
            self.update_code_panel(clicked_block)
        else:
            self.selected_block = None
    
    def on_canvas_drag(self, event):
        """Перетаскивание блока"""
        if self.drag_data["block"]:
            dx = event.x - self.drag_data["x"]
            dy = event.y - self.drag_data["y"]
            self.drag_data["block"].move(dx, dy)
            self.drag_data["x"] = event.x
            self.drag_data["y"] = event.y
            
            # Обновляем соединения
            self.update_connections()
    
    def on_canvas_release(self, event):
        """Отпускание кнопки мыши"""
        self.drag_data["block"] = None
    
    def on_right_click(self, event):
        """Правый клик - удаление блока"""
        clicked_block = self.get_block_at_position(event.x, event.y)
        if clicked_block:
            # Удаляем все соединения связанные с блоком
            connections_to_remove = []
            for conn in self.connections:
                if conn.from_block == clicked_block or conn.to_block == clicked_block:
                    conn.delete()
                    connections_to_remove.append(conn)
            
            for conn in connections_to_remove:
                self.connections.remove(conn)
            
            # Удаляем блок
            clicked_block.delete()
            self.blocks.remove(clicked_block)
            self.status_label.config(text=f"🗑️ Блок #{clicked_block.id} удален")
            
            if self.selected_block == clicked_block:
                self.selected_block = None
    
    def get_block_at_position(self, x, y):
        """Получение блока в позиции"""
        for block in reversed(self.blocks):  # Проверяем с конца (верхние блоки)
            if block.contains_point(x, y):
                return block
        return None
    
    def get_connection_at_position(self, x, y):
        """Получение соединения в позиции"""
        for conn in self.connections:
            if conn.contains_point(x, y):
                return conn
        return None
    
    def update_connections(self):
        """Обновление всех соединений"""
        for conn in self.connections:
            conn.update()
    
    def clear_canvas(self):
        """Очистка canvas"""
        if not self.blocks:
            messagebox.showinfo("Информация", "Canvas уже пуст!")
            return
        
        result = messagebox.askyesno(
            "Подтверждение",
            f"Удалить все {len(self.blocks)} блоков и {len(self.connections)} соединений?"
        )
        
        if result:
            for block in self.blocks:
                block.delete()
            for conn in self.connections:
                conn.delete()
            self.blocks.clear()
            self.connections.clear()
            self.selected_block = None
            self.status_label.config(text="🗑️ Canvas очищен")
    
    def toggle_execution(self):
        """Переключение выполнения"""
        if not self.is_running:
            self.start_execution()
        else:
            self.stop_execution()
    
    def start_execution(self):
        """Запуск выполнения потока"""
        if not self.blocks:
            messagebox.showwarning("Предупреждение", "Нет блоков для выполнения!")
            return
        
        # Находим начальные блоки (без входящих соединений)
        start_blocks = [block for block in self.blocks if not block.connections_in]
        
        if not start_blocks:
            messagebox.showwarning("Предупреждение", "Нет начальных блоков! Добавьте блок без входящих соединений.")
            return
        
        self.is_running = True
        self.run_btn.config(text="⏸ Остановить", bg="#e74c3c")
        self.status_label.config(text="🟢 Выполнение запущено...")
        
        # Запускаем в отдельном потоке
        thread = threading.Thread(target=self.execute_flow, args=(start_blocks,), daemon=True)
        thread.start()
    
    def stop_execution(self):
        """Остановка выполнения"""
        self.is_running = False
        self.run_btn.config(text="▶ Запустить", bg="#27ae60")
        self.status_label.config(text="⚫ Выполнение остановлено")
    
    def emergency_stop(self):
        """Экстренная остановка"""
        if self.is_running:
            self.stop_execution()
            messagebox.showinfo("Остановка", "Выполнение экстренно остановлено!")
    
    def execute_flow(self, start_blocks):
        """Выполнение потока"""
        try:
            def get_connection_delay(from_block, to_block):
                """Получить задержку на соединении между блоками"""
                for conn in self.connections:
                    if conn.from_block == from_block and conn.to_block == to_block:
                        return conn.delay
                return 0.0
            
            def execute_block(block, context=None):
                if not self.is_running:
                    return
                
                if context is None:
                    context = {'coordinates': None, 'repeat_count': 1}
                
                # Выполняем действие в зависимости от типа блока
                if isinstance(block, CoordinateBlock):
                    # Блок координат - сохраняем координаты в контекст
                    x, y = block.data.get('x'), block.data.get('y')
                    if x is None or y is None:
                        self.root.after(0, lambda b=block: messagebox.showerror(
                "Ошибка",
                            f"Блок #{b.id}: координаты не заданы!"
                        ))
                        self.stop_execution()
                        return
                    
                    context['coordinates'] = (x, y)
                    self.root.after(0, lambda b=block: self.status_label.config(
                        text=f"📍 Блок #{b.id}: координаты установлены ({x}, {y})"
                    ))
                    
                    # Выполняем следующие блоки с задержкой на соединении
                    for next_block in block.connections_out:
                        if not self.is_running:
                            break
                        # Применяем задержку из соединения
                        delay = get_connection_delay(block, next_block)
                        if delay > 0:
                            time.sleep(delay)
                        execute_block(next_block, context.copy())
                
                elif isinstance(block, ClickBlock):
                    # Блок клика - выполняем клик по координатам из контекста
                    coords = context.get('coordinates')
                    if coords:
                        x, y = coords
                        click_type = block.data['click_type']
                        pyautogui.click(x, y, button=click_type)
                        self.root.after(0, lambda b=block: self.status_label.config(
                            text=f"🖱️ Блок #{b.id}: {click_type} клик в ({x}, {y})"
                        ))
                    else:
                        # Ищем координаты из входящих блоков
                        for in_block in block.connections_in:
                            if isinstance(in_block, CoordinateBlock):
                                x, y = in_block.data.get('x'), in_block.data.get('y')
                                if x is not None and y is not None:
                                    click_type = block.data['click_type']
                                    pyautogui.click(x, y, button=click_type)
                                    context['coordinates'] = (x, y)
                                    self.root.after(0, lambda b=block: self.status_label.config(
                                        text=f"🖱️ Блок #{b.id}: {click_type} клик в ({x}, {y})"
                                    ))
                                    break
                    
                    time.sleep(0.3)
                    
                    # Выполняем следующие блоки
                    for next_block in block.connections_out:
                        if not self.is_running:
                            break
                        execute_block(next_block, context.copy())
                
                elif isinstance(block, DelayBlock):
                    # Блок задержки - ждем указанное время
                    delay = block.data['delay']
                    self.root.after(0, lambda b=block, d=delay: self.status_label.config(
                        text=f"⏱️ Блок #{b.id}: задержка {d} сек..."
                    ))
                    time.sleep(delay)
                    
                    # Выполняем следующие блоки
                    for next_block in block.connections_out:
                        if not self.is_running:
                            break
                        execute_block(next_block, context.copy())
                
                elif isinstance(block, RepeatBlock):
                    # Блок повторений - повторяем следующие блоки N раз
                    repeat_count = block.data['repeat_count']
                    self.root.after(0, lambda b=block, r=repeat_count: self.status_label.config(
                        text=f"🔄 Блок #{b.id}: повторение {r} раз..."
                    ))
                    
                    for i in range(repeat_count):
                        if not self.is_running:
                            break
                        self.root.after(0, lambda b=block, idx=i+1, r=repeat_count: self.status_label.config(
                            text=f"🔄 Блок #{b.id}: итерация {idx}/{r}"
                        ))
                        
                        # Выполняем следующие блоки
                        for next_block in block.connections_out:
                            if not self.is_running:
                                break
                            execute_block(next_block, context.copy())
                
                elif isinstance(block, GroupBlock):
                    # Блок группы - просто пропуск, группа это визуальный маркер
                    group_type = block.data['group_type']
                    group_name = block.data['name']
                    self.root.after(0, lambda b=block, t=group_type, n=group_name: self.status_label.config(
                        text=f"📦 Блок #{b.id}: {'Начало' if t == 'start' else 'Конец'} группы '{n}'"
                    ))
                    
                    # Выполняем следующие блоки
                    for next_block in block.connections_out:
                        if not self.is_running:
                            break
                        execute_block(next_block, context.copy())
                
                elif isinstance(block, KeyboardInputBlock):
                    # Блок ввода текста с клавиатуры
                    text = block.data['text']
                    press_enter = block.data['press_enter']
                    
                    self.root.after(0, lambda b=block, t=text: self.status_label.config(
                        text=f"⌨️ Блок #{b.id}: ввод текста '{t[:20]}...'"
                    ))
                    
                    # Простой метод - через буфер обмена (работает с любым языком)
                    try:
                        import pyperclip
                        pyperclip.copy(text)
                        time.sleep(0.15)
                        pyautogui.hotkey('ctrl', 'v')
                        time.sleep(0.2)
                    except Exception as e:
                        # Fallback - вводим посимвольно
                        self.root.after(0, lambda: messagebox.showwarning(
                            "Предупреждение",
                            f"Ошибка буфера обмена: {str(e)}\nИспользую посимвольный ввод"
                        ))
                        for char in text:
                            pyautogui.write(char, interval=0.05)
                    
                    # Нажимаем Enter если нужно
                    if press_enter:
                        time.sleep(0.2)
                        pyautogui.press('enter')
                    
                    time.sleep(0.3)
                    
                    # Выполняем следующие блоки с задержкой
                    for next_block in block.connections_out:
                        if not self.is_running:
                            break
                        delay = get_connection_delay(block, next_block)
                        if delay > 0:
                            time.sleep(delay)
                        execute_block(next_block, context.copy())
            
            # Запускаем выполнение от каждого начального блока ОДИН РАЗ
            for start_block in start_blocks:
                if not self.is_running:
                    break
                execute_block(start_block)
            
            # Завершаем выполнение
            self.root.after(0, self.stop_execution)
            self.root.after(0, lambda: self.status_label.config(text="✅ Выполнение завершено!"))
        
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Ошибка", f"Ошибка выполнения: {str(e)}"))
            self.root.after(0, self.stop_execution)
    
    def save_flow(self):
        """Сохранение потока"""
        data = {
            'blocks': [],
            'connections': []
        }
        
        # Сохраняем блоки
        for block in self.blocks:
            block_data = {
                'id': block.id,
                'type': block.type,
                'x': block.x,
                'y': block.y,
                'data': block.data
            }
            data['blocks'].append(block_data)
        
        # Сохраняем соединения
        for conn in self.connections:
            conn_data = {
                'from': conn.from_block.id,
                'to': conn.to_block.id,
                'delay': conn.delay
            }
            data['connections'].append(conn_data)
        
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            messagebox.showinfo("Успех", f"✅ Поток сохранен!\n\n📁 {self.config_file}\n📦 Блоков: {len(data['blocks'])}\n🔗 Соединений: {len(data['connections'])}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить: {str(e)}")
    
    def load_flow_silent(self):
        """Тихая загрузка потока при старте"""
        if not os.path.exists(self.config_file):
            return
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Очищаем текущий canvas
            for block in self.blocks:
                block.delete()
            for conn in self.connections:
                conn.delete()
            self.blocks.clear()
            self.connections.clear()
            
            # Загружаем блоки
            block_map = {}
            for block_data in data.get('blocks', []):
                block_type = block_data['type']
                x, y = block_data['x'], block_data['y']
                block_id = block_data['id']
                
                if block_type == 'coordinate':
                    block = CoordinateBlock(self.canvas, x, y, block_id)
                    if block_data['data'].get('x') is not None:
                        block.update_coordinates(block_data['data']['x'], block_data['data']['y'])
                elif block_type == 'click':
                    click_type = block_data['data'].get('click_type', 'left')
                    block = ClickBlock(self.canvas, x, y, block_id, click_type)
                elif block_type == 'delay':
                    delay = block_data['data'].get('delay', 1.0)
                    block = DelayBlock(self.canvas, x, y, block_id, delay)
                elif block_type == 'repeat':
                    repeat_count = block_data['data'].get('repeat_count', 1)
                    block = RepeatBlock(self.canvas, x, y, block_id, repeat_count)
                elif block_type == 'group':
                    group_type = block_data['data'].get('group_type', 'start')
                    block = GroupBlock(self.canvas, x, y, block_id, group_type)
                    if block_data['data'].get('name'):
                        block.update_name(block_data['data']['name'])
                elif block_type == 'keyboard_input':
                    text = block_data['data'].get('text', '')
                    press_enter = block_data['data'].get('press_enter', True)
                    block = KeyboardInputBlock(self.canvas, x, y, block_id, text, press_enter)
                else:
                    continue
                
                self.blocks.append(block)
                block_map[block_id] = block
                
                if block_id >= self.next_block_id:
                    self.next_block_id = block_id + 1
            
            # Загружаем соединения
            for conn_data in data.get('connections', []):
                from_block = block_map.get(conn_data['from'])
                to_block = block_map.get(conn_data['to'])
                delay = conn_data.get('delay', 0.0)
                if from_block and to_block:
                    connection = Connection(self.canvas, from_block, to_block, delay)
                    self.connections.append(connection)
                    from_block.connections_out.append(to_block)
                    to_block.connections_in.append(from_block)
            
            print(f"Загружен поток: {len(self.blocks)} блоков, {len(self.connections)} соединений")
        except Exception as e:
            print(f"Ошибка загрузки потока: {e}")
    
    def load_flow(self):
        """Загрузка потока с сообщением"""
        if not os.path.exists(self.config_file):
            messagebox.showwarning("Предупреждение", f"Файл {self.config_file} не найден!")
            return
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Очищаем текущий canvas
            for block in self.blocks:
                block.delete()
            for conn in self.connections:
                conn.delete()
            self.blocks.clear()
            self.connections.clear()
            
            # Загружаем блоки
            block_map = {}
            for block_data in data.get('blocks', []):
                block_type = block_data['type']
                x, y = block_data['x'], block_data['y']
                block_id = block_data['id']
                
                if block_type == 'coordinate':
                    block = CoordinateBlock(self.canvas, x, y, block_id)
                    if block_data['data'].get('x') is not None:
                        block.update_coordinates(block_data['data']['x'], block_data['data']['y'])
                elif block_type == 'click':
                    click_type = block_data['data'].get('click_type', 'left')
                    block = ClickBlock(self.canvas, x, y, block_id, click_type)
                elif block_type == 'delay':
                    delay = block_data['data'].get('delay', 1.0)
                    block = DelayBlock(self.canvas, x, y, block_id, delay)
                elif block_type == 'repeat':
                    repeat_count = block_data['data'].get('repeat_count', 1)
                    block = RepeatBlock(self.canvas, x, y, block_id, repeat_count)
                elif block_type == 'group':
                    group_type = block_data['data'].get('group_type', 'start')
                    block = GroupBlock(self.canvas, x, y, block_id, group_type)
                    if block_data['data'].get('name'):
                        block.update_name(block_data['data']['name'])
                elif block_type == 'keyboard_input':
                    text = block_data['data'].get('text', '')
                    press_enter = block_data['data'].get('press_enter', True)
                    block = KeyboardInputBlock(self.canvas, x, y, block_id, text, press_enter)
                else:
                    continue
                
                self.blocks.append(block)
                block_map[block_id] = block
                
                if block_id >= self.next_block_id:
                    self.next_block_id = block_id + 1
            
            # Загружаем соединения
            for conn_data in data.get('connections', []):
                from_block = block_map.get(conn_data['from'])
                to_block = block_map.get(conn_data['to'])
                delay = conn_data.get('delay', 0.0)
                if from_block and to_block:
                    connection = Connection(self.canvas, from_block, to_block, delay)
                    self.connections.append(connection)
                    from_block.connections_out.append(to_block)
                    to_block.connections_in.append(from_block)
            
            messagebox.showinfo("Успех", f"✅ Поток загружен!\n\n📦 Блоков: {len(self.blocks)}\n🔗 Соединений: {len(self.connections)}")
            self.status_label.config(text=f"✅ Загружено: {len(self.blocks)} блоков, {len(self.connections)} соединений")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить: {str(e)}")
    
    def export_to_python(self):
        """Экспорт потока в Python скрипт"""
        if not self.blocks:
            messagebox.showwarning("Предупреждение", "Нет блоков для экспорта!")
            return
        
        # Находим начальные блоки (без входящих соединений)
        start_blocks = [block for block in self.blocks if not block.connections_in]
        
        if not start_blocks:
            messagebox.showwarning("Предупреждение", "Не найдено начальных блоков!\n\nДобавьте хотя бы один блок без входящих соединений.")
            return
        
        # Генерируем Python код
        script_lines = []
        
        # Заголовок
        script_lines.append('#!/usr/bin/env python3')
        script_lines.append('# -*- coding: utf-8 -*-')
        script_lines.append('"""')
        script_lines.append('Автоматически сгенерированный скрипт из FlowClick Studio')
        script_lines.append('Для запуска: python <имя_файла>.py')
        script_lines.append('"""')
        script_lines.append('')
        
        # Импорты
        script_lines.append('import pyautogui')
        script_lines.append('import time')
        script_lines.append('import sys')
        
        # Проверяем нужен ли pyperclip
        has_keyboard_input = any(isinstance(b, KeyboardInputBlock) for b in self.blocks)
        if has_keyboard_input:
            script_lines.append('try:')
            script_lines.append('    import pyperclip')
            script_lines.append('except ImportError:')
            script_lines.append('    print("Ошибка: установите pyperclip (pip install pyperclip)")')
            script_lines.append('    sys.exit(1)')
        
        script_lines.append('')
        script_lines.append('def main():')
        script_lines.append('    """Основная функция выполнения скрипта"""')
        script_lines.append('    print("🚀 Запуск автоматизации...")')
        script_lines.append('    print("⏱️  Ожидание 2 секунды перед началом...")')
        script_lines.append('    time.sleep(2)')
        script_lines.append('    print("▶ Начало выполнения!\\n")')
        script_lines.append('')
        
        # Генерируем функции для каждого блока
        visited = set()
        block_counter = {'count': 0}
        
        def generate_block_code(block, indent=1, context=None):
            """Рекурсивная генерация кода для блока и его потомков"""
            if context is None:
                context = {'coordinates': None}
            
            if block.id in visited:
                return []
            
            visited.add(block.id)
            lines = []
            ind = '    ' * indent
            
            if isinstance(block, CoordinateBlock):
                x, y = block.data.get('x'), block.data.get('y')
                if x is None or y is None:
                    lines.append(f'{ind}print("⚠️  Блок #{block.id}: координаты не заданы, пропускаю...")')
                else:
                    context['coordinates'] = (x, y)
                    lines.append(f'{ind}# Блок #{block.id}: Координаты')
                    lines.append(f'{ind}coord_x, coord_y = {x}, {y}')
                    lines.append(f'{ind}print(f"📍 Координаты установлены: ({{coord_x}}, {{coord_y}})")')
            
            elif isinstance(block, ClickBlock):
                click_type = block.data['click_type']
                click_name = {'left': 'Левый', 'right': 'Правый', 'middle': 'Средний'}.get(click_type, click_type)
                
                lines.append(f'{ind}# Блок #{block.id}: {click_name} клик')
                if context.get('coordinates'):
                    lines.append(f'{ind}print(f"🖱️  {click_name} клик в ({{coord_x}}, {{coord_y}})")')
                    lines.append(f'{ind}pyautogui.click(coord_x, coord_y, button="{click_type}")')
                else:
                    lines.append(f'{ind}print("⚠️  Нет координат для клика, пропускаю...")')
                lines.append(f'{ind}time.sleep(0.3)')
            
            elif isinstance(block, DelayBlock):
                delay = block.data['delay']
                lines.append(f'{ind}# Блок #{block.id}: Задержка')
                lines.append(f'{ind}print(f"⏱️  Задержка {delay} сек...")')
                lines.append(f'{ind}time.sleep({delay})')
            
            elif isinstance(block, RepeatBlock):
                repeat_count = block.data['repeat_count']
                lines.append(f'{ind}# Блок #{block.id}: Повторение {repeat_count}x')
                lines.append(f'{ind}print(f"🔄 Повторение {repeat_count} раз...")')
                lines.append(f'{ind}for iteration in range({repeat_count}):')
                lines.append(f'{ind}    print(f"  → Итерация {{iteration + 1}}/{repeat_count}")')
                
                # Обрабатываем потомков внутри цикла
                for next_block in block.connections_out:
                    child_lines = generate_block_code(next_block, indent + 1, context.copy())
                    lines.extend(child_lines)
                
                return lines  # Возвращаем сразу, потомки уже обработаны
            
            elif isinstance(block, GroupBlock):
                group_type = block.data['group_type']
                group_name = block.data.get('name', 'Группа')
                marker = 'Начало' if group_type == 'start' else 'Конец'
                lines.append(f'{ind}# Блок #{block.id}: {marker} группы "{group_name}"')
                lines.append(f'{ind}print("📦 {marker} группы: {group_name}")')
            
            elif isinstance(block, KeyboardInputBlock):
                text = block.data.get('text', '')
                press_enter = block.data.get('press_enter', True)
                # Экранируем кавычки и переносы строк
                text_escaped = text.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')
                lines.append(f'{ind}# Блок #{block.id}: Ввод текста')
                lines.append(f'{ind}text_to_type = "{text_escaped}"')
                lines.append(f'{ind}print(f"⌨️  Ввод текста: {{text_to_type[:30]}}...")')
                lines.append(f'{ind}try:')
                lines.append(f'{ind}    pyperclip.copy(text_to_type)')
                lines.append(f'{ind}    time.sleep(0.15)')
                lines.append(f'{ind}    pyautogui.hotkey("ctrl", "v")')
                lines.append(f'{ind}    time.sleep(0.2)')
                lines.append(f'{ind}except Exception as e:')
                lines.append(f'{ind}    print(f"⚠️  Ошибка буфера обмена: {{e}}")')
                lines.append(f'{ind}    for char in text_to_type:')
                lines.append(f'{ind}        pyautogui.write(char, interval=0.05)')
                
                if press_enter:
                    lines.append(f'{ind}time.sleep(0.2)')
                    lines.append(f'{ind}pyautogui.press("enter")')
                
                lines.append(f'{ind}time.sleep(0.3)')
            
            # Обрабатываем потомков (если не RepeatBlock, он обработан выше)
            if not isinstance(block, RepeatBlock):
                for next_block in block.connections_out:
                    # Проверяем задержку на соединении
                    delay_on_connection = 0.0
                    for conn in self.connections:
                        if conn.from_block == block and conn.to_block == next_block:
                            delay_on_connection = conn.delay
                            break
                    
                    if delay_on_connection > 0:
                        lines.append(f'{ind}# Задержка на переходе')
                        lines.append(f'{ind}time.sleep({delay_on_connection})')
                    
                    child_lines = generate_block_code(next_block, indent, context.copy())
                    lines.extend(child_lines)
            
            return lines
        
        # Генерируем код для всех начальных блоков
        for start_block in start_blocks:
            code_lines = generate_block_code(start_block, indent=1)
            script_lines.extend(code_lines)
            script_lines.append('')
        
        script_lines.append('    print("\\n✅ Выполнение завершено!")')
        script_lines.append('')
        script_lines.append('if __name__ == "__main__":')
        script_lines.append('    try:')
        script_lines.append('        main()')
        script_lines.append('    except KeyboardInterrupt:')
        script_lines.append('        print("\\n⏹️  Прервано пользователем")')
        script_lines.append('        sys.exit(0)')
        script_lines.append('    except Exception as e:')
        script_lines.append('        print(f"\\n❌ Ошибка: {e}")')
        script_lines.append('        sys.exit(1)')
        
        # Объединяем строки
        script_content = '\n'.join(script_lines)
        
        # Сохраняем в файл
        from tkinter import filedialog
        default_name = "flow_script.py"
        file_path = filedialog.asksaveasfilename(
            title="Сохранить Python скрипт",
            defaultextension=".py",
            filetypes=[("Python файлы", "*.py"), ("Все файлы", "*.*")],
            initialfile=default_name
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(script_content)
                
                messagebox.showinfo(
                    "Успех",
                    f"✅ Скрипт успешно экспортирован!\n\n"
                    f"📁 Файл: {file_path}\n"
                    f"📦 Блоков экспортировано: {len(visited)}\n\n"
                    f"Для запуска:\n"
                    f'python "{file_path}"'
                )
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить скрипт: {str(e)}")
    
    def generate_single_block_code(self, block):
        """Генерация Python кода для одного блока (как в экспорте)"""
        lines = []
        
        # Заголовок с информацией
        lines.append(f"# ═══════════════════════════════════════════════════")
        lines.append(f"# Блок #{block.id} - {block.type.upper()}")
        lines.append(f"# ═══════════════════════════════════════════════════")
        lines.append("")
        
        # Генерируем код точно как в экспорте
        indent = ""  # Без отступа для просмотра одного блока
        
        if isinstance(block, CoordinateBlock):
            x, y = block.data.get('x'), block.data.get('y')
            if x is None or y is None:
                lines.append(f'{indent}# ⚠️  Coordinates not set!')
            else:
                lines.append(f'{indent}coord_x, coord_y = {x}, {y}')
        
        elif isinstance(block, ClickBlock):
            click_type = block.data['click_type']
            
            lines.append(f'{indent}pyautogui.click(coord_x, coord_y, button="{click_type}")')
            lines.append(f'{indent}time.sleep(0.3)')
        
        elif isinstance(block, DelayBlock):
            delay = block.data['delay']
            lines.append(f'{indent}time.sleep({delay})')
        
        elif isinstance(block, RepeatBlock):
            repeat_count = block.data['repeat_count']
            lines.append(f'{indent}for iteration in range({repeat_count}):')
            lines.append(f'{indent}    # Next blocks here')
        
        elif isinstance(block, GroupBlock):
            group_type = block.data['group_type']
            group_name = block.data.get('name', 'Группа')
            marker = 'start' if group_type == 'start' else 'end'
            lines.append(f'{indent}# Group {marker}: {group_name}')
        
        elif isinstance(block, KeyboardInputBlock):
            text = block.data.get('text', '')
            press_enter = block.data.get('press_enter', True)
            text_escaped = text.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')
            
            lines.append(f'{indent}text_to_type = "{text_escaped}"')
            lines.append(f'{indent}try:')
            lines.append(f'{indent}    pyperclip.copy(text_to_type)')
            lines.append(f'{indent}    time.sleep(0.15)')
            lines.append(f'{indent}    pyautogui.hotkey("ctrl", "v")')
            lines.append(f'{indent}    time.sleep(0.2)')
            lines.append(f'{indent}except Exception as e:')
            lines.append(f'{indent}    for char in text_to_type:')
            lines.append(f'{indent}        pyautogui.write(char, interval=0.05)')
            
            if press_enter:
                lines.append(f'{indent}time.sleep(0.2)')
                lines.append(f'{indent}pyautogui.press("enter")')
            
            lines.append(f'{indent}time.sleep(0.3)')
        
        else:
            lines.append(f'{indent}# ❓ Неизвестный тип блока')
        
        # Информация о соединениях
        lines.append("")
        lines.append("# ─────────────────────────────────────────────────")
        lines.append("# 🔗 Информация о соединениях:")
        
        if block.connections_in:
            lines.append(f"# ← Входящие: {len(block.connections_in)} блок(ов)")
            for in_block in block.connections_in:
                lines.append(f"#   • Блок #{in_block.id} ({in_block.type})")
        else:
            lines.append("# ← Входящие: нет (начальный блок)")
        
        if block.connections_out:
            lines.append(f"# → Исходящие: {len(block.connections_out)} блок(ов)")
            for out_block in block.connections_out:
                delay = 0.0
                for conn in self.connections:
                    if conn.from_block == block and conn.to_block == out_block:
                        delay = conn.delay
                        break
                
                delay_str = f" [⏱️  {delay}s]" if delay > 0 else ""
                lines.append(f"#   • Блок #{out_block.id} ({out_block.type}){delay_str}")
        else:
            lines.append("# → Исходящие: нет (конечный блок)")
        
        lines.append("# ═══════════════════════════════════════════════════")
        
        return '\n'.join(lines)
    
    def generate_connection_code(self, connection):
        """Генерация Python кода для соединения (задержка)"""
        lines = []
        
        # Заголовок
        lines.append(f"# ═══════════════════════════════════════════════════")
        lines.append(f"# СОЕДИНЕНИЕ: Блок #{connection.from_block.id} → Блок #{connection.to_block.id}")
        lines.append(f"# ═══════════════════════════════════════════════════")
        lines.append("")
        
        if connection.delay > 0:
            lines.append(f"# Задержка на переходе: {connection.delay} секунд")
            lines.append(f"time.sleep({connection.delay})")
        else:
            lines.append("# Нет задержки на переходе")
            lines.append("# Чтобы добавить задержку, измените значение:")
            lines.append("# time.sleep(1.0)")
        
        # Информация о соединении
        lines.append("")
        lines.append("# ─────────────────────────────────────────────────")
        lines.append("# 🔗 Информация о соединении:")
        lines.append(f"# От блока: #{connection.from_block.id} ({connection.from_block.type})")
        lines.append(f"# К блоку:  #{connection.to_block.id} ({connection.to_block.type})")
        lines.append("# ═══════════════════════════════════════════════════")
        
        return '\n'.join(lines)
    
    def update_code_panel(self, block):
        """Обновление панели с кодом выбранного блока"""
        if not hasattr(self, 'code_text'):
            return
        
        code = self.generate_single_block_code(block)
        
        # Панель теперь редактируема - просто вставляем код
        self.code_text.delete("1.0", "end")
        self.code_text.insert("1.0", code)
        
        # Сохраняем текущий код и блок для применения изменений
        self.current_code = code
        self.current_edited_block = block
        
        # Сохраняем текущий код для копирования
        self.current_code = code
    
    def update_code_panel_connection(self, connection):
        """Обновление панели с кодом выбранного соединения"""
        if not hasattr(self, 'code_text'):
            return
        
        code = self.generate_connection_code(connection)
        
        # Панель редактируема - просто вставляем код
        self.code_text.delete("1.0", "end")
        self.code_text.insert("1.0", code)
        
        # Сохраняем текущий код и соединение для применения изменений
        self.current_code = code
        self.current_edited_connection = connection
        self.current_edited_block = None  # Очищаем блок
    
    def copy_code_to_clipboard(self):
        """Копирование кода в буфер обмена"""
        if hasattr(self, 'current_code') and self.current_code:
            try:
                import pyperclip
                pyperclip.copy(self.current_code)
                self.status_label.config(text="✅ Код скопирован в буфер обмена!")
                self.root.after(2000, lambda: self.status_label.config(
                    text="⚫ Готов | Ctrl - выбор координат | Двойной клик на квадрат - захват координат | F6 - запуск | Q - остановка"
                ))
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось скопировать: {str(e)}")
        else:
            messagebox.showwarning("Предупреждение", "Нет кода для копирования!\nВыберите блок сначала.")
    
    def apply_code_changes(self):
        """Применение изменений из кода к блоку или соединению"""
        # Проверяем что редактируем - блок или соединение
        if hasattr(self, 'current_edited_connection') and self.current_edited_connection:
            # Редактируем соединение
            try:
                import re
                edited_code = self.code_text.get("1.0", "end-1c")
                connection = self.current_edited_connection
                
                # Ищем time.sleep(NUMBER)
                sleep_match = re.search(r'time\.sleep\s*\(\s*([\d.]+)\s*\)', edited_code)
                if sleep_match:
                    new_delay = float(sleep_match.group(1))
                    connection.delay = new_delay
                    connection.update()
                    self.status_label.config(text=f"✅ Задержка на соединении обновлена: {new_delay} сек")
                    # Обновляем панель кода
                    self.update_code_panel_connection(connection)
                    messagebox.showinfo("Успех", "✅ Изменения применены к соединению!")
                else:
                    messagebox.showwarning("Предупреждение", "Не удалось найти time.sleep() в коде!")
                return
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось применить изменения:\n{str(e)}")
                return
        
        if not hasattr(self, 'current_edited_block') or not self.current_edited_block:
            messagebox.showwarning("Предупреждение", "Сначала выберите блок или соединение для редактирования!")
            return
        
        try:
            # Получаем измененный код из текстового поля
            edited_code = self.code_text.get("1.0", "end-1c")
            block = self.current_edited_block
            
            # Парсим код в зависимости от типа блока
            import re
            
            if isinstance(block, CoordinateBlock):
                # Ищем coord_x = NUMBER и coord_y = NUMBER (только строки присваивания)
                x_match = re.search(r'^\s*coord_x\s*[,=]\s*(\d+)', edited_code, re.MULTILINE)
                y_match = re.search(r'^\s*coord_y\s*[=]\s*(\d+)', edited_code, re.MULTILINE)
                
                # Если не нашли отдельные строки, пробуем формат "coord_x, coord_y = X, Y"
                if not x_match or not y_match:
                    pair_match = re.search(r'coord_x\s*,\s*coord_y\s*=\s*(\d+)\s*,\s*(\d+)', edited_code)
                    if pair_match:
                        new_x = int(pair_match.group(1))
                        new_y = int(pair_match.group(2))
                        block.update_coordinates(new_x, new_y)
                        self.status_label.config(text=f"✅ Координаты обновлены: X={new_x}, Y={new_y}")
                        return
                
                if x_match and y_match:
                    new_x = int(x_match.group(1))
                    new_y = int(y_match.group(1))
                    block.update_coordinates(new_x, new_y)
                    self.status_label.config(text=f"✅ Координаты обновлены: X={new_x}, Y={new_y}")
                else:
                    messagebox.showwarning("Предупреждение", "Не удалось найти coord_x и coord_y в коде!")
                    return
            
            elif isinstance(block, ClickBlock):
                # Ищем button="..." для определения типа клика
                button_match = re.search(r'button\s*=\s*["\'](\w+)["\']', edited_code)
                if button_match:
                    new_button = button_match.group(1)
                    if new_button in ['left', 'right', 'middle']:
                        block.data['click_type'] = new_button
                        # Перерисовываем блок
                        block.delete()
                        block.__init__(block.canvas, block.x, block.y, block.id, new_button)
                        # Восстанавливаем соединения
                        for conn in self.connections:
                            if conn.from_block == block or conn.to_block == block:
                                conn.update()
                        self.status_label.config(text=f"✅ Тип клика изменен на: {new_button}")
                    else:
                        messagebox.showwarning("Предупреждение", f"Неверный тип кнопки: {new_button}")
                        return
            
            elif isinstance(block, DelayBlock):
                # Ищем time.sleep(NUMBER)
                sleep_match = re.search(r'time\.sleep\s*\(\s*([\d.]+)\s*\)', edited_code)
                if sleep_match:
                    new_delay = float(sleep_match.group(1))
                    block.update_delay(new_delay)
                    self.status_label.config(text=f"✅ Задержка обновлена: {new_delay} сек")
                else:
                    messagebox.showwarning("Предупреждение", "Не удалось найти time.sleep() в коде!")
                    return
            
            elif isinstance(block, RepeatBlock):
                # Ищем range(NUMBER)
                range_match = re.search(r'range\s*\(\s*(\d+)\s*\)', edited_code)
                if range_match:
                    new_count = int(range_match.group(1))
                    block.update_repeat_count(new_count)
                    self.status_label.config(text=f"✅ Количество повторов обновлено: {new_count}")
                else:
                    messagebox.showwarning("Предупреждение", "Не удалось найти range() в коде!")
                    return
            
            elif isinstance(block, GroupBlock):
                # Ищем название группы в комментарии: # Group start/end: НАЗВАНИЕ
                name_match = re.search(r'#\s*Group\s*(?:start|end):\s*(.+)', edited_code)
                if name_match:
                    new_name = name_match.group(1).strip()
                    block.update_name(new_name)
                    self.status_label.config(text=f"✅ Название группы обновлено: {new_name}")
                else:
                    messagebox.showwarning("Предупреждение", "Не удалось найти название группы в коде!")
                    return
            
            elif isinstance(block, KeyboardInputBlock):
                # Ищем text_to_type = "..."
                text_match = re.search(r'text_to_type\s*=\s*["\'](.* ?)["\']', edited_code, re.DOTALL)
                if text_match:
                    new_text = text_match.group(1)
                    # Обрабатываем escape-последовательности
                    new_text = new_text.replace('\\n', '\n').replace('\\\\', '\\').replace('\\"', '"')
                    
                    # Проверяем наличие pyautogui.press("enter")
                    press_enter = 'pyautogui.press("enter")' in edited_code or "pyautogui.press('enter')" in edited_code
                    
                    block.update_text(new_text, press_enter)
                    self.status_label.config(text=f"✅ Текст обновлен")
                else:
                    messagebox.showwarning("Предупреждение", "Не удалось найти text_to_type в коде!")
                    return
            
            else:
                messagebox.showinfo("Информация", f"Редактирование кода для типа {block.type} пока не поддерживается")
                return
            
            # Обновляем панель кода
            self.update_code_panel(block)
            
            messagebox.showinfo("Успех", "✅ Изменения применены к блоку!")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось применить изменения:\n{str(e)}")
                
    def on_closing(self):
        """Обработка закрытия окна"""
        self.is_running = False
        keyboard.unhook_all()
        self.root.destroy()

def main():
    root = tk.Tk()
    app = FlowEditor(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()
