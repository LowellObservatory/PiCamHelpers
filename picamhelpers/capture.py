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

from time import sleep
from fractions import Fraction
from datetime import datetime as dt

import picamera
from picamera import PiCamera, Color


def piCamInit(camSettings):
    if picamera is not None and camSettings is not None:
        picamera.PiCamera.CAPTURE_TIMEOUT = 60

        # https://picamera.readthedocs.io/en/latest/fov.html#camera-modes
        camera = PiCamera(sensor_mode=3)

        # Allow the camera to use a framerate that's high (1/10 per second)
        #   or fast (30 per second) depending on conditions. Best to do
        #   this first before anything else
        camera.framerate_range = (Fraction(1, 10), Fraction(30, 1))

        # Need to make sure these are integers since they're parsed in
        #   from a configuration file and are probably strings
        camera.resolution = (int(camSettings.resolution[0][1:]),
                             int(camSettings.resolution[1][:-1]))
        camera.vflip = camSettings.flipv
        camera.hflip = camSettings.fliph

        camera.drc_strength = camSettings.drc_strength
        camera.exposure_mode = camSettings.exposure_mode
        camera.meter_mode = camSettings.meter_mode
        # Same as resolution above - this needs to be an int!
        camera.exposure_compensation = int(camSettings.exposure_compensation)
        camera.image_denoise = camSettings.image_denoise

        print("Allowing camera to reticulate some splines...")
        sleep(40)

        # To fix exposure gains, let analog_gain and digital_gain settle on
        #   reasonable values, then set exposure_mode to 'off'.
        camera.exposure_mode = 'off'
    else:
        camera = None

    return camera


def piCamCapture(camSettings, outloc, debug=False, retries=10):
    startTime = dt.utcnow()
    startTimeStr = startTime.strftime("%Y%m%d_%H%M%S")
    print("Entering capture sequence at %s" % (startTimeStr))

    # Init the camera. Try a few times if it's busy
    retryCounter = 0
    intervalRetries = 10
    camera = None

    # This allows for a number of retries, in case another process
    #   is using the camera and isn't immediately available.
    while camera is None and retryCounter < retries:
        try:
            camera = piCamInit(camSettings)
        except picamera.exc.PiCameraMMALError:
            print("Camera is likely busy! Try again later.")
            retryCounter += 1
            print("%d retries remain." % (retries - retryCounter))
            sleep(intervalRetries)

    if camera is not None:
        # If camera.shutter_speed is 0, camera.exposure_speed will be the
        #   actual/used value determined during the above sleeps
        print("exp: %f, shut: %f" % (camera.shutter_speed,
                                     camera.exposure_speed))
        expspeed = round(camera.exposure_speed/1e6, 6)

        # Actually do the capture now!
        nowTime = dt.utcnow()
        nowTimeStr = nowTime.strftime("%Y%m%d_%H%M%S")
        timeAnnotate = nowTime.strftime("%Y-%m-%d %H:%M:%S UTC")

        # This has to happen *before* the capture!
        annotation = "%s, %.4f sec" % (timeAnnotate, round(expspeed, 4))
        camera.annotate_background = Color("black")
        camera.annotate_text = annotation

        print("Starting capture at %s" % (nowTimeStr))

        outname = "%s/%s.png" % (outloc, nowTimeStr)
        camera.capture(outname)
        print("Capture complete!")

        if debug is True:
            print("Captured %s" % (outname))

        print("Took a %d microseconds exposure." % (camera.exposure_speed))

        # https://github.com/waveform80/picamera/issues/528
        camera.framerate = 1
        camera.close()
    else:
        outname = None

    return outname
