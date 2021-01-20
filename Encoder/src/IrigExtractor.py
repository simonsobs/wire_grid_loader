import struct;
import numpy as np;

from PacketInfo import PacketInfo;

from constant import *;

class IrigExtractor() :
  def __init__(self, header) :
    '''
    struct IrigInfo {
        unsigned long int header;
        unsigned long int clock;
        unsigned long int clock_overflow;
        unsigned long int info[10];
        unsigned long int synch[10];
        unsigned long int synch_overflow[10];
    };
    '''

    self.header = header;
    self.pi = PacketInfo(header);

    # header
    self.pi.total_typte_size = self.pi.header_bytesize;
    self.pi.unpack_str = '%s%s' % (endian, self.pi.header_str);
    # for irig clock
    index = 1;
    self.pi.data_indices  .append(index);
    self.pi.data_nums     .append(1);
    self.pi.data_bytesizes.append(unsigned_long_int_size);
    self.pi.data_strs     .append(unsigned_long_int_str );
    # for irig clock overflow
    index += self.pi.data_nums[-1];
    self.pi.data_indices  .append(index);
    self.pi.data_nums     .append(1);
    self.pi.data_bytesizes.append(unsigned_long_int_size);
    self.pi.data_strs     .append(unsigned_long_int_str );
    # for irig info
    index += self.pi.data_nums[-1];
    self.pi.data_indices  .append(index);
    self.pi.data_nums     .append(10);
    self.pi.data_bytesizes.append(unsigned_long_int_size * 10);
    self.pi.data_strs     .append(unsigned_long_int_str  * 10);
    # for irig sync
    index += self.pi.data_nums[-1];
    self.pi.data_indices  .append(index);
    self.pi.data_nums     .append(10);
    self.pi.data_bytesizes.append(unsigned_long_int_size * 10);
    self.pi.data_strs     .append(unsigned_long_int_str  * 10);
    # for irig sync overflow
    index += self.pi.data_nums[-1];
    self.pi.data_indices  .append(index);
    self.pi.data_nums     .append(10);
    self.pi.data_bytesizes.append(unsigned_long_int_size * 10);
    self.pi.data_strs     .append(unsigned_long_int_str  * 10);

    # calculate total info
    self.pi.num_datatype = len(self.pi.data_indices);
    self.pi.total_bytesize = self.pi.header_bytesize + sum(self.pi.data_bytesizes);
    self.pi.unpack_str = ( '%s%s%s' %
        (endian, self.pi.header_str, ''.join(self.pi.data_strs)));
    pass;


  def de_irig(irig_signal, base_shift) :
      return (((irig_signal >> (0+base_shift)) & 1)
            + ((irig_signal >> (1+base_shift)) & 1) * 2
            + ((irig_signal >> (2+base_shift)) & 1) * 4
            + ((irig_signal >> (3+base_shift)) & 1) * 8
            + ((irig_signal >> (5+base_shift)) & 1) * 10
            + ((irig_signal >> (6+base_shift)) & 1) * 20
            + ((irig_signal >> (7+base_shift)) & 1) * 40
            + ((irig_signal >> (8+base_shift)) & 1) * 80);


  def extract(self, data, parse_index) :
  
    data_array = self.pi.unpack_data(data, parse_index);
    # Extract the clock
    clock_data    = data_array[0][0];
    # Extract the clock overflow
    overflow_data = data_array[1][0];
    # Extract the irig info
    info_data     = data_array[2];
    # Extract the irig sync clock !!NOT SAVED!!
    syncclock_data    = data_array[3];
    # Extract the irig sync clock overflow !!NOT SAVED!!
    syncoverflow_data = data_array[4];
  
    # modify data
    timercount = clock_data + (overflow_data << num_overflow_bits); # clock_data + overflow_data * 2^(num_overflow_bits)
    second = de_irig(info_data[0],1);
    minute = de_irig(info_data[1],0);
    hour   = de_irig(info_data[2],0);
    day    = de_irig(info_data[3],0) + de_irig(info_data[4],0)*100;
    year   = de_irig(info_data[5],0);
  
    # Create and return a frame with clock and encoder data
    irig_frame = {};
    irig_frame['timercount' ] = timercount;
    irig_frame['second'     ] = second;
    irig_frame['minute'     ] = minute;
    irig_frame['hour'       ] = hour;
    irig_frame['day'        ] = day;
    irig_frame['year'       ] = year;
    return irig_frame;

  pass; # end of class IrigExtractor()


