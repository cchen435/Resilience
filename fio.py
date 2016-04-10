#!/usr/bin/env python

import numpy

# NetCDF for reading netcdf files
#from Scientific.IO import NetCDF as nf
from scipy.io import netcdf as nf

# pygrib for reading GRIB files 
import pygrib
import adios
import os
import sys
import pdb
import re


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

'''
this file implements basic data abstraction
called database for datasets, each data set
contains multiple timesteps with each file 
represents a time step. the abstracted I/O operation
is to read a variable based on timestep, 
'''

''' a data base represents a set of data set '''
class DataBase():
    def __init__(self, workspace):
        path = os.path.abspath(workspace)
        if os.path.exists(path) == False:
            sys.exit('workspace (%s) not exist'%path)
        

        ''' files in the data set, expect each file represents a timestep '''
        files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
        sort_nicely(files)

        
        ''' empty directory '''
        if len(files) == 0:
            sys.exit('no file found in %s, please examine the setup' % path)


        ''' class global variables '''
        
        # path to files, used for reading
        self.workspace = path
        # data sets in terms of files 
        self.files = files
        # simulating current steps, 
        self.curr = 0;
        
        self.timesteps = len(files)
        
        # variables in the data set
        self.variables = self.__get_variables()
        
        self.finished = False

    
    # return the totla timesteps under the workspace, assuming each file
    # respresnets a time step.
    def get_timesteps(self):
        return self.timesteps

    def is_done(self):
        return self.finished

    # read a variable from a NetCDF file 
    def __nc_read(self, fname, v):
        try:
            fh = nf.netcdf_file(fname, 'r', mmap=True)
        except:
            sys,exit('error when reading var %s from file %s' %(variable, fname))
        if v not in fh.variables:
            print 'warning: variable %s not found in dataset' % variable
            fh.close()
            return None
        else:
            data = fh.variables[v][:].copy().ravel()
            fh.close()
            return data

    # get all variables from a NetCDF file
    def __nc_variables(self, fname):
        name = list();
        fh = nf.netcdf_file(fname, 'r')
        for v in fh.variables:
            name.append(v)

        fh.close()
        return name

    # read a bp file

    # read a variable data from BP file
    def __bp_read(self, fname, variable):
        if os.path.exists(fname) and os.path.isfile(fname):
            fh = adios.file(fname)
            v = fh.var[variable]
            data = v.read().ravel()
            fh.close()
            return data
        else:
            print "error happend: var%s file:%s" % (variable, fname)

    def __bp_variables(self, fname):
        name = list()
        fh = adios.file(fname)
        for v in fh.var:
            name.append(v)
        fh.close()
        return name


    # read an variable from a grib file
    def __grib_read(self, fname, variable):
        gribs = pygrib.open(fname)
        tmp = gribs.select(name = variable)
        gribs.close()

        data = list()
        for item in tmp:
            data.append(item.values)
        if len(data) == 0:
            return None
        return numpy.array(data).ravel()

    def __grib_variables(self, fname):
        gribs = pygrib.open(fname)
        name = list()
        for grb in gribs:
            name.append(grb.name)
        gribs.close()

        name.sort()
        return list(set(name))

    # general interface
    def read(self, variable, steps = 1):
        if self.curr == self.timesteps:
            self.finished = True
            return None

        if variable not in self.variables:
            sys.exit("the variable %s not in data set" % variable)
        
        data = list();

        for i in range(steps):
            if self.curr + i == self.timesteps:
                self.finished = True;
                break

            fname = os.path.join(self.workspace, self.files[self.curr+i])
            name, ext = os.path.splitext(fname) 
            if ext == '.grb':
                data.append(self.__grib_read(fname, variable))
            elif ext == '.nc':
                data.append(self.__nc_read(fname, variable))
            elif ext == '.bp':
                data.append(self.__bp_read(fname, variable))
            else:
                sys.exit('unknown file formate (%s) for (%s)' % (ext, fname))
            
        self.curr += 1
        if self.curr+steps > self.timesteps:
            self.finished = True

        return data

    
    # print progress infomation
    def progress(self):
        return float(self.curr)/(self.timesteps)

    # print current timestep
    def timestep(self):
        return self.curr

    def __get_variables(self):
        fname = os.path.join(self.workspace, self.files[0])
        name, ext = os.path.splitext(fname)
        if ext == '.grb':
            return self.__grib_variables(fname)
        elif ext == '.nc':
            return self.__nc_variables(fname)
        elif ext == '.bp':
            return self.__bp_variables(fname)
        else:
            sys.exit('unknown file formate')

    def get_files(self):
        return self.files
    
    # return varibles in the file 
    def get_variables(self):
        return self.variables

    def reset(self):
        self.curr = 0;
        self.finished = False
