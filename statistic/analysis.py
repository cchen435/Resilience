#!/usr/bin/env python
'''
This module is for analysis climate data
in format of grib
Author: Chao Chen
'''
import matplotlib
matplotlib.use('GTK')
import matplotlib.pyplot as plt
import math
import sys
import numpy
import os
import gc 


# glob can get files in directory
import glob

# pygrib for read GRIB files
import pygrib

from fio import getdata

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

    ratio = dict()

    # get number of files
    size = len(files)
    
    ''' just do first half of files now '''
    size /= 3 

    i = 1;
    while i < size:
        
        if i % 10 == 0:
            print '### log: finished', float(i)/size

        prev = files[i-1]
        curr = files[i]

        if DEBUG:
            print("doing calculation on file: prev-->" + prev + " , curr-->" + curr);

        # open grib file
        curr_fp = getdata(curr)
        prev_fp = getdata(prev)
        if i == 1:
            keys = curr_fp.keys()
        
        i+=1


        for key in keys:
            if curr_fp.has_key(key) == False:
                sys.exit('variable %s not found in %s' % ( key, curr) )
            if prev_fp.has_key(key) == False:
                sys.exit('variable %s not found in %s' % ( key, prev) )

            curr_values = abs(curr_fp[key])
            prev_values = abs(prev_fp[key])

            #prev_values[prev_values == 0] = 1
            prev_values += 1
            diff = curr_values/prev_values - 1

            if ratio.has_key(key) == False:
                ratio[key] = [diff]
            else:
                ratio[key].append(diff)
            
            # recall memory
            del curr_values, prev_values, diff
            gc.collect()

    print '### log: finished', float(i)/size
    for key in ratio.keys():
        ratio[key] = numpy.array(ratio[key]);
        gc.collect()
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
        
        mean_var = numpy.zeros(size, dtype = chg_ratio_array.dtype)
        maxv_var = numpy.zeros(size, dtype = chg_ratio_array.dtype)
        minv_var = numpy.zeros(size, dtype = chg_ratio_array.dtype)
        stdv_var = numpy.zeros(size, dtype = chg_ratio_array.dtype)
        
        for i in range(size):
            mean_var[i] = chg_ratio_array[:, i].mean()
            maxv_var[i] = chg_ratio_array[:, i].max()
            minv_var[i] = chg_ratio_array[:, i].min()
            stdv_var[i] = chg_ratio_array[:, i].std()

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

    return (maxv, minv, mean, stdv)
## end of calc_statistic

def plot_hist(name, data, title = 'Distribution of Change Ratio'):
    array = numpy.array(data)
    size = array.size
    
    binsize = 40
    hist, bins = numpy.histogram(array, bins=binsize)
    center = (bins[:-1]+bins[1:])/2
    width =  0.7 * (bins[1]-bins[0])

    plt.bar(center, hist, align='center', width = width)
    plt.title(title)
    plt.savefig('.'.join([name, 'pdf']))
    plt.clf()

def plot_line(fname, data, Title = 'Change ratio'):
    array = numpy.array(data)
    mean = array.mean()
    array[abs(array) > 100 * abs(mean)] = mean
    size = array.size
    x = range(size)
    plt.ylim(-2, 1)
    plt.plot(x, array)
    plt.savefig('.'.join([fname, 'pdf']))
    plt.clf()



## start point, main function in C
if __name__ == '__main__':

    if len(sys.argv) == 1:
        sys.exit('please specify a workspace')
    # list all files in curr dir
    workspace = os.path.join(os.getcwd(), sys.argv[1])

    files = [f for f in os.listdir(workspace) if os.path.isfile(os.path.join(workspace, f))]
    files.sort()

    #print files
    files = [os.path.join(workspace, f) for f in files]

    #cont = raw_input("please evaluate the file orders here: continue(y) or stop(n)")
    cont = 'y'

    while True:
        if cont == 'n' or cont == 'N':
            sys.exit(0)
        elif cont == 'y' or cont == 'Y':
            break
        else:
            cont = raw_input("input not recognized. \n please evaluate \
                    the file orders here: continue(y) or stop(n)")
    ratio = calc_change_ratio(files)
    (maxc, minc, mean, stdv) = calc_statistic(ratio)

    
    # remove extreme value

    for key in mean.keys():
        plot_hist('mean', mean[key], title='Mean Change Ratio')
        plot_hist('max', maxc[key], title='Max Change Ratio')
        plot_hist('min', minc[key], title='Min Change Ratio')
        plot_hist('stdv', stdv[key], title='standard diviation')
        plot_hist('location1', ratio[key][:, 63])
        plot_hist('location2', ratio[key][:, 126])
        plot_hist('location3', ratio[key][:, 253])
        plot_hist('location4', ratio[key][:, 507])
        plot_hist('location5', ratio[key][:, 1014])
        plot_hist('location6', ratio[key][:, 2028])
        plot_hist('location7', ratio[key][:, 4056])
        plot_hist('location8', ratio[key][:, 8112])
        plot_hist('location9', ratio[key][:, 16224])
        plot_hist('location10', ratio[key][:, 32449])
        print 'max stdv:', numpy.array(stdv[key]).max()
        print 'min stdv:', numpy.array(stdv[key]).min()
        plot_line('change1', ratio[key][:, 63])
        plot_line('change2', ratio[key][:, 126])
        plot_line('change3', ratio[key][:, 253])
        plot_line('change5', ratio[key][:, 1014])
        plot_line('change8', ratio[key][:, 8112])
        
        print 'ratio shape:', numpy.array(ratio[key]).shape
        print 'stdv shape:', numpy.array(stdv[key]).shape
        print 'stdv at location 5:', numpy.array(stdv[key]).ravel()[1014]
        print 'stdv at location 8:', numpy.array(stdv[key]).ravel()[8112]
        print 'min stdv:', numpy.array(stdv[key]).min()
        print 'min stdv:', numpy.array(stdv[key]).min()

