import os
import sys
import socket
import numpy as np
import pandas as pd
from datetime import datetime, timezone, timedelta

PRU_Clock_Counts = 200e6
Deg = 360/52000

UTC = timezone(timedelta(hours=+0), 'UTC')
JST = timezone(timedelta(hours=+9), 'JST')

def main(data_filename, start_line=0, isUTC=False):
    # start_line is the initial line number of the operating item you want to check in the item file

    if isUTC == True:
        now = datetime.now(UTC)
        pass
    else:
        now = datetime.now(JST)
        pass
    log_filename = 'PMX_' + now.strftime('%Y-%m-%d') + '.dat'
    item_filename = 'items_' + now.strftime('%Y-%m-%d') + '.dat'
    filelists = openlog('calibration_filelists.txt', verbose=1)
    filelists.write(f'{data_filename} {log_filename} {item_filename}')
    filelists.close()

    hostname = socket.gethostname();
    print('hostname : {}'.format(hostname));
    if hostname.endswith('wiregridpc-NUC7PJYH'):
        data_filepath = '../Encoder/Beaglebone/' + data_filename
        log_filepath = './log_ether/' + log_filename
        item_filepath = './item/' + item_filename
        pass
    else:
        data_filepath = './' + data_filename
        log_filepath = './' + log_filename
        item_filepath = './' + item_filename

    # define several parameters
    pack_size = 1
    capture_slice = 500

    plot_slice = 30
    capture_slice = 500
    capture_offset = 4

    cut_threshold = 2.3

    iteration = 100
    list_amp = [3.0]
    list_intv = ['0.100', '0.120', '0.140', '0.160', '0.180', '0.200', '0.220', '0.240', '0.260', '0.280', '0.300']
    matrix_size = 11

    # input log and data
    df = define_data_region(item_filepath, log_filepath, start_line)
    time_category0, error0, direction0, timercount0, reference0 = np.loadtxt(data_filepath, comments='#', unpack=True)

    reference = reference0
    ref_tmp = np.where(reference0 > 52000)[0]
    for i in ref_tmp:
        reference[i] = reference0[i]-62000

    # devide into block
    swt, inits, end = packet_capture(df, list_amp, list_intv, time_category0, isUTC, iteration, pack_size, capture_slice, capture_offset)

    time_block, reference_block, lincount_block, block_initials, onecycle_time, proceeded_degrees = devide_by_operation(timercount0, reference, swt, inits, end, matrix_size, iteration, capture_slice, capture_offset)

    error_position = error_subtraction(matrix_size, iteration, time_block, block_initials, cut_threshold, lincount_block, plot_slice)

    moved_angle, start_position = get_position_angle(time_block, lincount_block, block_initials, error_position, matrix_size, iteration, cut_threshold)

    # get feedback values
    movDeg_mean = []
    movDeg_stdv = []

    for i in range(matrix_size):
        movDeg_mean.append(np.mean(moved_angle[i]))
        movDeg_stdv.append(np.std(moved_angle[i]))
        pass

    try:
        commanded_value = set_feedback_value(movDeg_mean, 5)
    except ValueError:
        commanded_value = set_feedback_value(movDeg_mean,4)
        commanded_value.append(0.301)
        pass

    return commanded_value

def define_data_region(item_filepath, log_filepath, start_line=0):
    item = 'calibration'

    item_df = pd.read_csv(item_filepath, delim_whitespace=True)
    if start_line == 0:
        start_line = np.where(item_df.iloc[:,2] == item)[0][-2]
        pass
    else:
        pass
    start_at = item_df[item_df.iloc[:,2] == item].iloc[:,0].to_numpy()[start_line] + ' ' + item_df[item_df.iloc[:,2] == item].iloc[:,1].to_numpy()[start_line]
    stop_at = item_df[item_df.iloc[:,2] == item].iloc[:,0].to_numpy()[start_line + 1] + ' ' + item_df[item_df.iloc[:,2] == item].iloc[:,1].to_numpy()[start_line + 1]

    df0 = pd.read_csv(log_filepath, delim_whitespace=True)
    start_slice = np.where(start_at == df0.iloc[:,0].to_numpy()+' '+df0.iloc[:,1].to_numpy())[0][0]
    stop_slice = np.where(stop_at == df0.iloc[:,0].to_numpy()+' '+df0.iloc[:,1].to_numpy())[0][0]

    df = df0[start_slice:stop_slice]
    return df

