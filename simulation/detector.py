'''
this file implements the mean method
used to detect faults

Author: Chao Chen
'''

import math
import sys
import numpy
from scipy import stats

DEBUG=0

class Detector():
    def __init__(self, win_size = None, \
            method = None, threshold = None ):
        if method is None:
            sys.exit('should setup one of following \
                    methods: linear, mean, and threshold')
        if method == 'linear' or method == 'mean' \
                and win_size is None:
            sys.exit('the method is linear or mean, need to \
                    setup the window size')
        if method == 'threshold' and threshold is None:
            sys.exit('the method is set as threshold, but\
                    forgot to setup the threshold value')
        self.win_size = win_size
        self.thresh = threshold
        self.method = method
        self.history = list()


    # detect the method based on mean value along
    # with the time dimension. using stdv as an adjustment
    def _ft_mean(self, ratio):
        size = len(self.history)

        # for the first two time steps no
        # history is stored
        if size == 0 or size < self.win_size:
            self.history.append(ratio)
            return 0

        data = abs(numpy.array(self.histroy))
        means = numpy.mean(data, axis = 0)
        stddivs = numpy.mean(data, axis = 0)
        
        # delete the oldest timestep value
        # and append the new one to it.
        self.history.remove(self.history[0])
        self.history.append(ratio)

        # predict the value with history means and stdv
        # if actual ratio is large than predict value, 
        # treat it as a fault 
        means = means + 3*stddivs
        flag = abs(ratio) < means 
        if numpy.sum(flag) < numpy.size(flag):
            if DEBUG:
                (location,) = numpy.where(flag==False)
                print 'error happend at : ', zip(location)
            return True
        else:
            return False
    # end ft_mean

    # simple threshold method
    # return: 0 if no fault detected, 1 if fault detected
    def _ft_threshold( self, ratio):
        #print 'threshold value %f\n' % thresh
        flag = abs(ratio) < self.threshold
        if numpy.sum(flag) < numpy.size(flag):
            return True
        return False

    # linear method
    def _ft_linear(self, ratio ):
        size = len(history)
        faulty = False

        if self.win_size < 2:
            print 'ft_linear: in appropriate value for window size'
            sys.exit(1)

        if size < self.win_size:   # no enough history data
            print "no enough history"
            self.history.append(abs(ratio))
            return 0
        
        # enough history data
        x = numpy.array(range(window))
        data = numpy.array(history)
        # get standard diviation
        stddivs = numpy.std(numpy.array(history), axis=0)

        # using numpy.lstsq, y = a * x + b will be
        # transferred to y =Ap, where A = [x 1], p = [a b]
        Coeff = numpy.c_[x, numpy.ones_like(x)]
        (a, b) = numpy.linalg.lstsq(Coeff, data)[0]

        predict = abs(a) * self.win_size + abs(b);
        up = predict + 20 * stddivs + 0.002
        flag = abs(ratio) < up
        if numpy.sum(flag) < numpy.size(flag):
            if DEBUG:
                (location) = numpy.where(flag==False)
                indexes = zip(location)
                # print 'indexes: ', indexes
                print (" a = %f, b = %f, pred = %f, std = %f," +
                        " ratio = %f, up = %f, index (%d, %d)") % (a[indexes[0]],
                            b[indexes[0]], predict[indexes[0]], stddivs[indexes[0]],
                            ratio[indexes[0]], up[indexes[0]], indexes[0][0], indexes[0][1])
            faulty = True

        self.history.remove(self.history[0])
        self.history.append(abs(ratio))
        return faulty
    # end of ft_linear


    def detect(self, ratio):
        if self.method == 'linear':
            return _ft_linear(ratio)
        elif self.method == 'mean':
            return _ft_mean(ratio)
        elif self.method == 'threshold':
            return _ft_threshold(ratio)
        else:
            sys.exit('unknow detect methods: only support linear, mean, threshold now')

