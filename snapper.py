from __future__ import division, print_function, absolute_import

import glob
from os import remove
from os.path import basename

import numpy as np

from ligmos import utils

from picamhelpers.capture import piCamCapture
from picamhelpers.classes import piCamSettings
from picamhelpers.utils import copyStaticFilenames


if __name__ == "__main__":
    # Read in our config file
    confFile = './config/snapper.conf'
    camSettings = utils.confparsers.parseConfig(confFile, piCamSettings,
                                                passfile=None,
                                                searchCommon=False,
                                                enableCheck=False)

    maxagehrs = 24.
    captureintervalsec = 60.
    outloc = "./snaps/"

    lout = outloc + "/anim/"
    staticname = 'pizini'
    nstaticfiles = 24

    # Start logging to a file
    utils.logs.setup_logging(logName="./logs/pimcpiface.txt", nLogs=10)

    while True:
        piCamCapture(outloc, debug=True)

        # Cull the images to the last XX days worth
        print("Searching for old files...")
        now = dt.utcnow()
        young, old = utils.files.findOldFiles(outloc, "*.png", now,
                                              maxage=maxagehrs,
                                              dtfmt="%Y%m%d_%H%M%S.png")
        print("Deleting old files...")
        print(old)
        utils.files.deleteOldFiles(old)

        # Copy the static files that get animated
        print("Copying new files to static names for animation...")
        copyStaticFilenames(young, lout, staticname, nstaticfiles)

        # Sleep for sleeptime in 1 second intervals
        print("Sleeping for %f seconds..." % (captureintervalsec))
        i = 0
        while i < captureintervalsec:
            sleep(1)
            if (i + 1) % 5 == 0:
                print(".")
            i += 1
