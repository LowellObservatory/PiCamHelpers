FROM balenalib/raspberrypi3-python:3.7

USER root

ARG userid="31415"
ARG groupid="31415"
ARG vidid="31415"
ARG i2cid="31415"
ARG spiid="31415"
ARG gpioid="31415"

RUN addgroup --gid ${groupid} lig && \
    adduser lig --uid ${userid} --gid ${groupid} \
    --gecos '' --disabled-password

#RUN addgroup --gid ${vidid} video && \
#RUN addgroup --gid ${i2cid} i2c && \
RUN addgroup --gid ${spiid} spi && \
    addgroup --gid ${gpioid} gpio

RUN usermod -a -G video lig && \
    usermod -a -G i2c lig && \
    usermod -a -G spi lig && \
    usermod -a -G gpio lig

# This updates to the raspberry pi python repo to make sure that we
#   download binaries whenever possible vs. building from source
COPY ./config/pip.conf /etc/pip.conf

RUN apt update && apt install -y libatlas3-base libgfortran5 vim

RUN pip3 install --upgrade pip setuptools
RUN pip3 install matplotlib picamera

USER lig
RUN mkdir /home/lig/www/ && mkdir /home/lig/snaps/ && \
    mkdir /home/lig/snaps/anim/ && mkdir /home/lig/logs

WORKDIR /home/lig/

# NEED TO ADD IN LIGMOS HERE
# NEED TO ADD IN PiCamHelpers pip install here

COPY --chown=lig:lig snapper.py .
COPY --chown=lig:lig streamer.py .

CMD ["python", "snapper.py"]
