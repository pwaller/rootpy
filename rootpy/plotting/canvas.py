# Copyright 2012 the rootpy developers
# distributed under the terms of the GNU General Public License
"""
This module implements python classes which inherit from
and extend the functionality of the ROOT canvas classes.
"""

import ROOT

from ..core import NamedObject
from .. import QROOT


class _PadBase(NamedObject):

    def _post_init(self):

        self.members = []

    def Clear(self, *args, **kwargs):

        self.members = []
        super(_PadBase, self).Clear(*args, **kwargs)

    def OwnMembers(self):

        for thing in self.GetListOfPrimitives():
            if thing not in self.members:
                self.members.append(thing)


class Pad(_PadBase, QROOT.TPad):

    def __init__(self, *args, **kwargs):

        # trigger finalSetup
        ROOT.kTRUE
        super(Pad, self).__init__(*args, **kwargs)
        self._post_init()


class Canvas(_PadBase, QROOT.TCanvas):

    def __init__(self,
                 width=None, height=None,
                 x=None, y=None,
                 name=None, title=None,
                 size_includes_decorations=False):

        # The following line will trigger finalSetup and start the graphics
        # thread if not started already
        style = ROOT.gStyle
        if width is None:
            width = style.GetCanvasDefW()
        if height is None:
            height = style.GetCanvasDefH()
        if x is None:
            x = style.GetCanvasDefX()
        if y is None:
            y = style.GetCanvasDefY()
        # trigger finalSetup
        ROOT.kTRUE
        super(Canvas, self).__init__(x, y, width, height,
                                     name=name, title=title)
        if not size_includes_decorations:
            # Canvas dimensions include the window manager's decorations by
            # default in vanilla ROOT. I think this is a bad default.
            # Since in the most common case I don't care about the window
            # decorations, the default will be to set the dimensions of the
            # paintable area of the canvas.
            if self.IsBatch():
                self.SetCanvasSize(width, height)
            else:
                self.SetWindowSize(width + (width - self.GetWw()),
                                   height + (height - self.GetWh()))
        self._post_init()
