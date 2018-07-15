# -*- coding: utf-8 -*-
"""
Created on Fri Jul  6 15:32:15 2018

@author: Артём
"""

# файл для конвертации dat-файлов general array data format в 
# pole-dipole data types


import os
import pandas as pd
import numpy as np


#-------*-------*-------*-------*-------*-------*-------*-------*-------  


# функция для поиска файла в текущей директории
def findFiles(file_format):
    """
    Функция для поиска списка файлов формата file_format в текущей директории
    file_format = 'csv', 'txt', 'dat' и др.
    На выходе получаем list со всеми файлами указанного формата
    """
    try:
        all_files_in_folder = os.listdir(os.getcwd())
        files = [file for file in all_files_in_folder if file_format in file]
        return files
    except TypeError:
        print('Формат файла должен быть строкой')


# функция для выбора файла из списка
def chooseFile(some_files):
    """
    Возвращает имя файла к обработке
    """
    try:
        print('Выберите файлы для конвертации: ')
        for num, file in enumerate(some_files):
            print(num, ': ', file) # printing list of files in some directory
        choice1 = int(input('Введите номер файла AMN: '))
        choice2 = int(input('Введите номер файла MNB: '))
        return [some_files[choice1],some_files[choice2]]
    except:
        print('Ой! Что пошло не так. Проверьте исходный код =((( ')
        

# создание пути, открытие файла и формирование массивов со служебной инфой
# и данными
def DataFrameCreation(file_name):
    """
    Создаёт два объекта: 1) массив со служебной информацией и 
    2) DataFrame с переформатированными данными (C1, P1, P2)
    
    Input: имя файла для конвертирования
    Output: массив данных с общей информацией (f_info),
            frame с неформатированными данными из general data type
    """
    file_path = os.path.join(os.getcwd(), file_name)
    f = open (file_path, 'r')
    f_d = f.readlines()
    f_info = f_d[:9]
    f_data = f_d[9:]
    f.close()
    for n,i in enumerate(f_data):
        f_data[n] = i.rstrip('\n').split(' ')     
    f_dataFrame = pd.DataFrame(f_data, columns=['Array', 'C1', 'h1', 'P1', 'h2', 'P2', 'h3', 'Ro'],dtype=float)
    f_dataFrame.drop(['Array', 'h1', 'h2', 'h3'], axis=1, inplace=True)
    return f_info, f_dataFrame


# создание нового массива в формате pole-dipole data type
def PDDataFrame(df,file_name):
    """
    Создаёт новый DataFrame, содержащий данные в формате pole-dipole 
    data type
    
    Input: массив с неформатированными данными (df)
           имя форматируемого файла (file_name)
    Output: отформатированный массив с данными
    """
    df_new = pd.DataFrame(np.zeros(df.shape),columns=['x','a','n','Ro'])
    df_new.a = np.abs(df.P1-df.P2)
    if 'forward' in file_name:
        df_new.x = df.C1 + np.abs((df.C1-df.P2)/2)
        df_new.n = np.abs((df.P1-df.C1)/df_new.a)
        df_new.n = df_new.n.round(4)
    elif 'reverse' in file_name:
        df_new.x = df.C1 - np.abs((df.C1-df.P2)/2)
        df_new.n = (-1) * np.abs((df.P1-df.C1)/df_new.a)
        df_new.n = df_new.n.round(4)
    df_new.Ro = df.Ro
    return df_new


# создание нового .dat-файла формата pole-dipole array type с 
# прямой и обратной установками
def pdfile(i1, i2, d1, d2):
    """
    Формирует и выводит файл формата pole-dipole data type
    
    Input: два массива (i1,i2) с информационной частью из general data и
           два frame-а (d1,d2) с обработанными и сформированными данными
    Output: файл формата .dat для обработки в программе Res2DInv 
    """
    # создание временного файла с сортированными файлами
    all_data = pd.concat([d1,d2],join='outer',ignore_index=True)
    all_data.to_csv('temp.dat',sep=',',index=False,header=False)
    
    file_name = '{}_{}'.format(i1[0].strip('.dat\n'),i2[0].strip('.dat\n'))
    # создание результирующего файла
    f = open(file_name + '.dat', 'x')
    # строка 1 - название файла
    f.write(file_name + '\n')
    # строка 2 - расстояние между электродами
    f.write(i1[1])
    # строка 3 - тип установки (6 для pole-dipole)
    f.write('6\n')
    # строка 4 - количество отсчётов (записей)
    f.write(str(all_data.shape[0])+'\n')
    # строка 5 - точка отсчёта (0-для первого электрода, 1-для середины C1-P2)
    f.write('1\n')
    # строка 6 - данные ВП (0-без ВП, 1-с ВП)
    f.write('0\n')
    # запись массива данных из файла temp.dat
    with open('temp.dat','r') as t:
        f.writelines(t.readlines())
        t.close()
        os.remove('temp.dat') # удаление временного файла temp.dat
    # последняя строка с несколькими нулями
    f.write('0,0,0,0,0')
    f.close()


#-------*-------*-------*-------*-------*-------*-------*-------*-------  
  
# выбор файлов для AMN и MNB для конвертации и суммирования      
files = chooseFile(findFiles('dat'))

# выбор из файлов для AMN и MNB блока, содержащего информацию 
# и отсортированной таблицы с данными
information1,data1 = DataFrameCreation(files[0])
information2,data2 = DataFrameCreation(files[1])

# формирования объекта DataFrame с заново сформированными данными
data1n = PDDataFrame(data1,files[0])
data2n = PDDataFrame(data2, files[1])


pdfile(information1,information2,data1n,data2n)



        

