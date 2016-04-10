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
    gmean = numpy.mean(ratio, axis=0)
    gmaxv = numpy.max(ratio, axis=0)
    gminv = numpy.min(ratio, axis=0)
    gstdv = numpy.std(ratio, axis=0)

    # statistics alone with array, it calcs
    # the statistic for each time step
    tmean = numpy.mean(ratio, axis=1)
    tmaxv = numpy.max(ratio, axis=1)
    tminv = numpy.min(ratio, axis=1)
    tstdv = numpy.std(ratio, axis=1)

    return (gmaxv, gminv, gmean, gstdv, tmaxv, tminv, tmean, tstdv)
    #return (maxv, minv, mean, stdv)
    #return stdv

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

def plot_lines(fname, data, title = 'Change ratio'\
        , xlabel = None, ylabel = None):
    array = numpy.array(data)
    #style=['ro-', 'b*-', 'gs-', 'kD-', 'mx-'];
    style=['r', 'b', 'k', 'g', 'm'];
    if array.ndim == 1:
        items = 1
        size = array.size
    else:
        (items, size) = array.shape

    x = numpy.array(range(size))
    plt.ticklabel_format(useOffset=False, style='plain')
    plt.xlim(0, size)
    
    if array.max() < 0.01:
        yup   = array.max() * 3
        ydown = array.min() * 3
    else: 
        yup   = array.max() * 1.5
        ydown = array.min() - 0.2
    if yup is not None and ydown is not None:
        plt.ylim(ydown, yup)
    
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


