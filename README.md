# ThermoCube
Python library for control of the Solid State ThermoCube recirculating chiller. 

The [TermoCube](https://www.sscooling.com/product/thermocube-200-500/) is a recirculating chiller to control temperature and is made by the company Solid State Cooling Systems. The code was written using the ThermoCube-200-500-Manual-Rev-M33 downloaded from [here](https://www.sscooling.com/wp-content/uploads/2021/07/ThermoCube-200-500-Manual-Rev-M33.pdf).  

# Get started
- Make sure [pyserial](https://pythonhosted.org/pyserial/) is installed.
- Connect the ThermoCube using a serial to USB cable.
- Make the ThermoCube ready for opperation according to the manufacturers instructions. 
- In a Python interpreter, import the module: `import ThermoCube`.
- Find the USB address of the ThermoCube: `TC_address = ThermoCube.find_address()` 
- The find_address() function returns the address in the format of `COMX` on Windows or `dev/ttyUSBX` on Linux. The address will also be printed. 
- If you use a serial to USB converter that has an FTDI chip inside, the find_address() function will also return the ID nubmer for the FTDI chip. This ID is unique to the chip and can be used to find the port quicker in the future by: `ThermoCube.find_address(identifier = ID)`
- Initiate the valve: `TC = ThermoCube.ThermoCube(TC_address, name='My_TC')`
- Now the ThermoCube is ready for operation.

# Operation
The ThermoCube can be operated with 4 main functions:
- Set the temperature to a specified value in Celcius: `TC.set_temp(X)` 
- Read the set point in Celcius: `TC.read_set_point()`
- Read the actual temperature in Celcius: `TC.read_temp()`
- Check for errors on the ThermoCube and raise an error if the ThermoCube returns an error: `TC.check_error(verbose=True, raise_error=True)`

# Configuration and disclaimer
This code was developed and tested on a custom made ThermoCube 400 with extended temperature range. The code probably works for other models and configurations but this is not tested, always check and compare the communication manual before use. Our model can reach temperatures between -5C and 80C, if your model has a different temperature range please change this in the `set_temp()` function on line 221. Especially make sure the error detection works properly when using a different model. Furthermore, our model requires digital input in Fahrenheit (even though the display in in Celcius), so make sure your model requires the same because the code will convert Celcius to Fahrenheit. This could be dangerous if the code is sending Fahrenheit and the machine is interpreting it as Celcius.
