
import struct;
import numpy as np;
from constant import *;

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
    if verbose>1 : print('unpacked data = {}'.format(unpacked_data));
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



