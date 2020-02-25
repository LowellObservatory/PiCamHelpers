from __future__ import division, print_function, absolute_import

import glob
from os import remove
from os.path import basename

from time import sleep
from fractions import Fraction
from datetime import datetime as dt

import numpy as np
import picamera
from picamera import PiCamera, Color

import utils
import utils_logs


def camInit():
    # https://picamera.readthedocs.io/en/latest/fov.html#camera-modes
    camera = PiCamera(sensor_mode=3)
    picamera.PiCamera.CAPTURE_TIMEOUT = 60
    # camera.resolution = (2592, 1944)
    # camera.resolution = (1296, 972)
    camera.resolution = (864, 648)

    # Allow the camera to use a framerate that's high (1/10 per second)
    #   or fast (30 per second) depending on conditions
    camera.framerate_range = (Fraction(1, 10), Fraction(30, 1))
    camera.vflip = False
    camera.hflip = False

    camera.drc_strength = 'high'
    camera.exposure_mode = 'night'
    camera.meter_mode = 'matrix'
    camera.exposure_compensation = 25
    camera.image_denoise = False

    print("Allowing camera to reticulate some splines...")
    sleep(70)

    # To fix exposure gains, let analog_gain and digital_gain settle on
    #   reasonable values, then set exposure_mode to 'off'.
    camera.exposure_mode = 'off'

    return camera


def capture(outloc, debug=False, retries=10):
    now = dt.utcnow()
    nowstr = now.strftime("%Y%m%d_%H%M%S")
    print("Starting capture at %s" % (nowstr))

    # Init the camera. Try a few times if it's busy
    retryCounter = 0
    intervalRetries = 10
    camera = None

    # This allows for a number of retries, in case another process
    #   is using the camera and isn't immediately available.
    while camera is None and retryCounter < retries:
        try:
            camera = camInit()
        except picamera.exc.PiCameraMMALError:
            print("Camera is likely busy! Try again later.")
            retryCounter += 1
            print("%d retries remain." % (retries - retryCounter))
            sleep(intervalRetries)

    if camera is not None:
        outname = "./%s/%s.png" % (outloc, nowstr)

        # If camera.shutter_speed is 0, camera.exposure_speed will be the
        #   actual/used value determined during the above sleeps
        print("exp: %f, shut: %f" % (camera.shutter_speed,
                                     camera.exposure_speed))
        expspeed = np.round(camera.exposure_speed/1e6, 6)

        annotation = "Time: %s\nShutterSpeed: %s sec" % (nowstr, str(expspeed))

        # This has to happen *before* the capture!
        camera.annotate_background = Color("black")
        camera.annotate_text_size = 18
        camera.annotate_text = annotation

        # Actually do the capture now!
        print("Starting capture...")
        camera.capture(outname)
        print("Capture complete!")

        if debug is True:
            print("Captured %s" % (outname))
            print("Took a %d microseconds exposure." % (camera.exposure_speed))

    # https://github.com/waveform80/picamera/issues/528
    camera.framerate = 1
    camera.close()


if __name__ == "__main__":
    maxagehrs = 24.
    captureintervalsec = 60.
    outloc = "./snaps/"

    lout = outloc + "/anim/"
    staticname = 'pizini'
    nstaticfiles = 24

    # Start logging to a file
    utils_logs.setup_logging(logName="./logs/pimcpiface.txt", nLogs=10)

    while True:
        capture(outloc, debug=True)

        # Cull the images to the last XX days worth
        print("Searching for old files...")
        now = dt.utcnow()
        young, old = utils.findOldFiles(outloc, "*.png", now,
                                        maxage=maxagehrs,
                                        dtfmt="%Y%m%d_%H%M%S.png")
        print("Deleting old files...")
        print(old)
        utils.deleteOldFiles(old)

        # Copy the static files that get animated
        print("Copying new files to static names for animation...")
        utils.copyStaticFilenames(young, lout,
                                  staticname, nstaticfiles)

        # Sleep for sleeptime in 1 second intervals
        print("Sleeping for %f seconds..." % (captureintervalsec))
        i = 0
        while i < captureintervalsec:
            sleep(1)
            if (i + 1) % 5 == 0:
                print(".")
            i += 1
