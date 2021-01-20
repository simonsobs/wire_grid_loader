import multiprocessing
import socket
import errno
import ctypes
import signal
import time


class Collector(object):
    """
    In a separate process, listens for UDP packets from the Beaglebone and
    populates a queue that another script will read from
    """
    def __init__(self, port=8080, isTCP=False):
        """
        set up the socket connection (non-blocking)
        note that sockets are automatically closed
        when they are garbage collected
        Arguments:
            port     - port to use
            isTCP    - True : use TCP / Fasle : use UDP
        """
        # Number of bits to read in chunks from the input buffer
        self._read_chunk_size = 2**20
        #self._read_chunk_size = 2**12
        self._isTCP = isTCP;
        # Use IPv4 internet protocol, datagram type
        self._s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP) if self._isTCP \
          else socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) ;
        # Allow reuse of addresses in the bind call below
        self._s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # Make the connection non-blocking. This is critical
        self._s.setblocking(False)
        # Connect to the microcontroller unit
        self._s.bind(("", port))
        # Data colleciton object
        self._data = [b'', b''];
        self._data2= b'';
        # Enable connection
        if self._isTCP : self._s.listen(0)

        # Used to signal to stop recording
        self._should_stop = multiprocessing.Value(ctypes.c_bool, False)
        self._stopped = multiprocessing.Value(ctypes.c_bool, False)
        self._stopped2= multiprocessing.Value(ctypes.c_bool, False)

        # Start the relaying process
        self.queue = multiprocessing.Queue()
        self._pcount = [0,0];
        self._runprocess = 0b0;
        self._process = multiprocessing.Process(
            target=self.relay_data,
            args=(self._should_stop, self._stopped , 0b0))
        self._process2 = multiprocessing.Process(
            target=self.relay_data,
            args=(self._should_stop, self._stopped2, 0b1))
        self._process.start()
        self._process2.start()

        # Deal with SIGINT interruptions (nominally how we stop the DAQ) nicely
        signal.signal(signal.SIGINT , self.sigint_handler_parent)
        signal.signal(signal.SIGTERM, self.sigint_handler_parent)

    def sigint_handler_parent(self, signal, frame):
        """
        If SIGINT/SIGTERM is sent to the constructor, nicely terminate the
        child listening process without corrupting the queue
        """
        self.stop();
        exit(0);
        return;

    def relay_data(self, should_stop, stopped, processID):
        # In case the SIGINT/SIGTERM signal is sent to this process,
        # ignore it to avoid corrupting things
        signal.signal(signal.SIGINT , signal.SIG_IGN);
        signal.signal(signal.SIGTERM, signal.SIG_IGN);

        while True:
            # check to see if we need to stop recording
            if should_stop.value:
                break

            if self._pcount[processID]%1000 == 0 : print('process{} count in Collector = {}'.format(processID, self._pcount[processID]));

            # check the socket, continuing if there's nothing there yet
            try:
                if self._isTCP :
                  #print('try recv');
                  if processID==0b0 : self._sock, addr = self._s.accept()
                  #print(sock);
                  with sock:
                    recvcount = 0;
                    while True :
                      if processID!=self._runprocess : continue;
                      data = sock.recv(self._read_chunk_size)
                      #print('data = {}'.format(data));
                      #print('received data size = {}'.format(len(data)));
                      self._data[processID] += data;
                      if len(data)<self._read_chunk_size : break;
                      if recvcount%1000 == 0 : print('receive count = {}'.format(recvcount));
                      recvcount += 1;
                      pass;
                    self._runprocess = ( ~self._runprocess & 0b1 ); # bit reverse 0b0<->0b1
                    self._data2 = self._data[processID];
                    self._data[processID] = b'';
                    print('finish get data (data size = {})'.format(len(self._data2)));
                    #print('_data = {}'.format(self._data));
                    pass;
                else :
                  #print('try recv');
                  self._data2 += self._s.recv(self._read_chunk_size)
                  #print('_data2 = {}'.format(self._data));
                  pass;
            except socket.error as err:
                #print('error');
                # In the case of a real problem, re-raise the exception
                if err.errno != errno.EAGAIN:
                    print('Connection has a real problem');
                    raise
                # Otherwise if it's just empty, continue
                else:
                    #print('Just no connection');
                    pass

            # Push the data to the queue
            if len(self._data2) > 0:
                self.queue.put(obj=self._data2, block=True, timeout=None)
                self._data2 = b''
                pass;

            self._pcount[processID] += 1;
            pass;

        print('Stopping relay_data() process(processID={})...'.format(processID));
        # let the parent process know that it's now
        # safe to terminate this child process
        with stopped.get_lock():
            stopped.value = True
            pass;

        return;

    def stop(self):
        """
        Stops the listening process that's
        grabbing packets from the Beaglebone
        """
        # Signal to the child process that it should finish up and end
        with self._should_stop.get_lock():
            self._should_stop.value = True
            pass

        # Wait until the process is in a safe state, then terminate it
        while not (self._stopped.value and self._stopped2.value):
            time.sleep(0.001)
            pass
        self._process.terminate()

        # Block until the child process really is dead
        self._process.join()
        print('Stopped all the children processes.');

        return;
