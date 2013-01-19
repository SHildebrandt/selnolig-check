#!/usr/bin/python. 
# -*- coding: utf-8 -*-
"""
This module serves to extract all words from a given corpus (currently sDeWaC).

Version: 0.1
"""

import re
import codecs
import unicodedata
from time import time

from Ligatures import *

def contains_letters(token):
    """Returns true if a given (unicode) token contains at least one letter."""
    for char in token:
        if unicodedata.category(char)[0] == 'L': return True
    return False

def main(infile, outfile):
    """Takes an input file, reads it, filters all words we want to have
    and writes them to the output file.
    In particular all tags are filtered out and all words are considered which
    contain at least one letter.
    """
    start = time()
    print 'Extracting words from', infile, 'to', outfile
    in_file = codecs.open(infile, 'r', 'utf-8')
    out_file = codecs.open(outfile, 'wb', 'utf-8')
    
    for line in in_file:
        line = re.sub('<[^>]*>', '', line).split()
        for token in line:
            if contains_letters(token):
                out_file.write(token + '\n')
    
    in_file.close()
    out_file.close()
    print 'Runtime: ' + str(time()-start) + 's'

main('corpus.raw', 'words/words.raw')