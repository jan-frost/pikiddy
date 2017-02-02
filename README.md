# pikiddy

## Installation

sudo apt-get update
sudo apt-get install python-pip git libsdl-dev libsdl-image1.2-dev libsdl-mixer1.2-dev libsdl-ttf2.0-dev libsmpeg-dev libportmidi-dev libavformat-dev libswscale-dev python-dev

sudo apt-get install evtest tslib libts-bin
https://learn.adafruit.com/adafruit-pitft-28-inch-resistive-touchscreen-display-raspberry-pi/pitft-pygame-tips

install fbcp
https://github.com/notro/fbtft/wiki/Framebuffer-use

pip installation
	sudo apt-get install python-pip 

pygame installation
	sudo apt-get install libsdl-dev libsdl-image1.2-dev libsdl-mixer1.2-dev libsdl-ttf2.0-dev 
	sudo apt-get install libsmpeg-dev libportmidi-dev libavformat-dev libswscale-dev
	sudo apt-get install python-dev
	sudo pip install pygame
	sudo pip install pygameui
	sudo pip install eyeD3
	
git clone http://www.github.com/jhfrost/pikiddy.git
	
Enabling and disabling the splash screen is with some extra arguments in /boot/cmdline.txt – 
if this line includes “quiet splash”, the splash screen is shown; 
if it does not include those words, the old text-based boot is shown.
