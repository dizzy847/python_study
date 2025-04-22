import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import math
import time
import json
import logging
from logging.handlers import RotatingFileHandler
import random
import threading


class RobotARM_IMR165_GUI:
    def __init__(self, master):
        self.master = master
        master.title("Управление роботом ARM-IMR-165")
        master.geometry("1200x800")

        # Инициализация системы
        self.system_state = "off"
        self.movement_style = "normal"
        self.connection_status = True
        self.joint_angles = [0] * 6
        self.gripper_state = False
        self.motor_data = {'temp': [0.0] * 6, 'position_ticks': [0] * 6, 'position_rad': [0.0] * 6,
                           'position_deg': [0] * 6}

        self.setup_logging()
        self.create_widgets()
        self.update_status("Система выключена", "red")
        threading.Thread(target=self.monitor_motors, daemon=True).start()

    def setup_logging(self):
        self.logger = logging.getLogger('robot_logger')
        self.logger.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

        handlers = [
            RotatingFileHandler('robot_system.log', maxBytes=16, backupCount=3),
            logging.FileHandler('emergency.log'),
            logging.StreamHandler()
        ]
        for handler in handlers:
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def create_widgets(self):
        # Основные фреймы
        main_frame = ttk.Frame(self.master)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Левая панель
        left_panel = ttk.Frame(main_frame)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Правая панель
        right_panel = ttk.Frame(main_frame)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=False)

        # Создание компонентов
        self.create_state_indicators(left_panel)
        self.create_control_panel(left_panel)
        self.create_log_panel(left_panel)
        self.create_visualization_panel(right_panel)
        self.create_motor_monitor(right_panel)
        self.status_label = ttk.Label(main_frame, text="Готов к работе", relief=tk.SUNKEN)
        self.status_label.pack(fill=tk.X, ipady=5)

    def create_state_indicators(self, parent):
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=5)

        # Светофор
        traffic_frame = ttk.Frame(frame)
        traffic_frame.pack(side=tk.LEFT, padx=10)
        self.lights = {}
        for color in ['red', 'yellow', 'green']:
            canvas = tk.Canvas(traffic_frame, width=30, height=30, bg='white', bd=2, relief='ridge')
            canvas.pack(pady=2)
            canvas.create_oval(5, 5, 25, 25, fill='gray', outline='black', tags=color)
            self.lights[color] = canvas

        self.state_label = ttk.Label(frame, text="Состояние: ВЫКЛ", font=('Arial', 12))
        self.state_label.pack(side=tk.LEFT, expand=True)
        self.connection_label = ttk.Label(frame, text="Связь: ОК", foreground='green')
        self.connection_label.pack(side=tk.RIGHT, padx=10)

    def create_control_panel(self, parent):
        frame = ttk.LabelFrame(parent, text="Управление манипулятором", padding=10)
        frame.pack(fill=tk.BOTH, expand=True)

        # Кнопки управления
        power_frame = ttk.Frame(frame)
        power_frame.pack(fill=tk.X, pady=5)
        self.power_on_btn = ttk.Button(power_frame, text="Вкл", command=self.power_on)
        self.power_on_btn.pack(side=tk.LEFT, expand=True, padx=2)
        self.power_off_btn = ttk.Button(power_frame, text="Выкл", command=self.power_off, state=tk.DISABLED)
        self.power_off_btn.pack(side=tk.LEFT, expand=True, padx=2)
        self.pause_btn = ttk.Button(power_frame, text="Пауза", command=self.pause, state=tk.DISABLED)
        self.pause_btn.pack(side=tk.LEFT, expand=True, padx=2)

        # Управление суставами
        joints = ["Основание", "Плечо", "Локоть", "Запястье", "Поворот захвата", "Вращение инструмента"]
        for i, joint in enumerate(joints):
            f = ttk.Frame(frame)
            f.pack(fill=tk.X, pady=3)
            ttk.Label(f, text=f"{joint}:").pack(side=tk.LEFT, padx=5)
            scale = ttk.Scale(f, from_=0, to=180, value=0, command=lambda v, idx=i: self.update_joint_angle(v, idx))
            scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
            setattr(self, f"joint_{i}_scale", scale)
            setattr(self, f"joint_{i}_label", ttk.Label(f, text="0°", width=5))
            getattr(self, f"joint_{i}_label").pack(side=tk.LEFT, padx=5)

        # Захват
        f = ttk.Frame(frame)
        f.pack(fill=tk.X, pady=10)
        self.gripper_label = ttk.Label(f, text="Захват: Открыт")
        self.gripper_label.pack(side=tk.LEFT, padx=5)
        self.gripper_btn = ttk.Button(f, text="Закрыть", command=self.toggle_gripper)
        self.gripper_btn.pack(side=tk.RIGHT, padx=5)

        # Стиль движения
        f = ttk.LabelFrame(frame, text="Стиль движения", padding=10)
        f.pack(fill=tk.X, pady=10)
        self.movement_style = tk.StringVar(value="normal")
        for text, mode in [("Обычный", "normal"), ("Точный", "precise"), ("Быстрый", "rapid")]:
            ttk.Radiobutton(f, text=text, variable=self.movement_style, value=mode,
                            command=self.update_movement_style).pack(side=tk.LEFT)

        # Утилиты
        f = ttk.Frame(frame)
        f.pack(fill=tk.X, pady=10)
        for text, cmd in [("Домой", self.home_position), ("Сброс", self.reset_robot),
                          ("Сохранить", self.save_position)]:
            ttk.Button(f, text=text, command=cmd).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        # Аварийная кнопка (исправлено - сохраняем в self.emergency_btn)
        self.emergency_btn = ttk.Button(frame, text="АВАРИЙНАЯ ОСТАНОВКА", style='Emergency.TButton',
                                        command=lambda: self.emergency_stop("Ручная активация"))
        self.emergency_btn.pack(fill=tk.X, pady=10)
        ttk.Style().configure('Emergency.TButton', foreground='white', background='red', font=('Arial', 12, 'bold'))

    def create_log_panel(self, parent):
        frame = ttk.LabelFrame(parent, text="Логи системы", padding=10)
        frame.pack(fill=tk.BOTH, expand=True)

        self.log_text = scrolledtext.ScrolledText(frame, width=80, height=15)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        self.log_text.configure(state='disabled')

        class TextHandler(logging.Handler):
            def __init__(self, text):
                super().__init__()
                self.text = text

            def emit(self, record):
                self.text.configure(state='normal')
                self.text.insert(tk.END, self.format(record) + '\n')
                self.text.configure(state='disabled')
                self.text.see(tk.END)

        handler = TextHandler(self.log_text)
        handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        self.logger.addHandler(handler)

    def create_visualization_panel(self, parent):
        frame = ttk.LabelFrame(parent, text="Визуализация", padding=10)
        frame.pack(fill=tk.BOTH, expand=True)
        self.canvas = tk.Canvas(frame, bg='white', width=400, height=400)
        self.canvas.pack(fill=tk.BOTH, expand=True)

    def create_motor_monitor(self, parent):
        frame = ttk.LabelFrame(parent, text="Мониторинг моторов", padding=10)
        frame.pack(fill=tk.BOTH, expand=True)

        self.motor_tree = ttk.Treeview(frame, columns=('motor', 'temp', 'pos_ticks', 'pos_rad', 'pos_deg'),
                                       show='headings', height=6)
        for col, text in [('motor', 'Мотор'), ('temp', 'Темп (°C)'), ('pos_ticks', 'Поз. (тики)'),
                          ('pos_rad', 'Поз. (рад)'), ('pos_deg', 'Поз. (°)')]:
            self.motor_tree.heading(col, text=text)
            self.motor_tree.column(col, width=80 if col == 'motor' else 100, anchor=tk.CENTER)
        self.motor_tree.pack(fill=tk.BOTH, expand=True)

        for i in range(6):
            self.motor_tree.insert('', 'end', values=(f'Мотор {i + 1}', '0.0', '0', '0.00', '0'))

        ttk.Button(frame, text="Обновить данные", command=self.update_motor_monitor).pack(pady=5)

    def update_motor_monitor(self):
        for i, item in enumerate(self.motor_tree.get_children()):
            self.motor_tree.item(item, values=(
                f'Мотор {i + 1}',
                f'{self.motor_data["temp"][i]:.1f}',
                f'{self.motor_data["position_ticks"][i]}',
                f'{self.motor_data["position_rad"][i]:.2f}',
                f'{self.motor_data["position_deg"][i]}'
            ))

    def monitor_motors(self):
        while True:
            if self.system_state in ["ready", "running", "paused"]:
                for i in range(6):
                    self.motor_data['temp'][i] = random.uniform(25.0, 45.0)
                    self.motor_data['position_ticks'][i] = int(self.joint_angles[i] * 10)
                    self.motor_data['position_rad'][i] = math.radians(self.joint_angles[i])
                    self.motor_data['position_deg'][i] = self.joint_angles[i]

                self.master.after(0, self.update_motor_monitor)
                if any(temp > 60 for temp in self.motor_data['temp']):
                    self.emergency_stop("Перегрев двигателей")
            time.sleep(1)

    def power_on(self):
        self.system_state = "ready"
        self.update_system_state()
        self.power_on_btn.config(state=tk.DISABLED)
        self.power_off_btn.config(state=tk.NORMAL)
        self.pause_btn.config(state=tk.NORMAL)
        self.logger.info("Система включена")
        self.update_status("Система готова", "green")

    def power_off(self):
        if self.system_state == "emergency":
            messagebox.showwarning("Авария", "Невозможно выключить в аварийном режиме")
            return

        # Подтверждение выключения
        if not messagebox.askyesno("Подтверждение", "Вы уверены, что хотите выключить систему?"):
            return

        # Возврат в домашнее положение
        self.home_position()

        # Выключение системы
        self.system_state = "off"
        self.update_system_state()
        self.power_on_btn.config(state=tk.NORMAL)
        self.power_off_btn.config(state=tk.DISABLED)
        self.pause_btn.config(state=tk.DISABLED)
        self.logger.info("Система выключена")
        self.update_status("Система выключена", "red")

    def pause(self):
        if self.system_state == "running":
            self.system_state = "paused"
            self.pause_btn.config(text="Продолжить")
            self.logger.info("Пауза")
            self.update_status("Пауза", "orange")
        elif self.system_state == "paused":
            self.system_state = "running"
            self.pause_btn.config(text="Пауза")
            self.logger.info("Продолжение")
            self.update_status("Работает", "green")
        self.update_system_state()

    def update_system_state(self):
        states = {
            "off": ("Выключена", "red"),
            "ready": ("Готова", "green"),
            "running": ("Работает", "green"),
            "paused": ("Пауза", "orange"),
            "emergency": ("АВАРИЯ!", "red")
        }
        text, color = states.get(self.system_state, ("Неизвестно", "black"))
        self.state_label.config(text=f"Состояние: {text}")

        for color in self.lights:
            self.lights[color].itemconfig(color, fill='gray')
        if self.system_state == "off":
            self.lights['red'].itemconfig('red', fill='red')
        elif self.system_state == "ready":
            self.lights['yellow'].itemconfig('yellow', fill='yellow')
        elif self.system_state == "running":
            self.lights['green'].itemconfig('green', fill='green')
        elif self.system_state == "paused":
            self.lights['yellow'].itemconfig('yellow', fill='yellow')
        elif self.system_state == "emergency":
            self.lights['red'].itemconfig('red', fill='red')
            self.master.after(500, self.blink_red_light)

        state = tk.NORMAL if self.system_state in ["ready", "running", "paused"] else tk.DISABLED
        for i in range(6):
            getattr(self, f"joint_{i}_scale").config(state=state)
        self.gripper_btn.config(state=state)
        if hasattr(self, "emergency_btn"):
            self.emergency_btn.config(state=state)

    def blink_red_light(self):
        if self.system_state == "emergency":
            current = self.lights['red'].itemcget('red', 'fill')
            self.lights['red'].itemconfig('red', fill='gray' if current == 'red' else 'red')
            self.master.after(500, self.blink_red_light)

    def update_joint_angle(self, value, joint_idx):
        if self.system_state not in ["ready", "running", "paused"]: return
        angle = round(float(value))
        self.joint_angles[joint_idx] = angle
        getattr(self, f"joint_{joint_idx}_label").config(text=f"{angle}°")
        self.logger.debug(f"Сустав {joint_idx + 1} установлен на {angle}°")
        self.draw_robot()

    def toggle_gripper(self):
        if self.system_state not in ["ready", "running", "paused"]: return
        self.gripper_state = not self.gripper_state
        state = "Закрыт" if self.gripper_state else "Открыт"
        self.gripper_label.config(text=f"Захват: {state}")
        self.gripper_btn.config(text="Открыть" if self.gripper_state else "Закрыть")
        self.logger.info(f"Захват {state.lower()}")
        self.draw_robot()

    def update_movement_style(self):
        style = self.movement_style.get()
        styles = {"normal": "Обычный", "precise": "Точный", "rapid": "Быстрый"}
        self.logger.info(f"Стиль движения: {styles[style]}")
        self.update_status(f"Режим: {styles[style]}", "blue")

    def home_position(self):
        if self.system_state == "emergency": return
        for i in range(6):
            getattr(self, f"joint_{i}_scale").set(0)
            self.joint_angles[i] = 0
            getattr(self, f"joint_{i}_label").config(text="0°")
        if self.gripper_state: self.toggle_gripper()
        self.logger.info("Домашняя позиция")
        self.draw_robot()

    def reset_robot(self):
        if self.system_state == "emergency":
            messagebox.showwarning("Авария", "Сначала устраните аварию")
            return
        if messagebox.askyesno("Сброс", "Сбросить робота?"):
            self.home_position()
            self.logger.warning("Сброс системы")

    def save_position(self):
        data = {"joints": self.joint_angles, "gripper": self.gripper_state,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")}
        try:
            with open("positions.json", "a") as f:
                json.dump(data, f)
                f.write("\n")
            self.logger.info("Позиция сохранена")
            self.update_status("Позиция сохранена", "blue")
        except Exception as e:
            self.logger.error(f"Ошибка сохранения: {str(e)}")
            self.update_status("Ошибка сохранения", "red")

    def emergency_stop(self, reason="Неизвестно"):
        if self.system_state == "emergency": return
        self.system_state = "emergency"
        self.update_system_state()
        self.logger.critical(f"АВАРИЯ! Причина: {reason}")
        self.master.bell()
        self.update_status(f"АВАРИЯ! Причина: {reason}", "red")
        messagebox.showerror("Авария", f"Аварийная остановка!\nПричина: {reason}")

    def update_status(self, message, color="black"):
        self.status_label.config(text=message, foreground=color)

    def draw_robot(self):
        self.canvas.delete("all")
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        base_radius, lengths = 50, [80, 120, 80, 40]
        x0, y0 = w // 2, h - 50
        self.canvas.create_oval(x0 - base_radius, y0 - 20, x0 + base_radius, y0 + 20, fill="gray", outline="black")

        angles = [math.radians(a) for a in self.joint_angles]
        points = [(x0, y0)]
        for i in range(4):
            x = points[-1][0] + (base_radius if i == 0 else lengths[i - 1]) * math.cos(sum(angles[:i + 1]))
            y = points[-1][1] - (base_radius if i == 0 else lengths[i - 1]) * math.sin(sum(angles[:i + 1]))
            points.append((x, y))
            self.canvas.create_line(points[-2][0], points[-2][1], x, y,
                                    width=10 - 2 * i, fill=["blue", "green"][i % 2])
            self.canvas.create_oval(x - 5, y - 5, x + 5, y + 5, fill="red")

        gripper_width = 30 if self.gripper_state else 60
        angle = sum(angles[:5]) + angles[5]
        for side in [math.pi / 2, -math.pi / 2]:
            x = points[-1][0] + gripper_width * math.cos(angle + side)
            y = points[-1][1] - gripper_width * math.sin(angle + side)
            self.canvas.create_line(points[-1][0], points[-1][1], x, y, width=3, fill="red")

        self.canvas.create_text(w // 2, 20, text=f"Координаты: X={int(points[-1][0])}, Y={int(points[-1][1])}",
                                font=('Arial', 10))
        colors = {"off": "gray", "ready": "yellow", "running": "green", "paused": "orange", "emergency": "red"}
        self.canvas.create_rectangle(10, 10, 20, 20, fill=colors.get(self.system_state, "white"))


if __name__ == "__main__":
    root = tk.Tk()
    app = RobotARM_IMR165_GUI(root)
    root.mainloop()
