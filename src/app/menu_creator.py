# -*- coding: utf-8 -*-
"""
Created on Tue May 20 11:24:42 2025

@author: sheshukova
"""
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMenuBar, QMainWindow
# Не нужно импортировать QMainWindow здесь, так как мы получаем объект окна как аргумент

def create_main_menu(window: QMainWindow):
    """
    Создает и добавляет верхнее меню к заданному окну QMainWindow.

    Args:
        window: Экземпляр класса QMainWindow, к которому нужно добавить меню.
                Ожидается, что у этого объекта есть методы для действий меню.
    """
    # Получаем объект меню бара окна
    menu_bar = window.menuBar()
    # Если меню бара нет (например, если вы не используете QMainWindow),
    # возможно, нужно его создать: menu_bar = QMenuBar(window)
    # Но для QMainWindow метод menuBar() возвращает существующий или создает его при первом вызове.

    # --- Создаем меню "Файл" ---
    file_menu = menu_bar.addMenu("Файл")

    # Создаем действия (QAction) и связываем их с методами окна
    # ВАЖНО: Методы new_file, open_file, save_file, exit_application должны
    # существовать в классе MyMainWindow в файле main_window_ui.py
    new_action = QAction("Создать", window) # указываем родителя
    new_action.triggered.connect(window.new_file) # Соединяем с методом окна

    open_action = QAction("Открыть...", window)
    open_action.triggered.connect(window.open_file)

    save_action = QAction("Сохранить", window)
    save_action.triggered.connect(window.create_report)

    # Можно добавить разделитель
    file_menu.addSeparator()

    exit_action = QAction("Выход", window)
    exit_action.triggered.connect(window.exit_application)


    # Добавляем действия в меню "Файл"
    file_menu.addAction(new_action)
    file_menu.addAction(open_action)
    file_menu.addAction(save_action)
    file_menu.addSeparator() # Разделитель
    file_menu.addAction(exit_action)

    # --- Создаем меню "Справка" ---
    help_menu = menu_bar.addMenu("Справка")

    about_action = QAction("О программе", window)
    about_action.triggered.connect(window.show_about) # Соединяем с методом окна
    help_menu.addAction(about_action)
