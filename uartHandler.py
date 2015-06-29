#!/usr/bin/env python

"""uartHandler.py: Simple non blocking uart handler module .It assumes a newline
return protocol that separates ascii lines with \n.."""

__author__  = "Minos Galanakis"
__license__ = "LGPL"
__version__ = "0.0.1"
__email__   = "minos197@gmail.com"
__project__ = "misc_utils"
__date__    = "29-06-2015"

import serial
import time
import threading
from Queue import Queue


class UartHandler():

    def __init__(
            self,
            rx_callback,
            fifos=False,
            port="/dev/ttyUSB0",
            baud=115200):

        #Set up config parameters
        self.queue_buff_sz = 10
        self.background_poll_delay = 0.1
        self.use_queues = fifos
        self.stop_threads = False
        self.rx_cb = rx_callback

        #Insantiate the UART
        self.uart = serial.Serial(port, baud)

        if self.use_queues:
            # Remove size limit ofr memory limitted applications
            # or if the queues are not emptied using qeueu.get()
            self.tx_queue = Queue(maxsize=self.queue_buff_sz)
            self.rx_queue = Queue(maxsize=self.queue_buff_sz)

    def start_uart(self):
        """Start the serial port hadling thread/s"""
        # Add background processes
        def rx_uart_poll(rx_cb):

            #Continuously poll unless the flag terminates the thread
            while True:
                #This is required to reduce cpu load of program.Adjust in init
                time.sleep(self.background_poll_delay)
                if self.stop_threads:
                    print "\n ** Shutting Down RX UART polling Thread **"
                    return
                #If there is something in the line remove the last char "\n"
                #and pass it using the callback 
                elif self.uart.inWaiting():
                    uart_rx_data = self.uart.readline()[:-1]
                    (lambda x: rx_cb(x))(uart_rx_data)

        def tx_uart_poll():

            while True:      
                time.sleep(self.background_poll_delay)
                if self.stop_threads:
                    print "\n ** Shutting Down TX UART polling Thread **"
                    return
                #Qusize may not be accurate enough if there is something written
                # on the buffer but the routine will poll again
                elif self.tx_queue.qsize() > 0:
                    dt = self.tx_queue.get()
                    # Send the data dding the new line trail
                    self.raw_uart_send(dt)
                    self.tx_queue.task_done()

        # covert to a thread and start it
        if not self.use_queues:
            self.rx_thread=threading.Thread(
                target=rx_uart_poll,
                args=(self.rx_cb,))
            self.rx_thread.daemon = True
            self.rx_thread.start()
        # When using FIFO mode
        else:
            self.rx_thread = threading.Thread(
                target=rx_uart_poll,
                args=(self.bufferd_callback,))
            self.tx_thread = threading.Thread(target=tx_uart_poll)
            self.tx_thread.daemon = True
            self.rx_thread.daemon = True
            self.rx_thread.start()
            self.tx_thread.start()

    def bufferd_callback(self, data):
        """Intermediate helper function that stores data to a buffer as well
        serving it to client."""

        # Serve it using client callback
        (lambda x: self.rx_cb(x))(data)

        # Store the data to the queue
        self.rx_queue.put(data)

    def stop_uart(self):
        """Set the thread termination flag and join all asynchronous pars of 
        the code"""

        self.stop_threads = True
        self.rx_thread.join()
        if self.use_queues:
            self.tx_thread.join()
            self.rx_queue.join()
            self.tx_queue.join()


    def send(self, data):
        """Sends a line depending on the handling mode (user function) """

        if self.use_queues:
            self.buffered_send(data)
        else:
            self.uart.write(data + '\n')

    def buffered_send(self, data):
        """ Places data in the UART TX FIFO to be broadcast when
        the line is not busy"""

        self.tx_queue.put(data)

    def raw_uart_send(self, data):
        """Sends a line down the uart """

        self.uart.write(data + '\n')

    def rx_get_item(self):
        if self.use_queues and self.rx_queue.qsize() > 0:
            entry = self.rx_queue.get()
            self.rx_queue.task_done()
            return entry
        else:
            return None

if __name__ == "__main__":

    ####################  
    #### Test Code   ###
    ####################

    def test_callback(data):
        """User implemented uart rx handling function"""
        print "Uart Received: %s" % data


    # Create Two distinct datasets , containing 10 numbers in ASCII
    test_dataset_1 = [str(n) for n in range(0, 10)]
    test_dataset_2 = [str(n) for n in range(100, 110)]

    print "\nTesting Direct Callback\n-----------------------"

    # Test without using buffers
    uh = UartHandler(test_callback)
    uh.start_uart()

    for td in test_dataset_1:
        print "Uart Sending", td
        uh.send(td)

    # Wait 3 seconds
    time.sleep(3)

    # Cleanup
    uh.stop_uart()
    del(uh)

    print "\nTesting With FIFO\n-----------------------"
    # Test with Buffers
    uh = UartHandler(test_callback, fifos=True)
    uh.start_uart()
    for td in test_dataset_2:
        print "Uart Sending", td
        uh.send(td)

    # Wait 5 seconds
    time.sleep(3)

    print "\nPrinting Buffer Contents\n-----------------------"

    idx = 0
    while True:
        item = uh.rx_get_item()
        if not item:
            break
        else:
            print "bSlot %d: %s" % (idx, item)
        idx += 1

    # Cleanup
    uh.stop_uart()
    del(uh)
