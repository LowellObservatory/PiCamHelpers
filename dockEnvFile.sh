#/bin/bash
#
#   Bootstrap script to make a docker-compose .env file
#   that will set all of our default/desired variables for runtime.
#   Only works on Linux hosts.
#
#   Created by RTH
#     2018/08/22

# NO COMMAS!!!
#   This list is used to check/make the data storage directories
#services=("chronograf" "influxdb" "telegraf" "lig")
services=("snapper")

# If you're on OS X, `getent` isn't there because Apple didn't invent it,
#   so they instead invented a horribly more complex replacement.
#   I'm sure others have screwed around with `dscl` or whatever to
#   get the equivalent information but I'm not going to.
DCUSERID=`getent passwd $USER | cut -d: -f3`
DCGRPID=`getent passwd $USER | cut -d: -f4`
DCDOCKERID=`getent group docker | cut -d: -f3`
DOCKDATADIR="$HOME/DockerData/"
DOCKDEVDIR="$HOME/DockerDev/"

# Rasperry Pi only!
VIDID=`getent group video | cut -d: -f3`
I2CID=`getent group i2c | cut -d: -f3`
SPIID=`getent group spi | cut -d: -f3`
GPIOID=`getent group gpio | cut -d: -f3`

# Now put it all into the .env file
# Print a header so we know its vintage
echo "# Created on `date -u` by $USER" > .env
echo "#" >> .env
echo "# User/group setup, to keep containers from running as root" >> .env
echo "DCUSERID=$DCUSERID" >> .env
echo "DCGRPID=$DCGRPID" >> .env
echo "DCDOCKERID=$DCDOCKERID" >> .env
echo "DCDATADIR=$DOCKDATADIR" >> .env
echo "DCDEVDIR=$DOCKDEVDIR" >> .env
echo "# Raspberry Pi specific groups" >> .env
echo "VIDID=$VIDID" >> .env
echo "I2CID=$I2CID" >> .env
echo "SPIID=$SPIID" >> .env
echo "GPIOID=$GPIOID" >> .env

echo "./.env contents:"
echo "==========="
cat .env
echo "==========="

echo ""

echo "Checking docker data directories..."

if [ ! -d "$DOCKDATADIR" ]; then
    echo "$DOCKDATADIR doesn't exist!"
    mkdir "$DOCKDATADIR"
    echo "...so I made it good."
else
    echo "$DOCKDATADIR exists! Excellent..."
fi
if [ ! -d "$DOCKDATADIR/logs/" ]; then
    echo "$DOCKDATADIR/logs/ doesn't exist!"
    mkdir "$DOCKDATADIR/logs/"
    echo "...so I made it good."
else
    echo "$DOCKDATADIR/logs exists! Good..."
fi

echo ""

for i in "${services[@]}"
do
    # Check to see if the directories exist in the
    #   already specified $DCDATADIR
    dadir="$DOCKDATADIR/$i"
    if [ -d "$dadir" ]; then
        echo "$dadir is good!"
    else
        mkdir "$dadir"
        echo "...so I made it good."
    fi

    # Now do the same for the log directories
    # Check to see if the directories exist in the
    #   already specified $DCDATADIR

    ldir="$DOCKDATADIR/logs/$i"
    if [ -d "$ldir" ]; then
        echo "$ldir is good!"
    else
        echo "$ldir is nogood!"
        mkdir "$ldir"
        echo "...so I made it good."
    fi

done

# This is the required animation subdirectory for snapper
#   It's bind mounted into the container, so if the anim/ subdir
#   doesn't exist then it'll fail in the container too
animdir="$DOCKDEVDIR/snapper/anim"
if [ -d "$animdir" ]; then
    echo "$animdir is good!"
else
    echo "$animdir is nogood!"
    mkdir "$animdir"
    echo "...so I made it good."
fi

echo ""
echo "========== NOTE =========="
echo "If any directories are missed and docker creates"
echo "them at runtime, they'll get created as root:root"
echo "and everything will end in tears."
echo ""
echo "Same is true if there are any mkdir errors up there!"
echo "========== NOTE =========="
echo ""

echo "Done! You can now use 'docker-compose ...' as usual."
