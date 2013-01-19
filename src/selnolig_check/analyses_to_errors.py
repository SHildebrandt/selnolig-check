#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
This module looks at analyses.bad and puts the lines in different categories,
depending on the kind of selnolig error they're hinting at.

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
from time import time
start = time()

"""-------------------------------------------------
Basic definitions
-------------------------------------------------"""

"""
input file
"""
infilename = '03-analyses/analyses.bad'
infile = codecs.open(infilename, 'r', 'utf-8')
len_infile =  sum(1 for line in codecs.open(infilename, 'r', 'utf-8'))


"""
Glyph groups
TODO: Replace these by the Ligature classes
"""
LIGS = [u'ff', u'fi', u'fl', u'ft', u'fb', u'fh', u'fk', u'fj', u'th'] # u'ffi', u'ffl', u'fff'
    # omitting the triple ligatures because they're covered by the doubles
LC_UMLS = [u'ä', u'ö', u'ü', u'ß'] # "lower case umlauts"
REPL_LC_UMLS = [u'ae', u'oe', u'ue', u'ss'] # "replacement lower case umlauts"

""" These are used for sorting to a human-readable format.
    (ä -> ae) is more helpful than (ä -> a), which is used in dictionaries),
    because for really similar words, it'll separate umlaut and vowel,
    which is better for reviewing the lists.
    It does create a certain error in the order though, e.g. fluegge*, fluffig, flügge,
    but that seems to be irrelevant."""
len_LIGS = len(LIGS)

"""
Constants
"""
SEPARATOR = u' --- ' # used in many places to separate the "parts" of a line
BAR = u'|' # indicates a morpheme boundary in the input
    # The following three are used in the human-readable final output:
CURRLIG = u'|' # indicates the morpheme boundary "we're looking at"
OTHERLIG = u'\'' # indicates morpheme boundaries "we're not looking at right now"
BORINGLIG = u'.' # indicates morpheme boundaries on which SMOR and selnolig agree
len_SEPARATOR = len(SEPARATOR)
len_CURRLIG = len(CURRLIG)

"""
Some text that will appear at the beginning of each output file:
"""
starttext = u'''--------------------------------------------------------------------------------
Pattern:
word --- SMOR --- selnolig --- selnolig-patterns applied (if any)

Key:
''' + CURRLIG + u''' = current morpheme boundary that caused the bug we\'re looking at
''' + OTHERLIG + u''' = another morpheme boundary that\'s buggy (listed on its own somewhere else)
''' + BORINGLIG + u''' = morpheme boundary that SMOR and selnolig agreed on = boring!
--------------------------------------------------------------------------------\n\n'''

"""
In an earlier version, we used digits instead of Greek letters, but when we
started allowing numbers in out input words (e.g. "2köpfig"), we had to
switch to another system. This is just a reminder for what the categories
used to be.
0 = α (no ligature detected)
1 = β (ligature detected)
2 = γ (ligature detected + SMOR & selnolig agree)
3 = δ
4 = ε
5 = ζ
6 = η
7 = θ
8 = ι
9 = κ

0123456789
αβγδεζηθικ
"""

"""
Bug categories
"""
bug_cats = {
    u'δ': (u'innen', 1),
    u'ε': (u'ig', 1),
    u'ζ': (u'isch', 1),
    u'η': (u't-Endung', 1),
    u'θ': (u'pflicht', 2),
    u'ι': (u'hälfte', 2)
    }

"""
Known bugs in selnolig

These bugs are detected based on strings that are only on the right of a morpheme
boundary, e.g.: Genoss|innenschaft ('|innenschaft')
"""
type_one_bugs_right = [
    # "innen":
    (u'δ', [u'in', u'innen', u'innenschaft', u'innenschaften']),
    # "ig":
    (u'ε', [u'ig', u'iger', u'igen', u'igem', u'iges', u'ige', # Positive
           u'igerer', u'igeren', u'igerem', u'igeres', u'igere', # Comparative
           u'igst', u'igster', u'igsten', u'igstem', u'igste', # Superlative
           u'igkeit', u'igkeiten' # Property Nouns
           ]),
    # "isch":
    (u'ζ', [u'isch', u'ischer', u'ischen', u'ischem', u'isches', u'ische', # Positive
              u'ischerer', u'ischeren', u'ischerem', u'ischeres', u'ischere', # Comparative
              u'ischst', u'ischster', u'ischsten', u'ischstem', u'ischstes', u'ischste' # Superlative
              ])
    ]

