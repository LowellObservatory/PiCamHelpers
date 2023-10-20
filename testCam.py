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

    outloc = camSettings.savepath

    # Start logging to a file
#    utils.logs.setup_logging(logName="./logs/snapper.log", nLogs=10)

    piCamCapture(camSettings, outloc, debug=True, retries=3)


if __name__ == "__main__":
    main()
    print("Pi snapper has exited!")
