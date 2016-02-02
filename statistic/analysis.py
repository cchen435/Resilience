#!/usr/bin/env python
'''
This module is for analysis climate data
in format of grib
Author: Chao Chen
'''
import matplotlib.pyplot as plt
import math
import sys
import numpy

# glob can get files in directory
import glob

# pygrib for read GRIB files
import pygrib

from fio import getfile

#control arguments
#numpy.set_printoptions(precision=6)
numpy.set_printoptions(suppress=True)

DEBUG=0
DEBUG2=1


'''
calculate the change ratio between two successive
time steps for variable "variable" at the level "level"
'''
def calc_change_ratio(files):
    if DEBUG:
        print("working on files:");
        print(files)

    diff = []

    # get number of files
    size = len(files)

    i = 1;
    while i < size:
        prev = files[i-1];
        curr = files[i];
        i++;

        if DEBUG:
            print("doing calculation on file: prev-->" + prev + " , curr-->" + curr);

        # open grib file
        curr_fp = getfile(curr)
        prev_fp = getfile(prev)

        if i == 1:
            keys = curr_fp.keys()

        for key in keys:
            if curr_fp.has_key(key) == False:
                sys.exit('variable %s not found in %s' % ( key, curr) )
            if prev_fp.has_key(key) == False:
                sys.exit('variable %s not found in %s' % ( key, prev) )

            curr_values = curr_fp[key]
            prev_values = prev_fp[key]

            prev_values += 1
            diff = curr_values/prev_values - 1

            if ratio.has_key(key) == False:
                ratio[key] = [diff]
            else:
                ratio[key].append(diff)

    '''
    for key in ratio.keys():
        ratio[key] = numpy.array(ratio[key]);
    '''

    return ratio
## end of calc_change_ratio

'''
get the parameters and levels for each parameters in the file
'''

## calc statistic of a 3D cube along with
## the time step (1st) dimention
def calc_statistic(ratio):
    mean = dict()
    maxv = dict()
    minv = dict()
    stdv = dict()

    for key in ratio.keys():
        chg_ratio = ratio[key]    
        chg_ratio_array = numpy.array(chg_ratio)
        (steps, size) = chg_ratio_array.shape
        
        mean_var = numpy.zeros(size, dtype = chg_ratio.array.dtype)
        maxv_var = numpy.zeros(size, dtype = chg_ratio.array.dtype)
        minv_var = numpy.zeros(size, dtype = chg_ratio.array.dtype)
        stdv_var = numpy.zeros(size, dtype = chg_ratio.array.dtype)
        
        for i in range(size):
            mean_var[i] = chg_ratio_array[:, i].mean()
            maxv_var[i] = chg_ratio_array[:, i].max()
            minv_var[i] = chg_ratio_array[:, i].min()
            stdv_var[i] = chg_ratio_array[:. i].std()

        if mean.has_key(key) == False:
            mean[key] = [mean_var]
            maxv[key] = [maxv_var]
            minv[key] = [minv_var]
            stdv[key] = [stdv_var]
        else:
            mean[key].append(mean_var)
            maxv[key].append(maxv_var)
            stdv[key].append(stdv_var)
            minv[key].append(minv_var)

    return (maxv, minv, meanv, stdv)
## end of calc_statistic

def plot(name, data, title = 'Distribution of Change Ratio'):
    array = numpy.array(data)
    size = array.size
    binsize = min(size/100, 20)

    hist, bins = numpy.histogram(array, bins=binsize)
    center = (bins[:-1]+bins[1:])/2
    width =  1.0 * (bins[1]-bins[0])
    plt.bar(center, hist, align='center', width = width)
    plt.title(title)
    plt.savefig('.'.join([name, 'pdf']))

## start point, main function in C
if __name__ == '__main__':

    # list all files in curr dir
    workspace = os.getcwd()
    files = [f for f in os.listdir(workspace) if os.path.isfile(os.path.join(workspace, f))]
    files.sort()

    print files
    cont = raw_input("please evaluate the file orders here: continue(y) or stop(n)")
    
    while True:
        if cont == 'n' or cont == 'N':
            sys.exit(0)
        elif cont == 'y' or cont == 'Y':
            break
        else:
            cont = raw_input("input not recognized. \n please evaluate \
                    the file orders here: continue(y) or stop(n)")
    calc_change_ratio(files)

