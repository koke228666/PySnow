import sys
import random
import json
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QMenu, QSystemTrayIcon, QAction
)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QPainter, QColor, QPen, QIcon, QPixmap

# Основные параметры снегопада
config = {
    "fps": 60, #FPS
    "fall_speed": 2, #скорость падения
    "min_size": 2, #минимальный размер снежинки
    "max_size": 6, #максимальный размер снежинки
    "snowflake_frequency": 5, #плотность снежинок (меньше = больше)
    "snowflake_color": "#FFFFFF", #цвет снежинки
    "outline_color": "#000000", #цвет обводки
    "outline_width": 0, #толщина обводки (-1 = выкл, 0 = 1 пкс., 1 = 2 пкс., ...)
    "rainbow_mode": False, #случайный цвет новой снежинки
    "vibration_intensity": 0.5 #мощность "вибрации"
}

# Путь к файлу конфигурации
CONFIG_FILE = "config.json"

# Загрузка конфигурации из файла
def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as file:
            data = json.load(file)
            data["snowflake_color"] = data["snowflake_color"]
            data["outline_color"] = data["outline_color"]
            return data
    else:
        with open(CONFIG_FILE, "w") as file:
            json.dump(config, file, indent=4)
        return config



# Загружаем конфигурацию
config = load_config()

# Основное окно
class SnowfallApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.snowflakes = []
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_snowflakes)
        self.timer.start(1000 // config["fps"])
        self.paused = False
        self.initTrayIcon()

    def initUI(self):
        # Убираем рамку окна и делаем фон прозрачным
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setGeometry(0, 0, QApplication.desktop().screenGeometry().width(), QApplication.desktop().screenGeometry().height())

    def initTrayIcon(self):
        # Создаём иконку для трея
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(self.createSnowflakeIcon())
        self.tray_icon.setToolTip("PySnow")

        # Создаём контекстное меню
        menu = QMenu()
        pause_action = QAction("Пауза", self)
        pause_action.triggered.connect(self.togglePause)
        stop_action = QAction("Остановить", self)
        stop_action.triggered.connect(self.stop)
        menu.addAction(pause_action)
        menu.addAction(stop_action)

        self.tray_icon.setContextMenu(menu)
        self.tray_icon.show()

    def createSnowflakeIcon(self):
        # Генерируем иконку снежинки
        pixmap = QPixmap(32, 32)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(QPen(Qt.black, 2))
        painter.setBrush(Qt.white)
        painter.drawEllipse(4, 4, 24, 24)
        painter.end()
        return QIcon(pixmap)

    def togglePause(self):
        self.paused = not self.paused
        if self.paused:
            self.timer.stop()
        else:
            self.timer.start(1000 // config["fps"])

    def stop(self):
        self.timer.stop()
        self.tray_icon.hide()
        QApplication.quit()  # Явно завершаем приложение

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        for snowflake in self.snowflakes:
            painter.setPen(QPen(QColor(snowflake["outline_color"]), config["outline_width"]))
            painter.setBrush(QColor(snowflake["color"]))
            painter.drawEllipse(int(snowflake["x"]), int(snowflake["y"]), snowflake["size"], snowflake["size"])

    def update_snowflakes(self):
        if not self.paused:
            # Создание снежинок
            if random.randint(1, config["snowflake_frequency"]) == config["snowflake_frequency"]:
                self.create_snowflake()

            # Падение снежинок
            for snowflake in self.snowflakes:
                snowflake["y"] += config["fall_speed"]
                snowflake["x"] += random.uniform(-config["vibration_intensity"], config["vibration_intensity"])
                if snowflake["y"] > self.height():
                    self.snowflakes.remove(snowflake)

            self.update()

    def create_snowflake(self):
        x = random.randint(0, self.width())
        y = 0
        size = random.randint(config["min_size"], config["max_size"])
        color = config["snowflake_color"] if not config["rainbow_mode"] else QColor(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        self.snowflakes.append({"x": x, "y": y, "size": size, "color": color, "outline_color": config["outline_color"]})

# Запуск приложения
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SnowfallApp()
    window.show()
    sys.exit(app.exec_())