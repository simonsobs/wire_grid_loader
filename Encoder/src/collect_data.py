from Collector import Collector;

import os, sys;
import numpy as np;
import time;
import struct;


# TODO: TCP is under construction
isTCP = False; # True: TCP / False: UDP

port = 50007;


from constant import *;

from EncoderExtractor import EncoderExtractor;
from IrigExtractor import IrigExtractor;
from TimeoutExtractor import TimeoutExtractor;
from ErrorExtractor import ErrorExtractor;


def collect_data(outfilename) :
  
  collector = Collector(port,isTCP=isTCP);
  time.sleep(1);
  
  outfile_encoder = open(outfilename+'_encoder.dat','w');
  outfile_encoder.write('#TIME ERROR DIRECTION TIMERCOUNT REFERENCE\n');
  outfile_encoder.flush()
  outfile_irig = open(outfilename+'_irig.dat','w');
  outfile_irig.write('#TIMERCOUNT YEAR DAY HOUR MINUTE SECOND\n');
  outfile_irig.flush()
  outfile_timeout = open(outfilename+'_timeout.dat','w');
  outfile_timeout.write('#TIME TYPE\n');
  outfile_timeout.flush()
  outfile_error = open(outfilename+'_error.dat','w');
  outfile_error.write('#TIME ERRORCODE\n');
  outfile_error.flush()

  encoder_header  = 0x1EAF;
  irig_header     = 0xCAFE;
  timeout_header  = 0x1234;
  error_header    = 0xE12A;

  encoder_extractor = EncoderExtractor(encoder_header);
  encoder_bytesize  = encoder_extractor.pi.total_bytesize;
  irig_extractor = IrigExtractor(irig_header);
  irig_bytesize  = irig_extractor.pi.total_bytesize;
  timeout_extractor = TimeoutExtractor(timeout_header);
  timeout_bytesize  = timeout_extractor.pi.total_bytesize;
  error_extractor = ErrorExtractor(error_header);
  error_bytesize  = error_extractor.pi.total_bytesize;

  header_unpack_str = encoder_extractor.pi.header_str;
  header_size       = encoder_extractor.pi.header_num;
  header_bytesize   = encoder_extractor.pi.header_bytesize;

  while True :
    encoder_frames = [];
    irig_frames    = [];
    timeout_frames = [];
    error_frames   = [];
    # Empty the queue and parse its contents appropriately
    approx_size = collector.queue.qsize()
    if approx_size>0 and verbose>0 : print('approximate size = {}'.format(approx_size));
  
    for i in range(approx_size):
      # Block=True : Block execution until there is something in the queue to retrieve
      # timeout=None : the get() command will try indefinitely
      data = collector.queue.get(block=True, timeout=None);
    
      # Once data is extracted from the queue, parse its contents
      # and loop until data is empty
      data_len = len(data);
      if verbose>0 : 
          print('obtained data size = {}'.format(data_len));
          pass;
      parse_index = 0;
      while parse_index < data_len:
          if verbose>0 : print('parse_index = {} / data_len = {}'.format(parse_index, data_len));
          # Extract header
          header = data[parse_index : parse_index + header_bytesize];
          if verbose>0 : 
              if   header!=0 : print('obtained header (size) = {} ({})'.format(header,len(header)));
              elif verbose>1 : print('obtained header (size) = {} ({})'.format(header,len(header)));
              pass;
          # unpack from binary ( byte order: little endian(<), format : L (unsigned long) )
          header = struct.unpack(("%s%s" % (endian, header_unpack_str)), header)[0]
          # Check for Encoder packet
          if header == encoder_header:
              if verbose>0 : print('  header == encoder');
              encoder_frames.append(encoder_extractor.extract(data, parse_index));
              parse_index += encoder_bytesize
          elif header == irig_header:
              if verbose>0 : print('  header == irig');
              irig_frames.append(irig_extractor.extract(data, parse_index));
              parse_index += irig_bytesize
          elif header == timeout_header:
              if verbose>0 : print('  header == timeout');
              timeout_frames.append(timeout_extractor.extract(data, parse_index));
              parse_index += timeout_bytesize
          elif header == error_header:
              if verbose>0 : print('  header == error');
              error_frames.append(error_extractor.extract(data, parse_index));
              parse_index += error_bytesize
          elif header == 0:
              if verbose>1 : print('  header == 0');
              parse_index += header_bytesize
              #break;
          else:
              try :
                raise RuntimeError(("Bad header! This is not encoder/irig/timeout/error header! : %s" % (str(header))))
              except RuntimeError as e:
                  print(e);
                  if verbose>0 :
                    print('###get data###');
                    print(data);
                    print('##############');
                    pass;
                  #sys.exit(-1);
                  break;
                  pass;
              pass;
          pass; # end of ``while parse_index < data_len:``

      # Reset data string
      data = ''
      pass; # end of loop over ``i``

    currenttime = (int)(time.time());
    # write encoder data
    for frame in encoder_frames :
      ncount = len(frame['timercount']);
      for i in range(ncount) :
        outfile_encoder.write('{} {} {} {} {}\n'.format(currenttime, 1-frame['error'][i],frame['quad'][i],frame['timercount'][i],frame['position'][i]));
        pass;
      pass; 
    # write irig data
    for frame in irig_frames :
      outfile_irig.write('{} {} {} {} {} {}\n'.format(frame['timercount'],frame['year'],frame['day'],frame['hour'],frame['minute'],frame['second']));
      pass; 
    # write timeout data
    for frame in timeout_frames :
      outfile_timeout.write('{} {}\n'.format(currenttime, frame['type']));
      pass; 
    # write error data
    for frame in error_frames :
      outfile_error.write('{} {}\n'.format(currenttime, frame['error']));
      pass; 

    # flush output
    outfile_encoder.flush();
    outfile_irig.flush();
    outfile_timeout.flush();
    outfile_error.flush();

    pass; # end of ``while True :``
  
  collector.stop();
  outfile_encoder.close();
  outfile_irig.close();
  outfile_timeout.close();
  outfile_error.close();

  return 0;


if __name__ == '__main__' :
  outfilename = 'aho';
  if len(sys.argv) > 1 : outfilename = sys.argv[1];
  collect_data(outfilename);
  pass;
  


