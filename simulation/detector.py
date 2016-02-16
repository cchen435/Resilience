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
    def __init__(self, method = None, \
            win_size = None, threshold = None ):
        print win_size, threshold

        if method is None:
            sys.exit('should setup one of following \
                    methods: linear, mean, and threshold')
        if (method == 'linear' or method == 'mean' or method == 'mean_linear') and win_size is None:
            sys.exit('the method is linear or mean, need to %s' % 
                    'setup the window size')
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
        print 'hist size:', size
        # for the first two time steps no
        # history is stored
        if size == 0 or size < self.win_size:
            self.history.append(ratio)
            return 0

        data = numpy.array(self.history)
        means = numpy.mean(data, axis = 0)
        stddivs = numpy.std(data, axis = 0)
        
        # delete the oldest timestep value
        # and append the new one to it.
        self.history.remove(self.history[0])
        self.history.append(ratio)

        # predict the value with history means and stdv
        # if actual ratio is large than predict value, 
        # treat it as a fault 
        #up = means + 1*stddivs
        up = means + 0.001

        print means[0], up[0]

        flag = ratio < up 
        if numpy.sum(flag) < numpy.size(flag):
            if DEBUG:
                (indexes,) = numpy.where(flag==False)
                print 'error happend at : ', indexes
                print 'mean = ', means[indexes]
                print 'up = ', up[indexes]
                print 'ratio = ', ratio[indexes]
                print 'std = ', stddivs[indexes]
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
        size = len(self.history)
        faulty = False

        if self.win_size < 2:
            print 'ft_linear: in appropriate value for window size'
            sys.exit(1)

        if size < self.win_size:   # no enough history data; return
            print "no enough history"
            self.history.append(ratio)
            return 0
       
        # get statistic from history buffer
        x = numpy.array(range(self.win_size))
        data = numpy.array(self.history)
        # get standard diviation of history
        stddivs = numpy.std(data, axis=0)

        # using numpy.lstsq, y = a * x + b will be
        # transferred to y =Ap, where A = [x 1], p = [a b]
        Coeff = numpy.c_[x, numpy.ones_like(x)]
        (a, b) = numpy.linalg.lstsq(Coeff, data)[0]

        predict = a * self.win_size + b;
        up = predict + 20 * stddivs + 0.03

        diff1 = predict - ratio
        diff2 = up - ratio

        flag = ratio <= up
        index = numpy.argwhere(flag==False)

        if numpy.sum(flag) < numpy.size(flag):
            if DEBUG:
                '''
                (indexes,) = numpy.where(flag==False)
                print 'locations: ', indexes
                print 'a = ', a[indexes]
                print 'b = ', b[indexes]
                print 'pred = ', predict[indexes]
                print 'up = ', up[indexes]
                print 'ratio = ', abs(ratio)[indexes]
                print 'std = ', stddivs[indexes]
                '''
                print 'x = ', x
                index = index[0]
                print 'locations:', index
                print 'history1', data[:, index]
                print 'stdv:', stddivs[index]
                print 'a = %f, b = %f' % (a[index], b[index])
                print 'predict(%f) - ratio(%f):%f' %( predict[index], ratio[index], diff1[index])
                print 'up(%f) - ratio(%f): %f'%( up[index], ratio[index], diff2[index])


            faulty = True

        self.history.remove(self.history[0])
        self.history.append(ratio)
        return faulty
    # end of ft_linear

    # linear method based on mean value of each time step
    def _ft_mean_linear(self, ratio ):
        size = len(self.history)
        faulty = False

        if self.win_size < 2:
            print 'ft_linear: in appropriate value for window size'
            sys.exit(1)
        
        mean_ratio = numpy.mean(ratio)

        if size < self.win_size:   # no enough history data; return
            print "no enough history"
            self.history.append(mean_ratio)
            return 0
       
        # get statistic from history buffer
        x = numpy.array(range(self.win_size))
        data = numpy.array(self.history)
        
        # get standard diviation of history
        stddivs = numpy.std(data, axis=0)

        # using numpy.lstsq, y = a * x + b will be
        # transferred to y =Ap, where A = [x 1], p = [a b]
        Coeff = numpy.c_[x, numpy.ones_like(x)]
        (a, b) = numpy.linalg.lstsq(Coeff, data)[0]

        predict = a * self.win_size + b;
        up = predict + 50 * stddivs

        diff1 = predict - mean_ratio
        diff2 = up - mean_ratio

        flag = mean_ratio <= up
        index = numpy.argwhere(flag==False)

        if DEBUG: 
            print 'x = ', x
            print 'history:', data 
            print 'stdv:', stddivs 
            print 'a = %f, b = %f' % (a, b) 
            print 'predict(%f) - ratio(%f):%f' %( predict, mean_ratio, diff1)
            print 'up(%f) - ratio(%f): %f'%( up, mean_ratio, diff2)
        
        if numpy.sum(flag) < numpy.size(flag):
            print 'x = ', x
            print 'history:', data 
            print 'stdv:', stddivs 
            print 'a = %f, b = %f' % (a, b) 
            print 'predict(%f) - ratio(%f):%f' %( predict, mean_ratio, diff1)
            print 'up(%f) - ratio(%f): %f'%( up, mean_ratio, diff2)


            faulty = True

        self.history.remove(self.history[0])
        self.history.append(mean_ratio)
        return faulty
    # end of ft_mean_linear

    def detect(self, ratio):
        if self.method == 'linear':
            return self._ft_linear(ratio)
        if self.method == 'mean_linear':
            return self._ft_mean_linear(ratio)
        elif self.method == 'mean':
            return self._ft_mean(ratio)
        elif self.method == 'threshold':
            return self._ft_threshold(ratio)
        else:
            sys.exit('unknow detection method(%s): only support linear, mean, threshold now' % \
                    self.method)

