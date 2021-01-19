from Collector import Collector;

import os, sys;
import numpy as np;
import time;
import struct;
import signal;
# end process for kill signal
#signal.signal(signal.SIGINT, signal.SIG_DFL);

# TODO: TCP is under construction
isTCP = False; # True: TCP / False: UDP

port = 50007;
unsigned_long_int_size = 4;  # bytes
header_size            = unsigned_long_int_size ;
endian = '<';
unsigned_long_int_str = 'L';
num_overflow_bits = unsigned_long_int_size * 8;  # bits
REFERENCE_COUNT_MAX=70000; # max num_counts of a grid cycle

# Encoder packet
'''
#define ENCODER_COUNTER_SIZE 100
struct EncoderInfo {
  unsigned long int header;
  unsigned long int quad[ENCODER_COUNTER_SIZE];
  unsigned long int clock[ENCODER_COUNTER_SIZE];
  unsigned long int clock_overflow[ENCODER_COUNTER_SIZE];
  unsigned long int refcount[ENCODER_COUNTER_SIZE];
  unsigned long int error_signal[ENCODER_COUNTER_SIZE];
};
'''
encoder_counter_size = 100;
encoder_packet_indices = [];
# encoder header
encoder_packet_indices.append(0);
encoder_header = 0x1EAF ;
encoder_header_size  = unsigned_long_int_size;
encoder_header_str   = unsigned_long_int_str ;
# encoder quad
encoder_packet_indices.append(encoder_packet_indices[-1]+1);
encoder_quad_size = (encoder_counter_size * unsigned_long_int_size)
encoder_quad_str  = (encoder_counter_size * unsigned_long_int_str )
# encoder clock
encoder_packet_indices.append(encoder_packet_indices[-1]+encoder_counter_size);
encoder_clock_size   = (encoder_counter_size * unsigned_long_int_size)
encoder_clock_str    = (encoder_counter_size * unsigned_long_int_str )
# encoder clock_overflow
encoder_packet_indices.append(encoder_packet_indices[-1]+encoder_counter_size);
encoder_clock_overflow_size   = (encoder_counter_size * unsigned_long_int_size)
encoder_clock_overflow_str    = (encoder_counter_size * unsigned_long_int_str )
# encoder refcount
encoder_packet_indices.append(encoder_packet_indices[-1]+encoder_counter_size);
encoder_refcount_size   = (encoder_counter_size * unsigned_long_int_size)
encoder_refcount_str    = (encoder_counter_size * unsigned_long_int_str )
# encoder error_signal
encoder_packet_indices.append(encoder_packet_indices[-1]+encoder_counter_size);
encoder_error_signal_size   = (encoder_counter_size * unsigned_long_int_size)
encoder_error_signal_str    = (encoder_counter_size * unsigned_long_int_str )
# append last index
encoder_packet_indices.append(encoder_packet_indices[-1]+encoder_counter_size);

# Encoder packet size
encoder_packet_size = (
    encoder_header_size
    + encoder_quad_size
    + encoder_clock_size
    + encoder_clock_overflow_size
    + encoder_refcount_size
    + encoder_error_signal_size);
# String to unpack encoder data
encoder_unpack_str = ( "%s%s%s%s%s%s%s" % (
    endian, 
    encoder_header_str, 
    encoder_quad_str, 
    encoder_clock_str, 
    encoder_clock_overflow_str, 
    encoder_refcount_str, 
    encoder_clock_str)
);
print('encoder_packet_size= {}'.format(encoder_packet_size));
print('encoder_unpack_str = {}'.format(encoder_unpack_str));


