#!/usr/bin/env python

import argparse
import elitech
import datetime
from elitech.msg import (
    StopButton,
    ToneSet,
    AlarmSetting,
    TemperatureUnit,

)
from elitech.msg import _bin
import six

def main():
    args = parse_args()
    if (args.command == 'simple-set'):
        command_simpleset(args)
    elif(args.command == 'get'):
        command_get(args)
    elif(args.command == 'set'):
        command_set(args)
    elif(args.command == 'devinfo'):
        command_devinfo(args)
    elif(args.command == 'clock'):
        command_clock(args)
    elif(args.command == 'raw'):
        command_raw_send(args)
    elif(args.command == 'latest'):
        command_latest(args)

def _convert_time(sec):
    hour = int(sec / 3600.0)
    min = int((sec - hour * 3600) / 60.0)
    sec = sec % 60
    return datetime.time(hour=hour, minute=min, second=sec)

def command_simpleset(args):
    device = elitech.Device(args.serial_port, args.ser_baudrate, args.ser_timeout)
    device.init()
    dev_info = device.get_devinfo()

    device.set_clock(dev_info.station_no)

    param_put = dev_info.to_param_put()

    if args.interval:
        param_put.rec_interval = _convert_time(args.interval)
    device.update(param_put)

def command_get(args):
    device = elitech.Device(args.serial_port, args.ser_baudrate, args.ser_timeout)
    device.init()

    def output(data_list):
        for line in data_list:
            print("{0}\t{1:%Y-%m-%d %H:%M:%S}\t{2:.1f}".format(*line))

    if args.page_size:
        device.get_data(callback=output, page_size=args.page_size)
    else:
        device.get_data(callback=output)

def command_latest(args):
    device = elitech.Device(args.serial_port, args.ser_baudrate, args.ser_timeout)
    device.init()

    def output(latest):
        if args.value_only:
            print("{2:.1f}".format(*latest))
        else:
            print("{0}\t{1:%Y-%m-%d %H:%M:%S}\t{2:.1f}".format(*latest))

    if args.page_size:
        device.get_latest(callback=output, page_size=args.page_size)
    else:
        device.get_latest(callback=output)

def command_set(args):
    device = elitech.Device(args.serial_port, args.ser_baudrate, args.ser_timeout)
    device.init()
    dev_info = device.get_devinfo()
    param_put = dev_info.to_param_put()

    station_no = dev_info.station_no

    if args.interval:
        param_put.rec_interval = _convert_time(args.interval)
    if args.upper_limit:
        param_put.upper_limit = args.upper_limit
    if args.lower_limit:
        param_put.lower_limit = args.lower_limit
    if args.station_no:
        param_put.update_station_no = int(args.station_no)
        station_no = param_put.update_station_no
    if args.stop_button:
        param_put.stop_button = StopButton.ENABLE if args.stop_button == 'y' else StopButton.DISABLE
    if args.delay:
        param_put.delay = float(args.delay)
    if args.tone_set:
        param_put.tone_set = ToneSet.PERMIT if args.tone_set == 'y' else ToneSet.NONE
    if args.alarm:
        if args.alarm == 'x':
            param_put.alarm = AlarmSetting.NONE
        elif args.alarm == '3':
            param_put.alarm = AlarmSetting.T3
        elif args.alarm == '10':
            param_put.alarm = AlarmSetting.T10
    if args.temp_unit:
        param_put.temp_unit = TemperatureUnit.C if args.temp_unit == 'C' else TemperatureUnit.F

    if args.temp_calibration:
        param_put.temp_calibration = float(args.temp_calibration)
    for k,v in vars(param_put).items():
        print("{}={}".format(k, v))

    device.update(param_put)

    if args.dev_num:
        device.set_device_number(station_no, args.dev_num)
        print("{}={}".format("dev_num", args.dev_num))

    if args.user_info:
        device.set_user_info(station_no, args.user_info)
        print("{}={}".format("user_info", args.user_info))

def command_devinfo(args):
    device = elitech.Device(args.serial_port, args.ser_baudrate, args.ser_timeout)
    device.init()
    dev_info = device.get_devinfo()
    for k,v in vars(dev_info).items():
        print("{}={}".format(k, v))

def command_clock(args):
    device = elitech.Device(args.serial_port, args.ser_baudrate, args.ser_timeout)
    dev_info = device.get_devinfo()
    if args.time:
        clock = datetime.datetime.strptime(args.time, '%Y%m%d%H%M%S')
    else:
        clock = None
    device.set_clock(dev_info.station_no, clock)

def command_raw_send(args):
    device = elitech.Device(args.serial_port, args.ser_baudrate, args.ser_timeout)

    request_bytes = _bin(args.req)

    res = device.raw_send(request_bytes, args.res_len)

    print("\nresponse length={}".format(len(res)))
    for i, b in enumerate(res):
        if six.PY2:
            six.print_("{:02X} ".format(ord(b)), sep='', end='')
        else:
            six.print_("{:02X} ".format(b), end='')
        if (i + 1) % 16 == 0:
            six.print_()

    six.print_()

def parse_args():
    """
    :rtype: argparse.Namespace
    """
    parser = argparse.ArgumentParser('description Elitech RC-4 / RC-5 data reader')
    parser.add_argument('-c', "--command", choices=['init', 'get', 'latest', 'simple-set', 'set', 'devinfo', 'clock', 'raw'])
    parser.add_argument('-i', "--interval", type=int)
    parser.add_argument("--upper_limit", type=float)
    parser.add_argument("--lower_limit", type=float)
    parser.add_argument("--station_no", type=int)
    parser.add_argument("--stop_button", choices=['y', 'n'])
    parser.add_argument("--delay", choices=['0.0', '0.5', '1.0', '1.5', '2.0', '2.5', '3.0', '3.5', '4.0', '4.5', '5.0', '5.5', '6.0'])
    parser.add_argument('--tone_set', choices=['y', 'n'])
    parser.add_argument('--alarm', choices=['x', '3', '10'])
    parser.add_argument('--temp_unit', choices=['C', 'F'])
    parser.add_argument('--temp_calibration', type=float)
    parser.add_argument('--time', type=str)
    parser.add_argument('--dev_num', type=str)
    parser.add_argument('--user_info', type=str)
    parser.add_argument('--page_size', type=int, help='for command get')
    parser.add_argument('--req', type=str, help='for raw command')
    parser.add_argument('--res_len', type=int, help='for raw command', default=1000)
    parser.add_argument('--value_only', help='for latest command', action='store_true')
    parser.add_argument('--ser_baudrate', help='serial port baudrate default=115000', default=115000, type=int)
    parser.add_argument('--ser_timeout', help='serial port reading timeout sec', default=5, type=int)
    parser.add_argument('serial_port')
    return parser.parse_args()




if __name__ == '__main__':
    main()