def packet_capture(dataframe, list_ampere, list_interval, UnixTime_Data, isUTC, iteration=100, pack_size=1, capture_slice=500, capture_offset=4):
    UTC = timezone(timedelta(hours=+0), 'UTC')
    JST = timezone(timedelta(hours=+9), 'JST')
    initial_UnixTime = []
    switching_UnixTime = []
    start_UnixTime = []

    for i in range(iteration):
        start_UnixTime.append([])

    for i in list_ampere:
        for j in list_interval:
            list_datetime = ((dataframe[dataframe.iloc[:,5] == i])[(dataframe[dataframe.iloc[:,5] == i]).iloc[:,8] == j]).iloc[:,0:2].to_numpy()
            for k in range(len(list_datetime)):
                if k%pack_size == 0:
                    if isUTC == True:
                        start_UnixTime[int(k/pack_size)] = (((datetime.strptime(list_datetime[k][0]+' '+list_datetime[k][1],"%Y-%m-%d %H:%M:%S-%Z")).replace(tzinfo=timezone.utc)).astimezone(UTC)).timestamp()
                        pass
                    else:
                        start_UnixTime[int(k/pack_size)] = (((datetime.strptime(list_datetime[k][0]+' '+list_datetime[k][1],"%Y-%m-%d %H:%M:%S-%Z")).replace(tzinfo=timezone.utc)).astimezone(JST)).timestamp()
                        pass
                    initial_UnixTime = np.append(initial_UnixTime, start_UnixTime[int(k/pack_size)])
                    pass
                pass
            switching_UnixTime.append(min(start_UnixTime))
            pass
        pass

    stop_UnixTime = dataframe[dataframe.iloc[:,2] == 'OFF'].iloc[-1,:]
    if isUTC == True:
        end_UnixTime = (((datetime.strptime(stop_UnixTime[0]+' '+stop_UnixTime[1],"%Y-%m-%d %H:%M:%S-%Z")).replace(tzinfo=timezone.utc)).astimezone(UTC)).timestamp()
        pass
    else:
        end_UnixTime = (((datetime.strptime(stop_UnixTime[0]+' '+stop_UnixTime[1],"%Y-%m-%d %H:%M:%S-%Z")).replace(tzinfo=timezone.utc)).astimezone(JST)).timestamp()
        pass

    captured_initials = []
    captured_switching = []

    for i in range(len(switching_UnixTime)):
        captured_switching.append(max(np.where(UnixTime_Data[::capture_slice] <= switching_UnixTime[i])[0]))
        pass

    for i in range(len(initial_UnixTime)):
        captured_initials.append(max(np.where(UnixTime_Data[::capture_slice] <= initial_UnixTime[i])[0]))
        pass

    captured_end = min(np.where(end_UnixTime + capture_offset <= UnixTime_Data[::capture_slice])[0])

    return captured_switching, captured_initials, captured_end

