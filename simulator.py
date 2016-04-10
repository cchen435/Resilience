#!/usr/bin/env python

from optparse import OptionParser
import sys
import os

import fio
import detector
import pdb


def main():
    usage='usage: %prog workspace method -s windows -g groups -t threshold -v variable'
    parser = OptionParser(usage=usage)
    parser.add_option('-s', '--size', type='int', dest='win',
            help='window size')
    parser.add_option('-t', '--threshold', type='float', 
            dest='thresh', help='threhold value')
    parser.add_option('-v', '--variables', type='string', 
            dest='var', help='variable to evaluate')
    parser.add_option('-g', '--groups', type='int', 
            dest='groups', help='groups')

    (opts, args) = parser.parse_args()
    opts = vars(opts)
    
    if opts['win'] is None and opts['thresh'] is None:
        parser.print_help()
        sys.exit('need to set at least one value for %s' % \
                'either window size or threhold value')
    print args
    if len(args) != 2 or None in opts:
        parser.print_help()
        sys.exit('argument not correct, or opts error')
    workspace = args[0]
    method = args[1]
    win_size = opts['win']
    threshold = opts['thresh']
    variable = opts['var']
    groups = opts['groups']

    print workspace, method, win_size, threshold, variable

    datasets = fio.DataBase(workspace)
    #datasets.list_variables()

    detect = detector.Detector(method, win_size, threshold, groups)

    faults = 0
    faults_steps = list()
    while not datasets.is_done():
        print '\n\nFinished %.2f%%' % (datasets.progress() * 100)
        [prev, curr]=datasets.read(variable, 2)
        if prev is None or curr is None:
            print 'data is none'
            continue

        ratio = (curr - prev)/(abs(prev) + 1) 
        #pdb.set_trace()
        result = detect.detect(ratio)
        if result is True:
            faults += 1
            faults_steps.append(datasets.timestep())
            print 'detect error at timestep %d' % datasets.timestep()

    print 'number of faults %d, total steps %d' % (faults, datasets.get_timesteps())
    print 'time steps where a fault is detected: ', faults_steps
if __name__ == '__main__':
    main()
