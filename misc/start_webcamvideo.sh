#!/bin/bash

WIDTH=500; # 1920;
HEIGHT=1000; # 1080;
BRIGHTNESS=100;
BRIGHTNESSAUTO=1;
CONTRAST=100;
SATURATION=300;
HUE=0;
HUEAUTO=1;
WHITEAUTO=1;
GAIN=100;
GAINAUTO=1;
SHARPNESS=100;
ROTATE=0;

# VLC options (vlc -H --advanced)
# vlc video options
# Video capture controls (if supported by the device)
# --v4l2-controls-reset, --no-v4l2-controls-reset 
# Reset controls (default disabled)
# Reset controls to defaults. (default disabled)
# --v4l2-brightness <integer [-2147483648 .. 2147483647]> 
# Brightness
# Picture brightness or black level.
# --v4l2-brightness-auto {-1 (Unspecified), 0 (Off), 1 (On)} 
# Automatic brightness
# Automatically adjust the picture brightness.
# --v4l2-contrast <integer [-2147483648 .. 2147483647]> 
# Contrast
# Picture contrast or luma gain.
# --v4l2-saturation <integer [-2147483648 .. 2147483647]> 
# Saturation
# Picture saturation or chroma gain.
# --v4l2-hue <integer [-2147483648 .. 2147483647]> 
# Hue
# Hue or color balance.
# --v4l2-hue-auto {-1 (Unspecified), 0 (Off), 1 (On)} 
# Automatic hue
# Automatically adjust the picture hue.
# --v4l2-white-balance-temperature <integer [-1 .. 6500]> 
# White balance temperature (K)
# White balance temperature as a color temperation in Kelvin (2800 is minimum incandescence, 6500 is maximum daylight).
# --v4l2-auto-white-balance {-1 (Unspecified), 0 (Off), 1 (On)} 
# Automatic white balance
# Automatically adjust the picture white balance.
# --v4l2-red-balance <integer [-2147483648 .. 2147483647]> 
# Red balance
# Red chroma balance.
# --v4l2-blue-balance <integer [-2147483648 .. 2147483647]> 
# Blue balance
# Blue chroma balance.
# --v4l2-gamma <integer [-2147483648 .. 2147483647]> 
# Gamma
# Gamma adjust.
# --v4l2-autogain {-1 (Unspecified), 0 (Off), 1 (On)} 
# Automatic gain
# Automatically set the video gain.
# --v4l2-gain <integer [-2147483648 .. 2147483647]> 
# Gain
# Picture gain.
# --v4l2-sharpness <integer [-2147483648 .. 2147483647]> 
# Sharpness
# Sharpness filter adjust.
# --v4l2-chroma-gain <integer [-2147483648 .. 2147483647]> 
# Chroma gain
# Chroma gain control.
# --v4l2-chroma-gain-auto <integer [-2147483648 .. 2147483647]> 
# Automatic chroma gain
# Automatically control the chroma gain.
# --v4l2-power-line-frequency {-1 (Unspecified), 0 (Off), 1 (50 Hz), 2 (60 Hz), 3 (Automatic)} 
# Power line frequency
# Power line frequency anti-flicker filter.
# --v4l2-backlight-compensation <integer [-2147483648 .. 2147483647]> 
# Backlight compensation
# Backlight compensation
# --v4l2-band-stop-filter <integer [-2147483648 .. 2147483647]> 
# Band-stop filter
# Cut a light band induced by fluorescent lighting (unit undocumented).
# --v4l2-hflip, --no-v4l2-hflip 
# Horizontal flip (default disabled)
# Flip the picture horizontally. (default disabled)
# --v4l2-vflip, --no-v4l2-vflip 
# Vertical flip (default disabled)
# Flip the picture vertically. (default disabled)
# --v4l2-rotate <integer [-1 .. 359]> 
# Rotate (degrees)
# Picture rotation angle (in degrees).
# --v4l2-color-killer {-1 (Unspecified), 0 (Off), 1 
 

vlc v4l:// :v4l-vdev="/dev/video0"  \
	--v4l2-width $WIDTH \
	--v4l2-height $HEIGHT \
	--v4l2-brightness $BRIGHTNESS  \
	--v4l2-brightness-auto $BRIGHTNESSAUTO \
	--v4l2-contrast $CONTRAST \
	--v4l2-saturation $SATURATION \
	--v4l2-hue $HUE \
	--v4l2-hue-auto $HUEAUTO \
	--v4l2-auto-white-balance $WHITEAUTO \
	--v4l2-gain $GAIN \
	--v4l2-autogain $GAINAUTO \
	--v4l2-sharpness $SHARPNESS \
	--rotate-angle $ROTATE \

    # Alternative option for rotation
	#--no-autoscale \
	#--aspect-ratio 16:9 \
