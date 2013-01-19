#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
This module serves to convert the smor output to a suitable format

Version: 0.1


Copyright (c) 2012–2013, Steffen Hildebrandt and Felix Lehmann
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met: 

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer. 
2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution. 

This software is provided by the copyright holders and contributors "as is" and
any express or implied warranties, including, but not limited to, the implied
warranties of merchantability and fitness for a particular purpose are
disclaimed. In no event shall the copyright owner or contributors be liable for
any direct, indirect, incidental, special, exemplary, or consequential damages
(including, but not limited to, procurement of substitute goods or services;
loss of use, data, or profits; or business interruption) however caused and
on any theory of liability, whether in contract, strict liability, or tort
(including negligence or otherwise) arising in any way out of the use of this
software, even if advised of the possibility of such damage.
"""

import re
import codecs
from time import time
from Ligatures import *

"""
The symbol which is inserted for a morpheme boundary
"""
MORPHEME_SPLIT_SYMBOL = u'|'

"""
Definition of input and output files
"""
in_file = codecs.open('01-smor/smor', 'r', 'latin-1') # smor writes to latin-1

output_good = codecs.open('02-morphemes/morphemes.good', 'wb', 'utf-8')
output_different_possibilities = codecs.open(
    '02-morphemes/morphemes.differentPossibilities', 'wb', 'utf-8')
output_bad  = codecs.open('02-morphemes/morphemes.bad', 'wb', 'utf-8')
output_bad_oldorth = codecs.open(
    '02-morphemes/morphemes.bad.oldorth', 'wb', 'utf-8')

output = [output_good, output_different_possibilities, output_bad, output_bad_oldorth]


"""
A list of fixes for known smor bugs
"""
smor_fixes = [(u'beauftrag', u'beauf' + MORPHEME_SPLIT_SYMBOL + u'trag'),
              (u'Beauftrag', u'Beauf' + MORPHEME_SPLIT_SYMBOL + u'trag'),
              (u'beaufträg', u'beauf' + MORPHEME_SPLIT_SYMBOL + u'träg'),
              (u'Beaufträg', u'Beauf' + MORPHEME_SPLIT_SYMBOL + u'träg'),
              (u'auftakt', u'auf' + MORPHEME_SPLIT_SYMBOL + u'takt'),
              (u'Auftakt', u'Auf' + MORPHEME_SPLIT_SYMBOL + u'takt'),
              (u'auftrieb', u'auf' + MORPHEME_SPLIT_SYMBOL + u'trieb'),
              (u'Auftrieb', u'Auf' + MORPHEME_SPLIT_SYMBOL + u'trieb'),
              (u'auffällig', u'auf' + MORPHEME_SPLIT_SYMBOL + u'fällig'),
              (u'Auffällig', u'Auf' + MORPHEME_SPLIT_SYMBOL + u'fällig'),
              (u'aufhaltsam', u'auf' + MORPHEME_SPLIT_SYMBOL + u'haltsam'),
              (u'Aufhaltsam', u'Auf' + MORPHEME_SPLIT_SYMBOL + u'haltsam'),
              (u'ünfhundert', u'ünf' + MORPHEME_SPLIT_SYMBOL + u'hundert'),
              (u'ünftausend', u'ünf' + MORPHEME_SPLIT_SYMBOL + u'tausend'),
              #('echstausend', 'echs' + MORPHEME_SPLIT_SYMBOL + 'tausend'),# for st-ligature later
              #('chttausend', 'cht' + MORPHEME_SPLIT_SYMBOL + 'tausend'),# for tt-ligature later
              (u'lfhundert', u'lf' + MORPHEME_SPLIT_SYMBOL + u'hundert'),# elf + zwölf
              (u'lftausend', u'lf' + MORPHEME_SPLIT_SYMBOL + u'tausend'),# elf + zwölf
              #('underttausend', 'undert' + MORPHEME_SPLIT_SYMBOL + 'tausend'),
              (u'fünfte', u'fünf' + MORPHEME_SPLIT_SYMBOL + u'te'),# upper and lower b/c of "Zünfte"
              (u'Fünfte', u'Fünf' + MORPHEME_SPLIT_SYMBOL + u'te'),
              #('sechste', 'sechs' + MORPHEME_SPLIT_SYMBOL + 'te'),
              #('Sechste', 'Sechs' + MORPHEME_SPLIT_SYMBOL + 'te'),
              #('elfte', 'elf' + MORPHEME_SPLIT_SYMBOL + 'te'),# too risky, even though we can't think of an example
              (u'Elfte', u'Elf' + MORPHEME_SPLIT_SYMBOL + u'te'),
              (u'zwölfte', u'zwölf' + MORPHEME_SPLIT_SYMBOL + u'te'),
              (u'Zwölfte', u'Zwölf' + MORPHEME_SPLIT_SYMBOL + u'te'),
              (u'offline', u'off' + MORPHEME_SPLIT_SYMBOL + u'line'),
              (u'Offline', u'Off' + MORPHEME_SPLIT_SYMBOL + u'line')
              ]

"""
The current line (it was the easiest way make this variable a global,
since several methods may be interacting using it)
"""
line = ''


def nextline():
    """Loads the next word of the input into the the global variable line."""
    global line
    line = in_file.readline().rstrip() # remove newline character


def write(word, out_file):
    """Takes a word and writes it to the specified output file."""
    out_file.write(unicode(word + '\n'))


def cut_unnecessary(s):
    """Cuts / replaces unnecessary symbols out of the string s representing a line
    in the smor output
    The rules are translated from a perl script created by Helmut Schmid (University
    of Stuttgart).
    """
    s = re.sub('>:<>', '>', s)
    s = re.sub('<[^<>]*>:', '', s) #[^x]  --> everything except x
    # escaping backslash needs '\\\\' since it must be escaped
    # both in the regex and in the string itself!
    s = re.sub('[^\\\\]:', '', s)
    s = re.sub('<>', '', s)

    s = re.sub('([Gg]e)(.*?<Ge-Nom>)',
               lambda m: m.group(1) + '<IPREF>' + m.group(2),
               s)
    # original perl-command: """ s/([Gg]e)(.*?<PPast>)/$1<IPREF>$2/; """
    s = re.sub('([Gg]e)(.*?<PPast>)',
               lambda m: m.group(1) + '<IPREF>' + m.group(2),
               s)
    # original perl-command: """ s/(zu)(.*?<zu>)/$1<IPREF>$2/; """
    s = re.sub('(zu)(.*?<zu>)',
               lambda m: m.group(1) + '<IPREF>' + m.group(2),
               s)
    return s


def fix_smor(word):
    """Fixes errors in the morpheme boundaries of the given word if it is one of
    the known smor errors (cf. list smor_fixes)."""
    for fix in smor_fixes:
        word = re.sub(fix[0], fix[1], word)
    return word


def get_lig_morphemes(s):
    """Takes a line of smor output and replaces every from smor indicated morpheme
    boundary by:
     - MORPHEME_SPLIT_SYMBOL, if there is a ligature across the morpheme boundary
     - the empty string, otherwise
    """
    cut = re.split('<\+?\w+\-?\w*>|$', cut_unnecessary(s))
    morphemes = [morph for morph in cut if morph != '']
    result = morphemes[0]
    for n in range(0, len(morphemes)-1):
        lig_found = False # stop searching for ligs if a morpheme boundary was inserted
        for lig in LIGS:
            k = len(lig)
            # Problem here: Ligatures consisting of 3 letters (at which positions 
            # of morphemes[n] + [n+1] are we looking for the morphemes?)
            # Solution: look at morphemes[n][-(k-1):]+morphemes[n+1][:(k-1)]
            # this garuantees that the ligature goes across the boundary
            # and catches all relevant cases.
            if (not lig_found and
                    lig.glyph in morphemes[n][-(k-1):] + morphemes[n+1][:(k-1)]):
                result += MORPHEME_SPLIT_SYMBOL + morphemes[n+1]
                lig_found = True
        if not lig_found:
            result += morphemes[n+1]
    return fix_smor(result)


def process():
    """This method processes a word and writes every word to its dedicated
    output file:
     - If there is no result for a word, it is written to output_bad.
     - If a smor analysis contains an OLDORTH tag, the word is written to
       output_bad_oldorth (see documentation for further explanation on this).
     - If smor provides different analyses of the word, it is written to
       output_different possibilities.
     - Otherwise the word seems to be good and is written to output_good.
    """
    while not line.startswith('>'):
        nextline()
    word = line[2:]

    nextline()
    if line.startswith('no result'):
        write(word, output_bad)
        nextline()
        return

    morphemes = set([])
    while line and not line.startswith('>'):
        if '<OLDORTH>' in line:
            write(word + ' -> ' + cut_unnecessary(line), output_bad_oldorth)
        else:
            morphemes.add(get_lig_morphemes(line))
        nextline()

    if len(morphemes) == 1:
        write(word + ' -> ' + morphemes.pop(), output_good)
    elif len(morphemes) == 0:
        () # all analyses sorted out because of OLDORTH, do nothing
    else:
        write(word + ' -> ' + ' , '.join(morphemes),
              output_different_possibilities)
    return


def main():
    """Reads from the input file and processes the entries using the function process."""
    start = time()
    
    nextline()
    while line:
        process()
    
    in_file.close()
    for f in output:
        f.close()

    print 'Runtime: ' + str(time()-start) + 's'


main()