def devide_by_operation(timercount, reference, switching_time, initial_time, end_UnixTime, matrix_size=11, iteration=100, capture_slice=500, capture_offset=4):
    time = timercount/PRU_Clock_Counts
    time_block = []
    reference_block = []

    for i in range(len(switching_time)-1):
        slice0 = int(np.where(time == (time[::capture_slice])[switching_time[i]-capture_offset])[0])
        slice1 = int(np.where(time == (time[::capture_slice])[switching_time[i+1]-capture_offset])[0])
        time_block.append(time[slice0:slice1])
        reference_block.append(reference[slice0:slice1])
        pass
    time_block.append(time[int(np.where(time == (time[::capture_slice])[switching_time[-1]-capture_offset])[0])
                                                     :int(np.where(time == (time[::capture_slice])[end_UnixTime+capture_offset])[0])])
    reference_block.append(reference[int(np.where(time == (time[::capture_slice])[switching_time[-1]-capture_offset])[0])
                                     :int(np.where(time == (time[::capture_slice])[end_UnixTime+capture_offset])[0])])

    lincount_block = []
    block_initials = []
    onecycle_time = []
    proceeded_degrees = []
    casp_threshold = -100

    for i in range(matrix_size):
        lincount_block.append([])
        lincount_block[i] = np.array(np.zeros(len(reference_block[i])))

        count_offset = 0
        casp_flag = 0
        casp = np.where(np.diff(reference_block[i]) <= casp_threshold)[0].tolist()

        for j in range(len(reference_block[i])):
            lincount_block[i][j] = reference_block[i][j]+count_offset
            if casp:
                if j == casp[casp_flag]:
                    count_offset += reference_block[i][casp[casp_flag]]
                    if len(casp) > casp_flag+1:
                        casp_flag += 1
                        pass
                    pass
                pass
            pass

        block_initials.append([])
        for j in range(iteration):
            block_initials[i].append(int(np.where(time_block[i] == (time[::capture_slice])[(initial_time[i*iteration:(i+1)*iteration])[j]-capture_offset])[0]))
            pass

        onecycle_time.append([])
        proceeded_degrees.append([])
        for j in range(iteration):
            if j != iteration - 1:
                onecycle_time[i].append(time_block[i][block_initials[i][j+1]]-time_block[i][block_initials[i][j]])
                proceeded_degrees[i].append((lincount_block[i][block_initials[i][j+1]]-lincount_block[i][block_initials[i][j]])*Deg)
                pass
            else:
                onecycle_time[i].append(time_block[i][-1]-time_block[i][block_initials[i][j]])
                proceeded_degrees[i].append((lincount_block[i][-1]-lincount_block[i][block_initials[i][j]])*Deg)
            pass
        pass
    return time_block, reference_block, lincount_block, block_initials, onecycle_time, proceeded_degrees

def error_subtraction(matrix_size, iteration, time_block, block_initials, cut_threshold, lincount_block, plot_slice):
    ref_threshold = 100
    error_pack = []

    for i in range(matrix_size):
        except_sum = []
        except_sum.append(i)
        for j in range(iteration):
            if j != iteration - 1:
                tmp_timeblock = time_block[i][block_initials[i][j]:block_initials[i][j+1]]-time_block[i][block_initials[i][j]]
                place = min(np.where(tmp_timeblock >= cut_threshold)[0])
                except_ref = np.where(np.diff((lincount_block[i][block_initials[i][j]:block_initials[i][j] + place])[::plot_slice]) > ref_threshold)[0]
                pass
            else:
                tmp_timeblock = time_block[i][block_initials[i][j]:-1]-time_block[i][block_initials[i][j]]
                place = min(np.where(tmp_timeblock >= cut_threshold)[0])
                except_ref = np.where(np.diff((lincount_block[i][block_initials[i][j]:block_initials[i][j] + place])[::plot_slice]) > ref_threshold)[0]
                pass
            if except_ref:
                except_sum.append(j)
            pass
        if len(except_sum) < 2:
            del except_sum[0]
            pass
        if except_sum:
            error_pack.append(except_sum)
            pass
        pass

    if not error_pack:
        error_pack = [[0]]

    error_position = []
    error_flag0 = 0
    error_flag2 = 0

    for i in range(matrix_size):
        error_flag1 = 1
        error_position.append([])
        for j in range(iteration):
            if i == error_pack[error_flag0][0]:
                if error_flag1 <= len(error_pack[error_flag0])-1:
                    if j == error_pack[error_flag0][error_flag1]:
                        error_position[i].append([])
                        error_position[i][j] = False
                        error_flag1 += 1
                        error_flag2 = 1
                        pass
                    else:
                        error_position[i].append([])
                        error_position[i][j] = True
                        pass
                    pass
                else:
                    error_position[i].append([])
                    error_position[i][j] = True
                    pass
                pass
            else:
                error_position[i].append([])
                error_position[i][j] = True
                pass
            pass
        if error_flag2 == 1:
            if error_flag0 != len(error_pack)-1:
                error_flag0 += 1
                error_flag2 = 0
                pass
            pass
        pass
    return error_position

