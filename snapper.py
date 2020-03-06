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
    confFile = './config/picamSettings.conf'
    # We ignore the second return value since searchCommon is False
    camSettings, _ = utils.confparsers.parseConfig(confFile, piCamSettings,
                                                   passfile=None,
                                                   searchCommon=False,
                                                   enableCheck=False)

    # We're cheating by grabbing the relevant config section directly
    #   but it's ok, I'm abusing my own API so it's fine.
    camSettings = camSettings['picam']

    # Another hack
    try:
        camSettings.interval = int(camSettings.interval)
    except ValueError:
        camSettings.interval = 90

    maxagehrs = 24.
    outloc = "./snaps/"

    lout = outloc + "/anim/"
    staticname = 'pizini'
    nstaticfiles = 24

    # Start logging to a file
    utils.logs.setup_logging(logName="./logs/pimcpiface.txt", nLogs=10)

    # Set up our signal
    runner = utils.common.HowtoStopNicely()

    while runner.halt is False:
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
        copyStaticFilenames(young, lout, staticname, nstaticfiles)

        # Sleep for sleeptime in 1 second intervals
        print("Sleeping for %f seconds..." % (camSettings.interval))
        i = 0
        if runner.halt is False:
            print("Starting a big sleep")
            # Sleep for bigsleep, but in small chunks to check abort
            for _ in range(camSettings.interval):
                time.sleep(1)
                if (i + 1) % 30 == 0:
                    print(".", end=None)
                i += 1
                if runner.halt is True:
                    break
        print()


if __name__ == "__main__":
    main()
