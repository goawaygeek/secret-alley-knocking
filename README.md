# how to setup Rat Video installation Pi controller from scratch

Things you'll need:
- A Raspberry Pi (we're moving this onto a Pi 5)
- A motion sensor
- A continuous servo
- A standard 180 degree servo
- connection wire
- power supply
- Mini HDMI -> HDMI cable or converter
- a micro SD card

## Step 1 - installing the OS on the micro SD card

Use the Raspberry Pi installer software to create an OS image on the pi.  You'll want to go into settings and configure it so that you can SSH into the Pi once it boots with a username a password of your choice.  The one we're setting up today is 
Device: rat-vid-5.local
U/N: alley
P/W: alleyalley

## Step 2 - setup the pi to boot into the command line

You'll want to SSH into the pi using the details above (ssh alley@rat-vid-5.local).  Then once you're in there load the `raspi-config` and change the boot options: System Options>Boot / Auto Login>Console Autologin

# Step 3 - move all the required files onto the pi

Once the Pi has rebooted use the details above and an SFTP connection to move all the files across.  You'll be moving across:
 - motion.py
 - load.py
 - loop.mp4
 - rats.mp4

 To make things easier for myself I create a directory called /rats and load them into there.

# Step 4 - download dependencies

You're going to want to SSH onto the pi again and download all the libraries needed to run the motion.py file.  The latest version of the Raspberry Pi OS are externally managed and the standard GPIO python library doesn't want to work.  So you're going to want to use sudo apt remove to get rid of the old GPIO library and then use pip with the --break-system-packages flag for the dropin replacement of the new GPIO  and Qhue libraries.

sudo apt remove python3-rpi.gpio
sudo pip3 install rpi-lgpio --break-system-packages
python3 -m pip install qhue --break-system-packages


# Step 5 - wire up the servo and motion sensor

I've included an image of the Pi's GPIO pin breakout in the repo.  You're going to want to make the following hookup:

- standard 180 servo to Pin 18
- continuous servo to pin 17
- motion sensor to pin 23

The standard servo will go to 3.3V power and the other two to 5v

# Step 6 - confirm the Que settings

Here's the documentation for the Que PyPi install: https://pypi.org/project/qhue/ 

Setting up the Hue lights was a bit annoying.  Here's some links to pages that showed us what we needed to do.  
- https://www.hackster.io/ben-eagan/haunted-home-automation-a870fb
- https://developers.meethue.com/develop/get-started-2/

it involves setting up a developer account (on the hue page) and then using that to obtain the details for your lights.  If our local network ever goes down again we're going to have to go through the process of remapping these lights.  The details are currenly hard coded into the motion.py code.  Let's hope they don't change!  A BIG update to this would be using something like an ESP32 to control the lights and act as a physical switch to turn them on an off but that's probably overkill for our situation.

# Step 7 - set the script up so it runs on load.

We're simply adding a couple of lines to the .bash-rc file located at the users home directory.  Ssh into the machine again, in the home direcotry (where you should be once you login but you can confirm by typing `cd ~`) you want to run the command `sudo nano .bashrc` which will open the file in an editory.  Within that file go all the way down the bottom of the file and add the following lines:

```
clear
python ~/rats/motion.py
```
The first line clears the screen and the second starts the python script.

Save the file and you should be ready to go.


# Step 8 - test the script!

If everything has been done correctly the pi should now be in a mode where it can boot and play the script, you're ready to go!

Here are some common errors:
- the path to the video files have changed, they're hard coded into Motion.py and have to be full paths, if you've changed a user name or a directory name they're going to be wrong and you won't get any warnings.
- knocking or servoes aren't working: the connections for the components likely aren't hooked up properly, make sure you have everything hooked up properly
- There's no audio! Usually this is an HDMI issue, make sure you have an HDMI splitter that handles audio.  If it is more than that then you're going to want to start diving down some of these forum posts: https://forums.raspberrypi.com/viewtopic.php?t=373348 it looks like the pi5 made some significant changes to the way it handles audio as there's no audio jack anymore.

Remember, this code and these instructions were written for a Raspberry Pi 5 running the (at the time) latest version of the Raspberrian OS (Debian Bookworm released on 2024-07-04) if you're running something else there might be issues!

