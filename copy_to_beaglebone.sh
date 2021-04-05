#!/bin/bash
rsync -ruvvva --exclude=".*/" ./* beaglebone62:/home/debian/scripts/wire_grid_loader/
rsync -ruvvva --exclude=".*/" ./* beaglebone72:/home/debian/scripts/wire_grid_loader/
