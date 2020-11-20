from CHWPCollector import CHWPCollector;

import os, sys;
import numpy as np;
from time import sleep;
import struct;

port = 50007;
unsigned_long_int_size = 4;  # bytes
header_size            = unsigned_long_int_size ;
endian = '<';
unsigned_long_int_str = 'L'
num_overflow_bits = unsigned_long_int_size * 8  # bits
# All heaaders are unsigned long ints

# encoder header
encoder_header = 0x1EAF ;
encoder_header_units = 1;
encoder_header_size  = (encoder_header_units * unsigned_long_int_size);
encoder_header_str   = (encoder_header_units * unsigned_long_int_str );
# encoder quad
encoder_quad_units = 1
encoder_quad_size = (encoder_quad_units * unsigned_long_int_size)
encoder_quad_str  = (encoder_quad_units * unsigned_long_int_str )
# encoder data
# -- (unsigned long int) clock[counter_info_length]
# -- (unsigned long int) clock_overflow[counter_info_length]
# -- (unsigned long int) count[counter_info_length]
# -- (unsigned long int) refcount[counter_info_length]
#encoder_data_length = 150
#encoder_data_units  = 3 * encoder_data_length
encoder_data_length = 100
encoder_data_units  = 4 * encoder_data_length
encoder_data_size   = (encoder_data_units * unsigned_long_int_size)
encoder_data_str    = (encoder_data_units * unsigned_long_int_str )
# encoder whole packet
# Encoder packet size
encoder_packet_size = (encoder_header_size + encoder_quad_size + encoder_data_size)
# String to unpack encoder data
encoder_unpack_str = ( "%s%s%s%s" % (
    endian, encoder_header_str, encoder_quad_str, encoder_data_str)
);
print('encoder_packet_size= {}'.format(encoder_packet_size));
print('encoder_unpack_str = {}'.format(encoder_unpack_str ));


# unpack encoder packet
def process_encoder_packet(parse_index):
    # Unpack the encoder data
    start_ind = parse_index
    end_ind   = start_ind + encoder_packet_size
    unpacked_data = np.array(struct.unpack(encoder_unpack_str,data[start_ind:end_ind]))
    #print('encoder unpack data = {}'.format(unpacked_data));
    # Parse the counter packets
    # Extract the header
    ind1 = 0
    ind2 = ind1 + encoder_header_units
    header = unpacked_data[ind1:ind2][0]
    if header != encoder_header:
        raise RuntimeError("Encoder header error: 0x%04X" % (header))
    # Extract the quadrature data
    ind1 = ind2
    ind2 = ind1 + encoder_quad_units
    quad_data = unpacked_data[ind1:ind2][0]
    # Extract the encoder clock data
    ind1 = ind2
    ind2 = ind1 + encoder_data_length
    clock_data = unpacked_data[ind1:ind2]
    # Extract the overflow data
    ind1 = ind2
    ind2 = ind1 + encoder_data_length
    ovflw_data = unpacked_data[ind1:ind2]
    # Extract the encoder count data
    ind1 = ind2
    ind2 = ind1 + encoder_data_length
    count_data = unpacked_data[ind1:ind2]
    # Extract the encoder refcount data
    ind1 = ind2
    ind2 = ind1 + encoder_data_length
    refcount_data = unpacked_data[ind1:ind2]
    # Save the quadrature data as a G3UInt
    quad = int(quad_data)
    # Save the clock data
    clk = clock_data + (ovflw_data << num_overflow_bits) # clock_data + ovflw_data * 2^(num_overflow_bits)
    # Save the count data
    cnts = count_data
    refcnts = refcount_data

    # Create and return a frame with clock and encoder data
    encoder_frame = {};
    encoder_frame['chwp_encoder_quad' ] = quad;
    encoder_frame['chwp_encoder_clock'] = clk;
    encoder_frame['chwp_encoder_count'] = cnts;
    encoder_frame['chwp_encoder_refcount'] = refcnts;
    return encoder_frame



collector = CHWPCollector(port);

sleep(0.1);

outfile = open('aho.txt','w');

while True :

  # Empty the queue and parse its contents appropriately
  approx_size = collector.queue.qsize()
  return_frames = [];
  if approx_size>0 : print('approximate size = {}'.format(approx_size));
  for i in range(approx_size):
    # Block execution until there is something in
    # the queue to retrieve
    # timeout=None means the get() command will try indefinitely
    data = collector.queue.get(block=True, timeout=None);
 
    # Once data is extracted from the queue, parse its contents
    # and loop until data is empty
    data_len = len(data);
    parse_index = 0;
    while parse_index < data_len:
        # Extract header
        header = data[ parse_index : parse_index + header_size];
        # unpack from binary ( byte order: little endian(<), format : L (unsigned long) )
        header = struct.unpack(("%s%s" % (endian, unsigned_long_int_str)), header)[0]
        # Check for Encoder packet
        if header == encoder_header:
            return_frames.append(process_encoder_packet(parse_index))
            parse_index += encoder_packet_size
        else:
            try :
              raise RuntimeError(("Bad header! This is not encoder header! : %s" % (str(header))))
            except RuntimeError as e:
                print(e);
                break;
                pass;
            pass;
        pass;
    # Reset data string
    data = ''
    pass;
 
  for frame in return_frames :
    ncount = len(frame['chwp_encoder_count']);
    for i in range(ncount) :
      outfile.write('{} {} {}\n'.format(frame['chwp_encoder_count'][i],frame['chwp_encoder_refcount'][i],frame['chwp_encoder_clock'][i],));
      pass;
    pass;
  pass;
 

print('all frames:');
print('{}'.format(return_frames));

collector.stop();