"""
These bugs are detected based on strings that are on both sides of a morpheme
boundary, e.g.: du hoff|test ('f|test')
"""
type_one_bugs_both = [ # = string occurs only right of morpheme boundary
    # "t-Endung":
    (u'η',
        (u'f', [u't', u'te', u'test', u'ten', u'tet', # Present / Preterite
               u't', u'ter', u'ten', u'tem', u'tes', u'te', # PPP Positive
               u'terer', u'teren', u'terem', u'teres', u'tere', # PPP Comparative
               u'test', u'tester', u'testen', u'testem', u'testes', u'teste' # PPP Superlative
               ]))
    ]

"""
These bugs are also detected based on strings that are on both sides of an
alleged morpheme boundary, e.g.: Pf|lichtgefühl ('f|lich')
We honor these bugs with categories of their own because they are extremely
frequent and would render the other results virtually unusable. ('pflicht'
turns out to be the second most frequent category of all with over 10k lines.)
"""
type_two_bugs = [
    (u'θ', (u'pf', u'licht')),
    (u'θ', (u'Pf', u'licht')),
    (u'ι', (u'hälf', u'te')),
    (u'ι', (u'Hälf', u'te'))
    ]


"""-------------------------------------------------
Basic definitions
-------------------------------------------------"""

"""
Counters
"""
ligs_found = 0
ligs_processed = 0
lines_processed = 0 # lines in input processed

"""
Categories
"""
smor_bugs = []
smor_final_bugs = []
selnolig_bugs = []
selnolig_final_bugs = []
clean_bugs = []
clean_final_bugs = []
# "final" is equivalent to "bugs_right".
# "smor"/"selnolig" doesn't indicate where the bug comes from,
# but for which string this category will contain matching patterns.
# (Will become clear in create_buglists() and remove_hi_freq_bugs().)
# "clean" will contain the replacement strings.

"""
Error Supercategories
"""
typeone = (u'type1', [])
typetwo = (u'type2', [])
typenos = [typeone, typetwo] # to be constucted next

"""
Construct typenos, example: (typetwo analogous)
typeone =
(u'type1',
    [   (u'ff', []),
        ...
        (u'ig', []),
        (u'innen', []),
        (u't-Endung', []),
        (u'isch', [])
    ]
"""
[typeno[1].append((liga, [])) for typeno in typenos for liga in LIGS] # set up empty lists in types
for key in bug_cats:
    entry = bug_cats[key]
    if entry[1] == 1:
        typeone[1].append((entry[0], []))
    if entry[1] == 2:
        typetwo[1].append((entry[0], []))


"""-------------------------------------------------
FUNCTIONS
-------------------------------------------------"""

def splitline(line):
    """Turns
    'x --- y --- z'
    into
    ['x', 'y', 'z']
    """
    return line.split(SEPARATOR)


def create_buglists():
    """Turns the known bugs into strings with Greek letters at the morpheme boundaries,
    which we'll use for detecting and replacing the bugs in the strings later.
    The "clean" sets are the ones that the strings will eventually be replaced with,
    the include the detailed information, according to the bug_cats dictionary, e.g.:
    δinnenschaften
    εigem
    ζisches
    fηterer
    """
    global smor_bugs, selnolig_bugs, clean_bugs
    global smor_final_bugs, selnolig_final_bugs, clean_final_bugs
    
    for bug in type_one_bugs_right:
        for buggie in bug[1]:
            smor_final_bugs.append(u'β' + buggie)
            selnolig_final_bugs.append(u'α' + buggie)
            clean_final_bugs.append(bug[0] + buggie)
    
    for bug in type_one_bugs_both:
        for buggie in bug[1][1]:
            smor_final_bugs.append(bug[1][0] + u'β' + buggie)
            selnolig_final_bugs.append(bug[1][0] + u'α' + buggie)
            clean_final_bugs.append(bug[1][0] + bug[0] + buggie)

    for bug in type_two_bugs:
        smor_bugs.append(bug[1][0] + u'α' + bug[1][1])
        selnolig_bugs.append(bug[1][0] + u'β' + bug[1][1])
        clean_bugs.append(bug[1][0] + bug[0] + bug[1][1])