def plot_mean_stdv(fname, data, xlabel = None, \
                   Title = 'Mean and Stdv of Change Ratios for Each Location'):
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


    mydown = array[0].min() * 3
    myup   = array[0].max() * 3 

    plt.xlim(0, size)
    ax1.set_ylabel('Mean of Change Percentage (%)', color='r')
    if mydown is not None and myup is not None:
        ax1.set_ylim(mydown,myup)
    ax2.set_ylabel('Stdv of Change Percentage', color='b')
    
    sydown = array[1].min() * 3
    sydown = 0 
    syup   = array[1].max() * 3
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

    while not datasets.is_done():
        print '\n\n Progress. Finished: %.02f%%' % (datasets.progress() * 100)
        #time.sleep(1)
        [prev, curr] = datasets.read(variable, 2)
        if prev is None or curr is None:
            print 'Finished'
            break

        # calc and store the change ratio
        #tmp = abs(curr)/(abs(prev) + 1) - 1
        tmp = (curr - prev)/(abs(prev) + 1)
        #tmp = (abs(curr) - abs(prev))/(abs(prev) + 1)
        
        ratio_list.append(tmp)
        
    print '\n\n Progress. Finished: %.02f%%' % (datasets.progress() * 100)
    ratio = numpy.array(ratio_list)
    (gmaxc, gminc, gmean, gstdv, tmax, tmin, tmean, tstdv) = calc_statistic(ratio)


    # threshold based on each point care about the [min, max] for each time step 
    # among each pair of [min, max] for each time step to find [tmin, tmax] for
    # global
    plot_lines('threshold_p', [tmax, abs(tmin)], \
            title='Max/min Ratio of Each Time Step', xlabel = 'Time Step')
   
    print 'tmax: ', tmax
    print 'tmin: ', tmin
    print 'tmean: ', tmean

    # threhold based on average cares about mean value of each step, 
    # and find threshold with max abs(mean) among time steps
    plot_lines('threshold_l', tmean, title='Max Change of Each Time Step', \
            xlabel = 'Time Step')


    (steps, size) = ratio.shape
    # calculate the statistic for each point based on a time window
    # statistic on each point care about the predicts vaule against 
    # real value for each point, here plot their diff and predicted 
    # stdvs at location with max variations
    win_size = 3
    tmp_mean = list()
    tmp_stdv = list()
    for i in range(1, steps+1):
        if i < win_size:
            tmp_mean.append(numpy.mean(ratio[0:i, :], axis=0))
            tmp_stdv.append(numpy.std(ratio[0:i, :], axis=0))
        else:
            tmp_mean.append(numpy.mean(ratio[i-win_size:i, :], axis=0))
            tmp_stdv.append(numpy.std(ratio[i-win_size:i, :], axis=0))
    pmean = numpy.array(tmp_mean)
    pstdv = numpy.array(tmp_stdv)
    pdiff = abs(pmean-ratio)
    indexes = gstdv.argsort()
    thresh = 2;
    plot_lines('statistic_p', [pdiff[:, indexes[-1]], \
            pstdv[:, indexes[-1]], pstdv[:, indexes[-1]]*thresh])
    plot_lines('statistic_p_o', [pmean[:, indexes[-1]], ratio[:, indexes[-1]]])

    # statitic on each location care predict value of each location
    tmp_mean = list()
    tmp_stdv = list()

    size = tmean.size
    #win_size = 5
    for i in range(1,size+1):
        if i < win_size:
            tmp_mean.append(tmean[0:i].mean())
            tmp_stdv.append(tmean[0:i].std())
        else:
            tmp_mean.append(tmean[i-win_size:i+1].mean())
            tmp_stdv.append(tmean[i-win_size:i+1].std())
    lmean = numpy.array(tmp_mean)
    lstdv = numpy.array(tmp_stdv)
    ldiff = abs(lmean-tmean)

    plot_lines('statistic_l', [ldiff, lstdv, lstdv * thresh], \
            xlabel='Time Step')
    plot_lines('statistic_l_o', [lmean, tmean], xlabel='Time Step')

	## linear cares about the predicted value and square err
    #win_size = 5
    x = numpy.array(range(win_size))
    lstp_lst = list()
    lste_lst = list()
    for i in range(1, steps+1):
        if i < win_size:
            lstp_lst.append(numpy.mean(ratio[0:i, :], axis=0))
            lste_lst.append(numpy.std(ratio[0:i, :], axis=0))
        else:
            data = ratio[i-win_size:i, :]
            Coeff = numpy.c_[x, numpy.ones_like(x)]
            r = numpy.linalg.lstsq(Coeff, data)
            a,b = r[0] 
            err = r[1]
            lstp_lst.append(a*win_size+b)
            lste_lst.append(numpy.std(ratio[i-win_size:i, :], axis=0))
            
    lstp = numpy.array(lstp_lst)	
    lste = numpy.array(lste_lst)	
    lstdiff = abs(lstp - ratio)
    plot_lines('linear_p', [lstdiff[:, indexes[-1]], \
            lste[:, indexes[-1]], lste[:, indexes[-1]]*thresh], \
            title='Difference of predict value and original value+err')
    
    plot_lines('linear_p_o', [lstp[:, indexes[-1]], ratio[:, indexes[-1]]], \
            title='Difference of predict value and original value+err')
  
    print 'original_p:'
    print ratio[0:15,indexes[-1]]
    print 'linear_p:'
    print lstp[0:15, indexes[-1]]
    print 'linear_p_diff:'
    print lstdiff[0:15,indexes[-1]]

    size = tmean.size
    #win_size = 5
    x = numpy.array(range(win_size))
    lstl_lst = list()
    lste_lst = list()
    for i in range(1, size+1):
        if i < win_size:
            lstl_lst.append(tmean[0:i].mean())
            lste_lst.append(tmean[0:i].std())
        else:
            data = tmean[i-win_size:i]
            Coeff = numpy.c_[x, numpy.ones_like(x)]
            r = numpy.linalg.lstsq(Coeff, data)
            a,b = r[0]
            err = r[1]
            lstl_lst.append(a*win_size+b)
            lste_lst.append(tmean[i-win_size:i].std())
    lstl = numpy.array(lstl_lst)
    lste = numpy.array(lste_lst)
    lstdiff = abs(lstl - tmean)
    plot_lines('linear_l', [lstdiff, lste, lste*thresh], \
            title='Difference of predict value and original value+err')
    plot_lines('linear_l_o', [lstl, tmean], \
            title='Difference of predict value and original value+err')
    print 'original_p:'
    print tmean[0:15]
    print 'linear_l:'
    print lstl[0:15]
    print 'linear_l_diff:'
    print lstdiff[0:15]
    print lstl[0:15]

    ''' 
    plot_lines('line', ratio[:, indexes[-1]], \
            title='Change Ratio at Loc (%d)' % indexes[-1])
    plot_hist('maxhist', ratio[:, indexes[-1]], \
            title='Distribution of Change Ratio' \
              + ' at the location with max stdv')
    plot_hist('overalhist', ratio, \
            title='Distribution of Change Ration for Whole Data Set')

    locations = [indexes[stdv.size/4], indexes[stdv.size/2-20], \
            indexes[stdv.size/2]]
    #multiply 100 for percentage
    
    points = ratio[:, locations].transpose() * 100

    plot_lines('location', points, \
            title="Changes Ratios of Data Points along Temporal Dimension")

    plot_mean_stdv('average', [tmean, tstdv], \
            Title='Mean and Stdv of Relative Changes for Each Time Step', \
            xlabel='Time Step')
    
    plot_lines('stdv', stdv[:210000], \
            title="Standard Variation of each Data Point" \
            , ylabel='Standard Variation'\
            , xlabel='Data Points')
    print 'tstdv :', tstdv
    
   
    print 'tmean', tmean
    print 'mean of tmean', mean_of_tmean

    plot_lines('tmean_mean', [tmean, numpy.array(mean_of_tmean), \
        numpy.array(stdv_of_tmean), numpy.array(diffs_mean_tmean)], \
            title='tmean+mean of tmean', \
            xlabel='Time Step')

    print 'stdv of tmean', stdv_of_tmean
    print 'diff tmean m ', diffs_mean_tmean
    '''   
