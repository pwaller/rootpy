# Copyright 2012 the rootpy developers
# distributed under the terms of the GNU General Public License
"""
:py:mod:`rootpy.logger`
=======================

:py:mod:`rootpy` overrides the default logging class, inserting a check that there
exists a default logging handler. If there is not, it adds one.

In additon, this can be used to intercept ROOT's log messages and redirect them
through python's logging subsystem

Example use:

.. sourcecode:: python

    # Disable colored logging (not needed if writing into a file, this is automatic).
    # Must be done before :py:mod:`rootpy` logs any messages.
    import logging; logging.basicConfig(level=logging.DEBUG)

    from rootpy import log; log = log["/myapp"]
    log.debug("Hello") # Results in "DEBUG:myapp] Hello"

    # Suppress all myapp debug and info messages
    log.setLevel(log.WARNING)
    log.debug("Hello") # No effect

    mymod = log["mymod"]
    mymod.warning("Hello") # Results in "WARNING:myapp.mymod] Hello"

    # Suppress all rootpy debug and info messages
    log["/rootpy"].setLevel(log.WARNING)

    # Suppress messages coming from TCanvas like
    # INFO:ROOT.TCanvas.Print] png file /path/to/file.png has been created
    log["/ROOT.TCanvas.Print"].setLevel(log.WARNING)

    # Suppress warning messages coming the ``TClass`` constructor:
    log["/ROOT.TClass.TClass"].setLevel(log.ERROR)

    # Precisely remove messages containing the text "no dictionary for class"
    # (doesn't work when attached to parent logger)
    import logging
    class NoDictMessagesFilter(logging.Filter):
        def filter(self, record):
            return "no dictionary for class" not in record.msg
    log["/ROOT.TClass.TClass"].addFilter(NoDictMessagesFilter())

    # Turn ROOT errors into exceptions
    from rootpy.logger.magic import DANGER
    DANGER.enable = True

    import ROOT
    ROOT.Error("test", "Test fatal")
    # Result:
    # ERROR:ROOT.test] Test fatal
    # Traceback (most recent call last):
    #   File "test.py", line 36, in <module>
    #     ROOT.Fatal("test", "Test fatal")
    #   File "test.py", line 36, in <module>
    #     ROOT.Fatal("test", "Test fatal")
    #   File "rootpy/logger/roothandler.py", line 40, in python_logging_error_handler
    #     raise ROOTError(level, location, msg)
    # rootpy.ROOTError: level=6000, loc='test', msg='Test fatal'

    # Primitive function tracing:
    @log.trace()
    def salut():
        return

    @log.trace()
    def hello(what):
        salut()
        return "42"

    hello("world")
    # Result:
    #   DEBUG:myapp.trace.hello] > ('world',) {}
    #   DEBUG:myapp.trace.salut]  > () {}
    #   DEBUG:myapp.trace.salut]  < return None [0.00 sec]
    #   DEBUG:myapp.trace.hello] < return 42 [0.00 sec]


"""

import logging
import os
import re
import sys

from functools import wraps
from time import time

# Must import extended_logger, then others.
import rootpy.logger.extended_logger
root_logger = logging.getLogger("ROOT")
log = logging.getLogger("rootpy")

if not os.environ.get("DEBUG", False):
    log.setLevel(log.INFO)

import rootpy.logger.color

from .magic import set_error_handler

# Circular
from .roothandler import python_logging_error_handler

import threading
class TraceDepth(threading.local):
    value = -1

trace_depth = TraceDepth()

def log_trace(logger, level=logging.DEBUG, show_enter=True, show_exit=True):
    """
    log a statement on function entry and exit
    """
    def wrap(function):
        l = logger.getChild(function.__name__).log
        @wraps(function)
        def thunk(*args, **kwargs):
            global trace_depth
            trace_depth.value += 1
            try:
                start = time()
                if show_enter:
                    l(level, "{0}> {1} {2}".format(" "*trace_depth.value,
                                                   args, kwargs))
                try:
                    result = function(*args, **kwargs)
                except:
                    _, result, _ = sys.exc_info()
                    raise
                finally:
                    if show_exit:
                        l(level, "{0}< return {1} [{2:.2f} sec]".format(
                            " "*trace_depth.value, result, time() - start))
            finally:
                trace_depth.value -= 1
            return result
        return thunk
    return wrap


class LogFilter(logging.Filter):
    def __init__(self, logger, message_regex):
        logging.Filter.__init__(self)
        self.logger = logger
        self.message_regex = re.compile(message_regex)

    def __enter__(self):
        self.logger.addFilter(self)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.logger.removeFilter(self)

    def filter(self, record):
        return not self.message_regex.match(record.getMessage())


class LiteralFilter(logging.Filter):
    def __init__(self, literals):
        logging.Filter.__init__(self)
        self.literals = literals

    def filter(self, record):
        return record.getMessage() not in self.literals


# filter superfluous ROOT warnings
log["/ROOT.TH1D.Add"].addFilter(LiteralFilter(
    ["Attempt to add histograms with different axis limits",]))
log["/ROOT.TH1D.Divide"].addFilter(LiteralFilter(
    ["Attempt to divide histograms with different axis limits",]))
log["/ROOT.TH1D.Multiply"].addFilter(LiteralFilter(
    ["Attempt to multiply histograms with different axis limits",]))