"""
In general, whenever the list "parts" is used, it has three or four elements.
The line
Traumaufenthalte --- Traumaufenthalte --- Traumaufent|halte --- t|halt
(word --- SMOR analysis --- selnolig analysis --- selnolig pattern(s) applied, if any)
would correspond to:
parts = ['Traumaufenthalte', 'Traunaufenthalte', 'Traumaufent|halte', 't|halt']
(If there are no selnolig patterns applied in the input line, parts only has
three elements. This program is flexible enough to deal with three or four
elements equally.)
"""

def numerate_ligs(parts):
    """This function inserts Greek letters into the SMOR and selnolig strings,
    in accordance with which error type they are:
    'α' if there is no bar, but there is one in the corresponding SMOR/selnolig string
    'β' if there is a bar, but there none in the corresponding SMOR/selnolig string
    'γ' if there is a bar, and one in the corresponding SMOR/selnolig string as well
        (= no error)
    Example:
        Reit|halfter, Reithalf|ter
        becomes
        Reitβhalfαter, Reitαhalfβter
    I.e., both strings, SMOR and selnolig, are now of equal length, and both
    contain indicators of a morpheme boundary at the same positions.
    This way, the strings will be easier to compare and analyze.
    """
    global ligs_found
    smor = parts[1]
    smor_out = u'' # set up for later
    selnolig = parts[2]
    selnolig_out = u'' # set up for later
    smor_len = len(smor)
    selnolig_len = len(selnolig)
    smor_pos = 0
    selnolig_pos = 0
    # Do the following while we're not done with both words:
    while (smor_pos < smor_len) or (selnolig_pos < selnolig_len):
        smor_letter = smor[smor_pos]
        selnolig_letter = selnolig[selnolig_pos]
        if (smor_letter == selnolig_letter) and (smor_letter != BAR): # normal letter
            smor_out += smor_letter
            smor_pos += 1
            selnolig_out += smor_letter
            selnolig_pos += 1
        elif (smor_letter == selnolig_letter) and (smor_letter == BAR): # both detected the lig -> boring
            smor_out += u'γ'
            smor_pos += 1
            selnolig_out += u'γ'
            selnolig_pos += 1
        elif smor_letter == BAR: # only smor detected a lig
            smor_out += u'β'
            smor_pos += 1 # don't increase selnolig_pos
            selnolig_out += u'α'
            ligs_found += 1
        elif selnolig_letter == BAR: # only selnolig detected a lig
            smor_out += u'α'
            selnolig_out += u'β'
            selnolig_pos += 1 # don't increase smor_pos
            ligs_found += 1
        else: # Shouldn't ever happen, but has helped catching bugs :)
            for part in parts:
                print part
            raise Exception(u"Different character-pair in SMOR in selnolig, but neither is '|'.")
    return [parts[0], smor_out, selnolig_out, parts[3]] # "parts" configuration


def remove_hi_freq_bugs(parts):
    """This function replaces 'α' and 'β' with other Greek letters if the errors are
    known bugs as defined above.
    Example:αβ
        Reitβhelmpfαlicht Reitαhelmpfβlicht
        becomes
        Reitβhelmpfθlicht Reitαhelmpfθlicht
    We don't need to differentiate between the two 'θ' in the two strings because
    we know from their definition above if the '|' originally was in SMOR or in
    selnolig.
    """
    smor = parts[1]
    selnolig = parts[2]
    for j in range(0, len(smor_bugs)):
        smor_bug = smor_bugs[j]
        selnolig_bug = selnolig_bugs[j]
        clean_bug = clean_bugs[j]
        if (smor_bug in smor) and (selnolig_bug in selnolig):
            """ We've detected a "known bug", so we can replace it with its
            corresponding "clean bug". This way, it won't be put in the
            general type1/type2 lists later, but only in the list for that
            specific bug. Cf. below."""
            smor = smor.replace(smor_bug, clean_bug)
            selnolig = selnolig.replace(selnolig_bug, clean_bug)
    for j in range(0, len(smor_final_bugs)):
        smor_bug = smor_final_bugs[j]
        selnolig_bug = selnolig_final_bugs[j]
        clean_bug = clean_final_bugs[j]
        if smor.endswith(smor_bug) and selnolig.endswith(selnolig_bug):
            # Cf. above.
            selnolig = selnolig.replace(selnolig_bug, clean_bug)
            smor = smor.replace(smor_bug, clean_bug)
    return [parts[0], smor, selnolig, parts[3]] # "parts" configuration