# unpack encoder packet
def process_encoder_packet(data, parse_index):
    # Unpack the encoder data
    start_ind = parse_index ;
    end_ind   = start_ind + encoder_packet_size ;
    unpacked_data = np.array(struct.unpack(encoder_unpack_str,data[start_ind:end_ind]));
    #print('encoder unpack data = {}'.format(unpacked_data));
    # Parse the counter packets
    # Extract the header
    header = unpacked_data[encoder_packet_indices[0]:encoder_packet_indices[1]][0]
    print(unpacked_data[encoder_packet_indices[0]:encoder_packet_indices[1]]);
    if header != encoder_header:
        raise RuntimeError("Encoder header error: 0x%04X" % (header))
    # Extract the quadrature data
    quad_data = unpacked_data[ind1:ind2][0]
    quad_data = unpacked_data[encoder_packet_indices[1]:encoder_packet_indices[2]][0]
    # Extract the clock
    clock_data = unpacked_data[encoder_packet_indices[2]:encoder_packet_indices[3]][0]
    # Extract the clock overflow
    ovflow_data = unpacked_data[encoder_packet_indices[3]:encoder_packet_indices[4]][0]
    # Extract the count (refcount)
    count_data = unpacked_data[encoder_packet_indices[4]:encoder_packet_indices[5]][0]
    # Extract the error signal
    error_data = unpacked_data[encoder_packet_indices[5]:encoder_packet_indices[6]][0]

    # modify data
    quad        = int(quad_data);
    timer_count = clock_data + (ovflw_data << num_overflow_bits); # clock_data + ovflw_data * 2^(num_overflow_bits)
    position    = (count_data+REFERENCE_COUNT_MAX) % REFERENCE_COUNT_MAX;
    error       = error_data;

    # Create and return a frame with clock and encoder data
    encoder_frame = {};
    encoder_frame['quad'        ] = quad;
    encoder_frame['timer_count' ] = timer_count;
    encoder_frame['position'    ] = position;
    encoder_frame['error'       ] = error;
    return encoder_frame


def collect_data(outfilename) :
  
  collector = Collector(port,isTCP=isTCP);
  time.sleep(1);
  
  outfile = open(outfilename,'w');
  outfile.write('#TIME ERROR DIRECTION TIMERCOUNT REFERENCE\n');
  
  while True :
    return_frames = [];
    # Empty the queue and parse its contents appropriately
    approx_size = collector.queue.qsize()
    if approx_size>0 : print('approximate size = {}'.format(approx_size));
  
    for i in range(approx_size):
      # Block=True : Block execution until there is something in the queue to retrieve
      # timeout=None : the get() command will try indefinitely
      data = collector.queue.get(block=True, timeout=None);
    
      # Once data is extracted from the queue, parse its contents
      # and loop until data is empty
      data_len = len(data);
      parse_index = 0;
      while parse_index < data_len:
          # Extract header
          header = data[parse_index : parse_index + header_size];
          # unpack from binary ( byte order: little endian(<), format : L (unsigned long) )
          header = struct.unpack(("%s%s" % (endian, unsigned_long_int_str)), header)[0]
          # Check for Encoder packet
          if header == encoder_header:
              return_frames.append(process_encoder_packet(data, parse_index))
              parse_index += encoder_packet_size
          else:
              try :
                raise RuntimeError(("Bad header! This is not encoder header! : %s" % (str(header))))
              except RuntimeError as e:
                  print(e);
                  print('###get data###');
                  print(data);
                  print('##############');
                  #sys.exit(-1);
                  break;
                  pass;
              pass;
          pass; # end of ``while parse_index < data_len:``

      # Reset data string
      data = ''
      pass; # end of loop over ``i``

    # write data
    for frame in return_frames :
      ncount = len(frame['timercount']);
      for i in range(ncount) :
        outfile.write('{} {} {} {} {}\n'.format((int)(time.time()), 1-frame['error'][i],frame['quad'][i],frame['timercount'][i],frame['position'][i]));
        pass;
      pass; 

    pass; # end of ``while True :``
  
  #print('last return frames:');
  #print('{}'.format(return_frames));
  
  collector.stop();

  return 0;


if __name__ == '__main__' :
  outfilename = 'aho.txt';
  if len(sys.argv) > 1 : outfilename = sys.argv[1];
  collect_data(outfilename);
  pass;
  


