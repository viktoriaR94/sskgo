# -*- coding: utf-8 -*-
"""
Created on Tue May 20 11:28:58 2025

@author: sheshukova
"""

# main_app.py

import sys
from PySide6.QtWidgets import QApplication

# Импортируем класс главного окна из main_window_ui.py  
from main_window import MyMainWindow

# Импортируем функцию создания меню из menu_creator.py
from menu_creator import create_main_menu




if __name__ == '__main__':
    if not QApplication.instance():
        app = QApplication(sys.argv)
    else:
        app = QApplication.instance()

    # Создаем экземпляр нашего главного окна
    mainWindow = MyMainWindow()

    # Вызываем функцию из menu_creator.py, передавая ей наш объект окна
    create_main_menu(mainWindow)

    # Показываем окно
    mainWindow.show()

    # Запускаем цикл приложения
    sys.exit(app.exec_())# if __name__ == "__main__":
        
    #     if not QApplication.instance():
    #         app = QApplication(sys.argv)
    #     else:
    #         app = QApplication.instance()

    #     window = MyMainWindow()
    #     window.show()

    # sys.exit(app.exec())