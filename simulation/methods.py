'''
this file implements the mean method
used to detect faults

Author: Chao Chen
'''

import math
import sys
import numpy
from scipy import stats

history = []

# calculate the mean/median and stddvi
# along with time step dimention
def ft_mean( ratio, window ):
    global history
    (lat, lon) = ratio.shape
    size = len(history)

    # for the first two time steps no
    # history is stored
    if size == 0:
        history.append(ratio)
        print '1. history records %d\n' % len(history)
        return 0
    # history found, but less than window size
    # or take account into all history data
    elif size < window or window == 0:
        means = numpy.mean(abs(numpy.array(history)), axis=0)
        stddivs = numpy.std(abs(numpy.array(history)), axis=0)
    # history found, and larger than window size
    else:
        means = numpy.mean(abs(numpy.array(history[-window:])), axis=0)
        stddivs = numpy.std(abs(numpy.array(history[-window:])), axis=0)

    history.append(ratio)
    print 'history records %d\n' % len(history)

    # detech the fault by comparing current ratio with
    # mean and stddivs of history chage ratio
    means = means + 3*stddivs
    flag = abs(ratio) < means
    if numpy.sum(flag) < numpy.size(flag):
        (lat, lon) = numpy.where(flag==False)
        indexes = zip(lat, lon)
        # print 'indexes: ', indexes
        return 1
    else:
        return 0
# end ft_mean

# simple threshold method
# return: 0 if no fault detected, 1 if fault detected
def ft_threshold( ratio, thresh ):
    #print 'threshold value %f\n' % thresh
    flag = abs(ratio) < thresh
    if numpy.sum(flag) < numpy.size(flag):
        return 1
    return 0

# linear method
def ft_linear(ratio, window ):
    global history
    size = len(history)
    faulty = False

    # at least two history change ratios
    # is required
    if window < 2:
        print 'ft_linear: in appropriate value for window size'
        sys.exit(1)

    if size < window:   # no enough history data
        print "no enough history"
        history.append(abs(ratio))
        return 0
    else:   # enough history data
        (lat, lon) = ratio.shape
        x = numpy.array(range(window))

        # get standard diviation
        stddivs = numpy.std(numpy.array(history), axis=0)

        # using numpy.lstsq, y = m * x + c will be
        # transferred to y =Ap, where A = [x 1], p = [m c]

        Coeff = numpy.c_[x, numpy.ones_like(x)]
        temporary = numpy.array(history[-window:])

        (i, j, k) = temporary.shape
        temp = temporary.reshape(i, j * k )

        (a, b) = numpy.linalg.lstsq(Coeff, temp)[0]

        a = a.reshape(j,k)
        b = b.reshape(j,k)

        predict = abs(a) * window + abs(b);
        up = predict + 20 * stddivs + 0.002

        flag = abs(ratio) < up

        if numpy.sum(flag) < numpy.size(flag):
            (lat, lon) = numpy.where(flag==False)
            indexes = zip(lat, lon)
            # print 'indexes: ', indexes
            print (" a = %f, b = %f, pred = %f, std = %f," +
                            " ratio = %f, up = %f, index (%d, %d)") % (a[indexes[0]],
                                            b[indexes[0]], predict[indexes[0]], stddivs[indexes[0]],
                                            ratio[indexes[0]], up[indexes[0]], indexes[0][0], indexes[0][1])
            faulty = True


        '''
        # iterate over each data point, and get a, b
        # for each of them, using a, b to predict the
        # current value
        for i in xrange(lat):
                if faulty:
                        break
                for j in xrange(lon):
                        temporary = abs(numpy.array(history[-window:]))
                        y = numpy.array(temporary[-window:,i, j])
                        # print ' x= ', x
                        # print ' y= ', y
                        (a, b, tmp, tmp, tmp) = stats.linregress(x, y)


                        # using history standard diviation as a range
                        predict1 = abs(a) * window + b
                        predict2 = -1.0 * abs(a) * window + b

                        up = predict1 + 0.001
                        down = predict2 - 0.001

                        if abs(ratio[i, j]) < down or abs(ratio[i, j]) > up:
                                print (" a = %f, b = %f, pred = (%f, %f), std = %f," +
                                                " ratio = %f, down = %f, up = %f ") % (a, b, predict1,
                                                                predict2, stddivs[i,j], ratio[i,j], down, up)
                                faulty = True;
                                break
                # end of j loop
        # end of i loop
        '''
    # end of if-else
    history.append(abs(ratio))
    return faulty
# end of ft_linear


def ft_quad( window ):
    pass
