#!/usr/bin/env python

import numpy

# NetCDF for reading netcdf files
from Scientific.IO import NetCDF as nf

# pygrib for reading GRIB files 
import pygrib

import os
import sys

'''
this file implements the I/O
operations to read data from 
netCDF, grib and bp files
return variable is a dictionary 
with variable names as keys, and
variable contents as values. 
'''

# read a netcdf file
def ncget(fname):
    variables = dict()
    fh = nf.NetCDFFile(fname, 'r')
    for v in fh.variables:
        data = fh.variables[v][:].ravel()
        variables[v] = data
    fh.close()
    return variables


# read a bp file 
def bpget(fname):
    variables = dict()
    tmpfile = '/tmp/fault'
    tmpdatafile = '/tmp/faultdata'

    # using 'bpls' command to get the vairalbe lists
    cmd = 'bpls ' + fname +  ' > ' + tmpfile
    os.system(cmd)

    # analyze each line of 'bpls output'
    # and only focuse on double type array data
    with open(tmpfile, 'r') as fh:
        for line in fh:
            line = line.strip()
            if line.startswith('double'):
                line = line.replace('{', '')
                line = line.replace('}', '')
                line = line.replace(',', '')
                line = line.split()

                # get the variable name and dimention info
                name = line[1]
                dim = (int(line[2]), int(line[3]), int(line[4]))
                #print line, name, dim

                # extract the related data for the variable using 'bp2ascii'
                # utility
                cmd = (' ').join(['bp2ascii -v', name, fname, tmpdatafile, '> /tmp/tmpfile'])
                os.system(cmd)

                with open(tmpdatafile, 'r') as f:
                    data =numpy.array(map(float, f.read().split()))
                    variables[name] = data

    return variables



# read a grib file
def gribget(fname):
    variables = dict()
    gribs = pygrib.open(fname)
    for grb in gribs:
        name = grb.name
        if variables.has_key(name) == False:
            variables[name] = [grb.values]
        else:
            variables[name].append(grb.values)
    # convert list to flattened numpy array
    for key in variables.keys():
        variables[key] = numpy.array(variables[key]).ravel()

    return variables


# general interface
def getfile(fname):
    file_name, file_extension = os.path.splitext(fname)
    if file_extension == 'grb':
        return gribget(fname)
    elif file_extension == 'nc':
        return ncget(fname)
    elif file_extension == 'bp':
        return bpget(fname)
    else:
        sys.exit('unknown file formate')



