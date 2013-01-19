# -*- coding: utf-8 -*-
"""
This module serves to merge the ligs files to the ligdict.

Version: 0.1
"""

import codecs
from time import time

"""
Definition of all input files that should be used
"""
base_folder = 'ligs/'

infiles = [
    base_folder + 'ligs.good.normal',
    base_folder + 'ligs.good.Innen',
    base_folder + 'ligs.good.laws',
    base_folder + 'ligs.good.hyphen.startsWithHyphen',
    base_folder + 'ligs.good.hyphen.beginnings',
    base_folder + 'ligs.good.hyphen.end']

"""
Reads the words from all input files to a set (for removing duplicates) and
prints them to the given output file.

The output will be encoded in latin-1, since SMOR (which is the next step)
cannot handle utf-8.
"""
def main(outfile):
    start = time()
    
    output = set([])
    for infile in infiles:
        in_file = codecs.open(infile, 'r', 'utf-8')
        for line in in_file:
            output.add(line)
        in_file.close()

    out_file = codecs.open(outfile, 'wb', 'latin-1')
    for elem in output:
        try:
            out_file.write(elem)
        except Exception as e:
            print ('WARNING: Couldn\'t write "' + elem.rstrip() +
                   '" to file "' + out_file.name + '"')

    print 'Runtime: ' + str(time()-start) + 's'

main('ligdict')
