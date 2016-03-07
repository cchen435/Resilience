#!/usr/bin/env python

import os
import sys


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
    
    print 'workspace: %s, variable: %s' % (workspace, varialbe)

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
        print '%s dir %s:'%(prefix, i)
        path = os.path.join(workspace, i) 
        
        normal_datesets = fio.DataBase(normal_path, variable);
        faulty_datasets = fio.DataBase(path, variable)    
        
        normal_files = normal_datasets.get_files()
        faulty_files = faulty_datasets.get_files()

        if normal_files != faulty_files:
            print 'data from the two dir not match'
            break;
        
        output_buf = list();
        rfile = os.path.join(workspace, i+'_res.txt')

        # compareing file by file
        while not normal_datasets.done():
            faulty = 0;
            ndata= normal_datasets.next()
            fdata= faulty_datasets.next()
            if ndata.size != fdata.size:
                print 'faulty because of different array dimension (%d, %d)' +\
                      'for file %s' % (ndata_array.size, fdata_array.size, f)

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
            
            mean_diff = mean_diff/(total+1)
            res_tmp = dict()
            timestep = normal_datasets.get_curr();
            res_tmp['step'] = timestep
            res_tmp['total'] = total
            res_tmp['min'] = min_diff
            res_tmp['max'] = max_diff
            res_tmp['mean'] = mean_diff
            output_buf.append(res_tmp.copy())
        
        fh = open(rfile, 'w')
        fmt = "%10s %10s %20s %20s %20s %20s\n"
        fh.write(fmt % (' ', 'timestep', 'total', 'min', 'max', 'mean'))
        for f in output_buf:
            fh.write(fmt % \
                     (var, str(f['step']), str(f['total']),        \
                      str(f['min']), str(f['max']), str(f['mean']) \
                     )     \
                    )
            print '\n'
        fh.close()

if __name__ == '__main__':
    main(sys.argv)
