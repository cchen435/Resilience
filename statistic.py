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
from matplotlib.ticker import FuncFormatter

import math
import sys
import numpy
import os

import fio

#import pdb

#control arguments
#numpy.set_printoptions(precision=6)
numpy.set_printoptions(suppress=True)

DEBUG=0


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

def to_percent(y, position):
    s = str(100 * y)
    if matplotlib.rcParams['text.usetex'] is True:
        return s+r'$\%$'
    else:
        return s+'%'

def plot_hist(name, data, title = 'Distribution of Change Ratio'):
    #pdb.set_trace()
    array = numpy.array(data)
    size = array.size
    
    binsize = 40
    hist, bins = numpy.histogram(array, bins=binsize)
    center = (bins[:-1]+bins[1:])/2
    width =  0.7 * (bins[1]-bins[0])
    hist = hist * 1.0 /size

    plt.bar(center, hist, align='center', width = width)
    formatter=FuncFormatter(to_percent)
    plt.gca().yaxis.set_major_formatter(formatter)
    plt.title(title)
    plt.ylabel('Count in Percentage')
    plt.xlabel('Change Percentage')
    plt.savefig('.'.join([name, 'pdf']))
    plt.clf()

def plot_lines(fname, data, title = 'Change ratio', yup = None,\
               ydown = None, xlabel = None):
    array = numpy.array(data)
    style=['ro-', 'b*-', 'gs-', 'kD-', 'mx-'];
    if array.ndim == 1:
        items = 1
        size = array.size
    else:
        (items, size) = array.shape

    x = numpy.array(range(size))
    plt.ticklabel_format(useOffset=False, style='plain')
    plt.xlim(0, size)
    
    if yup is not None and ydown is not None:
        plt.ylim(ydown, yup)
    
    print 'dim: ', array.ndim
    if array.ndim > 1:
        for i in range(items):
            plot = plt.plot(x, array[i], style[i], label='Location %d'%i)
    else:
        print 'name', fname
        plot = plt.plot(x, array, style[0])

    if array.ndim > 1:
        plt.legend(loc=4)

    plt.xlabel('Time Step')
    if xlabel is not None:
        plt.xlabel(xlabel)
    plt.ylabel('Change Percentage')
    plt.title(title)
    
    plt.savefig('.'.join([fname, 'pdf']))
    plt.clf()


def plot_mean_stdv(fname, data, \
                   Title = 'Mean and Stdv of Change Ratios for Each Location', \
                   xlabel = None, ydown = -1.5, yup = 1.5):
    array = numpy.array(data)
    (tmp, size) = array.shape
    x = numpy.array(range(size))
    #plt.ylim(-2, 1)

    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx()
    plot1 = ax1.plot(x, array[0], 'r-', label='Mean')
    plot2 = ax2.plot(x, array[1], 'b--', label='Stdv')
    plots=plot1+plot2
    labs=[l.get_label() for l in plots]

    ax1.set_xlabel('Data Point ID');
    if xlabel is not None:
        ax1.set_xlabel(xlabel)

    plt.xlim(0, size)
    ax1.set_ylabel('Mean of Change Percentage', color='r')
    ax1.set_ylim(ydown,yup)
    ax2.set_ylabel('Stdv of Change Percentage', color='b')
    ax2.set_ylim(ydown,yup)
    ax1.legend(plots, labs)
    plt.title(Title)
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
    '''
    plot_hist('mean', mean, title='Mean Change Ratio')
    plot_hist('max', maxc, title='Max Change Ratio')
    plot_hist('min', minc, title='Min Change Ratio')
    plot_hist('stdv', stdv, title='standard diviation')
    plot_hist('hist', ratio[:, index], title='Change Ratio at Loc with max stdv')
    plot_lines('line', ratio[:, index], title='Change Ratio at Loc with max stdv')

    plot_lines('tmean', tmean, title='tmean')
    plot_lines('tstdv', tstdv, title='tstdv')
    plot_lines('tmax', tmax, title='tmax')
    plot_lines('tmin', tmin, title='tmin')
    '''
    plot_hist('maxhist', ratio[:, index], title='Distribution of Change Ratio' \
              + 'at the location with max stdv')
    plot_hist('overalhist', ratio, title='Distribution of Change Ration for Whole Data Set')

    locations = list()
    locations.append(ratio[:, 63]);
    locations.append(ratio[:, 1014]);
    locations.append(ratio[:, 3214]);
    locations.append(ratio[:, 5897]);
    locations.append(ratio[:, 8112]);
    
    plot_lines('location', locations, \
            title="Relative Changes in Data Values for Randomly" + \
                  "Selected Data Points", \
            ydown = -1.0, yup=0.0)

    plot_mean_stdv('distrib', [mean[2000:10000], stdv[2000:10000]], \
            Title = 'Mean and Stdv along Temperal Dimension for Each Data Point')
    
    plot_mean_stdv('average', [tmean, tstdv], \
            Title='Mean and Stdv of Relative Changes for Each Time Step', \
            xlabel='Time Step')
