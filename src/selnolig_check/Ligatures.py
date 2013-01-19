#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Definition of a class for ligatures

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


class Ligature:
    """A ligature is defined by a glyph which is just a string."""

    def __init__(self, ligature):
        self.glyph = ligature
        self.rules = []

    def __str__(self):
        return (u'<' + self.glyph + u'>').encode('utf-8')

    def __len__(self):
        return len(self.glyph)


"""Definition of all the needed ligatures"""
ff  = Ligature(u'ff')
fi  = Ligature(u'fi')
fl  = Ligature(u'fl')
ffi = Ligature(u'ffi')
ffl = Ligature(u'ffl')
ft  = Ligature(u'ft')
fb  = Ligature(u'fb')
fh  = Ligature(u'fh')
fk  = Ligature(u'fk')
fj  = Ligature(u'fj')
fff = Ligature(u'fff')
th  = Ligature(u'th')


"""List of all created ligatures"""
LIGS = [ff, fi, fl, ffi, ffl, ft, fb, fh, fk, fj, fff, th]


"""List of all ligatures consisting of exactly two letters"""
LIGS_TWO_GLYPHS = [lig for lig in LIGS if len(lig) == 2]
