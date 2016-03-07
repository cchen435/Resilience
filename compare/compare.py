#!/usr/bin/env python

import os
import sys


# import self defined io routines
from fio import ncget, bpget2



def main(argv):
    if len(argv) < 2:
        sys.exit('Usage: %s work-directory' % argv[0])
    if not os.path.exists(argv[1]):
        sys.exit('ERROR: work-directory %s was not found!' % argv[1])

    CWD = os.getcwd()
    workspace = os.path.join(CWD, argv[1])
    print 'workspace %s ' % workspace

    dirs = [ x for x in os.listdir(workspace) if os.path.isdir(os.path.join(workspace, x))]
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

    files = [ f for f in os.listdir(normal_path) if os.path.isfile(os.path.join(normal_path, f))]
    if len(files) == 0:
        sys.exit('No data found for correct data');
    files.sort()

    file_ext = files[0].split('.')[-1]

    # comparing data in other dirs with data normal dir
    prefix = '  '
    for i in dirs:
        print '%s dir %s:'%(prefix, i)
        path = os.path.join(workspace, i)

        # get the file list and file extention in faulty directory
        tmp = [f for f in os.listdir(path)]
        tmp.sort()
        tmp_ext = tmp[0].split('.')[-1]

        # check wthether the data in faulty directory can match the data in normal directory
        if tmp != files or tmp_ext != file_ext:
            print ("files not matched in \"%s\"" % path)
            print 'tmp:', tmp
            print 'files:', files
            print 'tmp_ext:', tmp_ext
            print 'file_ext:', file_ext
            break

        output_buf = dict();
        rfile = os.path.join(workspace, i+'_res.txt')

        # compareing file by file
        timestep = 0
        for f in files:
            print '%s file %s:'%(prefix*2, f)
            faulty = 0;
            normal_file = os.path.join(normal_path, f);
            faulty_file = os.path.join(path, f);
            if file_ext == 'bp':
                ndata = bpget2(normal_file)
                fdata = bpget2(faulty_file)
            elif file_ext == 'nc':
                ndata = ncget(normal_file)
                fdata = ncget(faulty_file)

            # check whther two files has the same variables
            nvars = ndata.keys()
            fvars = fdata.keys()
            nvars.sort()
            fvars.sort()
            if nvars != fvars:
                sys.exit('variabes in correct data and faulty data not matched')

            # compare the data variable by variable
            for var in nvars:
                print '%s var %s:'%(prefix*3, var)
                var_faulty = 0
                ndata_array = ndata[var]
                fdata_array = fdata[var]
                if ndata_array.size != fdata_array.size:
                    print 'faulty because of different array dimension (%d, %d) for \
                            file %s' % (ndata_array.size, fdata_array.size, f)

                max_diff = 0.0
                min_diff = 100000000.0
                mean_diff = 0.0
                total = 0
                for i in range(ndata_array.size):
                    if ndata_array[i] != fdata_array[i]:
                        var_faulty = 1
                        total = total + 1
                        tmp = abs(1 - fdata_array[i]/(ndata_array[i] + 1))
                        if tmp > max_diff:
                            max_diff = tmp;
                        if tmp < min_diff:
                            min_diff = tmp
                        mean_diff = mean_diff + tmp
                mean_diff = mean_diff/(total+1)

                '''
                print '%s total %10d:'%(prefix*4, total)
                print '%s min  %4.6f:'%(prefix*4, min_diff)
                print '%s max  %4.6f:'%(prefix*4, max_diff)
                print '%s mean %4.6f:'%(prefix*4, mean_diff)
                '''

                res_tmp = dict()
                res_tmp['step'] = timestep
                res_tmp['total'] = total
                res_tmp['min'] = min_diff
                res_tmp['max'] = max_diff
                res_tmp['mean'] = mean_diff
                if output_buf.has_key(var):
                    output_buf[var].append(res_tmp.copy())
                else:
                    output_buf[var] = [res_tmp.copy()]
            timestep = timestep + 1
        fh = open(rfile, 'w')
        fmt = "%10s %10s %20s %20s %20s %20s\n"
        fh.write(fmt % (' ', 'timestep', 'total', 'min', 'max', 'mean'))
        for var in output_buf.keys():
            for f in output_buf[var]:
                fh.write(fmt % (var, str(f['step']), str(f['total']), str(f['min']), str(f['max']), str(f['mean'])))
        print '\n'
        fh.close()

if __name__ == '__main__':
    main(sys.argv)
