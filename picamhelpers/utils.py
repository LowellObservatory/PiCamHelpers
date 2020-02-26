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


def copyStaticFilenames(nstaticfiles, lout, staticname, cpng):
    """
    """
    latestname = '%s/%s_latest.png' % (lout, staticname)

    if cpng != []:
        if len(cpng) < nstaticfiles:
            lindex = len(cpng)
        else:
            lindex = nstaticfiles

        # It's easier to do this via reverse list indicies
        icount = 0
        for findex in range(-1*lindex, 0, 1):
            try:
                lname = "%s/%s_%03d.png" % (lout, staticname, icount)
                icount += 1
                copyfile(cpng[findex], lname)
            except Exception as err:
                # TODO: Figure out the proper/specific exception
                print(str(err))
                print("WHOOPSIE! COPY FAILED")

        # Put the very last file in the last file slot
        latest = cpng[-1]
        try:
            copyfile(latest, latestname)
            print("Latest file copy done!")
        except Exception as err:
            # TODO: Figure out the proper/specific exception to catch
            print(str(err))
            print("WHOOPSIE! COPY FAILED")
