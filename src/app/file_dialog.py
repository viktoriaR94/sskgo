# -*- coding: utf-8 -*-
"""
Created on Fri Apr 25 11:52:01 2025

@author: sheshukova
"""

import sys
import pandas as pd
import random

from PySide6.QtCharts import QChart, QChartView, QLineSeries, QDateTimeAxis, QValueAxis
from PySide6.QtCore import QDir, QAbstractTableModel, Qt, QDateTime, QThread, Signal 
from PySide6.QtWidgets import (QApplication, QWidget, QHBoxLayout, QVBoxLayout, QGridLayout,
                                QTreeView, QFileSystemModel, QTableView, QTableWidgetItem, QHeaderView)
from PySide6.QtGui import QPainter


#from topmenu import MyWindow
 




class ChartThread(QThread):
    chart_updated = Signal(QLineSeries)
    
    def __init__(self, df, column_y_name):
        super().__init__()
        self.df = df
        self.column_y_name = column_y_name
        
        
        
    def run(self):
        try:
            # преобразование столбца "Время" в тип datetime
            self.df['Время'] = pd.to_datetime(self.df['Время'])
            # группируем данные по минутам 
            
            df_resampled = self.df.resample('1Min', on = 'Время').mean()
            print(df_resampled)
            # создаем qlineseries
            series = QLineSeries()
            for i in range(len(df_resampled)):
                try:
                    x = df_resampled.index[i].timestamp() * 1000  #используем индекс время
                    y = float(df_resampled).iloc[i , 0]
                    series.append(x, y)
                except (ValueError, TypeError, IndexError) as e:
                    print(f"Ошибка преобразования данных в строке {i+1}: {e}")
                    continue

            self.chart_updated.emit(series)

        except Exception as e: # Обрабатываем исключения внутри run()
            print(f"Ошибка в потоке: {e}")
                    


class TableModel(QAbstractTableModel):
    def __init__(self, data):
        super().__init__()
        self._data = data

    def data(self, index, role):
        if role == Qt.DisplayRole:
            # See below for the nested-list data structure.
            # .row() indexes into the outer list,
            # .column() indexes into the sub-list
            return self._data[index.row()][index.column()]

    def rowCount(self, index):
        # The length of the outer list.
        return len(self._data)

    def columnCount(self, index):
        # The following takes the first sub-list, and returns
        # the length (only works if all rows are an equal length)
        return len(self._data[0])
     

def folderView_selectionchanged():
    current_index = folderView.currentIndex()
    selected_folder_path = folderModel.fileInfo(current_index).absoluteFilePath()
    fileView.setRootIndex(fileModel.setRootPath(selected_folder_path))
    

def fileView_selectionchanged():
    current_file = fileView.currentIndex()
    selected_file_path = fileModel.fileInfo(current_file).absoluteFilePath()
    colnames = ['Время' , fileModel.fileInfo(current_file).fileName()]
    
    print(colnames, len(colnames))

    try:
        df = pd.read_csv(selected_file_path, sep = '\t', header=None, 
                         index_col=False, decimal=',') # Читаем DataFrame здесь
        df.columns = ['Время', fileModel.fileInfo(current_file).fileName(), 'Undefined'] # Присваиваем имена столбцов
        df[fileModel.fileInfo(current_file).fileName()] = df[fileModel.fileInfo(current_file).fileName()].round(2)
        df = df.drop(['Undefined'], axis=1)
        model = TableModel(df.values.tolist()) # Преобразуем DataFrame в список списков
        tableView.setModel(model)
        tableView.setColumnWidth(0, 130) 
        tableView.setColumnWidth(1, 120)
        tableView.verticalHeader().setVisible(False)
           
                
        print(type(df.iloc[:,0][0]))
        update_chart(df)
    except Exception as e:
        print(f"Ошибка при чтении файла: {e}")
        
        
