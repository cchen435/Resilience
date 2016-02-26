#!/usr/bin/env python
'''
This module is for analysis climate data
in format of grib
Author: Chao Chen
'''

from optparse import OptionParser

import matplotlib
matplotlib.use('GTK')
import matplotlib.pyplot as plt

import math
import sys
import numpy
import os

import fio

#control arguments
#numpy.set_printoptions(precision=6)
numpy.set_printoptions(suppress=True)

DEBUG=0
DEBUG2=0

'''
get the parameters and levels for each parameters in the file
'''

## calc statistic of a 2D aray along with
## the time step (1st) dimention
def calc_statistic(ratio):

    (steps, size) = ratio.shape
    
    # statistics alone with timestep, it calcs 
    # the statistic for each location
    mean = numpy.zeros(size, dtype = ratio.dtype)
    maxv = numpy.zeros(size, dtype = ratio.dtype)
    minv = numpy.zeros(size, dtype = ratio.dtype)
    stdv = numpy.zeros(size, dtype = ratio.dtype)
    
    mean = numpy.mean(ratio, axis=0)
    maxv = numpy.max(ratio, axis=0)
    minv = numpy.min(ratio, axis=0)
    stdv = numpy.std(ratio, axis=0)

    # statistics alone with array, it calcs
    # the statistic for each time step
    tmean = numpy.zeros(steps, dtype = ratio.dtype)
    tmaxv = numpy.zeros(steps, dtype = ratio.dtype)
    tminv = numpy.zeros(steps, dtype = ratio.dtype)
    tstdv = numpy.zeros(steps, dtype = ratio.dtype)

    tmean = numpy.mean(ratio, axis=1)
    tmaxv = numpy.max(ratio, axis=1)
    tminv = numpy.min(ratio, axis=1)
    tstdv = numpy.std(ratio, axis=1)

    return (maxv, minv, mean, stdv, tmaxv, tminv, tmean, tstdv)
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

def plot_line(fname, data, title = 'Change ratio', yup = None, ydown = None):
    array = numpy.array(data)
    mean = array.mean()
    array[abs(array) > 100 * abs(mean)] = mean
    size = array.size
    x = range(size)
    plt.ticklabel_format(useOffset=False, style='plain')
    if yup is not None and ydown is not None:
        plt.ylim(ydown, yup)
    plt.plot(x, array)
    plt.savefig('.'.join([fname, 'pdf']))
    plt.clf()



## start point, main function in C
if __name__ == '__main__':
    
    usage='usage: %prog workspace variable [size]'
    parser = OptionParser(usage=usage)
    (opts, args) = parser.parse_args()
    if len(args) < 2:
        parser.print_help()
        sys.exit('arguments error')

    workspace = args[0]
    variable = args[1]
    if len(args) == 3:
        size = int(args[2])
    else:
        size = None

    datasets = fio.DataBase(workspace, variable)

    ratio_list = list()
    while not datasets.done():
        print '\n\n Progress. Finished: %.02f%%' % (datasets.get_progress() * 100)
        (prev, curr) = datasets.get()
        if prev is None or curr is None:
            print 'Finished'
            break

        if size is not None and datasets.get_curr() == size:
            print 'Finished with up to expected timesteps'
            break
        
        tmp = abs(curr)/(abs(prev) + 1) - 1
        ratio_list.append(tmp)

    ratio = numpy.array(ratio_list)
    (maxc, minc, mean, stdv, tmax, tmin, tmean, tstdv) = calc_statistic(ratio)

    index = numpy.argmax(stdv)

    plot_hist('mean', mean, title='Mean Change Ratio')
    plot_hist('max', maxc, title='Max Change Ratio')
    plot_hist('min', minc, title='Min Change Ratio')
    plot_hist('stdv', stdv, title='standard diviation')
    plot_hist('hist', ratio[:, index], title='Change Ratio at Loc with max stdv')
    plot_line('line', ratio[:, index], title='Change Ratio at Loc with max stdv')
    plot_line('tmean', tmean, title='tmean')
    plot_line('tstdv', tstdv, title='tstdv')
    plot_line('tmax', tmax, title='tmax')
    plot_line('tmin', tmin, title='tmin')
        