def ungreek(string, smor_bool):
    """This function "undoes" the previous replacements to prepare a string for the
    output file, i.e. it replaces Greek letters with appropriate symbols as
    defined in the constants way above.
    It will only be applied to take care of the ligatures that we're *not* currently
    looking at -- CURRLIG is never inserted, that is taken care of in sortligs().

    The input Boolean contains the information whether we are in an SMOR string
    or not (= we're in a selnolig string)
    """
    outstring = u'' # set up for later
    for char in string:
        if char == u'α':   # no '|' in original
            pass # -> no indication in outstring
        elif char == u'β': # '|' in original
            outstring += OTHERLIG
        elif char == u'γ': # identical analyses
            outstring += BORINGLIG
        elif char == u'δ': # type 1: innen
            if smor_bool:
                outstring += OTHERLIG
        elif char == u'ε': # type 1: ig
            if smor_bool:
                outstring += OTHERLIG
        elif char == u'ζ': # type 1: isch
            if smor_bool:
                outstring += OTHERLIG
        elif char == u'η': # type 1: t-Endung
            if smor_bool:
                outstring += OTHERLIG
        elif char == u'θ': # type 2: pflicht
            if not smor_bool:
                outstring += OTHERLIG
        elif char == u'ι': # type 2: hälfte
            if not smor_bool:
                outstring += OTHERLIG
        else:              # normal letter
            outstring += char
    return outstring


def file_away(parts, smorpart, selnoligpart, typenoo, bugno, lig):
    """This function reassembles the "line" like it was in the input and puts it in
    the appropriate list.
    """
    line = parts[0] + SEPARATOR + smorpart + SEPARATOR + selnoligpart + SEPARATOR + parts[3]
    if bugno in u'αβ': # a "true" type 1 or 2 error (no known bug)
        idx = LIGS.index(lig) # all categories are built parallel to the LIGS list
                              # so we can reuse this order.
        typenoo[1][idx][1].append(line) # put line in appropriate list
    else: # known bug
        j = len_LIGS
        for cat in typenoo[1][len_LIGS:]: # we start looping after the LIGS lists,
                                         # since these were taken care of already
            if cat[0] == bug_cats[bugno][0]:
                idx = j
                break # break out of for-loop
            j += 1
        typenoo[1][idx][1].append(line) # put line in appropriate list


def find_neighbors(word, position):
    """This function takes a string and an integer and returns the two characters
    that are left and right of the character at the position integer in the string.
    """
    return word[position - 1] + word[position + 1]


