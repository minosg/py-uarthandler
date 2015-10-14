# UartHandler #


* Simple non blocking uart handler module written in python.
*.It assumes a newline return protocol that separates ascii lines with \n.
* Raises ValueError if Serial fails.
* Contains arduino echo test code, since the majority of starter's project require
a serial interface between RaspberryPI and Arduino.
* Uses buffers
* Version 0.1

### Requirements ###

* Tested in python 2.7.xx
* Requires [pyserial](https://pypi.python.org/pypi/pyserial) module 


### How to include it in your own project ###

```
cd yourprojectdir
git submodule add git@github.com:minosg/py-uarthandler.git ./submodules
from submodules.uarthandler import UartHandler

    # Set up a receive callback fucntion to do something with the data
    def test_callback(data):
        print "Uart Received: %s" % data

    # Instantiate with buffers
    uh = UartHandler(test_callback)

    # Instantiate without buffers
    uh = UartHandler(test_callback, fifos=True)

    # Start it
    uh.start_uart()
```

 UartHandler can be then updated with:
`git submodule update --recursive`

