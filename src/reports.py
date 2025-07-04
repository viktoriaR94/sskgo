# -*- coding: utf-8 -*-
"""
Created on Wed Jul  2 10:36:46 2025

@author: sheshukova
"""

from report_generator import ReportGenerator

name = 'Vika'
score = 0.5

# Пример использования 1: Заполнение шаблона
def generate_report():
    context = {
        "{DATE}": datetime.now().strftime("%d.%m.%Y"),
        "{USER}": name,  # Пример данных из вашего приложения
        "{SCORE}": score # Пример вызова функции из вашего кода
    }
    
    ReportGenerator.generate_from_template(
        template_path="C:/Users/sheshukova/Documents/diaprom/sskgo/src/templates/template.docx",
        output_path=f"C:/Users/sheshukova/Documents/diaprom/sskgo/src/reports/report_{datetime.now().date()}.docx",
        context=context
    )
