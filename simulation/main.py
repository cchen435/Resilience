#!/usr/bin/env python

from optparse import OptionParser
import sys
import os

import fio
import detector


def main():
    usage='usage: %prog workspace, method, [-s windows], [-t threshold]'
    parser = OptionParser(usage=usage)
    parser.add_option('-s', '--size', type='int', dest='win',
            help='window size')
    parser.add_option('-t', '--threshold', type='string', 
            dest='thresh', help='threhold value')
    parser.add_option('-v', '--variables', type='string', 
            dest='var', help='variable to evaluate')

    (opts, args) = parser.parse_args()
    opts = vars(opts)
    
    if opts['win'] is None and opts['thresh'] is None:
        sys.exit('need to set at least one value for %s' % \
                'either window size or threhold value')
    print args
    if len(args) != 2:
        parser.print_help()
        sys.exit('argument not correct')
    workspace = args[0]
    method = args[1]
    win_size = opts['win']
    threshold = opts['thresh']
    variable = opts['var']
    print workspace, method, win_size, threshold

    datasets = fio.DataBase(workspace, variable)
    datasets.list_variables()

    detect = detector.Detector(method, win_size)
    
    while not datasets.done():
        print datasets.get_progress()
        (prev, curr)=datasets.get()
        if prev is None or curr is None:
            print 'data is none'
            continue

        ratio = abs(curr)/(abs(prev) + 1) - 1
        detect.detect(ratio)


if __name__ == '__main__':
    main()
