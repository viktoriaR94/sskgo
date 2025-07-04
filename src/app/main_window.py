# -*- coding: utf-8 -*-
"""
Created on Fri Apr 25 11:52:01 2025

@author: sheshukova
"""

import sys
import pandas as pd
import random
import numpy as np


from PySide6.QtCharts import QChart, QChartView, QLineSeries, QDateTimeAxis, QValueAxis
from PySide6.QtCore import QDir, QAbstractTableModel, Qt, QDateTime, QThread, Signal, QModelIndex 
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QLabel, QHBoxLayout,  
                               QGridLayout, QMessageBox, QVBoxLayout, QTreeView,
                               QFileSystemModel, QTableView, QTableWidgetItem, QHeaderView)
from PySide6.QtGui import QPainter

class TableModel(QAbstractTableModel):
    def __init__(self, data, header = None, parent = None,
                 centered_cols_indices = None):
        super().__init__(parent)
        self._data = data
        self._centered_columns = {0, 1, 2} # Используем множество для эффективной проверки
        self._header = header if header else  []  # Обработка отсутствия заголовков
        
  
    def rowCount(self, parent = QModelIndex()):
        # The length of the outer list.
        return len(self._data) if self._data else 0

    def columnCount(self, parent = QModelIndex()):
        # The following takes the first sub-list, and returns
        # the length (only works if all rows are an equal length)
        return len(self._data[0]) + 1 if self._data else 0
    
    def data(self, index, role = Qt.DisplayRole):
        if not index.isValid():
            return None
        
        if role == Qt.TextAlignmentRole: # Запрашивается выравнивание текста
            column = index.column()
            if column in self._centered_columns:
                # Центрируем по горизонтали и вертикали
                return int(Qt.AlignCenter | Qt.AlignVCenter)
            else:
                # Оставляем по умолчанию слева, по центру по вертикали
                return int(Qt.AlignLeft | Qt.AlignVCenter)
            
        # --- Отображение данных ---
        elif role == Qt.DisplayRole:
            row = index.row()
            col = index.column()
            if col == 0:
                return str(row + 1)
            else:
                try:
                    # Возвращаем данные из нашеего списка списков
                    return str(self._data[row][col - 1]) # Преобразуем в строку
                except (IndexError, TypeError):
                    return None # Возвращаем None, если индекс выходит за границы
        return None
            
    def headerData(self, section, orientation, role = Qt.DisplayRole):
        # Метод для предоставления данных заголовков (шапки таблицы)
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                if section == 0:
                    return "№"
                elif 0 <= section - 1 < len(self._header):
                    return self._header[section - 1]
                else:
                    return None
            else:
                return str(section - 1)
                
            
class MyMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
            
        self.setWindowTitle('Главное окно с графиком')
        self.setGeometry(100, 100, 1200, 800)
             
        ### Центральный виджет ### 
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QGridLayout(central_widget)
        
        ### Создание FolderView ###
        
        # Выбираем папку
        self.folderView = QTreeView()
        self.folderModel = QFileSystemModel()
            
        # Меняем корневую папку!!!! (потому что лень клацать каждый раз до нужной директории, или можно положить проект в корневую папку)
        self.folderModel.setRootPath(QDir.rootPath())  #   Устанавливаем корневой путь модели
        self.folderView.setModel(self.folderModel)
         
        ##########################################################################################   
         
        # Устанавливаем корневой индекс для отображения в дереве
        target_dir = "C:/Users/sheshukova/Documents/diaprom/sskgo/2025-04-09"  # <- замените на желаемую директорию
        self.folderView.setRootIndex(self.folderModel.index(target_dir))
        
        self.folderModel.setFilter(QDir.NoDotAndDotDot | QDir.AllDirs)
        #  folderModel.setRootPath(QDir.currentPath()) ###
        self.folderView.selectionModel().selectionChanged.connect(self.folderView_selectionchanged)
        
        # Расшираяем место по первой папке  - раньше работало
        self.folderView.setColumnWidth(0, 220) # Ширина столбца "Name" - 200 пикселей
        self.folderView.setColumnWidth(1, 100) # Ширина столбца "Type" - 100 пикселей
        self.folderView.setColumnWidth(2, 100) # Ширина столбца "Size" - 80 пикселей
        
        #layout.addWidget(QLabel('Выберите папку: '))
        layout.addWidget(self.folderView, 0, 0, 1, 2)
        

        ### Создание FileView ###
        
        self.fileView = QTreeView()
    
        self.fileModel = QFileSystemModel()
        self.fileModel.setRootPath("/")
        self.fileModel.setFilter(QDir.NoDotAndDotDot | QDir.Files)
        self.fileView.setModel(self.fileModel)
        
        self.fileView.setColumnWidth(0, 220) # Ширина столбца "Name" - 200 пикселей
        self.fileView.setColumnWidth(1, 100) # Ширина столбца "Type" - 100 пикселей
        self.fileView.setColumnWidth(2, 80) # Ширина столбца "Size" - 80 пикселей
        
        #layout.addWidget(QLabel('Выберите файл: '))
        layout.addWidget(self.fileView, 0, 2, 1, 2)
        
            
        ### Создание ChartView ###
            
        self.chart = QChart()
        self.chartView = QChartView()
        self.chartView.setRenderHint(QPainter.Antialiasing)

        self.chartView.setChart(self.chart)
        self.chart.setAnimationOptions(QChart.SeriesAnimations)
        
        layout.addWidget(self.chartView, 1, 2, 1, 2)
        
        ### Создание TableView ###
        
        self.tableView = QTableView()
        
               
        # Пока создаем пустую модель. Она будет заменена при выборе файла.
        
        self.table_model = TableModel([], header = ['0', '1']) # Используем нашу модель
        self.tableView.setModel(self.table_model)
        self.tableView.setColumnWidth(1, 70)
        
       # main_layout.addWidget(QLabel("Данные из файла:")) # Метка
        layout.addWidget(self.tableView, 1, 0, 1, 1)
        
        # Выводим статистику по выбранному параметру

        self.label = QLabel()
        layout.addWidget(self.label, 1, 1, 1, 1)
        


        # --- Соединение сигналов ---
        
        # Соединяем сигнал изменения текущего элемента в fileView
        self.fileView.selectionModel().currentChanged.connect(self.fileView_selectionchanged)
        
        # --- Методы, которые будут вызваны из меню ---
        # Эти методы содержат логику действий меню
        self.create_menu_actions_methods() # Создадим эти методы
    
    def create_menu_actions_methods(self):
        # Определяем методы, которые будут вызываться через меню
        def new_file(self):
            QMessageBox.information(self, "Действие меню", "Выбрано: Создать")
            # Здесь ваша логика для создания нового файла/документа
            pass # Замените на реальную логику
    
        def open_file(self):
            QMessageBox.information(self, "Действие меню", "Выбрано: Открыть")
            # Здесь ваша логика для открытия файла
            pass # Замените на реальную логику
    
        def create_report(self):
            QMessageBox.information(self, "Действие меню", "Выбрано: Создать отчет")
            # Здесь ваша логика для сохранения файла
            pass # Замените на реальную логику
    
        def exit_application(self):
            QMessageBox.information(self, "Действие меню", "Выбрано: Выход")
            self.close() # Закрыть окно и выйти из приложения
    
        def show_about(self):
             QMessageBox.information(self, "О программе", "Это главное окно с графиком и таблицей.")
    
        # Добавляем эти методы как атрибуты экземпляра класса
        self.new_file = new_file.__get__(self, MyMainWindow)
        self.open_file = open_file.__get__(self, MyMainWindow)
        self.create_report = create_report.__get__(self, MyMainWindow)
        self.exit_application = exit_application.__get__(self, MyMainWindow)
        self.show_about = show_about.__get__(self, MyMainWindow)
            
    # Метод, который вызывается при выборе файла в folderView # 
    
    def folderView_selectionchanged(self):
        current_index = self.folderView.currentIndex()
        selected_folder_path = self.folderModel.fileInfo(current_index).absoluteFilePath()
        self.fileView.setRootIndex(self.fileModel.setRootPath(selected_folder_path))
        
    # Метод, который вызывается при выборе файла в fileView # 
        
    def fileView_selectionchanged(self, current_index):
        #current_file = self.fileView.currentIndex()
        selected_file_path = self.fileModel.fileInfo(current_index).absoluteFilePath()
        file_name = self.fileModel.fileName(current_index)
     
        # Проверяем, является ли выбранный элемент файлом, а не папкой
        if not self.fileModel.fileInfo(current_index).isFile():
             print(f"Выбрана папка или не файл: {selected_file_path}")
             # Очистить таблицу и график, если выбрана папка
             self.table_model = TableModel([]) # Пустая модель
             self.tableView.setModel(self.table_model)
             self.update_chart_data(pd.DataFrame()) # Обновляем график с пустым DataFrame
             return # Прекращаем выполнение
        
        print(f"Выбран файл: {selected_file_path}")

        try:
            # Читаем DataFrame здесь:
            df = pd.read_csv(selected_file_path, sep = '\t', header = None, 
                             index_col = False, decimal = ',') 
                       
            if df.shape[1] > 1:
                df = df.iloc[:, [0, 1]]
                df.columns = ['Время', file_name]
                try:
                    df[file_name] = df[file_name].round(2)
                except Exception as num_e:
                    print(f"Предупреждение: Не удалось преобразовать столбец '{file_name}' в числовой формат: '{num_e}'")
                    pass # Продолжает с тем, что есть
            else:
                print(f"В файле '{file_name}' недостаточно столбцов.")
                df = pd.DataFrame()
            
            if df.empty:
                 self.table_model = TableModel([])
                 self.tableView.setModel(self.table_model)
                 self.update_chart_data(pd.DataFrame())
                 QMessageBox.warning(self, "Ошибка данных", f"Не удалось обработать данные из файла '{file_name}'.")
                 return
                    
            
            # Преобразуем DataFrame в список списков
            self.table_model = TableModel(data = df.values.tolist(), 
                               header = ['ВРЕМЯ', file_name[: -4] if file_name.endswith('.csv') else file_name],    
                               centered_cols_indices = {1}) 
            
            self.tableView.setModel(self.table_model)
            
            # Настраиваем TableView
            # Столбцы существуют ?:
            if self.table_model.columnCount() > 0:
                self.tableView.setColumnWidth(0, 130) 
            if self.table_model.columnCount() > 1:
                self.tableView.setColumnWidth(1, 230)
                
            self.tableView.verticalHeader().setVisible(False)
            self.tableView.resizeColumnsToContents() # Если надо подогнать ширину
            
            self.update_chart(df)
            self.update_label(df)
        except Exception as e:
            print(f"Критическая ошибка при чтении файла: {e}")
            import traceback
            traceback.print_exc() 
            QMessageBox.critical(self, "Ошибка", f"Не удалось обработать файл '{file_name}':\n{e}")
            # Очищаем таблицу и график при ошибке
            self.table_model = TableModel([], header = 'Выберите файл')  
            self.tableView.setModel(self.table_model)
            self.update_chart(pd.DataFrame())
            
            
    def update_label(self, df):
        label = self.label
        
    
        #Можно вычислить среднее и СКО по всем данным сразу
        size_df = df.shape[0]
        mean = round(np.mean(df.iloc[:,1]), 2)
        stdev = round(np.std(df.iloc[:,1]), 2)
        med = round(np.median(df.iloc[:,1]), 2)
        label.setText(f"СТАТИСТИКА\n\nЧисло строк: {size_df} \nСреднее: {mean} \nМедиана: {med} \nСКО: {stdev}\n\n\n\n")
        
        
            
            
    def update_chart(self, df): # 
        chart = self.chart
        chart.removeAllSeries() # Очищаем предыдущие серии данных
        
        # удаляем старые оси
        for axis in chart.axes():
            chart.removeAxis(axis)
        
        if df.empty or len(df.columns) < 2:
            print("Файл не содержит достаточно данных для построения графика.")
            return
        
        df_copy = df.copy()
        
        try:
            df_copy[df_copy.columns[0]] = pd.to_datetime(df_copy[df_copy.columns[0]])
        except Exception as e:
            print(f"Ошибка преобразования столбца 'Время' в datetime: {e}")
            return
        
        df_copy.set_index(df_copy.columns[0], inplace = True)
        
        try:
            # Усредняем по 10 минут
            average = df_copy.resample('10min').mean()
            
        except Exception as e:
            print(f"Ошибка при попытке усреднить значения: {e}")
            
        if average.empty:
            print("Недостаточно данных для построения графика.")
            return
        
        series = QLineSeries()
        
        if len(average.columns) == 0:
            print("Данные после усреднения не содержат колонок со значениями.")
            return
        
        #value_column = average.columns[0]

        for index, value in average.iterrows():
            try:
                x = index.timestamp() * 1000
                y = float(round(value, 1))
                    
                series.append(x, y)
            except (ValueError, TypeError):
                continue # Просто пропускаем эту точку
                    
        if series.count() == 0:
            print("Не удалось добавить точки на график.")
            chart.update()
            return
        
        chart.addSeries(series)
        #    chart.setTitle(average.columns[0])
        chart.legend().setVisible(False)
        
        # Настройка осей (опционально):
        #chart.createDefaultAxes()
        axis_x = QDateTimeAxis()
        axis_x.setFormat("dd.MM.yyyy. hh:mm")
        axis_x.setTickCount(10)
        axis_x.setLabelsAngle(70)
        axis_x.setTitleText('Время')
            
        axis_y = QValueAxis()
        axis_y.setTitleText(df.columns[1][:-4])
        
        if df.columns[1][:-6] == 'ПЛОТ ПОТОКА НЕЙТР':
            chart.setTitle('ПЛОТНОСТЬ ПОТОКА НЕЙТРОНОВ')
        else:
            chart.setTitle(df.columns[1][:-4])
            
        #axis_y.setRange(df_copy.min().values[0], df_copy.max().values[0])
        
        chart.addAxis(axis_x, Qt.AlignBottom)
        
        chart.addAxis(axis_y, Qt.AlignLeft)
                
        
        series.attachAxis(axis_x)
        series.attachAxis(axis_y)
        
        
        chart.update()
        



