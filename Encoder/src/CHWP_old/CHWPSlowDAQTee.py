import sys
import struct
import socket
import errno
from spt3g import core  # pylint: disable=import-error


@core.indexmod
class CHWPSlowDAQTee(object):
    '''
    Module that serves CHWP data to the slowDAQ publisher when asked
    '''
    def __init__(self, port=50029, chunk_secs=1):
        # Store passed attributes
        self._port = port
        self._chunk_sec = int(chunk_secs)

        # Definitions for reading data strings
        self._endian = '<'
        self._uint_str = 'Q'
        self._double_str = 'd'
        # String to describe data length for 'struct' module
        self._len_str = self._endian + 'i'
        # String for packing values from G3DoubleObjects
        # as long long ints
        self._pack_str = self._endian + 'q'

        # Establish socket connection to slowDAQ publisher
        self.socket = socket.socket()
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(('', port))
        self.socket.listen(5)
        self.socket.setblocking(False)
        core.log_info(
            "Listening for requests from slowdaq on port %d'" % (self._port),
            unit='CHWPSlowDAQTee')

        # Store and send data as a dictionary
        self.data = {}
        self.time_chunk = None

    def __call__(self, frame):
        # If Timepoint frame of bolometer data, update timer
        if frame.type == core.G3FrameType.Timepoint and 'DfMux' in frame:
            seconds = int(frame['EventHeader'].time / core.G3Units.s)
            self.time_chunk = seconds - seconds % self._chunk_sec

        # If Timepoint frame of CHWP data, fill the buffer
        if frame.type == core.G3FrameType.Timepoint and 'DfMux' not in frame:
            # Generate dict of lists if first time within this time chunk
            if self.time_chunk not in self.data:
                self.data[self.time_chunk] = {
                    'chwp_encoder_quad': [],
                    'chwp_encoder_clock': [],
                    'chwp_encoder_count': [],
                    'chwp_irig_time': [],
                    'chwp_irig_clock': []}
            # Populate dictionary lists with encoder data
            if 'chwp_encoder_quad' in frame.keys():
                self.data[self.time_chunk]['chwp_encoder_quad'] += (
                    [frame['chwp_encoder_quad']])
                self.data[self.time_chunk]['chwp_encoder_clock'] += (
                    list(frame['chwp_encoder_clock']))
                self.data[self.time_chunk]['chwp_encoder_count'] += (
                    list(frame['chwp_encoder_count']))
            # Populate dictionary lists with IRIG data
            elif 'chwp_irig_time' in frame.keys():
                self.data[self.time_chunk]['chwp_irig_time'].append(
                    frame['chwp_irig_time'])
                self.data[self.time_chunk]['chwp_irig_clock'].append(
                    frame['chwp_irig_clock'])

        # Once the buffer has something, check for new connections
        if len(self.data) == 2:
            keys = list(self.data.keys())
            keys.sort()
            try:
                s, origin_ip = self.socket.accept()
            except socket.error as e:
                # Raise the exception if there is a real problem
                if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                    raise e
                # If nobody is listening, prune the buffer
                del self.data[keys[0]]
                return

            # If someone is listening, then send the data
            core.log_debug(
                "Accepted connection from %s:%d"
                % (origin_ip), unit='CHWPSlowDAQTee')
            s.setblocking(True)
            # Send the data over the socket to the slowDAQ publisher
            # and assert that nothing was sent back
            to_send = self._pack_for_slow_daq(self.data[keys[0]])
            retval = s.sendall(to_send)
            assert retval is None
            # Close the socket after the data is sent
            s.close()

            # Only keep the most recent data
            del self.data[keys[0]]

        elif len(self.data) > 2:
            raise RuntimeError('Buffer too long!')

    def _pack_for_slow_daq(self, data):
        # Start with an empty buffer
        buf = b''

        # Unpack contents into the buffer
        self._pack_uint(buf, data['chwp_encoder_quad'])
        self._pack_uint(buf, data['chwp_encoder_clock'])
        self._pack_uint(buf, data['chwp_encoder_count'])
        self._pack_double(buf, data['chwp_irig_time'])
        self._pack_uint(buf, data['chwp_irig_clock'])

        # Prepend buffer length to safeguard against incomplete
        # transmissions over the network
        buf = struct.pack(self._uint_str, sys.getsizeof(buf)) + buf
        return buf

    def _pack_uint(self, buf, data):
        # Unpack the data into the buffer
        buf += struct.pack(self._uint_str, len(data))
        for dat in data:
            buf += struct.pack(self._uint_str, dat)
        return buf
    
    def _pack_double(self, buf, data):
        # Unpack the data into the buffer
        buf += struct.pack(self._uint_str, len(data))
        for dat in data:
            buf += struct.pack(self._double_str, dat)
        return buf
