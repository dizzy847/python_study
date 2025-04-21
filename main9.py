# Импорт необходимых библиотек
import tkinter as tk  # Для создания GUI
from tkinter import ttk, messagebox, scrolledtext  # Виджеты, диалоги, текстовое поле
import math  # Математические функции
import time  # Работа со временем
import json  # Для работы с JSON-файлами
import logging  # Система логирования
from logging.handlers import RotatingFileHandler  # Ротация лог-файлов
import random  # Генерация случайных чисел
import threading  # Многопоточность

class RobotARM_IMR165_GUI:
    def __init__(self, master):
        # Инициализация главного окна
        self.master = master
        master.title("Управление роботом ARM-IMR-165")  # Заголовок окна
        master.geometry("1200x800")  # Размер окна
        
        # Состояние системы (off/ready/running/paused/emergency)
        self.system_state = "off"  
        # Стиль движения (normal/precise/rapid)
        self.movement_style = "normal"  
        # Статус соединения
        self.connection_status = True  
        # Данные моторов (температура, позиции)
        self.motor_data = {
            'temp': [0.0]*6,
            'position_ticks': [0]*6,
            'position_rad': [0.0]*6,
            'position_deg': [0]*6
        }
        
        # Настройка системы логирования
        self.setup_logging()
        
        # Настройка стилей интерфейса
        self.style = ttk.Style()
        self.style.configure('TFrame', background='#f0f0f0')  # Стиль фрейма
        self.style.configure('TButton', font=('Arial', 10), padding=5)  # Стиль кнопки
        self.style.configure('TLabel', background='#f0f0f0', font=('Arial', 10))  # Стиль метки
        # Дополнительные стили
        self.style.configure('Red.TFrame', background='#ffdddd')
        self.style.configure('Green.TFrame', background='#ddffdd')
        self.style.configure('Yellow.TFrame', background='#ffffdd')
        
        # Основные фреймы интерфейса
        self.main_frame = ttk.Frame(master)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Левая панель (управление и логи)
        self.left_panel = ttk.Frame(self.main_frame)
        self.left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Панель управления
        self.control_frame = ttk.LabelFrame(self.left_panel, text="Управление манипулятором", padding=10)
        self.control_frame.pack(fill=tk.BOTH, expand=True)
        
        # Панель состояния и светофора
        self.state_frame = ttk.Frame(self.left_panel)
        self.state_frame.pack(fill=tk.X, pady=5)
        self.create_state_indicators()  # Создание индикаторов
        
        # Панель логов
        self.log_frame = ttk.LabelFrame(self.left_panel, text="Логи системы", padding=10)
        self.log_frame.pack(fill=tk.BOTH, expand=True)
        self.create_log_panel()  # Создание панели логов
        
        # Правая панель (визуализация и мониторинг)
        self.right_panel = ttk.Frame(self.main_frame)
        self.right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=False)
        
        # Панель визуализации
        self.visual_frame = ttk.LabelFrame(self.right_panel, text="Визуализация", padding=10)
        self.visual_frame.pack(fill=tk.BOTH, expand=True)
        
        # Холст для отрисовки робота
        self.canvas = tk.Canvas(self.visual_frame, bg='white', width=400, height=400)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Панель мониторинга моторов
        self.monitor_frame = ttk.LabelFrame(self.right_panel, text="Мониторинг моторов", padding=10)
        self.monitor_frame.pack(fill=tk.BOTH, expand=True)
        self.create_motor_monitor()  # Создание монитора моторов
        
        # Параметры робота
        self.joint_angles = [0, 0, 0, 0, 0, 0]  # Углы 6 суставов
        self.gripper_state = False  # Состояние захвата
        
        # Создание элементов управления
        self.create_power_controls()  # Кнопки вкл/выкл
        self.create_joint_controls()  # Управление суставами
        self.create_gripper_control()  # Управление захватом
        self.create_utility_buttons()  # Служебные кнопки
        self.create_movement_style_controls()  # Стили движения
        
        # Инициализация системы
        self.update_status("Система выключена", "red")  # Статус
        self.update_traffic_light()  # Светофор
        
        # Запуск потока мониторинга моторов
        self.monitor_thread = threading.Thread(target=self.monitor_motors, daemon=True)
        self.monitor_thread.start()
        
        # Первоначальная отрисовка робота
        self.draw_robot()

    def setup_logging(self):
        """Настройка системы логирования"""
        # Основной логгер
        self.logger = logging.getLogger('robot_logger')
        self.logger.setLevel(logging.INFO)  # Уровень логирования
        
        # Логгер аварийных ситуаций
        self.emergency_logger = logging.getLogger('emergency_logger')
        self.emergency_logger.setLevel(logging.WARNING)  # Только предупреждения и выше
        
        # Формат записей в логе
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        
        # Обработчик для основного лога с ротацией файлов
        main_handler = RotatingFileHandler('robot_system.log', maxBytes=1e6, backupCount=3)
        main_handler.setFormatter(formatter)
        self.logger.addHandler(main_handler)
        
        # Обработчик для аварийного лога (отдельный файл)
        emergency_handler = logging.FileHandler('emergency.log')
        emergency_handler.setFormatter(formatter)
        self.emergency_logger.addHandler(emergency_handler)
        
        # Вывод логов в консоль для отладки
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

    def create_state_indicators(self):
        """Создание индикаторов состояния системы"""
        # Фрейм для светофора
        self.traffic_frame = ttk.Frame(self.state_frame)
        self.traffic_frame.pack(side=tk.LEFT, padx=10)
        
        # Красный свет
        self.red_light = tk.Canvas(self.traffic_frame, width=30, height=30, bg='white', bd=2, relief='ridge')
        self.red_light.pack(pady=2)
        self.red_light.create_oval(5, 5, 25, 25, fill='gray', outline='black', tags='red')
        
        # Желтый свет
        self.yellow_light = tk.Canvas(self.traffic_frame, width=30, height=30, bg='white', bd=2, relief='ridge')
        self.yellow_light.pack(pady=2)
        self.yellow_light.create_oval(5, 5, 25, 25, fill='gray', outline='black', tags='yellow')
        
        # Зеленый свет
        self.green_light = tk.Canvas(self.traffic_frame, width=30, height=30, bg='white', bd=2, relief='ridge')
        self.green_light.pack(pady=2)
        self.green_light.create_oval(5, 5, 25, 25, fill='gray', outline='black', tags='green')
        
        # Метка состояния системы
        self.state_label = ttk.Label(self.state_frame, text="Состояние: ВЫКЛ", font=('Arial', 12))
        self.state_label.pack(side=tk.LEFT, expand=True)
        
        # Индикатор связи
        self.connection_label = ttk.Label(self.state_frame, text="Связь: ОК", foreground='green')
        self.connection_label.pack(side=tk.RIGHT, padx=10)

    def update_traffic_light(self):
        """Обновление состояния промышленного светофора"""
        # Выключение всех ламп
        self.red_light.itemconfig('red', fill='gray')
        self.yellow_light.itemconfig('yellow', fill='gray')
        self.green_light.itemconfig('green', fill='gray')
        
        # Включение нужной лампы в зависимости от состояния
        if self.system_state == "off":
            self.red_light.itemconfig('red', fill='red')
        elif self.system_state == "ready":
            self.yellow_light.itemconfig('yellow', fill='yellow')
        elif self.system_state == "running":
            self.green_light.itemconfig('green', fill='green')
        elif self.system_state == "paused":
            self.yellow_light.itemconfig('yellow', fill='yellow')
        elif self.system_state == "emergency":
            self.red_light.itemconfig('red', fill='red')
            self.master.after(500, self.blink_red_light)  # Запуск мигания
    
    def blink_red_light(self):
        """Мигание красного света при аварийном состоянии"""
        if self.system_state == "emergency":
            current = self.red_light.itemcget('red', 'fill')
            new_color = 'gray' if current == 'red' else 'red'  # Переключение цвета
            self.red_light.itemconfig('red', fill=new_color)
            self.master.after(500, self.blink_red_light)  # Регулярное обновление

    def create_log_panel(self):
        """Создание панели для отображения логов"""
        # Текстовое поле с прокруткой
        self.log_text = scrolledtext.ScrolledText(self.log_frame, width=80, height=15)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        self.log_text.configure(state='disabled')  # Только для чтения
        
        # Кастомный обработчик для вывода логов в текстовое поле
        class TextHandler(logging.Handler):
            def __init__(self, text_widget):
                super().__init__()
                self.text_widget = text_widget
            
            def emit(self, record):
                msg = self.format(record)  # Форматирование записи
                self.text_widget.configure(state='normal')  # Включение редактирования
                self.text_widget.insert(tk.END, msg + '\n')  # Добавление записи
                self.text_widget.configure(state='disabled')  # Блокировка редактирования
                self.text_widget.see(tk.END)  # Прокрутка вниз
        
        # Добавление обработчика к логгерам
        text_handler = TextHandler(self.log_text)
        text_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        self.logger.addHandler(text_handler)
        self.emergency_logger.addHandler(text_handler)

    def create_motor_monitor(self):
        """Создание таблицы для мониторинга состояния моторов"""
        # Определение колонок
        columns = ('motor', 'temp', 'pos_ticks', 'pos_rad', 'pos_deg')
        self.motor_tree = ttk.Treeview(self.monitor_frame, columns=columns, show='headings', height=6)
        
        # Настройка заголовков колонок
        self.motor_tree.heading('motor', text='Мотор')
        self.motor_tree.heading('temp', text='Температура (°C)')
        self.motor_tree.heading('pos_ticks', text='Позиция (тики)')
        self.motor_tree.heading('pos_rad', text='Позиция (рад)')
        self.motor_tree.heading('pos_deg', text='Позиция (°)')
        
        # Настройка ширины и выравнивания колонок
        self.motor_tree.column('motor', width=80, anchor=tk.CENTER)
        self.motor_tree.column('temp', width=100, anchor=tk.CENTER)
        self.motor_tree.column('pos_ticks', width=100, anchor=tk.CENTER)
        self.motor_tree.column('pos_rad', width=100, anchor=tk.CENTER)
        self.motor_tree.column('pos_deg', width=80, anchor=tk.CENTER)
        
        self.motor_tree.pack(fill=tk.BOTH, expand=True)
        
        # Заполнение таблицы начальными данными
        for i in range(6):
            self.motor_tree.insert('', 'end', values=(
                f'Мотор {i+1}', 
                '0.0', 
                '0', 
                '0.00', 
                '0'
            ))
        
        # Кнопка для ручного обновления данных
        ttk.Button(self.monitor_frame, text="Обновить данные", 
                  command=self.update_motor_monitor).pack(pady=5)

    def update_motor_monitor(self):
        """Обновление данных в таблице мониторинга моторов"""
        for i, item in enumerate(self.motor_tree.get_children()):
            self.motor_tree.item(item, values=(
                f'Мотор {i+1}',
                f'{self.motor_data["temp"][i]:.1f}',  # Температура с 1 знаком после запятой
                f'{self.motor_data["position_ticks"][i]}',  # Позиция в тиках
                f'{self.motor_data["position_rad"][i]:.2f}',  # Позиция в радианах (2 знака)
                f'{self.motor_data["position_deg"][i]}'  # Позиция в градусах
            ))

    def monitor_motors(self):
        """Фоновый поток для мониторинга состояния моторов"""
        while True:
            if self.system_state in ["ready", "running", "paused"]:
                # Генерация тестовых данных
                for i in range(6):
                    self.motor_data['temp'][i] = random.uniform(25.0, 45.0)  # Температура
                    self.motor_data['position_ticks'][i] = int(self.joint_angles[i] * 10)  # Тики
                    self.motor_data['position_rad'][i] = math.radians(self.joint_angles[i])  # Радианы
                    self.motor_data['position_deg'][i] = self.joint_angles[i]  # Градусы
                
                # Обновление интерфейса в основном потоке
                self.master.after(0, self.update_motor_monitor)
                
                # Проверка на перегрев
                if any(temp > 60 for temp in self.motor_data['temp']):
                    self.emergency_stop("Перегрев двигателей")
            
            time.sleep(1)  # Пауза между обновлениями

    def create_power_controls(self):
        """Создание кнопок управления питанием"""
        frame = ttk.Frame(self.control_frame)
        frame.pack(fill=tk.X, pady=5)
        
        # Кнопка включения
        self.power_on_btn = ttk.Button(frame, text="Вкл", command=self.power_on)
        self.power_on_btn.pack(side=tk.LEFT, expand=True, padx=2)
        
        # Кнопка выключения (изначально отключена)
        self.power_off_btn = ttk.Button(frame, text="Выкл", command=self.power_off, state=tk.DISABLED)
        self.power_off_btn.pack(side=tk.LEFT, expand=True, padx=2)
        
        # Кнопка паузы (изначально отключена)
        self.pause_btn = ttk.Button(frame, text="Пауза", command=self.pause, state=tk.DISABLED)
        self.pause_btn.pack(side=tk.LEFT, expand=True, padx=2)

    def power_on(self):
        """Включение системы"""
        self.system_state = "ready"
        self.update_system_state()
        # Переключение состояний кнопок
        self.power_on_btn.config(state=tk.DISABLED)
        self.power_off_btn.config(state=tk.NORMAL)
        self.pause_btn.config(state=tk.NORMAL)
        self.logger.info("Система включена и готова к работе")
        
        # Задержка для имитации инициализации
        self.master.after(1000, lambda: self.update_status("Система готова к работе", "green"))

    def power_off(self):
        """Выключение системы"""
        if self.system_state == "emergency":
            messagebox.showwarning("Авария", "Невозможно выключить систему в аварийном режиме")
            return
            
        self.system_state = "off"
        self.update_system_state()
        # Переключение состояний кнопок
        self.power_on_btn.config(state=tk.NORMAL)
        self.power_off_btn.config(state=tk.DISABLED)
        self.pause_btn.config(state=tk.DISABLED)
        self.logger.info("Система выключена")
        self.update_status("Система выключена", "red")

    def pause(self):
        """Постановка системы на паузу/снятие с паузы"""
        if self.system_state == "running":
            self.system_state = "paused"
            self.pause_btn.config(text="Продолжить")
            self.logger.info("Работа приостановлена")
            self.update_status("Система на паузе", "orange")
        elif self.system_state == "paused":
            self.system_state = "running"
            self.pause_btn.config(text="Пауза")
            self.logger.info("Работа продолжена")
            self.update_status("Система работает", "green")
        
        self.update_system_state()

    def update_system_state(self):
        """Обновление всех элементов интерфейса при изменении состояния системы"""
        # Соответствие состояний тексту и цвету
        states = {
            "off": ("Система выключена", "red"),
            "ready": ("Система готова к работе", "green"),
            "running": ("Система работает", "green"),
            "paused": ("Система на паузе", "orange"),
            "emergency": ("АВАРИЙНАЯ ОСТАНОВКА!", "red")
        }
        
        # Обновление метки состояния
        text, color = states.get(self.system_state, ("Неизвестное состояние", "black"))
        self.state_label.config(text=f"Состояние: {text.upper()}")
        
        # Обновление светофора
        self.update_traffic_light()
        
        # Блокировка/разблокировка элементов управления
        state = tk.NORMAL if self.system_state in ["ready", "running", "paused"] else tk.DISABLED
        for i in range(6):
            getattr(self, f"joint_{i}_scale").config(state=state)
        self.gripper_btn.config(state=state)
        
        # Кнопка аварийной остановки
        if self.system_state != "emergency":
            self.emergency_btn.config(state=state)

    def create_joint_controls(self):
        """Создание элементов управления для каждого сустава"""
        joints = ["Основание", "Плечо", "Локоть", "Запястье", "Поворот захвата", "Вращение инструмента"]

        for i, joint in enumerate(joints):
            frame = ttk.Frame(self.control_frame)
            frame.pack(fill=tk.X, pady=5)

            # Метка с названием сустава
            label = ttk.Label(frame, text=f"{joint}:")
            label.pack(side=tk.LEFT, padx=5)

            # Слайдер для управления углом
            scale = ttk.Scale(frame, from_=0, to=180, value=0,
                              command=lambda val, idx=i: self.update_joint_angle(val, idx))
            scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

            # Метка для отображения текущего угла
            value_label = ttk.Label(frame, text="0°", width=5)
            value_label.pack(side=tk.LEFT, padx=5)

            # Сохранение ссылок на элементы для последующего доступа
            setattr(self, f"joint_{i}_scale", scale)
            setattr(self, f"joint_{i}_label", value_label)

    def create_gripper_control(self):
        """Создание элементов управления захватом"""
        frame = ttk.Frame(self.control_frame)
        frame.pack(fill=tk.X, pady=10)

        # Метка состояния захвата
        self.gripper_label = ttk.Label(frame, text="Захват: Открыт")
        self.gripper_label.pack(side=tk.LEFT, padx=5)

        # Кнопка переключения состояния
        self.gripper_btn = ttk.Button(frame, text="Закрыть", command=self.toggle_gripper)
        self.gripper_btn.pack(side=tk.RIGHT, padx=5)

    def create_movement_style_controls(self):
        """Создание переключателей стиля движения"""
        frame = ttk.LabelFrame(self.control_frame, text="Стиль движения", padding=10)
        frame.pack(fill=tk.X, pady=10)
        
        # Переменная для хранения выбранного стиля
        self.movement_style = tk.StringVar(value="normal")
        
        # Варианты стилей движения
        ttk.Radiobutton(frame, text="Обычный", variable=self.movement_style, 
                       value="normal", command=self.update_movement_style).pack(side=tk.LEFT)
        ttk.Radiobutton(frame, text="Точный", variable=self.movement_style, 
                       value="precise", command=self.update_movement_style).pack(side=tk.LEFT)
        ttk.Radiobutton(frame, text="Быстрый", variable=self.movement_style, 
                       value="rapid", command=self.update_movement_style).pack(side=tk.LEFT)

    def update_movement_style(self):
        """Обновление стиля движения робота"""
        style = self.movement_style.get()
        styles = {
            "normal": "Обычный режим движения",
            "precise": "Точный режим движения",
            "rapid": "Быстрый режим движения"
        }
        self.logger.info(f"Изменен стиль движения: {styles[style]}")
        self.update_status(styles[style], "blue")

    def create_utility_buttons(self):
        """Создание служебных кнопок"""
        frame = ttk.Frame(self.control_frame)
        frame.pack(fill=tk.X, pady=10)

        # Кнопка возврата в домашнее положение
        ttk.Button(frame, text="Домой", command=self.home_position).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        # Кнопка сброса системы
        ttk.Button(frame, text="Сброс", command=self.reset_robot).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        # Кнопка сохранения текущей позиции
        ttk.Button(frame, text="Сохранить", command=self.save_position).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        # Фрейм для кнопки аварийной остановки
        emergency_frame = ttk.Frame(self.control_frame)
        emergency_frame.pack(fill=tk.X, pady=10)

        # Сама кнопка аварийной остановки
        self.emergency_btn = ttk.Button(emergency_frame, text="АВАРИЙНАЯ ОСТАНОВКА",
                                      style='Emergency.TButton', command=lambda: self.emergency_stop("Ручная активация"))
        self.emergency_btn.pack(fill=tk.X, expand=True)
        # Стиль для кнопки аварийной остановки
        self.style.configure('Emergency.TButton', foreground='white', background='red', font=('Arial', 12, 'bold'))

    def update_joint_angle(self, value, joint_idx):
        """Обновление угла сустава"""
        if self.system_state not in ["ready", "running", "paused"]:
            return
            
        # Округление значения угла
        angle = round(float(value))
        self.joint_angles[joint_idx] = angle
        # Обновление метки с углом
        getattr(self, f"joint_{joint_idx}_label").config(text=f"{angle}°")
        
        # Логирование изменения угла
        self.logger.debug(f"Сустав {joint_idx+1} установлен на {angle}°")
        
        # Обновление визуализации и статуса
        self.draw_robot()
        self.update_status(f"Сустав {joint_idx + 1} установлен на {angle}°")

    def toggle_gripper(self):
        """Переключение состояния захвата"""
        if self.system_state not in ["ready", "running", "paused"]:
            return
            
        # Инверсия состояния
        self.gripper_state = not self.gripper_state
        state = "Закрыт" if self.gripper_state else "Открыт"
        
        # Обновление интерфейса
        self.gripper_label.config(text=f"Захват: {state}")
        self.gripper_btn.config(text="Открыть" if self.gripper_state else "Закрыть")
        
        # Логирование
        self.logger.info(f"Захват {state.lower()}")
        
        # Обновление визуализации и статуса
        self.draw_robot()
        self.update_status(f"Захват {state.lower()}")

    def home_position(self):
        """Возврат робота в домашнее положение"""
        if self.system_state == "emergency":
            return
            
        # Сброс всех углов
        for i in range(6):
            getattr(self, f"joint_{i}_scale").set(0)
            self.joint_angles[i] = 0
            getattr(self, f"joint_{i}_label").config(text="0°")

        # Закрытие захвата, если он открыт
        if self.gripper_state:
            self.toggle_gripper()

        self.logger.info("Робот перемещен в домашнее положение")
        self.draw_robot()
        self.update_status("Робот в домашнем положении", "green")

    def reset_robot(self):
        """Сброс системы"""
        if self.system_state == "emergency":
            messagebox.showwarning("Авария", "Сначала устраните аварийную ситуацию")
            return
            
        # Подтверждение сброса
        if messagebox.askyesno("Сброс", "Вы уверены, что хотите сбросить робота?"):
            self.home_position()
            self.logger.warning("Система сброшена")
            self.update_status("Робот сброшен", "orange")

    def save_position(self):
        """Сохранение текущей позиции в файл"""
        data = {
            "joints": self.joint_angles,
            "gripper": self.gripper_state,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        try:
            # Запись в JSON-файл
            with open("positions.json", "a") as f:
                json.dump(data, f)
                f.write("\n")
            self.logger.info("Текущая позиция сохранена")
            self.update_status("Положение сохранено", "blue")
        except Exception as e:
            self.logger.error(f"Ошибка сохранения позиции: {str(e)}")
            self.update_status("Ошибка сохранения", "red")

    def emergency_stop(self, reason="Неизвестно"):
        """Аварийная остановка системы"""
        if self.system_state == "emergency":
            return
            
        self.system_state = "emergency"
        self.update_system_state()
        
        # Логирование аварии
        self.emergency_logger.critical(f"АВАРИЙНАЯ ОСТАНОВКА! Причина: {reason}")
        
        # Визуальное оповещение
        self.master.bell()  # Звуковой сигнал
        self.update_status(f"АВАРИЙНАЯ ОСТАНОВКА! Причина: {reason}", "red")
        messagebox.showerror("Аварийная остановка", f"Робот остановлен в аварийном режиме!\nПричина: {reason}")
        
        # Блокировка управления
        for i in range(6):
            getattr(self, f"joint_{i}_scale").config(state=tk.DISABLED)
        self.gripper_btn.config(state=tk.DISABLED)
        self.pause_btn.config(state=tk.DISABLED)

    def update_status(self, message, color="black"):
        """Обновление строки состояния"""
        self.status_label.config(text=message, foreground=color)

    def draw_robot(self):
        """Отрисовка робота на холсте"""
        self.canvas.delete("all")  # Очистка холста
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()

        # Параметры робота
        base_radius = 50  # Радиус основания
        link_lengths = [80, 120, 80, 40]  # Длины звеньев

        # Отрисовка основания
        x0, y0 = width // 2, height - 50  # Центр основания
        self.canvas.create_oval(x0 - base_radius, y0 - 20,
                              x0 + base_radius, y0 + 20, fill="gray", outline="black")

        # Преобразование углов в радианы
        angles = [math.radians(a) for a in self.joint_angles]

        # Сустав 1 (поворот основания)
        x1 = x0 + base_radius * math.cos(angles[0])
        y1 = y0 - base_radius * math.sin(angles[0])
        self.canvas.create_line(x0, y0, x1, y1, width=10, fill="blue")
        self.canvas.create_oval(x1 - 5, y1 - 5, x1 + 5, y1 + 5, fill="red")  # Маркер сустава

        # Сустав 2 (плечо)
        x2 = x1 + link_lengths[0] * math.cos(angles[0] + angles[1])
        y2 = y1 - link_lengths[0] * math.sin(angles[0] + angles[1])
        self.canvas.create_line(x1, y1, x2, y2, width=8, fill="green")
        self.canvas.create_oval(x2 - 5, y2 - 5, x2 + 5, y2 + 5, fill="red")  # Маркер сустава

        # Сустав 3 (локоть)
        x3 = x2 + link_lengths[1] * math.cos(angles[0] + angles[1] + angles[2])
        y3 = y2 - link_lengths[1] * math.sin(angles[0] + angles[1] + angles[2])
        self.canvas.create_line(x2, y2, x3, y3, width=6, fill="blue")
        self.canvas.create_oval(x3 - 5, y3 - 5, x3 + 5, y3 + 5, fill="red")  # Маркер сустава

        # Сустав 4 (запястье)
        x4 = x3 + link_lengths[2] * math.cos(sum(angles[:4]))
        y4 = y3 - link_lengths[2] * math.sin(sum(angles[:4]))
        self.canvas.create_line(x3, y3, x4, y4, width=4, fill="green")
        self.canvas.create_oval(x4 - 5, y4 - 5, x4 + 5, y4 + 5, fill="red")  # Маркер сустава

        # Захват
        gripper_width = 30 if self.gripper_state else 60  # Ширина раскрытия
        angle = sum(angles[:5]) + angles[5]  # Общий угол для захвата

        # Левая часть захвата
        x5_left = x4 + gripper_width * math.cos(angle + math.pi / 2)
        y5_left = y4 - gripper_width * math.sin(angle + math.pi / 2)
        self.canvas.create_line(x4, y4, x5_left, y5_left, width=3, fill="red")

        # Правая часть захвата
        x5_right = x4 + gripper_width * math.cos(angle - math.pi / 2)
        y5_right = y4 - gripper_width * math.sin(angle - math.pi / 2)
        self.canvas.create_line(x4, y4, x5_right, y5_right, width=3, fill="red")

        # Отображение текущих координат
        self.canvas.create_text(width // 2, 20,
                              text=f"Координаты: X={int(x4)}, Y={int(y4)}",
                              font=('Arial', 10))

        # Индикатор состояния системы (квадратик в углу)
        state_colors = {
            "off": "gray",
            "ready": "yellow",
            "running": "green",
            "paused": "orange",
            "emergency": "red"
        }
        self.canvas.create_rectangle(10, 10, 20, 20, fill=state_colors.get(self.system_state, "white"))

# Точка входа в программу
if __name__ == "__main__":
    root = tk.Tk()  # Создание главного