def sort_ligs(parts):
    """This function takes "parts" and, for each (alleged) morpheme boundary detected
    by either SMOR or selnolig, replaces the Greek letters with the appropriate
    symbols as definied above and puts the entire line in the appropriate list,
    i.e. one set of "parts" results in multiple lines being put in lists
    iff morpheme boundaries were detected at several positions in the string.
    """
    smor = parts[1]
    selnolig = parts[2]
    for done_chars in range(0, len(smor)):
        smor_char = smor[done_chars]
        # selnolig_char = selnolig[done_chars] # not used
        if smor_char == u'γ': # boring lig
            pass
        elif smor_char in u'αθι': # type 2 error, i.e. originally no bar in smor
            typ = typetwo
            smor_file = ungreek(smor[:done_chars], True) + ungreek(smor[done_chars + 1:], True) # left + right
            selnolig_file = ungreek(selnolig[:done_chars], False) + CURRLIG + ungreek(selnolig[done_chars + 1:], False) # left + CURRLIG + right
            if smor_char == u'α':
                ligg = find_neighbors(smor, done_chars)
            else:
                ligg = u'' # θ and ι are "known bugs", which shouldn't be put in liga-categories
            file_away(parts, smor_file, selnolig_file, typ, smor_char, ligg)
        elif smor_char in u'βδεζη': # type 1 error, i.e. originally no bar in selnolig
            typ = typeone
            smor_file = ungreek(smor[:done_chars], True) + CURRLIG + ungreek(smor[done_chars + 1:], True) # left + CURRLIG + right
            selnolig_file = ungreek(selnolig[:done_chars], False) + ungreek(selnolig[done_chars + 1:], False) # left + right
            if smor_char == u'β':
                ligg = find_neighbors(smor, done_chars)
            else:
                ligg = u'' # δ, ε, ζ, and η are "known bugs", which shouldn't be put in liga-categories
            file_away(parts, smor_file, selnolig_file, typ, smor_char, ligg)


def make_sort_alphapure(string):
    """This function takes a string and returns a version optimized for alphabetic sorting.
    Instead of looping over the characters, we're looping over the strings to be
    replaced and replace them. (If they're not there, nothing happens.)
    """
    j = 0
    # looking for some punctuation as well:
    for char in (LC_UMLS + [u'-', OTHERLIG, BORINGLIG]):
        if char in string:
            # replace punctuation with nothing:
            string = string.replace(char, (REPL_LC_UMLS + [u'', u'', u''])[j])
        j += 1
    return string


def make_type1_key(line):
    """This function takes a line and returns a string that will be used for sorting
    that line. This function is aimed at type 1 error lines, i.e. we're sorting
    without regard to a selnolig patterns that might have been applied.

    Example:
        The line
        Reithalfter --- Reit|halfter --- Reithalf'ter --- lf|te
        results in they key
        'tier', 'halfter'
        
    key1 is all letters left of the '|' (in SMOR), read from right to left.
    key2 is all letters right of the '|' (in SMOR).

    To see why this sorting makes sense, have a look at any of the
    'errors.type1.*' files.
    """
    pos_CURRLIG = line.find(CURRLIG)
    pos_SEPARATOR1 = line.find(SEPARATOR)
    pos_SEPARATOR2 = line.find(SEPARATOR, pos_SEPARATOR1 + 1)
    
        # CURRLIG to first SEPARATOR, reversed = part left of '|', reversed:
    key1 = (line[(pos_CURRLIG - len_CURRLIG):(pos_SEPARATOR1 + len_SEPARATOR - 1): - 1]).lower()
        # CURRLIG to second SEPARATOR = part right of '|':
    key2 = (line[(pos_CURRLIG + len_CURRLIG):(pos_SEPARATOR2)]).lower()
    
    sortkey = [make_sort_alphapure(key1), make_sort_alphapure(key2)]
    return sortkey


