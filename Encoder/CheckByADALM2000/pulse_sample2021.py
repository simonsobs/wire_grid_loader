#this is a digital pulse generator sample for counts test of encoder signal

import math
import time
import numpy as np

import libm2k

DigitalChannels = 16                    # All digital channels in ADALM
channels = [0,1,2]                      # channels in use
samplerate = 8e+5                      # sampling rate [Hz]
timeperiod = [1e-5, 1e-5, 0.01]        # periods [sec]
duty = [0.5, 0.5, 25e-5]                 # duty of waveform
timeoffset = [0.0, 0.25e-5, -0.375e-5]       # offset of each wave, see below
repeats = 3

def ConnectADALM(ctx = None):
    if ctx is None:
        ctx = libm2k.m2kOpen()
        if ctx is None:
            print("Connection Error: No ADALM2000 device available/connected to your PC.")
            exit(1)
            pass
        ctx.calibrateADC()
        ctx.calibrateDAC()
        pass
    return ctx

def MakeWave(
    digital_channels = 16,
    channels = [0,1,2],
    sample_rate = 8e+5,
    time_period = [1e-5, 1e-5, 0.01],
    duty = [0.5, 0.5, 25e-5],
    time_offset = [0.0, 0.25e-5, 0.0]
    ):
    array_length = int(max(time_period) * sample_rate)
    buffer_array = []
    for ch in range(digital_channels):
        if not ch in channels:
            buffer_array.append(np.zeros(array_length, dtype=int))
            continue
        PointsInPeriod = int(time_period[ch] * sample_rate)
        PointsON = int(time_period[ch] * sample_rate * duty[ch])
        PointsOFF = int((PointsInPeriod - PointsON) * 0.5)

        waveformON = [0b1]*PointsON
        waveformOFF = [0b0]*PointsOFF
        waveform = np.concatenate([waveformOFF, waveformON])
        waveform = np.concatenate([waveform, waveformOFF])
        #print(len(waveform))

        if time_offset[ch] != 0.0: # look here about time_offset
            waveform = np.roll(waveform, int(time_offset[ch]*sample_rate))
            pass

        waveform = np.tile(waveform, math.ceil(max(time_period)/time_period[ch]))

        buffer_array.append(waveform)
        pass

    buffer_bits = np.zeros(array_length, dtype=int)
    for i, t in enumerate(buffer_array):
        buffer_bits[:] = buffer_bits[:] + (t << i)
        pass

    return buffer_bits.tolist()

def PushWave(ctx, buffer_bits, digital_channels=16, channels=[0,1,2], sample_rate=8e+5):
    dig = ctx.getDigital()
    for ch in range(digital_channels):
        dig.enableChannel(ch, False)
        dig.setValueRaw(ch, 0)
        pass

    dig.setCyclic(False)

    for ch in channels:
        dig.setDirection(ch, libm2k.DIO_OUTPUT)
        dig.enableChannel(ch, True)
        pass
    dig.setSampleRateIn(sample_rate)
    dig.setSampleRateOut(sample_rate)

    dig.push(buffer_bits)

    return ctx

if __name__=='__main__':
    ctx = ConnectADALM()
    buffer_bits = MakeWave(DigitalChannels, channels, samplerate, timeperiod, duty, timeoffset)

    for i in range(repeats):
        ctx = PushWave(ctx, buffer_bits, DigitalChannels, channels, samplerate)
        print("this is the {}th time.".format(i+1))
        time.sleep(20)
        pass

    libm2k.contextClose(ctx)
