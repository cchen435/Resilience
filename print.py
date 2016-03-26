#!/usr/bin/env python
# Copyright (c) Georgia Instituted of Technology
# Author: C. Chen
# Script functionality description
# Create time: 2016-03-15 13:23:24


import os
import sys
import pdb
import re
import numpy as np
from scipy.io import netcdf as nf

def tryint(s):
    try:
        return int(s)
    except:
        return s

def alphanum_key(s):
    '''
    turn "z23a" --> ['z', 23, 'a']
    '''
    return [tryint(c) for c in re.split('([0-9]+)', s)]

def sort_nicely(l):
    l.sort(key=alphanum_key)


def main(argv):
    if len(argv) < 2:
        sys.exit('Usage: %s work-directory [variable-name]' % argv[0])
    if not os.path.exists(argv[1]):
        sys.exit('ERROR: work-directory %s was not found!' % argv[1])
    #pdb.set_trace()

    if argv[1][0] !='/':
        CWD = os.getcwd()
        workspace = os.path.join(CWD, argv[1])
    else:
        workspace = argv[1]

    files = [f for f in os.listdir(workspace) \
            if os.path.isfile(os.path.join(workspace, f))]
    
    sort_nicely(files)

    print "%20s %7s %15s %15s %15s %15s" % ('file', 'vars', 'sum', \
            'mean', 'shape', 'idx') 
    for f in files:
        path = os.path.join(workspace, f)
        fh = nf.netcdf_file(path, 'r')
        for v in fh.variables:
            data = fh.variables[v][:]
            sumx = data.sum()
            mean = data.mean()
            if sumx != 0:
                idx  = np.transpose(data.nonzero())
                if len(idx) > 4:
                    idx = idx[0:3]
                else:
                    idx = idx[0:len(idx)]

            else:
                idx = None

            print "%20s %7s %15s %15s %15s %15s" % (f, v, str(sumx), \
                    str(mean), str(data.shape), str(idx).replace('\n', '')) 
        print '\n'

if __name__ == '__main__':
    main(sys.argv)
