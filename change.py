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
import pygrib
import adios

import matplotlib.pyplot as plt

def __bp_read(fname, variable):
    try:
        fh = adios.file(fname)
    except:
        print "error happend: var=%s file%s" % (variable, fname)
    if v in fh.var:
        v = fh.var[variable]
        data = v.read().ravel()
        fh.close()
        return data
    else:
        print "warning, variable %s not found in file %s" % (variable, fname)


def __bp_variables(fname):
    name = list()
    fh = adios.file(fname)
    for v in fh.var:
        name.append(v)
    fh.close()
    return name 

# read an variable from a grib file
def __grib_read(fname, variable):
    gribs = pygrib.open(fname)
    tmp = gribs.select(name = variable)
    gribs.close() 
    data = list()
    for item in tmp:
        data.append(item.values)
    
    if len(data) == 0:
        return None
    return np.array(data).ravel()

   
def __grib_variables(fname):
    gribs = pygrib.open(fname)
    name = list()
    for grb in gribs:
        name.append(grb.name)
    gribs.close()

    name.sort()
    return list(set(name))

# read a variable from a NetCDF file 
def __nc_read(fname, v):
    try:
        fh = nf.netcdf_file(fname, 'r', mmap=False)
    except:
        sys,exit('error when reading var %s from file %s' %(variable, fname))

    if v not in fh.variables:
        print 'warning: variable %s not found in dataset' % variable
        fh.close()
        return None
    else:
        data = fh.variables[v][:].ravel()
        fh.close()
        return data

# get all variables from a NetCDF file
def __nc_variables(fname):
    name = list();
    fh = nf.netcdf_file(fname, 'r')
    for v in fh.variables:
        name.append(v)

    fh.close()
    return name
        
# general interface
def read(fname, variable):
    name, ext = os.path.splitext(fname)
    if ext == '.grb':
        data = __grib_read(fname, variable)
    elif ext == '.nc':
        data = __nc_read(fname, variable)
    elif ext == '.bp':
        data = __bp_read(fname, variable)
    else:
        sys.exit('unknown file formate (%s) for (%s)' % (ext, fname))     
    
    return data

def get_variables(fname):
    name, ext = os.path.splitext(fname)
    if ext == '.grb':
        data = __grib_variables(fname)
    elif ext == '.nc':
        data = __nc_variables(fname)
    elif ext == '.bp':
        data = __bp_variables(fname)
    else:
        sys.exit('unknown file formate (%s) for (%s)' % (ext, fname))     
    
    return data


def main(argv):
    if len(argv) < 3:
        sys.exit('Usage: %s file1 file2' % argv[0])
    if not os.path.exists(argv[1]):
        sys.exit('ERROR: file- %s was not found!' % argv[1])
    if not os.path.exists(argv[2]):
        sys.exit('ERROR: file- %s was not found!' % argv[2])
    #pdb.set_trace()

    CWD = os.getcwd()
    if argv[1][0] !='/':
        file1 = os.path.join(CWD, argv[1])
    else:
        file1 = argv[1]

    if argv[2][0] !='/':
        file2 = os.path.join(CWD, argv[2])
    else:
        file2 = argv[2]

    var1 = get_variables(file1)
    var2 = get_variables(file2)
    if var1 != var2:
        print 'different output'
    
    print "number of variables", len(var1)

    for var in var1:
        data1 = read(file1, var)
        data2 = read(file2, var)
        diff = (data2-data1)/(abs(data1) + 0.2)
        diff *= 100.0
        plt.plot(diff, 'b')
        plt.xlim([0, diff.size])
        plt.xlabel('Data Point ID')
        plt.ylabel('Change Percentage (%)')
        plt.savefig('.'.join([var, 'chg', 'pdf']))
        plt.clf()

        hist, bins = np.histogram(diff, bins=21)
        center = (bins[:-1]+bins[1:])/2
        width =  0.7 * (bins[1]-bins[0])
        hist = hist * 100.0 /diff.size
        plt.bar(center, hist, align='center', width = width)
        plt.ylabel('Data Point Counts (in Percentage)')
        plt.xlabel('Change Percentage (%)')
        plt.savefig('.'.join([var, 'hist', 'pdf']), bbox_inches='tight')
        plt.clf()
        

if __name__ == '__main__':
    main(sys.argv)
