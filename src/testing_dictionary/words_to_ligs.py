# -*- coding: utf-8 -*-
"""
This module serves to split the words to separate files according to their
expected usefulness.

Version: 0.1
"""

import re, codecs
import unicodedata
from Ligatures import *
from time import time


"""--------------------------------------------------------------------------
Definition of the output files
--------------------------------------------------------------------------"""
base_folder = 'ligs/'

good_normal            = codecs.open(base_folder +
                    'ligs.good.normal', 'wb', 'utf-8')
good_startswith_hyphen = codecs.open(base_folder +
                    'ligs.good.hyphen.startsWithHyphen', 'wb', 'utf-8')
good_hyphen_beginnings = codecs.open(base_folder +
                    'ligs.good.hyphen.beginnings', 'wb', 'utf-8')
good_hyphen_end        = codecs.open(base_folder +
                    'ligs.good.hyphen.end', 'wb', 'utf-8')
good_innen             = codecs.open(base_folder +
                    'ligs.good.Innen', 'wb', 'utf-8')
good_laws              = codecs.open(base_folder +
                    'ligs.good.laws', 'wb', 'utf-8')

review_lig_across_punctuation  = codecs.open(base_folder +
                    'ligs.review.ligAcrossPunctuation', 'wb', 'utf-8')
review_punctuation             = codecs.open(base_folder +
                    'ligs.review.punctuation', 'wb', 'utf-8')

interesting_allcaps            = codecs.open(base_folder +
                    'ligs.interesting.allcaps', 'wb', 'utf-8')
interesting_single_letter_abbr = codecs.open(base_folder +
                    'ligs.interesting.singleLetterAbbr', 'wb', 'utf-8')


bad_camel                   = codecs.open(base_folder +
                    'ligs.bad.camel', 'wb', 'utf-8')

"""
List of all output files
"""
out_files = [good_normal, good_startswith_hyphen,
             good_hyphen_beginnings, good_hyphen_end,
             good_innen, good_laws,
             review_lig_across_punctuation, review_punctuation,
             interesting_allcaps, interesting_single_letter_abbr,
             bad_camel]

"""
Takes a word and writes it to the specified output file
"""
def write(word, out_file):
    out_file.write(word + '\n')


"""--------------------------------------------------------------------------
Definition of some helping functions
--------------------------------------------------------------------------"""

"""
Returns a flattened version of a list.
"""
def flatten(lis):
    return [item for sublist in lis for item in sublist]

"""
All (combinations of) symbols which are considered as hyphens.
These are different versions of hyphens, each to the left xor right concatenated
with one of the symbols {",',`,´,<<,>>}
"""
hyphen_equivalent = ([u'\u00AD'] + [u'\u002D'] + [u'\u2010'] + [u'\u2212'] +
                     [u'\u2011'] + 
                    flatten([[u'\u00AD'+q, q+u'\u00AD', # hyphen-minus
                              u'\u002D'+q, q+u'\u002D', # minus sign
                              u'\u2010'+q, q+u'\u2010', # hyphen
                              u'\u2011'+q, q+u'\u2011', # non-breaking hyphen
                              u'\u2012'+q, q+u'\u2012'] # figure dash
                                            for q in [u'\u0022', # "
                                                      u'\u0027', # '
                                                      u'\u0060', # `
                                                      u'\u00AB', # «
                                                      u'\u00BB', # »
                                                      u'\u00B4', # ´
                                                      u'\u2018', # LEFT SINGLE QUOTATION MARK
                                                      u'\u2019', # RIGHT SINGLE QUOTATION MARK
                                                      u'\u201A', # SINGLE LOW-9 QUOTATION MARK
                                                      u'\u2039', # SINGLE LEFT-POINTING ANGLE QUOTATION MARK
                                                      u'\u203A', # SINGLE RIGHT-POINTING ANGLE QUOTATION MARK
                                                      u'\u201C', # LEFT DOUBLE QUOTATION MARK
                                                      u'\u201D', # RIGHT DOUBLE QUOTATION MARK
                                                      u'\u201E']])) # DOUBLE LOW-9 QUOTATION MARK
                                                      

"""
A regular expression built up of hyphen equivalent.
"""
hyphen_regex = re.compile('|'.join(hyphen_equivalent))

"""
Takes a word and splits it at hyphens (using hyphen-regex)
and returns a list of tokens.
"""
def split_at_hyphens(word):
    return re.split(hyphen_regex, word)

"""
Test whether a unicode character is letter, lowercase letter, uppercase leter
"""
def uni_alpha(char): return unicodedata.category(char)[0] == 'L'
def uni_lower(char): return unicodedata.category(char) == 'Ll'
def uni_upper(char): return unicodedata.category(char) == 'Lu'

"""
Takes a word and returns it with all puctuation removed
"""
def remove_punctuation(word):
    return ''.join([char for char in word if uni_alpha(char)])

