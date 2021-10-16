#Python 3 class to control a ThermoCube 200/300/400 by Solid State Cooling Systems
#Date: 08 November 2016
#Author: Lars E. Borm
#E-mail: lars.borm@ki.se or larsborm@gmail.com
#Python version: 3.5.1
#Based on: ThermoCube 200/300/400 Product Manual Rev M27

#If you want to use Python 2, the "to_bytes" function to create the messages 
#does not exist. replace it with "struckt.pack"
#similar for decoding: change "int.from_bytes" to "struct.pack"

#The Thermo Cube works in Farenheit but I made the set_temp() function to use
#Celcius as input. This can be deleted if Farenheit is required.

import serial
import time
import warnings
from serial.tools import list_ports

#   FIND SERIAL PORT
def find_address(identifier = None):
    """
    Find the address of a serial device. It can either find the address using
    an identifier given by the user or by manually unplugging and plugging in 
    the device.
    Input:
    `identifier`(str): Any attribute of the connection. Usually USB to Serial
        converters use an FTDI chip. These chips store a number of attributes
        like: name, serial number or manufacturer. This can be used to 
        identify a serial connection as long as it is unique. See the pyserial
        list_ports.grep() function for more details.
    Returns:
    The function prints the address and serial number of the FTDI chip.
    `port`(obj): Returns a pyserial port object. port.device stores the 
        address.
    
    """
    found = False
    if identifier != None:
        port = [i for i in list(list_ports.grep(identifier))]
        
        if len(port) == 1:
            print('Device address: {}'.format(port[0].device))
            found = True
        elif len(port) == 0:
            print('''No devices found using identifier: {}
            \nContinue with manually finding USB address...\n'''.format(identifier))
        else:
            for p in connections:
                print('{:15}| {:15} |{:15} |{:15} |{:15}'.format('Device', 'Name', 'Serial number', 'Manufacturer', 'Description') )
                print('{:15}| {:15} |{:15} |{:15} |{:15}\n'.format(str(p.device), str(p.name), str(p.serial_number), str(p.manufacturer), str(p.description)))
            raise Exception("""The input returned multiple devices, see above.""")

    if found == False:
        print('Performing manual USB address search.')
        while True:
            input('    Unplug the USB. Press Enter if unplugged...')
            before = list_ports.comports()
            input('    Plug in the USB. Press Enter if USB has been plugged in...')
            after = list_ports.comports()
            port = [i for i in after if i not in before]
            if port != []:
                break
            print('    No port found. Try again.\n')
        print('Device address: {}'.format(port[0].device))
        try:
            print('Device serial_number: {}'.format(port[0].serial_number))
        except Exception:
            print('Could not find serial number of device.')
    
    return port[0]


class ThermoCube():
    '''
    Class to controll a Solid State Thermo Cube 200/300/400
    
    Use the high level functions to control the Thermo Cube:
        -set_temp( celcius ) Set a required temperature
        -read_set_point() Read the current set point
        -read_temp() Read the current temperature
        -check_error() Check for errors
    
    The Thermo Cube works in Farenheit, but the set_temp() function wants
    Celcius values. read_set_point() and read_temp() return Farenheit
    '''
    
    def __init__(self, address, name = ''):
        '''
        Input:
        `address`: address of Thermo Cube, '/dev/ttyUSBX' on linux. 
                   'COMX' on windows.
        `name`(str): Name to identify the Thermo Cube for user (not necessary)
        If connection is made "self.connected" will be set to True
        
        '''
        self.address = address
        self.name = name
        self.ser = serial.Serial(address, timeout = 2, baudrate = 9600)
        self.connected = False
        #9600 is the default baudrate for the Thermo Cube

        #Check for errors and check if a connection is made
        try:
            self.check_error()
            self.connected = True
        except Exception as e:
            print('Could not connect to ThermoCube. Is it on and connected? Is the address correct?')

# Low level funcitons

    def celsius_to_farenheit(self, C):
        """
        Converts degree Celsius to degree Farenheit.
        Input:
        `C` (float or int): degree Celsius.
        Returns:
        Degree farenheit as float with one decimal.
        
        """
        F = (C * (9/5)) + 32
        return round(F, 1)
    
    def farenheit_to_celsius(self, F):
        """
        Converts degree Farenheit to degree Celcius.
        Input:
        `F` (float or int): degree Farenheit.
        Returns:
        Degree celcius as float with one decimal.
        
        """
        C = (F - 32) * (5/9)
        return round(C, 1)

