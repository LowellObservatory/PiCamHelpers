from __future__ import division, print_function, absolute_import

import time
from datetime import datetime as dt

from ligmos import utils

from picamhelpers.capture import piCamCapture
from picamhelpers.classes import piCamSettings
from picamhelpers.utils import copyStaticFilenames


def main():
    """
    """
    # Read in our config file
    confFile = './config/snapper.conf'
    # We ignore the second return value since searchCommon is False
    camSettings, _ = utils.confparsers.parseConfig(confFile, piCamSettings,
                                                   passfile=None,
                                                   searchCommon=False,
                                                   enableCheck=False)

    # We're cheating by grabbing the relevant config section directly
    #   but it's ok, I'm abusing my own API so it's fine.
    camSettings = camSettings['picam']

    maxagehrs = 24.
    captureintervalsec = 60.
    outloc = "./snaps/"

    lout = outloc + "/anim/"
    staticname = 'pizini'
    nstaticfiles = 24

    # Start logging to a file
    utils.logs.setup_logging(logName="./logs/pimcpiface.txt", nLogs=10)

    while True:
        piCamCapture(camSettings, outloc, debug=True)

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
        copyStaticFilenames(nstaticfiles, lout, staticname, young)

        # Sleep for sleeptime in 1 second intervals
        print("Sleeping for %f seconds..." % (captureintervalsec))
        i = 0
        while i < captureintervalsec:
            time.sleep(1)
            if (i + 1) % 5 == 0:
                print(".")
            i += 1


if __name__ == "__main__":
    main()
