# Copyright 2012 the rootpy developers
# distributed under the terms of the GNU General Public License

from array import array

from .. import QROOT
from ..decorators import snake_case_methods
from ..core import NamedObject
from .utils import canvases_with


class AxisScalingMixin(object):
    
    def scale(self, factor):
        """
        Apply a scale factor to this axis. Useful for changeing MeV->GeV->TeV,
        for example.
        """
        
        bins = self.bin_positions
        new_bins = array("d", (factor * bin for bin in bins))
        self.Set(self.GetNbins(), new_bins)
        self.invalidate()
    
    def __mul__(self, factor):
        """
        Return a copy of this axis scaled by a factor
        """
        
        new = self.Clone()
        new *= factor
        return new
        
    def __div__(self, factor):
        """
        Return a copy of this axis scaled by a factor
        """
        
        new = self.Clone()
        new /= factor
        return new
    
    def __imul__(self, factor):
        """
        See Axis.scale(factor)
        
        Usage:

        # Convert histogram from GeV units to MeV
        xaxis *= 1000
        """
        
        if not isinstance(factor, (int, float)):
            raise TypeError
        
        self.scale(factor)
        return self
    
    def __idiv__(self, factor):
        """
        See Axis.scale(factor)
        
        Usage:

        # Convert histogram from MeV units to GeV
        xaxis /= 1000
        """
        
        if not isinstance(factor, (int, float)):
            raise TypeError
        
        self.scale(1. / factor)
        return self


@snake_case_methods
class Axis(AxisScalingMixin, NamedObject, QROOT.TAxis):

    def __init__(self, name=None, title=None, **kwargs):

        super(Axis, self).__init__(name=name, title=title)
    
    def Clone(self, *args, **kwargs):
        """
        Forwards to superclass Clone but sets the clones' name to self.name
        """
        new = super(Axis, self).Clone(*args, **kwargs)
        # Unique names aren't needed for axes
        new.name = self.name
        return new

    @property
    def range_user(self):
        
        first, last = self.GetFirst(), self.GetLast()
        return self.GetBinLowEdge(first), self.GetBinUpEdge(last)

    @range_user.setter
    def range_user(self, r):
        
        lo, hi = r
        self.SetRangeUser(lo, hi)

    def SetRangeUser(self, lo, hi):

        super(Axis, self).SetRangeUser(lo, hi)
        self.invalidate()

    def invalidate(self):
        
        # Notify relevant canvases that they are modified.
        # Note: some might be missed if our parent is encapsulated in some
        #       other class.
        
        for c in canvases_with(self.GetParent()):
            c.Modified()
        
    @property
    def bin_positions(self):
        """
        Returns the list of bin positions
        """
        
        bins = self.GetXbins()
        if bins.fN:
            return [bins[i] for i in xrange(bins.fN)]
        xn, xmin, xmax = self.GetNbins(), self.GetXmin(), self.GetXmax()
        bwidth = (xmax - xmin) / xn
        return [xmin + bwidth*i for i in xrange(xn)] + [xmax]
