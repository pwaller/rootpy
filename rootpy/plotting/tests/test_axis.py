# Copyright 2012 the rootpy developers
# distributed under the terms of the GNU General Public License
from rootpy.plotting import Hist, Hist2D, Hist3D, HistStack
from nose.tools import raises, assert_equals, assert_raises


epsilon = 1e-3

def test_axis_scaling():
    h = Hist(100, 0, 1000. + epsilon)
    
    assert_equals(h.xaxis.find_bin(1000), 100)
    
    # Check that copy operations don't break it
    h.xaxis * 10
    assert_equals(h.xaxis.find_bin(1000), 100)
    
    h.xaxis / 10
    assert_equals(h.xaxis.find_bin(1000), 100)
    
    # Check that scaling operations work
    
    factor = 1000
    h.xaxis /= factor
    assert_equals(h.xaxis.find_bin(1000 / factor), 100)
    
    factor = 1000
    h.xaxis *= factor
    assert_equals(h.xaxis.find_bin(1 * factor), 100)
    
def test_axis_assignment():
    
    h1 = Hist(100, 0, 1000.)
    h1.xaxis.range_user = 10, 20    
    
    assert_equals(h1.xaxis.find_bin(1000 - epsilon), 100)
    print "Blah: ", h1.xaxis.find_bin(1000 - epsilon)
    
    h2 = Hist(100, 0, 100.)
    assert_equals(h2.xaxis.find_bin(100 - epsilon), 100)
    
    h2.xaxis = h1.xaxis
    
    # should be unchanged, since h2 is the one which is modified
    assert_equals(h1.xaxis.find_bin(1000 - epsilon), 100)
    
    # h2 should inherit all properties of h1
    assert_equals(h1.xaxis.range_user, h2.xaxis.range_user)
    
    assert_equals(h1.xaxis.find_bin(1000 - epsilon), h2.xaxis.find_bin(1000 - epsilon))
    
