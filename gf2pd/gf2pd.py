# -*- coding: utf-8 -*-
"""
Created on Fri Jul  6 15:32:15 2018

@author: Artem Gorbunov
"""

# script converts general array dat-files (forward and reverse) to conventional pole-dipole array data-file (forward+reverse)
# this file could be used in programs for inversion of geophysical (electrical tomography) data


import os
import pandas as pd
import numpy as np


#-------*-------*-------*-------*-------*-------*-------*-------*-------  


def findFiles(file_format):
    """
    Return list of .file_format files in current directory
    
    file_formats: 'csv', 'doc', 'xls' etc.
    """
    try:
        all_files_in_folder = os.listdir(os.getcwd())
        files = [file for file in all_files_in_folder if file_format in file]
        return files
    except TypeError:
        print('File format must be string')


def chooseFile(some_files):
    """
    Return names of forward and reverse array files for other manipulations
    
    Input: some_files - list with file's names
    Output: two file names of forward and reverse arrays files for convertion
    """
    try:
        print('Choose files: ')
        for num, file in enumerate(some_files):
            print(num, ': ', file) # printing list of files in some directory
        choice1 = int(input('Enter index of C1P1P2 array file: '))
        choice2 = int(input('Enter index of P2P1C1 array file: '))
        return [some_files[choice1],some_files[choice2]]
    except:
        print('Oops! Something goes wrong!')
        

def DataFrameCreation(file_name):
    """
    Return two object: 1) list with general information (name, general array type, electrode spacing etc.), 
    2) DataFrame object with formatted data (C1, P1, P2 electrode position)
    
    Input: file_name - name of file (string)
    Output: f_info - list with general information
            f_dataFrame - DataFrame object with formatted data
    """
    file_path = os.path.join(os.getcwd(), file_name)
    f = open (file_path, 'r')
    f_d = f.readlines()
    f_info = f_d[:9]
    f_data = f_d[9:]
    f.close()
    for n,i in enumerate(f_data):
        f_data[n] = i.rstrip('\n').split()     
    f_dataFrame = pd.DataFrame(f_data, columns=['Array', 'C1', 'h1', 'P1', 'h2', 'P2', 'h3', 'Ro'],dtype=float)
    f_dataFrame.drop(['Array', 'h1', 'h2', 'h3'], axis=1, inplace=True)
    return f_info, f_dataFrame


def PDDataFrame(df,file_name):
    """
    Return new DataFrame object with forward and reverse data in conventional format
    
    Input: df - DataFrame object with initial data
           file_name - file name of converted file
    Output: DataFrame object with formatted data
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


def pdfile(i1, i2, d1, d2):
    """
    Create and save new .dat file in conventional data type format
     
    Input: i1, i2 - lists with general information of forward and reverse data files
           d1, d2 - DataFrame objects with formatted data
    Output: .dat format file for invrsion in Res2dInv or ZondRes2D
    """
    # creation of temp file with sorted data
    all_data = pd.concat([d1,d2],join='outer',ignore_index=True)
    all_data.to_csv('temp.dat',sep=',',index=False,header=False)
    
    file_name = '{}_{}'.format(i1[0].strip('.dat\n'),i2[0].strip('.dat\n'))
    # creation of dat-file
    f = open(file_name + '.dat', 'x')
    # line 1 - file name
    f.write(file_name + '\n')
    # line 2 - electrode spacing
    f.write(i1[1])
    # line 3 - array type (6 - pole-dipole)
    f.write('6\n')
    # line 4 - number of data points
    f.write(str(all_data.shape[0])+'\n')
    # line 5 - position of data point (0-first electrode, 1-half C1-P2 distance)
    f.write('1\n')
    # line 6 - IP data (0-no, 1-yes)
    f.write('0\n')
    # import data from temp.dat file
    with open('temp.dat','r') as t:
        f.writelines(t.readlines())
        t.close()
        os.remove('temp.dat') # removing of temp.dat file
    # last line with some zeros
    f.write('0,0,0,0,0')
    f.close()


#-------*-------*-------*-------*-------*-------*-------*-------*-------  
  
# choosing of files   
files = chooseFile(findFiles('dat'))

# choosing from files blocks with general information and data
information1,data1 = DataFrameCreation(files[0])
information2,data2 = DataFrameCreation(files[1])

# creation of DataFrame object with formatted data
data1n = PDDataFrame(data1,files[0])
data2n = PDDataFrame(data2, files[1])

# creation of final dat-file
pdfile(information1,information2,data1n,data2n)
