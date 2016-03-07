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

class DataBase():
    def __init__(self, workspace, variable):
        path = os.path.abspath(workspace)
        if os.path.exists(path) == False:
            sys.exit('workspace (%s) not exist'%path)

        files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
        files.sort()

        self.workspace = path
        if len(files) == 0:
            sys.exit('no file found in %s, please examine the setup' % path)

        self.files = files
        self.curr = 0;
        self.timesteps = len(files)
        self.variable = variable
        self.finished = False

	
	# return the totla timesteps under the workspace, assuming each file
	# respresnets a time step.
    def get_timesteps(self):
        return self.timesteps

    def done(self):
        return self.finished

    # read a netcdf file
    def ncget(self, fname, variable):
        fh = nf.NetCDFFile(fname, 'r')
        for v in fh.variables:
            if v == variable:
                data = fh.variables[v][:].ravel()
                return data
        fh.close()
        return None

    def nclist(self, fname):
        fh = nf.NetCDFFile(fname, 'r')
        for v in fh.variables:
            print v
        fh.close()

    # read a bp file
    '''
    def bpget(self, fname, variable):
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
                    if name == variable:
                        cmd = (' ').join(['bp2ascii -v', name, fname, tmpdatafile, '> /tmp/tmpfile'])
                        os.system(cmd)

                        with open(tmpdatafile, 'r') as f:
                            data =numpy.array(map(float, f.read().split()))
                        return data
        return None
    '''

    def bpget(self, fname, variable):
        tmpfile = '/tmp/fault'
        #tmpdatafile = '/tmp/data.nc'
        #ncfile = '.'.join([fname.split('.')[0], 'nc'])
        ncfile = '/tmp/nc' 
        cmd = ' '.join(['bp2ncd', fname, ncfile, '>', 'tmpfile'])
        os.system(cmd);
        data = self.ncget(ncfile, variable)
        cmd = ' '.join(['rm', ncfile])
        os.system(cmd)
        return data

    def bplist(self, fname):
        tmpfile = '/tmp/fault'
        cmd = 'bpls ' + fname +  ' > ' + tmpfile
        os.system(cmd)
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
                    print name

    # read a grib file
    def gribget(self, fname, variable):
        gribs = pygrib.open(fname)
        tmp = gribs.select(name = variable)
        gribs.close()

        data = list()
        for item in tmp:
            data.append(item.values)
        if len(data) == 0:
            return None
        return numpy.array(data).ravel()

    def griblist(self, fname):
        gribs = pygrib.open(fname)
        name = list()
        for grb in gribs:
            name.append(grb.name)
        gribs.close()

        for item in set(name):
            print item

    # general interface
    def next(self):
        if self.curr == self.timesteps:
            self.finished = True
            return None

        fname = os.path.join(self.workspace, self.files[self.curr])
        self.curr += 1
        
        tmp, file_extension = os.path.splitext(fname)
        if file_extension == '.grb':
            data = self.gribget(fname, self.variable)
        elif file_extension == '.nc':
            data = self.ncget(fname, self.variable)
        elif file_extension == '.bp':
            data = self.bpget(fname, self.variable)
        else:
            sys.exit('unknown file formate (%s)' % fname)
        
        if self.curr == self.timesteps:
            self.finished = True

        return data

    def get(self):
        if self.curr == self.timesteps - 1:
            self.finished = True
            return (None, None)

        f1 = os.path.join(self.workspace, self.files[self.curr])
        f2 = os.path.join(self.workspace, self.files[self.curr+1])
        
        #print f1
        #print f2

        self.curr += 1
        tmp, file_extension = os.path.splitext(f1)
        if file_extension == '.grb':
            prev = self.gribget(f1, self.variable)
            curr = self.gribget(f2, self.variable)
        elif file_extension == '.nc':
            prev = self.ncget(f1, self.variable)
            curr = self.ncget(f2, self.variable)
        elif file_extension == '.bp':
            prev = self.bpget(f1, self.variable)
            curr = self.bpget(f2, self.variable)
        else:
            sys.exit('unknown file formate (%s %s)' % (tmp, file_extension))
        
        if self.curr == self.timesteps - 1:
            self.finished = True

        return (prev, curr)

    def get_progress(self):
        return float(self.curr)/(self.timesteps)

    def get_curr(self):
        return self.curr

    def list_variables(self):
        fname = os.path.join(self.workspace, self.files[0])
        tmp, extension = os.path.splitext(fname)
        if extension == '.grb':
            self.griblist(fname)
        elif extension == '.nc':
            self.nclist(fname)
        elif extension == '.bp':
            self.bplist(fname)
        else:
            sys.exit('unknown file formate')

    def get_files(self):
        return self.files;R
    def reset(self):
        self.curr = 0;
