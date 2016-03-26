#!/usr/bin/env python

import os
import sys
import pdb

# import self defined io routines

import fio


def main(argv):
    if len(argv) < 2:
        sys.exit('Usage: %s work-directory [variable-name]' % argv[0])
    if not os.path.exists(argv[1]):
        sys.exit('ERROR: work-directory %s was not found!' % argv[1])

    CWD = os.getcwd()
    workspace = os.path.join(CWD, argv[1])
    variable = 'all'
    if len(argv) > 2: 
        variable = argv[2]
    
    print 'workspace: %s, variable: %s' % (workspace, variable)

    # get subdirectory where store the acture data
    dirs = [ x for x in os.listdir(workspace) \
            if os.path.isdir(os.path.join(workspace, x))]
    if len(dirs) == 0:
        sys.exit('the working directory is empty');

    dirs.sort()
    print 'evaluate the order: ', dirs

    if dirs[0] != '0':
        sys.exit('directory for correct/normal data not found')
   
    normal_path = os.path.join(workspace, dirs[0])
    
    dirs.remove('0')
    if len(dirs) == 0:
        sys.exit('no faulty data found in working directory');

    
    # comparing data in other dirs with data in normal dir
    for i in dirs:
        print '%s dir %s:'%(workspace, i)
        path = os.path.join(workspace, i) 
        
        normal_datasets = fio.DataBase(normal_path);
        faulty_datasets = fio.DataBase(path)    
        

        # check whether the two data set has the same timesteps
        normal_files = normal_datasets.get_files()
        faulty_files = faulty_datasets.get_files()

        if normal_files != faulty_files:
            print 'data from the two dir not match'
            break

        # check whehter the two data set has the same variables
        normal_variables = normal_datasets.get_variables()
        faulty_variables = faulty_datasets.get_variables()

        if normal_variables != faulty_variables: 
            print 'the variable in data set (%s) not match' \
                    'with normal execution' % i
            break

        if variable != 'all' and variable not in normal_variables:
            sys.exit('error, variable %s not found' % variable)

        if variable != 'all':
            variables = [variable]
        else:
            variables = normal_variables
            
        output_buf = dict();
        rfile = os.path.join(workspace, i+'_res.txt')

        # comparing the dataset by comparing each variable
        for var in variables:
            output_buf[var] = list()

            normal_datasets.reset()
            faulty_datasets.reset()
            # compareing file by file

            print "looking at variable %s" % var

            while not normal_datasets.is_done():

                faulty = 0;
                [ndata]= normal_datasets.read(var)
                [fdata]= faulty_datasets.read(var)
                print 'Progress. Finished: %.02f%%' % \
                        (normal_datasets.progress() * 100)
                
                if ndata.size != fdata.size:
                    print 'faulty because of different array dimension'+\
                            ' (%d, %d) for file %s' % (ndata_array.size, \
                            fdata_array.size, f) 
            
                max_diff = 0.0
                min_diff = 100000000.0
                mean_diff = 0.0
                total = 0

                for i in range(ndata.size):
                    if ndata[i] != fdata[i]:
                        var_faulty = 1
                        total = total + 1
                        tmp = abs(1 - fdata[i]/(abs(ndata[i]) + 1))
                        if tmp > max_diff:
                            max_diff = tmp;
                        if tmp < min_diff:
                            min_diff = tmp
                        mean_diff = mean_diff + tmp
            
                mean_diff = mean_diff/ndata.size
                res_tmp = dict()
                timestep = normal_datasets.timestep();
                res_tmp['step'] = timestep
                res_tmp['total'] = total
                res_tmp['min'] = min_diff
                res_tmp['max'] = max_diff
                res_tmp['mean'] = mean_diff
                output_buf[var].append(res_tmp.copy())

            print 'Progress. Finished: %.02f%%\n\n' % \
                        (normal_datasets.progress() * 100)


        
        fh = open(rfile, 'w')
        fmt = "%10s %10s %20s %20s %20s %20s\n"
        fh.write(fmt % ('variable', 'timestep', 'total_diff', 'min', \
                'max', 'mean'))
        for var in output_buf:
            for item in output_buf[var]:
                step  = item['step']
                total = item['total']
                min   = item['min']
                max   = item['max']
                mean  = item['mean']
                fh.write(fmt % (var, str(step), str(total), str(min), str(max), str(mean)))
        fh.close()

if __name__ == '__main__':
    main(sys.argv)
