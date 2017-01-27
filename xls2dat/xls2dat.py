# this script convert .xls files into .dat
# .dat files could be used in IPI2Win and Zond1D geophysical softwares

import os
import os.path
from functools import reduce
from pyexcel_xls import get_data



file_path = os.getcwd()			# path of xls and xls2dat.py filse


all_files = os.listdir(file_path)			# number of files in file_path


for f in all_files:			# removing of unnecessary files
    if (not (f.endswith('.xlsx') or f.endswith('.xls'))):
        all_files.remove(f)


new_dat = open('new_dat_file.dat', 'w', encoding = 'utf-8')			# creating of new dat file




for i, item in enumerate(all_files):
	
    xls_file_path = os.path.join(file_path, all_files[i])

    xls_file = get_data(xls_file_path, start_row = 0, row_limit = 7)			# getting data from xls file


    if i == 0:

        new_dat.write(xls_file['Лист1'][0][1] + '\n' + xls_file['Лист1'][0][6])		# header of file
                
        VES_points = len(all_files)
        data_type = '0'
        spacings = xls_file['Лист1'][5][12:]
        array_type = 'S'
        
        # 1) number of VES points if file, 2) data type(0 - ap.res, 1 - induced polarisation), 3) number of spacings, 4) array type(S - Schlumberger)
        new_dat.write('\n{} {} {} {}'.format(VES_points, data_type, len(spacings), array_type))		
        new_dat.write('\n' + reduce(lambda x, y: (str(x) + ' ' + str(y)), spacings))		# spacings of VES array

    
    spacings = xls_file['Лист1'][5][12:]
    apparent_res = [round(i, 3) for i in xls_file['Лист1'][6][12:]]


    new_dat.write('\n{}'.format(xls_file['Лист1'][1][1]))		# name of current VES point
    new_dat.write('\n' + len(apparent_res))		# number of ap.res. values
    new_dat.write('\n' + reduce((lambda x, y: (str(x) + ' ' + str(y))), apparent_res))		# ap.res. values


new_dat.close()