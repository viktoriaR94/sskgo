# -*- coding: utf-8 -*-
"""
Created on Tue May 20 12:16:09 2025

@author: sheshukova
"""


from docx import Document
import subprocess

def generate_odt_report(data, output_filename):
    doc = Document()
    # ... (здесь ваш код генерации контента в docx) ...

    doc.save("temp.docx") 

    try:
        subprocess.run(["libreoffice", "--headless", "--convert-to", "odt", "temp.docx", "--outdir", ".", "--infilter=docx:Word 2007 XML"], check=True)
        subprocess.run(["mv", "temp.odt", output_filename], check=True) #Переименовываем
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при преобразовании: {e}")
    finally:
        #Удаляем временный файл
        import os
        try:
            os.remove("temp.docx")
        except FileNotFoundError:
            pass

# Пример использования:
data = {"name": "Иван", "age": 30}
generate_odt_report(data, "report.docx")
