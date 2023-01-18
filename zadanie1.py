import sqlite3
import os
import time

import pandas
from PIL import Image
from PIL.ExifTags import TAGS


def SozdatInfObKartinke(path, root, metadata):
    img_file = Image.open(path)
    exif_data = img_file.getexif()
    for tag_id in exif_data:
        tag = TAGS.get(tag_id, tag_id)
        data = exif_data.get(tag_id)
        if isinstance(data, bytes):
            data = data.decode()
        metadata.append(f"{tag:25}: {data}")
    filename = path.split('\\').pop()
    cur.execute(f'INSERT INTO data VALUES ("{filename}", "{root}", "{str(metadata)}")')
    connect.commit()


def RecursivObhod(path):
    content = os.listdir(path)
    root = path.split("\\").pop()
    for data in content:
        new_path = path + '\\' + data
        print("Загрузка ... " + data)
        _, file_extension = os.path.splitext(new_path)
        if os.path.isdir(new_path):
            cur.execute(f'INSERT INTO data VALUES ("{data}", "{root}", "folder")')
            connect.commit()
            RecursivObhod(new_path)
        else:
            dannie = [f"{'<size>':25}: {os.path.getsize(new_path)}",
                        f"{'<data_create>':25}: {time.ctime(os.path.getmtime(new_path))}",
                        f"{'Time edit':25}: {time.ctime(os.path.getctime(new_path))}"]
            if file_extension in ['.jpg', '.jpeg', '.png']:
                SozdatInfObKartinke(new_path, root, dannie)
            else:
                cur.execute(f'INSERT INTO data VALUES ("{data}", "{root}", "{str(dannie)}")')
                connect.commit()


connect = sqlite3.connect('files.db')
print("База данных подключена к SQLite")
cur = connect.cursor()

path_to_folder = input("Введите путь: ")
path_to_folder = path_to_folder.replace('/', '\\')

cur.execute("DROP TABLE data")
cur.execute("CREATE TABLE IF NOT EXISTS data(name TEXT NOT NULL, root TEXT NOT NULL, metadata TEXT)")

folder = path_to_folder.split('\\').pop()
cur.execute(f'INSERT INTO data VALUES ("{folder}", "<root>", "no data")')
connect.commit()

RecursivObhod(path_to_folder)
cur.close()

df = pandas.read_sql('select * from data', connect)
df.to_excel(r'C:\qwerty_\data.xlsx', index=False)