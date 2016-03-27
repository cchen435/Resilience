#!/usr/bin/env python2.7

'''
This module is for analysis climate data
in format of grib
Author: Chao Chen
'''

from optparse import OptionParser

import matplotlib
#matplotlib.use('GTK')
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

import math
import sys
import numpy
import os
import time

import fio

#import pdb

#control arguments
#numpy.set_printoptions(precision=6)
numpy.set_printoptions(suppress=True)

DEBUG=0

'''
get the parameters and levels for each parameters in the file
'''

## calc statistic of a 2D aray along with
## the time step (1st) dimention
def calc_statistic(ratio):

    (steps, size) = ratio.shape
    
    # statistics alone with timestep, it calcs 
    # the statistic for each location
    mean = numpy.mean(ratio, axis=0)
    maxv = numpy.max(ratio, axis=0)
    minv = numpy.min(ratio, axis=0)
    stdv = numpy.std(ratio, axis=0)

    '''
    # statistics alone with array, it calcs
    # the statistic for each time step
    tmean = numpy.mean(ratio, axis=1)
    tmaxv = numpy.max(ratio, axis=1)
    tminv = numpy.min(ratio, axis=1)
    tstdv = numpy.std(ratio, axis=1)

    return (maxv, minv, mean, stdv, tmaxv, tminv, tmean, tstdv)
    '''
    return (maxv, minv, mean, stdv)


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
    plt.savefig('.'.join([name, 'pdf']), bbox_inches='tight')
    plt.clf()

def plot_lines(fname, data, title = 'Change ratio', yup = None,\
               ydown = None, xlabel = None, ylabel = None):
    array = numpy.array(data)
    #style=['ro-', 'b*-', 'gs-', 'kD-', 'mx-'];
    style=['r', 'b', 'k', 'g', 'm'];
    if array.ndim == 1:
        items = 1
        size = array.size
    else:
        (items, size) = array.shape

    print 'items, size :', items, size
    x = numpy.array(range(size))
    plt.ticklabel_format(useOffset=False, style='plain')
    plt.xlim(0, size)
    
    if yup is not None and ydown is not None:
        plt.ylim(ydown, yup)
    
    print 'dim: ', array.ndim
    if array.ndim > 1:
        for i in range(items):
            plot = plt.plot(x, array[i], style[i], label='Data Point %d'%i)
    else:
        print 'name', fname
        plot = plt.plot(x, array, style[0])

    if array.ndim > 1:
        plt.legend(loc=4)

    plt.xlabel('Time Step')
    if xlabel is not None:
        plt.xlabel(xlabel)
    plt.ylabel('Change Percentage (%)')
    if ylabel is not None:
        plt.ylabel(ylabel)
    plt.title(title)
    
    plt.savefig('.'.join([fname, 'pdf']), bbox_inches='tight')
    plt.clf()


def plot_mean_stdv(fname, data, \
                   Title = 'Mean and Stdv of Change Ratios for Each Location', \
                   xlabel = None, mydown = None, myup = None, \
                   sydown = None, syup = None):
    array = numpy.array(data)
    (tmp, size) = array.shape
    x = numpy.array(range(size))

    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx()
    array[0] = array[0] * 100
    plot1 = ax1.plot(x, array[0], 'r-', label='Mean')
    plot2 = ax2.plot(x, array[1], 'b--', label='Stdv')
    plots=plot1+plot2
    labs=[l.get_label() for l in plots]

    ax1.set_xlabel('Data Point ID');
    if xlabel is not None:
        ax1.set_xlabel(xlabel)

    plt.xlim(0, size)
    ax1.set_ylabel('Mean of Change Percentage (%)', color='r')
    if mydown is not None and myup is not None:
        ax1.set_ylim(mydown,myup)
    ax2.set_ylabel('Stdv of Change Percentage', color='b')
    if sydown is not None and syup is not None:
        ax2.set_ylim(sydown,syup)
    ax1.legend(plots, labs)
    plt.title(Title)
    plt.savefig('.'.join([fname, 'pdf']), bbox_inches='tight')
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

    datasets = fio.DataBase(workspace)

    # storing the change ratio
    ratio_list = list()

    # recording the mean value for each time step
    tmean_list = list()
    tstdv_list = list()

    while not datasets.is_done():
        print '\n\n Progress. Finished: %.02f%%' % (datasets.progress() * 100)
        time.sleep(1)
        [prev, curr] = datasets.read(variable, 2)
        if prev is None or curr is None:
            print 'Finished'
            break

        # calc and store the mean and stdv value for each time step
        tmean_list.append(curr.mean()/prev.mean() - 1)
        #tmean_list.append(abs(curr).mean()/abs(prev).mean() - 1)
        tstdv_list.append(numpy.array(tmean_list).std())

        # calc and store the change ratio
        #tmp = abs(curr)/(abs(prev) + 1) - 1
        tmp = (curr - prev)/(prev + 1)
        #tmp = (abs(curr) - abs(prev))/(abs(prev) + 1)
        ratio_list.append(tmp)
        
        if size is not None and datasets.get_timestep() == size:
            print 'Finished with up to expected timesteps'
            break

    ratio = numpy.array(ratio_list)
    #(maxc, minc, mean, stdv, tmax, tmin, tmean, tstdv) = calc_statistic(ratio)
    (maxc, minc, mean, stdv) = calc_statistic(ratio)

    tmean = numpy.array(tmean_list)
    tstdv = numpy.array(tstdv_list)

    indexes = stdv.argsort()
    
    plot_lines('line', ratio[:, indexes[-1]], title='Change Ratio at Loc (%d)' % indexes[-1])
    plot_hist('maxhist', ratio[:, indexes[-1]], title='Distribution of Change Ratio' \
              + ' at the location with max stdv')
    plot_hist('overalhist', ratio, title='Distribution of Change Ration for Whole Data Set')

    locations = [indexes[stdv.size/4], indexes[stdv.size/2-20], indexes[stdv.size/2]]
    print 'locations:', locations
    points = ratio[:, locations].transpose() * 100

    print "points shape", points.shape

    plot_lines('location', points, \
            title="Changes Ratios of Data Points along Temporal Dimension" \
            , ydown=-0.01, yup = 0.01)
    '''
    plot_mean_stdv('distrib', [mean[0:2000], stdv[0:2000]], \
            Title = 'Mean and Stdv along Temperal Dimension for Each Data Point', \
            mydown = -1.3, myup = -0.3, sydown= -0.1, syup = 0.1)
    '''
    plot_mean_stdv('distrib', [mean, stdv], \
            Title = 'Mean and Stdv along Temperal Dimension'+\
            ' for Each Data Point')
    '''
    \
            mydown = -1.3, myup = -0.5, sydown = -0.01, syup = 0.01);
    '''

    ''' 
    plot_mean_stdv('average', [tmean, tstdv], \
            Title='Mean and Stdv of Relative Changes for Each Time Step', \
            xlabel='Time Step', mydown = -0.8, myup = -0.5, \
            sydown = 0.3, syup = 0.5)
    '''

    plot_mean_stdv('average', [tmean, tstdv], \
            Title='Mean and Stdv of Relative Changes for Each Time Step', \
            xlabel='Time Step')
    
    plot_lines('stdv', stdv, \
            title="Standard Variation of each Data Point" \
            , ydown = 0, yup = 0.004, ylabel='Standard Variation'\
            , xlabel='Data Points')
    '''
    mydown=0.01, myup = 0.01, \
            sydown=0.0, syup = 0.01) 
    '''