def update_chart(df): # <--- Новая функция для построения графика
    chart.removeAllSeries() # Очищаем предыдущие серии данных
    
    # удаляем старые оси
    for axis in chart.axes():
        chart.removeAxis(axis)
    
    if len(df.columns) < 2:
        print("Файл не содержит достаточно данных для построения графика.")
        return

    series = QLineSeries()
    df['Время'] = pd.to_datetime((df['Время'])) 
    df.set_index('Время', inplace=True)
    
    if len(df) > 1000: 
        average = df.resample('10min').mean()
        
        if average.empty or average.shape[0] < 2:
            print("Недостаточно данных для построения графика.")
            return
        
        for i in range(len(average)):
            try:
                x = average.index[i].timestamp() * 1000
                y = float(average.iloc[i, 0].round(1))
                series.append(x, y) 
                
            except (ValueError, TypeError, IndexError) as e:
                print(f"Ошибка преобразования данных в строке {i+1}: {e}")
                continue # Пропускаем строку с некорректными данными  
                
        axis_x = QDateTimeAxis()
        chart.setTitle(average.columns[0][: -4])
        axis_y = QValueAxis()
        axis_y.setTitleText(average.columns[0][: -4]) 
    
    else:
 ######## Графики, которые строятся по всем значениям (долго):   
        for i in range(len(df)):
            try: # Обработка потенциальных ошибок преобразования типов
                
                x = df.index[i].timestamp() * 1000 
                y = float(df.iloc[i , 0].round(1)) 
                series.append(x, y)
                
            except (ValueError, TypeError, IndexError) as e:
                print(f"Ошибка преобразования данных в строке {i+1}: {e}")
                continue # Пропускаем строку с некорректными данными
                
        axis_x = QDateTimeAxis()
        chart.setTitle(df.columns[0])
        axis_y = QValueAxis()
        axis_y.setTitleText(df.columns[0]) 

    chart.addSeries(series)
    
#    chart.setTitle(average.columns[0])
    chart.legend().setVisible(False)
    
    # Настройка осей (опционально):
    #axis_x = QDateTimeAxis()
    axis_x.setTickCount(10)
    axis_x.setFormat("dd.MM.yyyy. hh:mm")
    axis_x.setLabelsAngle(70)
    axis_x.setTitleText('Время')
    chart.addAxis(axis_x, Qt.AlignBottom)
    series.attachAxis(axis_x)

    #axis_y = QValueAxis()
#   axis_y.setTitleText(average.columns[0]) 
    chart.addAxis(axis_y, Qt.AlignLeft)
    series.attachAxis(axis_y)


if __name__ == "__main__":
    if not QApplication.instance():
        app = QApplication(sys.argv)
    else:
        app = QApplication.instance()

    window = QWidget()
    window.setFixedSize(1300, 900)
    layout = QGridLayout()
    
# Выбираем папку
    folderView = QTreeView()
    folderModel = QFileSystemModel()
    
    # Меняем корневую папку!!!!
    
    folderModel.setRootPath(QDir.rootPath())  #   Устанавливаем корневой путь модели

    folderView.setModel(folderModel)
 
 ##########################################################################################   
 
    # Устанавливаем корневой индекс для отображения в дереве
    target_dir = "C:/Users/sheshukova/Documents/diaprom/sskgo/2025-04-09"  # <- замените на желаемую директорию
    folderView.setRootIndex(folderModel.index(target_dir))
   
 ##########################################################################################     
    
    
 #  folderModel.rootDirectory()
 #  folderModel.setRootPath("/")
    folderModel.setFilter(QDir.NoDotAndDotDot | QDir.AllDirs)
 #  folderView.setModel(folderModel)
 #  folderModel.setRootPath(QDir.currentPath()) ###
    folderView.selectionModel().selectionChanged.connect(folderView_selectionchanged)
    
 # Расшираяем по первой папке  - раньше работало
    folderView.setColumnWidth(0, 220) # Ширина столбца "Name" - 200 пикселей
    folderView.setColumnWidth(1, 100) # Ширина столбца "Type" - 100 пикселей
    folderView.setColumnWidth(2, 80) # Ширина столбца "Size" - 80 пикселей
            
 # Смотрим файлы в выбранной папке   
    fileView = QTreeView()
    fileModel = QFileSystemModel()
    fileModel.setRootPath("/")
    fileModel.setFilter(QDir.NoDotAndDotDot | QDir.Files)
    fileView.setModel(fileModel)
    
    fileView.setColumnWidth(0, 220) # Ширина столбца "Name" - 200 пикселей
    fileView.setColumnWidth(1, 100) # Ширина столбца "Type" - 100 пикселей
    fileView.setColumnWidth(2, 80) # Ширина столбца "Size" - 80 пикселей
    
        
    
    tableView = QTableView()
    
  ## Растягивание столбцов на всю ячейку сетки  
    #tableView.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    chartView = QChartView()
    chartView.setRenderHint(QPainter.Antialiasing)

    # Create the chart and add it to the view
    chart = QChart()
    chartView.setChart(chart)
    chart.setAnimationOptions(QChart.SeriesAnimations)
    #chart.setTheme(QChart.ChartThemeDark)


    layout.addWidget(folderView, 0, 0)
    layout.addWidget(fileView, 0, 1)
    layout.addWidget(tableView, 1, 0)
    layout.addWidget(chartView, 1, 1)
    
    window.setLayout(layout)
    
    window.show()

fileView.selectionModel().selectionChanged.connect(fileView_selectionchanged)
sys.exit(app.exec())