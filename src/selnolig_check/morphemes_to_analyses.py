#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
This module serves to check which morphemes from the last step
are analyzed correct by the selnolig rules and which are not.

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
import operator
from time import time
from morphemes_to_analyses__read_selnolig_patterns import *

"""
Definition of input, output, and statistic files
"""
(nolig, keeplig) = read_rules('selnolig-german-patterns.sty')
morph_dict = codecs.open('02-morphemes/morphemes.good', 'r', 'utf-8')

out_good = codecs.open('03-analyses/analyses.good', 'wb', 'utf-8')
out_bad = codecs.open('03-analyses/analyses.bad', 'wb', 'utf-8')

out_stats_good = codecs.open(
                '03-analyses/stats.analyses.good', 'wb', 'utf-8')
out_stats_type2single = codecs.open(
                '03-analyses/stats.analyses.type2single', 'wb', 'utf-8')
out_stats_type2multiple = codecs.open(
                '03-analyses/stats.analyses.type2multiple', 'wb', 'utf-8')


"""
The statistic files are a Dictionary from rules to int
(number of good/bad words per rule)
"""
stats_good = dict() # rule -> int
stats_type2single = dict()
stats_type2multiple = dict()


"""
Initialize the statistics (add all the rules with 'rule -> 0')
"""
for stat in [stats_good, stats_type2single, stats_type2multiple]:
    for rule in nolig:
        stat['|'.join(nolig[rule])] = 0
    for rule in keeplig:
        stat[rule] = 0


"""
List of tuples with Dictionary and output file, makes it easier to process later
"""
stats = [(stats_good, out_stats_good),
         (stats_type2single, out_stats_type2single),
         (stats_type2multiple, out_stats_type2multiple)]


def exists(f, xs):
    """PROBABLY NOT NEEDED ANYMORE !!
    The exists-function for lists, well-known from other functional languages 
    exists takes a predicate (function) and a list
    and returns true, if the predicate fits on one or more elements of the list.
    """
    def or_function(a,b): return a or b
    return reduce(or_function, map(f, xs))


def selnolig(word):
    """Takes a word and simulates selnolig on it, i.e. applies all rules to it."""
    applied_rules = []
    for rule in nolig:
        if rule in word:
            applied = '|'.join(nolig[rule])
            applied_rules.append(applied)
            keep = False
            for k in keepligs:
                if k in word and rule in k:
                    applied_rules.append(k)
                    keep = True
            if not keep: 
                word = word.replace(rule, applied)
    return (word, applied_rules)


def main():
    """Reads the lines from morphdict (morphemes.good), verifies whether selnolig
    yields the same results on this word and writes the word to the dedicated
    file (output_good or output_bad).
    At the same time it maintains some statistics about the rules and errors.
    """
    global stats, stats_good, stats_type2single, stats_type2multiple
    
    start = time()
    
    for line in morph_dict:
        line = line.rstrip()
        morpheme_split = re.split(' -> ', line)
        (word, morphemes) = (morpheme_split[0], morpheme_split[1])
        (selnolig_morphemes, applied_rules) = selnolig(word)
        if morphemes != selnolig_morphemes:
            # write statistics
            if len(applied_rules) == 1:
                stats_type2single[applied_rules[0]] += 1
            else:
                for rule in applied_rules: # will catch len(applied_rules)==0 (and just do nothing)
                    stats_type2multiple[rule] += 1
            # write output
            out_bad.write(word + ' --- ' + morphemes +
                                 ' --- ' + selnolig_morphemes +
                                 ' --- ' + ','.join(applied_rules) + '\n')
        else:
            # write statistics
            for rule in applied_rules: stats_good[rule] += 1
            # write output
            out_good.write(word + ' --- ' + ','.join(applied_rules) + '\n')

    morph_dict.close()
    out_good.close()
    out_bad.close()

    # sort and print statistics
    for stat in stats:
        rules = sorted(stat[0].iteritems(), key=operator.itemgetter(1), reverse=True)
        for rule in rules:
            stat[1].write(rule[0] + ' : ' + unicode(rule[1]) + '\n')
        stat[1].close()
    
    print 'Runtime: ' + str(time()-start) + 's' 


main()
