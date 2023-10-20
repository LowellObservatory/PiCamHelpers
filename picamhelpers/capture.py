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

from time import sleep, strftime
from fractions import Fraction
from datetime import datetime as dt

import cv2
from libcamera import Transform
from picamera2 import Picamera2, MappedArray


def apply_timestamp(request):
    colour = (0, 255, 0)
    origin = (0, 30)
    font = cv2.FONT_HERSHEY_SIMPLEX
    scale = 1
    thickness = 2
    timestamp = strftime("%Y-%m-%d %X")
    with MappedArray(request, "main") as m:
        cv2.putText(m.array, timestamp, origin, font, scale, colour, thickness)


def piCamInit(camSettings):
    try:
#        picamera2.Picamerai2.CAPTURE_TIMEOUT = 60

        print("Connecting to camera...")
        camera = Picamera2()
        camera.pre_callback = apply_timestamp

        print("Camera modes")
        print(camera.sensor_modes)
        config = camera.create_still_configuration({"size": (int(camSettings.resolution[0][1:]),
                                                             int(camSettings.resolution[1][:-1]))})
        print("Created barebones config, setting additional parameters...")

        # Need to make sure these are integers since they're parsed in
        #   from a configuration file and are probably strings

        config["transform"] = Transform(vflip=camSettings.flipv, 
                                        hflip=camSettings.fliph)

        camera.set_controls({"FrameDurationLimits": (100, 3e7), 
                             "AeEnable": True,
                             "AeExposureMode": camSettings.exposure_mode,
                             "AeMeteringMode": camSettings.meter_mode})

#        camera.exposure_compensation = int(camSettings.exposure_compensation)
#        camera.image_denoise = camSettings.image_denoise

        print(config)
        camera.align_configuration(config)
        camera.configure(config)
        camera.start(show_preview=True)
#        print(config)
        print("Allowing camera to reticulate some splines...")
        sleep(40)

        # To fix exposure gains, let analog_gain and digital_gain settle on
        #   reasonable values, then set exposure_mode to 'off'.
        print("Disabling auto exposure control")
        camera.set_controls({"AeEnable": False})

    except Exception as err:
        print(str(err))
        camera.stop()
        camera = None

    return camera, config


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
            camera, config = piCamInit(camSettings)
        except Exception as err:
            print(str(err))
            retryCounter += 1
            print("%d retries remain." % (retries - retryCounter))
            sleep(intervalRetries)

    if camera is not None:
        # If camera.shutter_speed is 0, camera.exposure_speed will be the
        #   actual/used value determined during the above sleeps
#        print("exp: %f, shut: %f" % (camera.shutter_speed,
#                                     camera.exposure_speed))
#        expspeed = round(camera.exposure_speed/1e6, 6)
        expspeed = 0.

        # Actually do the capture now!
        nowTime = dt.utcnow()
        nowTimeStr = nowTime.strftime("%Y%m%d_%H%M%S")
        timeAnnotate = nowTime.strftime("%Y-%m-%d %H:%M:%S UTC")

        # This has to happen *before* the capture!
        annotation = "%s, %.4f sec" % (timeAnnotate, round(expspeed, 4))
#        camera.annotate_background = Color("black")
#        camera.annotate_text = annotation

        print("Starting capture at %s" % (nowTimeStr))
        print(config)

        outname = "%s/%s.png" % (outloc, nowTimeStr)
        camera.start_and_capture_file(outname, capture_mode=config)
        print("Capture complete!")
        #print(camera.capture_metadata())

        if debug is True:
            print("Captured %s" % (outname))

#        print("Took a %d microseconds exposure." % (camera.exposure_speed))

        # https://github.com/waveform80/picamera/issues/528
#        camera.framerate = 1
        camera.stop()
    else:
        outname = None

    return outname
