Elitech RC4 DataReader
====================================


Description
-----------

This software is a data collecting tool, written in python for Temperature data logger RC-4.

[Elitech RC-4](http://www.e-elitech.com/jingChuang3/shouYe.do?operate=doProductDetail&chanpinId=156) is a reasonable data logger.

Enables to use RC-4 on Mac, Linux, Windows.

Requirements
------------

- Python2.7 or Python3.4
- Silicon Labs CP210x USB-UART bridge VCP driver.  <http://www.silabs.com/products/mcu/Pages/USBtoUARTBridgeVCPDrivers.aspx>
- pySerial (data access library for serial port)


Setup
------------

1. Install CP210x USB-UART bridge VCP driver.  Download and install CP210x driver for your platform.
 <http://www.silabs.com/products/mcu/Pages/USBtoUARTBridgeVCPDrivers.aspx>
2. install dependencies.

```
$ python setup.py install
```

OR pip

```
$ pip install elitech-datareader
```

Example(Script)
--------------

### Initialize device.

initialize. rec interval 10sec. set clock now.

```
$ elictec-device --command simple-set --interval=10 /dev/tty.SLAB_USBtoUART
```

### Get data

Press stop button for stop recording.

output to stdout.

```
$ elitec-device.py --command get /dev/tty.SLAB_USBtoUART
6
1	2015-06-07 13:53:36	25.0
2	2015-06-07 13:53:46	25.1
3	2015-06-07 13:53:56	25.1
4	2015-06-07 13:54:06	25.1
5	2015-06-07 13:54:16	25.1
6	2015-06-07 13:54:26	25.1
```

### Get device information

get device information.

```
$ elitec-device.py --command devinfo /dev/tty.SLAB_USBtoUART
station_no=3
last_online=2015-06-09 01:13:13
temp_unit=TemperatureUnit.C
alarm=AlarmSetting.NONE
work_sts=WorkStatus.STOP
lower_limit=-30.0
tone_set=ToneSet.NONE
rec_count=272
upper_limit=60.0
delay=0.0
stop_button=StopButton.ENABLE
current=2015-06-09 07:42:00
start_time=2015-06-07 13:53:36
rec_interval=00:00:10
temp_calibration=-1.5
user_info=RC-4 Data Logger
dev_num=9900112233
```

### Parameter set

set device parameter.

```
$ elitec-device.py --command set --interval=10 --upper_limit=60.0 --lower_limit=-30.0 \
--station_no=1 --stop_button=y --delay=0 --tone_set=y --alarm=y --temp_unit=C \
--temp_calibration=-1.5 /dev/tty.SLAB_USBtoUART
```

Example(Python module)
-------

### Get device infomation.

```python
import elitech

device = elitech.Device("/dev/tty.SLAB_USBtoUART")
devinfo = device.get_devinfo()
print(devinfo.info)
```

### Get record data

```python
import elitech

device = elitech.Device("/dev/tty.SLAB_USBtoUART")
body = device.get_data()
for elm in body:
    print elm
    
```

### update param

```python
device = elitech.Device("/dev/tty.SLAB_USBtoUART")
devinfo = device.get_devinfo()  # get current parameters.

param_put = devinfo.to_param_put()  #convart devinfo to parameter
param_put.rec_interval = datetime.time(0, 0, 10)    # update parameter
param_put.stop_button = elitech.StopButton.ENABLE   # update parameter

param_put_res = device.update(param_put)    # update device

```
