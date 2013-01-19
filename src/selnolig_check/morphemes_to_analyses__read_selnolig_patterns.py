#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
This module provides the method read_rules which reads and returns
the nolig patterns.

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

import codecs
from Ligatures import *

"""
The list of rules which will be filled and returned by read_rules
"""
noligs = {}  # pattern -> list of parts
keepligs = []


def read_rules(nolig_file):
    """The main function
    Takes a nolig file (e.g. 'selnolig-german-patterns.sty') and returns
    a tuple containing:
     - a dictionary of a pattern to a list of parts
     - a list of keeplig patterns
    It also checks the rules for consistency (see check_rules)
    """
    global noligs, keepligs
    in_file = codecs.open(nolig_file, 'r', 'utf-8')
    
    for line in in_file:
        process_line(line)
    in_file.close()
    
    check_rules()
    print 'Number of nolig patterns:', len(noligs)
    print 'Number of keeplig patterns:', len(keepligs)
    return (noligs, keepligs)


def process_line(line):
    """Processes a line, i.e. ignores comments (%) and looks for \nolig commands."""
    n = 0
    while n < len(line):
        if line[n] == '%': return
        # nolig?
        if (line[n] == '\\' and
                len(line) > n + 6 and
                line[n:n+7] == '\\nolig{'):
            n += 7
            key = ''
            while line[n] != '}':
                key += line[n]
                n += 1
            while line[n] != '{': n += 1
            n += 1
            value = ''
            while line[n] != '}':
                value += line[n]
                n += 1
            process_nolig_pattern(key, value)
        # keeplig?
        if (line[n] == '\\' and
                len(line) > n + 8 and
                line[n:n+9] == '\\keeplig{'):
            n += 9
            pattern = ''
            while line[n] != '}':
                pattern += line[n]
                n += 1
            process_keeplig_pattern(pattern)
        
        n += 1
    return


def process_nolig_pattern(k, v):
    """Takes a pattern (key value pair), processes it and inserts it into the noligs
    dictionary.
    Since the syntax, especially regarding the regex part, is not yet completely specified,
    we're making some assumptions:
     - There's at most one regex component (i.e. at most one pair of brackets)
     - If there is a regex component:
         * the second argument contains exactly one bar
         * the regex component is in the second morpheme and occurs only in the first argument
    Consequence: We basically just 
    """
    global noligs
    keys = read_regex(k)
    bar_pos = v.find(u'|')
    if bar_pos < 0:
        print ('!!!!!  NOLIG RULE WITHOUT A BAR  !!!!!   ----->  ' + k)
        return #raise Exception('Invalid nolig pattern: ' + k + ' , ' + v)
    if keys[0][:bar_pos] != v[:bar_pos]:
        raise Exception('Non-matching pattern: ' + k + ' , ' + v)
    
    if v.find(u'|', bar_pos+1) > -1: # more than one bar (i.e. more than two morphemes)
        if len(keys) > 1:
            raise Exception('Can\'t handle a regexed pattern with more ' +
                            'than two morphemes: ' + k + ' , ' + v)
        else:
            value = []    
            current = ''
            n = 0
            while n < len(v):
                if v[n] != '|':
                    current += v[n]
                else:
                    value.append(current)
                    current = ''
                n += 1      
                
            value.append(current)
            noligs.update({k:value})
    else: # only one bar 
        for k in keys:
            noligs.update({ k : [k[:bar_pos], 
                                 k[bar_pos:]]  })
    return


def process_keeplig_pattern(k):
    """Takes a pattern (single string), and inserts it into keeplig.
    Since the syntax, especially regarding the regex part, is not yet completely specified,
    we're assuming that there is only one regex component (i.e. pair of brackets).
    """
    global keepligs
    keepligs += read_regex(k)
    return


def read_regex(pattern):
    """Returns a list of words that are created by the pattern.
    The number of bracket pairs is restricted to at most 1.
    """
    words = ['']   # current list of words
    basisWord = '' # for when we're inBrackets
    inBrackets = False
    bracketsSeen = False 
    
    for char in pattern:
        if char == '[':
            if bracketsSeen: 
                raise Exception('Can\'t handle more than one pair of brackets in one pattern: ' + k)
            else:
                inBrackets = bracketsSeen = True
                basisWord = words[0]
                words = []
        elif char == ']':
            if not inBrackets:
                raise Exception('Closing bracket without opening one: ' + pattern)
            else:
                inBrackets = False
        elif not inBrackets:
            words = map(lambda w: w+char, words)
        else:
            words.append(basisWord + char)
    return words


def exists(f, xs):
    """The exists-function for lists, well-known from other functional languages 
    exists takes a predicate (function) and a list
    and returns true, if the predicate fits on one or more elements of the list.
    """
    def or_function(a,b): return a or b
    return reduce(or_function, map(f, xs))


def findInBetween(p1, p2, ligs):
    """Takes a set of rules (ligs) and two keys p1 and p2
    and looks for a rule in ligs 'in between' p1 and p2,
    i.e. a rule with key k, s.t. (p1 < k < p2) or (p2 < k < p1)
    ('<' meaning 'is contained in')
    """
    if p1 in p2:
        return exists(lambda k: p1 in k and k in p2, ligs)
    elif p2 in p1:
        return exists(lambda k: p2 in k and k in p1, ligs)
    else:
        raise Exception('Invalid arguments!')


def check_rules():
    """Checks all the rules in noligs for consistency, i.e.
     - checks for typos (key - value don't match)
     - checks for conflicting rules (patterns containing each other)
    """
    global noligs
    def conflicting_rules(a, b):
        print ('!!!!! CONFLICTING RULES DETECTED !!!!!   ----->  ' +
               a + ' contains ' + b)
    for rule in noligs:
        nol = noligs[rule]
        if rule != ''.join(nol):
            print ('!!!!!   INVALID   RULE  DETECTED !!!!!   ----->  ' +
                   rule + ' <--> ' + '[' + ', '.join(nol) + ']')
        for n in range(0,len(nol)-1):
            if not (nol[n][-1] + nol[n+1][0] in [lig.glyph for lig in LIGS]):
                print nol[n][-1] + nol[n+1][0]
                print ('!!!!!   INVALID   RULE  DETECTED !!!!!   ----->  ' +
                   rule + ' <--> ' + '[' + ', '.join(nol) + ']')
        for rule1 in noligs:
            if ((rule1 in rule) and (rule1 != rule) and
                not findInBetween(rule, rule1, keepligs)):
                conflicting_rules(rule, rule1)
    for rule in keepligs:
        for rule1 in keepligs:
            if ((rule1 in rule) and (rule1 != rule) and
                not findInBetween(rule, rule1, noligs)):
                conflicting_rules(rule, rule1)
        


#read_rules('selnolig-german-patterns.sty')
#read_rules('selnolig-english-patterns.sty') 