"""
Returns true if the given word contains a ligature
"""
def contains_any_lig(word):
    for lig in LIGS:
        if lig.glyph in word: return True
    return False

"""
Returns true if the given word contains a ligature,
ignoring the case of word and ligatures
"""
def contains_any_lig_non_case_sensitive(word):
    for lig in LIGS:
        if lig.glyph.lower() in word.lower(): return True
    return False

"""
Returns true if the given word contains only letters
"""
def only_alpha(word):
    for char in word:
        if not uni_alpha(char): return False
    return True

"""
Returns true if the given word contains only lowercase letters
"""
def all_lower(word):
    for char in word:
        if uni_upper(char): return False
    return True

"""
Returns true if the given word contains only uppercase letters
"""
def all_upper(word):
    for char in word:
        if uni_lower(char): return False
    return True

"""
Returns true if the given word is titelcase
"""
def title_case(word):
    if len(word) < 1 or uni_lower(word[0]): return False
    for char in word[1:]:
        if uni_upper(char): return False
    return True

"""
Returns true if the given word is camelcase
"""
def camel_case(word):
    if len(word) > 0 and uni_lower(word[0]):
        for i in range(1, len(word)):
            if uni_upper(word[i]): return True
        return False
    else:
        return not (len(word) == 1 or all_upper(word[1:]) or all_lower(word[1:]))

"""
Returns true if the given word ends with 'In' or contains 'Innen'
and the word without the letter combintion 'In' is titlecase
"""
def endswith_innen(word):
    pattern = re.compile('\\w*(Innen\\w*|In)$', re.UNICODE)
    return re.match(pattern, word) != None and title_case(re.sub('In','',word))

"""
Returns true if the given word seems to be a law,
i.e. is longer than two characters, starts with uppercase and ends with 'G' or 'V'
"""
def is_law(word):
    return (len(word) > 2 and uni_upper(word[0]) and
              (word.endswith('G') or word.endswith('V')))

"""
Returns true if the given word contains no other punctuation than hyphens
"""
def only_hyphens(word):
    pattern = re.compile(u'^(\\w|' + '|'.join(hyphen_equivalent) + u')*$',
                         re.UNICODE)
    return re.match(pattern, word) != None   # len(remove_punctuation(word)) == len(''.join(split_at_hyphens(word)))

"""
Returns true if the given word is a single letter abbreviation
"""
def single_letter_abbr(word):
    pattern = re.compile('((\\w\\.)+\w?$)', re.UNICODE) # -> 'X.y.Z' | 'X.y.Z.'
    return re.match(pattern, word) != None 



"""--------------------------------------------------------------------------
Main functions
--------------------------------------------------------------------------"""

"""
Takes a word for which [[only_hyphens(word) == True]] and processes the word
finally writing it or parts of it to some output file.
 - if the word contains only one hyphen and this hyphen is at the beginning,
     the word is written into good_startswith_hyphen
 - otherwise the last token including hyphen is written to good_hyphen_end,
     and all previous tokens excluding all hyphens are written to
     good_hyphen_beginnings

For more detailed information about these decisions please take a look
at our documentation.
"""
def hyphen_filter(word):
    if (word[0] in hyphen_equivalent and re.match(hyphen_regex, word[1:]) == None
        and contains_any_lig(word[1:])):
        write('-' + word[1:], good_startswith_hyphen)
        return

    tokens = split_at_hyphens(word)
    if tokens[0] == '': start = 1 # the word started with a hyphen
    else: start = 0
    for t in tokens[start:-1]:
        if contains_any_lig(t):
            write(t, good_hyphen_beginnings)
    if contains_any_lig(tokens[-1]):
        write('-' + tokens[-1], good_hyphen_end)
        

"""
Takes a file (output file 'words' from the previous stop) sorts those words
into the output files defined above.
For more detailed information please take a look at our documentation.
"""
def main(infile):    
    start = time()
    print ('Filtering words with ligatures: ' +
               ','.join([str(lig) for lig in LIGS]))

    in_file = codecs.open(infile, 'r', 'utf-8')
    # out_files have already been opened
    
    for line in in_file:
        word = line.rstrip()
        if single_letter_abbr(word): # just because it is interesting
            write(word, interesting_single_letter_abbr)
        if all_upper(word):
            write(word, interesting_allcaps)
        if contains_any_lig(word):
            if only_alpha(word):
                if camel_case(word):
                    if endswith_innen(word):
                        write(word, good_innen)
                    elif is_law(word):
                        write(word, good_laws)
                    else:
                        write(word, bad_camel)
                else:
                    write(word, good_normal)
            else:
                if only_hyphens(word):
                    hyphen_filter(word)
                else:
                    write(word, review_punctuation)
        elif contains_any_lig(remove_punctuation(word)):
            write(word, review_lig_across_punctuation)

    for f in out_files:
        f.close()
        
    print 'Runtime: ' + str(time()-start) + 's'


main('words/words.raw')
