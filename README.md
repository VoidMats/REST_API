# TEMPERATURE_API
REST API in python and flask which could be installed on a Raspberry Pi. For now the API can read and record the temperature from an one-wire sensor of type DS18B20. 

## FUNCTIONALITIES OF THE API
- Add/Get/Remove sensor that could be used to read the temperature
- Record the temperature on each sensor at a certain interval
- Get recorded values from database
- Set a maximum limit of recorded values in database

## ABOUT DS18B20
The DS18B20 can be operated under what is called parasite power mode. Normally the chip or sensor has three wire; _Vcc_, _ground_ and _data_. Each sensor has an unique 64-bit address which is used to communicate through One-Wire protocol. Nowdays the operating system of a Raspberry Pi have an One-Wire Interface which this project is heavily depends on. The interface has to be enabled before use.

![DS18B20 pinout](/images/DS18B20_pinout.png){:height="150px" width="150px"}

### TECHNICAL SPECIFICATIONS
- -55&deg;C to 125&deg;C range
- 3,0V to 5,0V operating voltage
- 750 ms sampling
- 0,5&deg;C (9 bit), 0,25&deg;C (10 bit), 0,125&deg;C (11 bit), 0,0625&deg; (12 bit) resolution
- One-Wire communication protocol

For more details on configuring parasite power, setting alarm etc please search for a DS18B20 Datasheet.

## TECHNOLOGIES AND DEPENDENCIES
The API uses the following dependencies to implement the API.  
- Sqlite3 
- Python3
- Flask
- Flask_jwt_extended

## SETUP RASPBERRY PI
Before any software could be installed the Raspberry Pi should be prepared with all wiring for one or as many sensors you need. Remember that the power voltage 3,3V goes into pin Vcc on the sensor and ground to the GND pin of the sensor. Finally find a free BCM channel which could be used for data communication (Middle pin of the sensor). The default One-Wire channel is 4, but any channel could be used as long its not configured for something else. Between the power and the data pin there should be a resistor of 4,7K-10K Ohm. See example of a setup BCM4.  

![Simple setup of one sensor on BCM4 channel](/images/Setup_BCM4.png){:height="150px" width="150px"}

In order to use the DS18B20 sensor it has to be enabled in the operating system. This could be done in the _raspi-config_. But preferably each connected sensor is added to the file _/boot/config.txt_, before rebooting your Pi. By adding following line/s in the bottom of the file each BCM channel will be configured for One-Wire protocol. Please use link for more info - [pinout explained](https://pinout.xyz/pinout/1_wire#)

```linux
dtoverlay=w1-gpio,gpiopin=x
```
Ones the raspberry Pi has been rebooted and discored all sensors (devices) can be listed under the folder /sys/bus/w1/devices. It is now possible to see each sensor as a folder with its unique 64-bit address name. Example 28-000006637696. Write down each sensor name because this will be used later for the API.  

```linux
$ ls /sys/bus/w1/devices/
```

It is now possible to read the temperature from a sensor by reading the file w1_slave in each folder. 

```linux
$ cat /28-XXXXXXXXXXXX/w1_slave
```
The result should be something in the form of two lines, where the temperature could be read from variable t=XXXXX. The number has to be divided with 1000. Ex 28625 will become 28,625&deg;C.

```linux
ca 01 4b 46 7f ff 06 10 65 : crc=65 YES
ca 01 4b 46 7f ff 06 10 65 t=28625
```

## INSTALLATION

## CONFIG FILE