def make_type2_key(line):
    """This function takes a line and returns a string that will be used for sorting
    that line. This function is aimed at type 2 error lines.

    Example:
        The line
        drauflostherapieren --- drauflostherapieren --- drauf'lost|herapieren --- st|her,uf|los
        results in they key
        'st|her,uf|los', 'herapiere', 'herapieren', 'tsolfuard'
        
    key1 is the selnolig patterns applied. (However, the applied selnolig patterns
        are dealt with as a string, not as a list, cf. documentation.)
    key2 is all letters right of the '|' (in selnolig)
        ignoring the letters 'm', 'n', 's', which are a rough approximation for
        "inflectional endings (mostly of nouns/adjectives, but also verbs)".
    key3 is like key2, but not ignoring the endings.
        (key2 and key3 might be identical, but that does no harm.)
    key4 is all letters left of the '|' (in selnolig), read from right to left.

    To see why this sorting makes sense, have a look at any of the
    'errors.type2.*' files.
    """
    pos_CURRLIG = line.find(CURRLIG)
    pos_SEPARATOR1 = line.find(SEPARATOR)
    pos_SEPARATOR2 = line.find(SEPARATOR, pos_SEPARATOR1 + 1)
    pos_SEPARATOR3 = line.find(SEPARATOR, pos_SEPARATOR2 + 1) # equiv.: = line.rfind(SEPARATOR)
        # approximation for "ignore inflectional endings":
    if line[pos_SEPARATOR3 - 1] in u'mns':
        ignore_ending = 1 # this will lead to one fewer character
                          # being taken into consideration.
    else:
        ignore_ending = 0
    
        # last SEPARATOR to end = selnolig-pattern(s):
    key1 = (line[(pos_SEPARATOR3 + len_SEPARATOR):]).lower()
        # CURRLIG to third SEPARATOR = part right of '|', ignoring endings:
    key2 = (line[(pos_CURRLIG + len_CURRLIG):(pos_SEPARATOR3 - ignore_ending)]).lower()
        # CURRLIG to third SEPARATOR = part right of '|', not ignoring endings:
    key3 = (line[(pos_CURRLIG + len_CURRLIG):(pos_SEPARATOR3)]).lower()
        # CURRLIG back to second SEPARATOR, reversed = part left of '|', reversed:
    key4 = (line[(pos_CURRLIG - len_CURRLIG):(pos_SEPARATOR2 + len_SEPARATOR - 1): - 1]).lower()
    
        # keep umlauts and special chars in the selnolig-pattern:
    sortkey = [key1, make_sort_alphapure(key2), make_sort_alphapure(key3), make_sort_alphapure(key4)]
    return sortkey


def writetofiles():
    """This function sorts all the lists using the keys defined above, writes
    all the lines to a file named according to their categorization, and prints
    statistics about the categories to the console.
    """
    global ligs_processed
    for item in typeone[1]:
        linelist = item[1]
        linelist.sort(key=lambda x: make_type1_key(x))
    for item in typetwo[1]:
        linelist = item[1]
        linelist.sort(key=lambda x: make_type2_key(x))
    for typenoo in typenos:
        type_name = typenoo[0]
        print u'\n--- ', type_name, u'---'
        for cat in typenoo[1]:
            bug_name = cat[0]
            ofile = codecs.open(u'04-errors/errors.' + type_name + u'.' + bug_name, 'wb', 'utf-8')
            print bug_name + u': ' + str(len(cat[1]))
            ofile.write(starttext) # add start text to file, cf. above
            for line in cat[1]:
                ofile.write(line + u'\n')
                ligs_processed += 1
            ofile.close()


def print_stats():
    """This function prints stats about the entire run."""
    if len_infile == lines_processed:
        check1 = u'-- none missed, success!'
    else:
        check1 = u'-- uh-oh, missed some.'

    if ligs_found == ligs_processed:
        check2 = u'-- none missed, success!'
    else:
        check2 = u'-- uh-oh, missed some.'
        
    print u'\n--- summary ---'
    print u'input lines detected: ', len_infile
    print u'input lines processed:', lines_processed, check1
    print u'ligatures detected:', ligs_found
    print u'ligatures processed:', ligs_processed, check2
    print u'   (i.e. at least', ligs_processed - lines_processed, u'ligatures were not the only ligature in their line.)'
    print u'runtime: ' + str(time() - start) + u's'


def main():
    """This is the main function, which executes all second order functions defined
    so far.

    The counter i has proven to be helpful for debugging.
    if i > 0:
        only process i lines
    if i <= 0:
        process all lines (I prefer to use -1 for this case)
    """
    global lines_processed
    i = -1
    create_buglists()
    for line in infile:
        #print line # uncomment for debugging. (Don't forget to change i ;-)
        line = line.rstrip(u'\n') # remove trailing newline symbol
        simple_parts = splitline(line)
        num_parts = numerate_ligs(simple_parts)
        parts = remove_hi_freq_bugs(num_parts)
        sort_ligs(parts)
        lines_processed += 1
        i -= 1
        if i == 0:
            print u'\n-- testrun done --\n'
            break
    writetofiles()
    print_stats()
    infile.close()

main()
