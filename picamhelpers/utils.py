# -*- coding: utf-8 -*-
#
#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
#  Created on 25 Feb 2020
#
#  @author: rhamilton

"""One line description of module.

Further description.
"""

from __future__ import division, print_function, absolute_import

from shutil import copyfile


def copyStaticFilenames(cpng, lout, staticname, nstaticfiles):
    """
    cpng should be a dict, whose key is the filename and the
    value is that filename's determined age (in seconds)
    errorAge is given in hours and then converted to seconds

    A paired-down copy of the NightShift util:
    https://github.com/LowellObservatory/NightShift/blob/master/nightshift/common/utils.py
    """
    latestname = '%s/%s_latest.png' % (lout, staticname)

    # Since we gave it a dict we just put it into a list to make
    #   indexing below a little easier.
    clist = list(cpng.keys())

    # Make sure we don't try to operate on an empty dict, or one too small
    if len(cpng) < nstaticfiles:
        lindex = len(cpng)
    else:
        lindex = nstaticfiles

    icount = 0
    # It's easier to do this in reverse
    for findex in range(-1*lindex, 0, 1):
        try:
            lname = "%s/%s_%03d.png" % (lout, staticname, icount)
            icount += 1
            copyfile(clist[findex], lname)
        except Exception as err:
            # TODO: Figure out the proper/specific exception
            print(str(err))
            print("WHOOPSIE! COPY FAILED")

    # Put the very last file in the last file slot
    latest = clist[-1]
    try:
        copyfile(latest, latestname)
        print("Latest file copy done!")
    except Exception as err:
        # TODO: Figure out the proper/specific exception to catch
        print(str(err))
        print("WHOOPSIE! COPY FAILED")
