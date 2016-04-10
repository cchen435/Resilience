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
    def __init__(self, method = None, win_size = None, \
            threshold = None, groups = None ):
        #print win_size, threshold

        if method is None:
            sys.exit('should setup one of following \
                    methods: linear, mean, and threshold')
        if ('linear' in method or 'statistic' in method) and \
                (win_size is None or threshold is None):
            sys.exit('the method is linear or mean, need to %s' % 
                    'setup the window size')
        if 'threshold' in method and threshold is None:
            sys.exit('the method is set as threshold, but\
                    forgot to setup the threshold value')
        self.win_size = win_size
        self.thresh = threshold
        self.method = method
        self.groups = groups
        self.history = list()
        # endif __init__

    ## begin definition of core kernels
    def _threshold( self, ratio):
        #print 'threshold value %f\n' % thresh
        flag = abs(ratio) < self.thresh
        if numpy.sum(flag) < numpy.size(flag):
            return True
        return False

    def _statistic( self, ratio):
        size = len(self.history)
        if size == 0 or size < self.win_size:
            self.history.append(ratio)
            return 0
        data = numpy.array(self.history)
        mean = numpy.mean(data, axis = 0)
        stdv = numpy.std(data, axis = 0)
        
        # delete the oldest timestep value
        # and append the new one to it.
        self.history.remove(self.history[0])
        self.history.append(ratio)

        diff = abs(ratio - mean)
        flag = diff <= self.thresh * stdv
        if numpy.sum(flag) < numpy.size(flag):
            return True
        else:
            return False
    # end of statistic 
    
    # linear method
    def _linear(self, ratio ):
        size = len(self.history)
        faulty = False
        if self.win_size < 2:
            print 'ft_linear: in appropriate value for window size'
            sys.exit(1)

        if size < self.win_size:   # no enough history data; return
            #print "no enough history"
            self.history.append(ratio)
            return 0
       
        # get statistic from history buffer
        x = numpy.array(range(self.win_size))
        data = numpy.array(self.history)

        # using numpy.lstsq, y = a * x + b will be
        # transferred to y =Ap, where A = [x 1], p = [a b]
        Coeff = numpy.c_[x, numpy.ones_like(x)]
        r = numpy.linalg.lstsq(Coeff, data)
        stdv = numpy.std(data, axis = 0)
        a, b = r[0]
        err  = r[1]

        predict = a * self.win_size + b;
        diff = abs(predict - ratio)

        flag = diff <= self.thresh * stdv 
        index = numpy.argwhere(flag==False)

        if numpy.sum(flag) < numpy.size(flag):
            faulty = True

        self.history.remove(self.history[0])
        self.history.append(ratio)
        return faulty
    # end of _linear

    # simple threshold method
    # return: 0 if no fault detected, 1 if fault detected
    def _ft_threshold( self, ratio):       
        (size, ) = ratio.shape
        if self.method == 'threshold_p':
            tmp_ratio = ratio
        elif self.method == 'threshold_l':
            tmp_mean = list()
            if self.groups is None:
                sys.exit('group is zero')
            size_per_group = size / self.groups
            for i in range(self.groups):
                tmp = numpy.mean(ratio[i:(i+1)*size_per_group])
                tmp_mean.append(tmp)
            tmp_ratio = numpy.array(tmp_mean);
        elif self.method == 'threshold_g':
            tmp_ratio = numpy.mean(ratio)
        else:
            sys.exit('unknown method')
        return self._threshold(tmp_ratio)
    
    def _ft_statistic( self, ratio):       
        (size, ) = ratio.shape
        if self.method == 'statistic_p':
            tmp_ratio = ratio
        elif self.method == 'statistic_l':
            tmp_mean = list()
            if self.groups is None:
                sys.exit('group is zero')
            size_per_group = size / self.groups
            for i in range(self.groups):
                tmp = numpy.mean(ratio[i:(i+1)*size_per_group])
                tmp_mean.append(tmp)
            tmp_ratio = numpy.array(tmp_mean);
        elif self.method == 'statistic_g':
            tmp_ratio = numpy.mean(ratio)
        else:
            sys.exit('unknown method')
        return self._statistic(tmp_ratio)
        
    def _ft_linear( self, ratio):       
        (size, ) = ratio.shape
        if self.method == 'linear_p':
            tmp_ratio = ratio
        elif self.method == 'linear_l':
            tmp_mean = list()
            if self.groups is None:
                sys.exit('group is zero')
            size_per_group = size / self.groups
            for i in range(self.groups):
                tmp = numpy.mean(ratio[i:(i+1)*size_per_group])
                tmp_mean.append(tmp)
            tmp_ratio = numpy.array(tmp_mean);
        elif self.method == 'linear_g':
            tmp_ratio = numpy.mean(ratio)
        else:
            sys.exit('unknown method')
        return self._linear(tmp_ratio)

    def detect(self, ratio):
        if self.method == 'linear_p' or      \
                self.method == 'linear_l' or \
                self.method == 'linear_g':
            return self._ft_linear(ratio)
        elif self.method == 'statistic_p' or    \
                self.method == 'statistic_l' or \
                self.method == 'statistic_g':
            return self._ft_statistic(ratio)
        elif self.method == 'threshold_p' or  \
                self.method == 'threshold_l' or \
                self.method == 'threshold_g':
            return self._ft_threshold(ratio)
        else:
            sys.exit('unknow detection method(%s): only support linear, mean, threshold now' % \
                    self.method)

