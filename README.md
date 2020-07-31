# TEMPERATURE_API
REST API in python and flask which could be installed on a Raspberry Pi. For now the API can read and record the temperature from an one-wire sensor of type DS18B20. 

# ABOUT DS18B20
The DS18B20 can be operated under what is called parasite power mode. Normally the chip or sensor has three wire; _Vcc_, _ground_ and _data_. Each sensor has an unique 64-bit address which is used to communicate through One-Wire protocol. Nowdays the operating system of a Raspberry Pi have an One-Wire Interface which this project is heavily depends on. The interface has to be enabled before use.

![DS18B20 pinout](/images/DS18B20_pinout.png)

## TECHNICAL SPECIFICATIONS
- -55&deg;C to 125&deg;C range
- 3,0V to 5,0V operating voltage
- 750 ms sampling
- 0,5&deg;C (9 bit), 0,25&deg;C (10 bit), 0,125&deg;C (11 bit), 0,0625&deg; (12 bit) resolution
- One-Wire communication protocol

For more details on configuring parasite power, setting alarm etc please search for a DS18B20 Datasheet.

# TECHNOLOGIES AND DEPENDENCIES
The API uses the following dependencies to implement the API.  
- Sqlite3 
- Python3
- Flask
- Flask_jwt_extended

# SETUP RASPBERRY PI
In order to use the DS18B20 sensor it has to be enabled in the operating system. This could be done in the _raspi-config_. But preferably each connected sensor is added to the file _/boot/config.txt_, before rebooting your Pi. By adding following line/s in the bottom of the file each BCM channel will be configured for One-Wire protocol. Please follwoing link for more info [pinout explained](https://pinout.xyz/pinout/1_wire#)

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

# INSTALLATION

# CONFIG FILE

# FUNCTIONALITIES OF THE API
- Add/Get/Remove sensor that could be used to read the temperature
- Record the temperature on each sensor at a certain interval
- Get recorded values from database
- Set a maximum limit of recorded values in database






