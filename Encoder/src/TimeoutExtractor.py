import struct;
import numpy as np;

from PacketInfo import PacketInfo;

from constant import *;

class TimeoutExtractor() :
  def __init__(self, header) :
    '''
    struct TimeoutInfo {
        unsigned long int header;
        unsigned long int type;
    };
    '''

    self.header = header;
    self.pi = PacketInfo(header);

    # header
    self.pi.total_typte_size = self.pi.header_bytesize;
    self.pi.unpack_str = '%s%s' % (endian, self.pi.header_str);
    # for type
    index = 1;
    self.pi.data_indices  .append(index);
    self.pi.data_nums     .append(1);
    self.pi.data_bytesizes.append(unsigned_long_int_size);
    self.pi.data_strs     .append(unsigned_long_int_str );

    # calculate total info
    self.pi.num_datatype = len(self.pi.data_indices);
    self.pi.total_bytesize = self.pi.header_bytesize + sum(self.pi.data_bytesizes);
    self.pi.unpack_str = ( '%s%s%s' %
        (endian, self.pi.header_str, ''.join(self.pi.data_strs)));
    pass;


  def extract(self, data, parse_index) :
  
    data_array = self.pi.unpack_data(data, parse_index);
    # Extract the type
    type_data = data_array[0][0];
  
    # Create and return a frame with clock and encoder data
    timeout_frame = {};
    timeout_frame['type' ] = type_data;
    return timeout_frame;

  pass; # end of class TimeoutExtractor()