# Composing, writing and reading commands

    def TC_command(self, command, temperature = None):
        """
        Function to format the command for the Thermo cube as hexadecimal byte
        string.
        Input:
        `command`(int): Decimal representation of the command
        `temperature`(float/int, optional): temperature in farenheid
        
        """
        #command 
        command_byte = command.to_bytes(1, byteorder='little')
        message = command_byte

        #if the command is "set temperature", the temperature is added
        if temperature != None:
            temperature = int(temperature * 10)
            temperature_byte = temperature.to_bytes(2, byteorder='little')
            message += temperature_byte
        return message
    
    def write_message(self, message):
        """
        Write message to the Thermo Cube. 
        Input:
        `message`: Message to sent to Thermo Cube
        
        """
        self.ser.write(message)
        #The Thermo Cube can handle up to 3 commands per second
        time.sleep(0.4)
        
    def read_response(self):
        """
        Read response of the Thermo Cube.
        Output: response of the pump.
        
        """
        n = self.ser.inWaiting()
        response = self.ser.read(n)
        return response
 
    def resp_int(self, response):
        """
        Interpret the respons of the Thermo Cube
        Input:
        `response`: Thermo cube response read by "read_response" function
        Depending on the respons the output is either:
            option1: temperature value
            option2: Status of thermal cube (True/False), Error code
        
        """
        #Temperature response
        if len(response) == 2:
            received_temp = int.from_bytes(response, byteorder='little')
            received_temp = received_temp / 10 #get decimal in right place
            return received_temp
        #Error code response
        if len(response) == 1:
            if int.from_bytes(response, byteorder='little') == 0:
                return [True, 'No errors on Thermo Cube "{}"'.format(self.name)]
            else:
                error_dict = {1:"Tank level low", 2:"Fan fail", 8:"Pump fail",
                              16:"RTD open", 32:"RTD short", 
                              128:"Unassigned error code" }
                error_code = int.from_bytes(response, byteorder='little')
                if error_code in error_dict:
                    return False, error_dict[error_code]
                else:
                    return False, ('Unknown error code on Thermo Cube "{}"'
                                   .format(self.name))
        else:
            raise ValueError('Unknown response: "{}" from Thermo Cube "{}"'
                             .format(response, self.name))

# High level functions

    def set_temp(self, temp_C):
        """
        Set the temperature of the Thermo Cube. Checks for errors first.
        Input:
        `temp_C`: temperature to set in celcius.
        
        """
        if not -5 <= temp_C <= 80:
            raise ValueError('''temperature in C for {0} should be between -5C
                            and 80C, not {1}C'''
                            .format(self.name, temp_C))
        
        #Check for errors
        self.check_error(verbose = False)
        
        #Flush output
        self.read_response()
        
        #Command
        temp_F = self.celsius_to_farenheit(temp_C)
        msg = self.TC_command(225, temperature = temp_F)
        
        n_try = 1
        while n_try <= 5:
            #Send messages
            self.write_message(msg)
            
            #Check if set point is set correctly
            set_point = self.read_set_point()
            if (temp_F - 1) <= set_point <= (temp_F + 1): #Made a range in case there is an error in rounding up or down
                return 'Thermo cube "{}" set to {}C'.format(self.name, temp_C)
            else:
                print('''Could not set Thermo cube {} to right temperature,\n 
                      try: {}/5'''.format(self.name, n_try))
                n_try += 1
                
        print('''Failed to set temperature of Thermo Cube "{}" to {}C,\n
              Will check for errors'''.format(self.name, temp_C))
        self.check_error(verbose = True)
        raise Exception('Failed to set temperature of Thermo Cube "{}" to {}C'
                        .format(self.name, temp_C))
        
    def read_set_point(self):
        """
        Read the set point of the Thermal cube
        Output:
        returns set point in farenheid
            
        """
        #Flush output
        self.read_response()
        #Command
        msg = self.TC_command(193)
        #Send message
        self.write_message(msg)
        #Read response
        response = self.read_response()
        #interpret response
        set_point = self.resp_int(response)
        return set_point
    
    def read_temp(self):
        """
        CURRENT temperature of RTD sensor
        Output:
        current temperature in Farenheid read by the RTD sensor
        
        """
        #Flush output
        self.read_response()
        
        #Command
        msg = self.TC_command(201)
        #Send message
        self.write_message(msg)
        #Read message
        response = self.read_response()
        #interpret response
        current_temp = self.resp_int(response)
        return current_temp

    def read_error(self):
        """
        Cecks for errors and returns error code.
         
        """
        #Flush output
        self.read_response()
        
        #Command
        msg = self.TC_command(200)
        #Send message
        self.write_message(msg)
        #Read message
        response = self.read_response()
        return response

    def check_error(self, verbose = True, raise_error=True):
        """
        Check for errors. Raises exeption if there is an error.
        Retruns a warning if error is resolved after 100 seconds.
        If verbose = True, will print that there is no error if there is no error.
        
        """
        #Check for errors and interpret the response
        error = self.resp_int(self.read_error())

        if error[0] == True:
            if verbose == True:
                print(error[1])
            return error

        #See if error resolves itselve
        else:
            #Will check 5 times to see if the error persists.
            print('Error from Thermo Cube "{}": {}'.format(self.name, error[1]))
            n_try = 2
            while n_try <= 5:
                time.sleep(10)
                #Check for errors and interpret the response
                error = self.resp_int(self.read_error())
                if error[0] == True:
                    warnings.warn('''\nError resolved after {} tries.\n
!!! Check the Thermo Cube "{}" to resolve the issue: "{}" !!!'''.format( n_try, self.name, error[1]))
                    break
                else: 
                    print('Error from Thermo Cube "{}": {}, try {}/5'
                          .format(self.name, error[1], n_try))
                    n_try += 1

            if raise_error == True:
                raise Exception('Error from Thermo Cube "{}": {}'.format(self.name, error[1]))
            else:
                return [False, '{}: {}'.format(self.name, error[1])]




















