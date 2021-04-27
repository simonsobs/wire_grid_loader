#!/bin/python3
import sys, os;
import csv;
import numpy as np;
from matplotlib import pyplot as plt;

outfilename   = './output/test_encoder.png';
inputfilename = './output/test_encoder.dat';

def main () :

    infile = open(inputfilename, 'r');
    reader = csv.reader(infile, delimiter=' ', );
    header = next(reader);
    unixtime  = [];
    error     = [];
    direction = [];
    timercount= [];
    position  = [];
    for row in reader :
        unixtime  .append(int(row[0]));
        error     .append(int(row[1]));
        direction .append(int(row[2]));
        timercount.append(int(row[3]));
        position  .append(int(row[4]));
        pass;
    unixtime   = np.array(unixtime);
    error      = np.array(error);
    direction  = np.array(direction);
    timercount = np.array(timercount);
    position   = np.array(position);
    diff_position = np.diff(position);
    for i, diff in enumerate(diff_position) :
        if diff>40000: diff_position[i] = diff-52000; # 
        pass;

    timercount = timercount  - timercount[0];

    fig, axs = plt.subplots(2,1);
    fig.tight_layout(rect=[0,0,1,1]);
    plt.subplots_adjust(wspace=1,hspace=1,left=0.15,right=0.85,bottom=0.15,top=0.85);

    axs[0].plot(timercount, position);
    axs[1].plot(timercount[1:], diff_position);

    print('save plot to {}.'.format(outfilename));
    plt.savefig(outfilename);

    return 0;



if __name__=='__main__' :
  main();
  pass;
