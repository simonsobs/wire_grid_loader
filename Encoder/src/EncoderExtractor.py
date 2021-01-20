import struct;
import numpy as np;

from PacketInfo import PacketInfo;

from constant import *;
REFERENCE_COUNT_MAX=70000; # max num_counts of a grid cycle

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