def get_position_angle(time_block, lincount_block, block_initials, error_position, matrix_size=11, iteration=100, cut_threshold=2.3):
    moved_angle = []
    start_position = []

    for i in range(matrix_size):
        moved_angle.append([])
        start_position.append([])
        for j in range(iteration-1):
            if error_position[i][j] != False:
                if j != iteration - 1:
                    tmp_timeblock = time_block[i][block_initials[i][j]:block_initials[i][j+1]]-time_block[i][block_initials[i][j]]
                    place = min(np.where(tmp_timeblock >= cut_threshold)[0])
                    moved_angle[i].append((lincount_block[i][block_initials[i][j] + place]-lincount_block[i][block_initials[i][j]])*Deg)
                    start_position[i].append(lincount_block[i][block_initials[i][j]]%52000*Deg)
                    pass
                else:
                    tmp_timeblock = time_block[i][block_initials[i][j]:-1]-time_block[i][block_initials[i][j]]
                    place = min(np.where(tmp_timeblock >= cut_threshold)[0])
                    moved_angle[i].append((lincount_block[i][block_initials[i][j] + place]-lincount_block[i][block_initials[i][j]])*Deg)
                    start_position[i].append(lincount_block[i][block_initials[i][j]]%52000*Deg)
                pass
            pass
        pass
    return moved_angle, start_position

def set_feedback_value(mean_deg_list, deg_range):
    commanded_list = np.arange(0.101, 0.321, 0.02)
    commanded_value = []

    for i in range(deg_range):
        dist0 = (i+1) - mean_deg_list[commanded_list.tolist().index(max(commanded_list[np.array(mean_deg_list) < (i+1)]))]
        dist1 = mean_deg_list[commanded_list.tolist().index(min(commanded_list[np.array(mean_deg_list) > (i+1)]))] - (i+1)
        if (np.abs(dist1 - dist0) > 0.5) & (np.sign(dist1 - dist0) == 1.0):
            candidate0 = round(max(commanded_list[np.array(mean_deg_list) < (i+1)]),3)
            pass
        elif (np.abs(dist1 - dist0) > 0.5) & (np.sign(dist1 - dist0) == -1.0):
            candidate0 = round(min(commanded_list[np.array(mean_deg_list) > (i+1)]),3)
            pass
        else:
            candidate0 = round((min(commanded_list[np.array(mean_deg_list) > (i+1)]) + max(commanded_list[np.array(mean_deg_list) < (i+1)]))/2,3)
            pass
        commanded_value.append(candidate0)
        pass

    return commanded_value

def writelog(logfile, fb_amount, isUTC=False):
    if isUTC == True:
        now = datetime.now(UTC)
        pass
    else:
        now = datetime.now(JST)
        pass
    nowStr  = now.strftime('%Y/%m/%d_%H:%M:%S-%Z')
    log = ('{} {} {} {} {} {}\n'.format(nowStr, fb_amount[0], fb_amount[1], fb_amount[2], fb_amount[3], fb_amount[4]))
    logfile.write(log)
    pass

def openlog(logfilename, verbose=0):
    if os.path.exists(logfilename) :
        logfile = open(logfilename, 'a+')
    else :
        logfile = open(logfilename, 'w' )
        if verbose == 0:
            log = '#Date_Time-Timezone Feedback_amount\n'
            pass
        else:
            log = '#data_file log_file item_file'
            pass
        logfile.write(log)
        pass
    return logfile

def parseCmdLine(args):
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option('-s', '--start_line', dest='start_line', help='start_line is the initial line number of the operating item you want to check in the item file', type=int, default=0)
    parser.add_option('-i', '--isUTC', action="store_true", dest='is_UTC', help='TimeZone False: JST, True: UTC, default is False', default=False)
    parser.add_option('--datafile',dest='data_file_name')
    (config, args) = parser.parse_args(args)
    return config

if __name__ == '__main__':
    config = parseCmdLine(sys.argv)
    start_line = config.start_line
    isUTC = config.is_UTC
    data_filename = config.data_file_name

    if not sys.argv:
        start_line = 0
        isUTC = False

    commanded_value = main(data_filename, start_line, isUTC)
    logfile = openlog('feedback_amount.txt')
    writelog(logfile, commanded_value, isUTC)
    logfile.close()
    print('Completed!')
