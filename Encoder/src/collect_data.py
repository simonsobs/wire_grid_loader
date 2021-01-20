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
endian = '<';
unsigned_long_int_str = 'L';
num_overflow_bits = unsigned_long_int_size * 8;  # bits
REFERENCE_COUNT_MAX=70000; # max num_counts of a grid cycle

verbose = 0; # -1: No output / 0: Normal output / 1: verbose output

class PacketInfo() :
  def __init__(self, header):
    self.header = header;
    self.header_num  = 1; # number of data in header
    self.header_bytesize = unsigned_long_int_size; # byte size of header
    self.header_str       = unsigned_long_int_str ; # unpac str of header
    self.num_overflow_bits = unsigned_long_int_size * 8; # bits

    self.num_datatype = 0 ; # number of data type
    self.data_indices = []; # initial indices for each data type
    self.data_nums    = []; # number of data for each data type
    self.data_bytesizes = []; # total byte sizes of datas for each data type
    self.data_strs    = []; # unpack str for each data type

    self.total_bytesize = 0 ; # total byte size of header + all the data
    self.unpack_str = '';
    pass;

  def unpack_data(self, data, parse_index):
    # Unpack the encoder data
    start_ind = parse_index ;
    end_ind   = start_ind + self.total_bytesize ;
    unpacked_data = np.array(struct.unpack(self.unpack_str,data[start_ind:end_ind]));
    if verbose>0 : print('unpacked data = {}'.format(unpacked_data));
    # Parse the counter packets
    # Extract the header
    header = unpacked_data[0:self.header_num][0];
    if header != self.header:
        raise RuntimeError("Header error: 0x%04X" % (header))
    data_array = [];
    for i in range(self.num_datatype) :
      init_ind = self.data_indices[i];
      end_ind  = init_ind+self.data_nums[i];
      if verbose>0 :
          print('init index = {} / {}(unpacked data size)'.format(init_ind, len(unpacked_data)));
          print('end  index = {} / {}(unpacked data size)'.format(end_ind , len(unpacked_data)));
          pass;
      data_array.append(unpacked_data[init_ind:end_ind]);
      pass;

    return data_array;


class EncoderExtractor() :
  def __init__(self, header) :
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
    self.header = header;
    self.pi = PacketInfo(header);
    self.encoder_packet_size = 100;

    # header
    self.pi.total_typte_size = self.pi.header_bytesize;
    self.pi.unpack_str = '%s%s' % (endian, self.pi.header_str);
    # for encoder quad
    index = 1;
    self.pi.data_indices  .append(index);
    self.pi.data_nums     .append(self.encoder_packet_size);
    self.pi.data_bytesizes.append(unsigned_long_int_size * self.encoder_packet_size);
    self.pi.data_strs     .append(unsigned_long_int_str  * self.encoder_packet_size);
    # for encoder clock
    index += self.pi.data_nums[-1];
    self.pi.data_indices  .append(index);
    self.pi.data_nums     .append(self.encoder_packet_size);
    self.pi.data_bytesizes.append(unsigned_long_int_size * self.encoder_packet_size);
    self.pi.data_strs     .append(unsigned_long_int_str  * self.encoder_packet_size);
    # for encoder clock_overflow
    index += self.pi.data_nums[-1];
    self.pi.data_indices  .append(index);
    self.pi.data_nums     .append(self.encoder_packet_size);
    self.pi.data_bytesizes.append(unsigned_long_int_size * self.encoder_packet_size);
    self.pi.data_strs     .append(unsigned_long_int_str  * self.encoder_packet_size);
    # for encoder refcount
    index += self.pi.data_nums[-1];
    self.pi.data_indices  .append(index);
    self.pi.data_nums     .append(self.encoder_packet_size);
    self.pi.data_bytesizes.append(unsigned_long_int_size * self.encoder_packet_size);
    self.pi.data_strs     .append(unsigned_long_int_str  * self.encoder_packet_size);
    # for encoder error signal
    index += self.pi.data_nums[-1];
    self.pi.data_indices  .append(index);
    self.pi.data_nums     .append(self.encoder_packet_size);
    self.pi.data_bytesizes.append(unsigned_long_int_size * self.encoder_packet_size);
    self.pi.data_strs     .append(unsigned_long_int_str  * self.encoder_packet_size);

    # calculate total info
    self.pi.num_datatype = len(self.pi.data_indices);
    self.pi.total_bytesize = self.pi.header_bytesize + sum(self.pi.data_bytesizes);
    self.pi.unpack_str = ( '%s%s%s' %
        (endian, self.pi.header_str, ''.join(self.pi.data_strs)));
    pass;

  def extract(self, data, parse_index) :
  
    data_array = self.pi.unpack_data(data, parse_index);
    # Extract the quadrature data
    quad_data     = data_array[0];
    # Extract the clock
    clock_data    = data_array[1];
    # Extract the clock overflow
    overflow_data = data_array[2];
    # Extract the count (refcount)
    count_data    = data_array[3];
    # Extract the error signal
    error_data    = data_array[4];
  
    # modify data
    quad       = quad_data;
    timercount = clock_data + (overflow_data << num_overflow_bits); # clock_data + overflow_data * 2^(num_overflow_bits)
    position   = (count_data+REFERENCE_COUNT_MAX) % REFERENCE_COUNT_MAX;
    error      = error_data;
  
    # Create and return a frame with clock and encoder data
    encoder_frame = {};
    encoder_frame['quad'       ] = quad;
    encoder_frame['timercount' ] = timercount;
    encoder_frame['position'   ] = position;
    encoder_frame['error'      ] = error;
    return encoder_frame;

  pass; # end of class EncoderExtractor()


