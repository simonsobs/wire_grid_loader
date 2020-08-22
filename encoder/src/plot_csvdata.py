#!/bin/python3

import matplotlib.pyplot as plt
import numpy
import pandas as pd


df = pd.read_csv('aho.txt',sep=' ',header=None,
    skiprows = lambda x : x%100!=0, nrows=1e+5 );
print(df);

starttime = df[2][0];
clk = df[2] - starttime;
clk = (clk)/200.e+6; # 200MHz clock
print(clk);

plt.figure(figsize=(100,4.8),dpi=100);
plt.plot(clk,df[1],linestyle='', marker='.',markersize=1,color='k');
plt.grid(True);
plt.savefig('aho.pdf');

