#!/bin/python3
import sys, os;
import csv;
import numpy as np;
from matplotlib import pyplot as plt;
from matplotlib import ticker;

inputfilename0 = './output/test_encoder.dat';
outputfilename0   = './output/test_encoder.png';

clock_freq = 200e+6;

def main (inputfilename, outputfilename) :

    print('open '+inputfilename);
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
    diff_timer = np.diff(timercount);
    timercount = np.array(timercount)/float(clock_freq);
    position   = np.array(position);
    diff_position = np.diff(position);
    for i, diff in enumerate(diff_position) :
        #if diff<=-50000: diff_position[i] = -1.; # 
        pass;

    timercount = timercount  - timercount[0];

    fig, axs = plt.subplots(10,1);
    fig.tight_layout(rect=[0,0,1,1]);
    plt.subplots_adjust(wspace=1,hspace=1,left=0.15,right=0.95,bottom=0.05,top=0.95);
    fig.set_size_inches(8,30);

    axs[0].scatter(timercount, position,marker='o',s=5.0,color='tab:blue');
    axs[1].scatter(timercount[1:], diff_position,marker='o',s=5.0,color='tab:blue');
    axs[2].scatter(timercount[1:], diff_position,marker='o',s=5.0,color='tab:blue');
    axs[3].scatter(timercount[1:], diff_timer   ,marker='o',s=5.0,color='tab:blue');
    axs[4].scatter(timercount[1:], diff_timer   ,marker='o',s=5.0,color='tab:blue');
    axs[5].scatter(diff_timer    , diff_position,marker='o',s=5.0,color='tab:blue');

    # selection of large diff position
    outliercut =   1e+6; # in diff. of timercount
    is_outlier = (diff_timer>outliercut);
    index_outlier = np.array([i for i in range(len(is_outlier))])[is_outlier];
    diff_index_outlier = np.diff(index_outlier);
    diff_position_outlier = diff_position[is_outlier];
    timercount_outlier    = timercount[1:];
    timercount_outlier    = timercount_outlier[is_outlier];
    print('timercount_outlier = {}'.format(timercount_outlier));
    diff_timer_outlier    = np.diff(timercount_outlier);
    axs[6].scatter(index_outlier[1:], diff_index_outlier,marker='o',s=5.0,color='tab:blue');
    axs[7].scatter(timercount_outlier[1:], diff_timer_outlier,marker='o',s=5.0,color='tab:blue');

    axs[0].set_title('Position [counts]');
    axs[0].set_xlabel('Time [sec]');
    axs[0].set_ylabel('Position Counts [pulse counts]');

    axs[1].set_title('Difference from previous counts');
    axs[1].set_xlabel('Time [sec]');
    axs[1].set_ylabel('Counts Difference [pulse counts]');
    axs[1].grid(True);

    axs[2].set_title('Difference from previous counts');
    axs[2].set_xlabel('Time [sec]');
    axs[2].set_ylabel('Counts Difference [pulse counts]');
    #axs[2].set_xlim(0.,1.);
    axs[2].set_ylim(1.,max(diff_position)*1.2);
    axs[2].grid(True);
    pmin = 1.;
    pmax = max(diff_position);
    yticks = np.logspace(1,20,20);
    ytickslim = yticks[(yticks>pmin) & (yticks<pmax)];
    axs[2].yaxis.set_ticks(ytickslim);

    axs[3].set_title('Time Difference');
    axs[3].set_xlabel('Time [sec]');
    axs[3].set_ylabel('Time Difference [clock counts]');
    axs[3].set_yscale('log');
    axs[3].grid(True);
    tmin = min(diff_timer);
    tmax = max(diff_timer);
    yticks = np.logspace(1,20,20);
    ytickslim = yticks[(yticks>=tmin*0.9) & (yticks<=tmax*1.1)];
    axs[3].yaxis.set_ticks(ytickslim);
    
    axs[4].set_title('Time Difference [Short period (1 sec)]');
    axs[4].set_xlabel('Time [sec]');
    axs[4].set_ylabel('Time Difference [clock counts]');
    axs[4].set_xlim(0.,1.);
    axs[4].set_ylim(min(diff_timer)*0.5,max(diff_timer)*2.);
    axs[4].set_yscale('log');
    axs[4].grid(True);
    
    axs[5].set_title('Time diff v.s. Counts diff');
    axs[5].set_xlabel('Time Difference [clock counts]');
    axs[5].set_ylabel('Counts Difference [pulse counts]');
    ymax = max(diff_position);
    ymax = ymax if ymax>0. else 1.;
    axs[5].set_ylim(0.,ymax*1.2);
    axs[5].set_xlim(0.,max(diff_timer)*1.2);
    axs[5].set_xscale('log');
    axs[5].grid(True);
    axs[5].set_xlim(min(diff_timer),max(diff_timer));

    axs[6].set_title('Outlier (diff. counts>{})'.format(outliercut));
    axs[6].set_xlabel('Index');
    axs[6].set_ylabel('Index Difference btw Outliers');
    ymin = min(diff_index_outlier) if len(diff_index_outlier)>0 else 0.;
    ymax = max(diff_index_outlier) if len(diff_index_outlier)>0 else 1.;
    print('diff_index_outlier = {} ~ {}'.format(ymin, ymax));
    axs[6].set_ylim(ymin*0.8,ymax*1.2);
    axs[6].grid(True);

    axs[7].set_title('Outlier (diff. counts>{})'.format(outliercut));
    axs[7].set_xlabel('Time [sec]');
    axs[7].set_ylabel('Time Difference btw Outliers [sec]');
    ymin = min(diff_timer_outlier) if len(diff_timer_outlier)>0 else 0.;
    ymax = max(diff_timer_outlier) if len(diff_timer_outlier)>0 else 1.;
    print('diff_timer_outlier = {} ~ {}'.format(ymin, ymax));
    axs[7].set_ylim(ymin*0.8,ymax*1.2);
    yticks = np.linspace(0,1,51);
    ytickslim = yticks[(yticks>=ymin*0.5) & (yticks<=ymax*1.5)];
    print(ytickslim);
    axs[7].yaxis.set_ticks(ytickslim);
    axs[7].grid(True);
 

    print('save plot to {}.'.format(outputfilename));
    plt.savefig(outputfilename);

    return 0;



if __name__=='__main__' :
  inputfilename  = inputfilename0;
  outputfilename = outputfilename0;
  if len(sys.argv)>1 :
    inputfilename = sys.argv[1];
    outputfilename= '.'.join(inputfilename.split('.')[:-1]) + '.png';
    pass;
  if len(sys.argv)>2 :
    outputfilename = sys.argv[2];
    pass;
  main(inputfilename, outputfilename);
  pass;