'''
def define_encoder_packet(){
  # Encoder packet
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
  if verbose>-1: print('encoder_packet_size= {}'.format(encoder_packet_size));
  if verbose>-1: print('encoder_unpack_str = {}'.format(encoder_unpack_str));

  return encoder_packet
  

# unpack encoder packet
def process_encoder_packet(data, parse_index):
    # Unpack the encoder data
    start_ind = parse_index ;
    end_ind   = start_ind + encoder_packet_size ;
    unpacked_data = np.array(struct.unpack(encoder_unpack_str,data[start_ind:end_ind]));
    # Parse the counter packets
    # Extract the header
    header = unpacked_data[encoder_packet_indices[0]:encoder_packet_indices[1]][0]
    if header != encoder_header:
        raise RuntimeError("Encoder header error: 0x%04X" % (header))
    # Extract the quadrature data
    quad_data     = unpacked_data[encoder_packet_indices[1]:encoder_packet_indices[2]]
    # Extract the clock
    clock_data    = unpacked_data[encoder_packet_indices[2]:encoder_packet_indices[3]]
    # Extract the clock overflow
    overflow_data = unpacked_data[encoder_packet_indices[3]:encoder_packet_indices[4]]
    # Extract the count (refcount)
    count_data    = unpacked_data[encoder_packet_indices[4]:encoder_packet_indices[5]]
    # Extract the error signal
    error_data    = unpacked_data[encoder_packet_indices[5]:encoder_packet_indices[6]]

    # modify data
    quad       = quad_data;
    timercount = clock_data + (overflow_data << num_overflow_bits); # clock_data + overflow_data * 2^(num_overflow_bits)
    position   = (count_data+REFERENCE_COUNT_MAX) % REFERENCE_COUNT_MAX;
    error      = error_data;

    # Create and return a frame with clock and encoder data
    encoder_frame = {};
    encoder_frame['quad'       ] = quad;
    encoder_frame['timercount' ] = timercount;
    encoder_frame['position'   ] = position;
    encoder_frame['error'      ] = error;
    return encoder_frame
'''


def collect_data(outfilename) :
  
  collector = Collector(port,isTCP=isTCP);
  time.sleep(1);
  
  outfile = open(outfilename,'w');
  outfile.write('#TIME ERROR DIRECTION TIMERCOUNT REFERENCE\n');

  encoder_header  = 0x1EAF;
  irig_header     = 0xCAFE;
  timeout_header  = 0x1234;
  error_header    = 0xE12A;

  encoder_extractor = EncoderExtractor(encoder_header);
  header_unpack_str = encoder_extractor.pi.header_str;
  header_size       = encoder_extractor.pi.header_num;
  header_bytesize   = encoder_extractor.pi.header_bytesize;
  encoder_bytesize  = encoder_extractor.pi.total_bytesize;
  
  while True :
    return_frames = [];
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
          # Extract header
          header = data[parse_index : parse_index + header_bytesize];
          if verbose>0 : 
              print('obtained header      = {}'.format(header));
              print('obtained header size = {}'.format(len(header)));
              pass;
          # unpack from binary ( byte order: little endian(<), format : L (unsigned long) )
          header = struct.unpack(("%s%s" % (endian, header_unpack_str)), header)[0]
          # Check for Encoder packet
          if header == encoder_header:
              return_frames.append(encoder_extractor.extract(data, parse_index));
              parse_index += encoder_bytesize
          else:
              try :
                raise RuntimeError(("Bad header! This is not encoder header! : %s" % (str(header))))
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

    # write data
    for frame in return_frames :
      ncount = len(frame['timercount']);
      for i in range(ncount) :
        outfile.write('{} {} {} {} {}\n'.format((int)(time.time()), 1-frame['error'][i],frame['quad'][i],frame['timercount'][i],frame['position'][i]));
        pass;
      pass; 

    pass; # end of ``while True :``
  
  collector.stop();

  return 0;


if __name__ == '__main__' :
  outfilename = 'aho.txt';
  if len(sys.argv) > 1 : outfilename = sys.argv[1];
  collect_data(outfilename);
  pass;
  


