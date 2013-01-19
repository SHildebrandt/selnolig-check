# -*- coding: utf-8 -*-
"""
Definition of a class for ligatures

Version: 0.1
"""

"""
A ligature is defined by a glyph which is just a string.
"""
class Ligature:

    """
    Constructor
    """
    def __init__(self, ligature):
        self.glyph = ligature
        self.rules = []

    """
    Return the glyph
    """
    def get_glyph(self):
        return self.glyph
    
    """
    Override __str__
    """
    def __str__(self):
        return (u'<' + self.glyph + u'>').encode('utf-8')

    """
    Override __len__
    """
    def __len__(self):
        return len(self.glyph)
    
"""
Definition of all the needed ligatures
"""
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

"""
List of all created ligatures
"""
LIGS = [ff, fi, fl, ffi, ffl, ft, fb, fh, fk, fj, fff, th]

"""
List of all ligatures consisting of exactly two letters
"""
LIGS_TWO_GLYPHS = [lig for lig in LIGS if len(lig) == 2]
