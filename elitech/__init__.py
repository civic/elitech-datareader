__author__ = 'civic'

from serial import Serial

import time
from datetime import (
    datetime,
    timedelta
)
import serial
import math

from .msg import (
    AlarmSetting,
    StopButton,
    TemperatureUnit,
    ToneSet,
    WorkStatus,
    RequestMessage,
    ResponseMessage,
    InitRequest,
    InitResponse,
    DevInfoRequest,
    DevInfoResponse,
    ParamPutRequest,
    ParamPutResponse,
    DataHeaderRequest,
    DataHeaderResponse,
    DataBodyRequest,
    DataBodyResponse,
    ClockSetRequest,
    ClockSetResponse,
    DevNumRequest,
    DevNumResponse,
    UserInfoRequest,
    UserInfoResponse,
)
import six

class Device:
    def __init__(self, serial_port, baudrate=115000, timeout=5):
        if serial_port is not None:
            self._ser = serial.Serial(serial_port, baudrate=baudrate, timeout=timeout)
            self._ser.close()
        self.debug = False
        self.wait_time = 0.5

    def _talk(self, request, response):
        """
        :type request: RequestMessage
        """
        ba = request.to_bytes()

        if (self.debug):
            print("\nba length={}".format(len(ba)))
            for i, b in enumerate(ba):
                if six.PY2:
                    six.print_("{:02X} ".format(ord(b)), sep='', end='')
                else:
                    six.print_("{:02X} ".format(b), end='')
                if (i + 1) % 16 == 0:
                    six.print_()
            six.print_()

        self._ser.write(ba)

        response.read(self._ser)

        return response

    def init(self):
        """
        :rtype: InitResponse
        """
        req = InitRequest()

        try:
            self._ser.open()
            res = self._talk(req, InitResponse())
        finally:
            self._ser.close()
            time.sleep(self.wait_time)

        return res

    def get_devinfo(self):
        """
        :rtype: DevInfoResponse
        """
        req = DevInfoRequest()
        try:
            self._ser.open()
            res = self._talk(req, DevInfoResponse())
        finally:
            self._ser.close()
            time.sleep(self.wait_time)

        return res

    def update(self, req):
        """
        :type req: ParamPutRequest
        :rtype: ParamPutResponse
        """
        try:
            self._ser.open()
            res = self._talk(req, ParamPutResponse())
        finally:
            self._ser.close()
            time.sleep(self.wait_time)

        return res

    def get_data(self, callback=None, page_size=None):
        """
        :type devinfo: DevInfoResponse
        :rtype:list[(int,datetime,float)]
        """
        devinfo = self.get_devinfo()
        header = self.get_data_header(devinfo.station_no)

        if page_size is None:
            if devinfo.model_no == 40: # RC-4
                page_size = 100
            elif devinfo.model_no == 50: #RC-5
                page_size = 500
            else:
                raise ValueError("Unknowm model_no (%d). can't decide page_size", devinfo.model_no)

        page = int(math.ceil(header.rec_count / float(page_size)))
        dt = timedelta(hours=devinfo.rec_interval.hour,
                      minutes=devinfo.rec_interval.minute,
                      seconds=devinfo.rec_interval.second)

        data_list = []
        base_time = devinfo.start_time
        no = 1
        try:
            self._ser.open()
            for p in range(page):

                req = DataBodyRequest(devinfo.station_no, p)
                count = page_size if (p+1) * page_size <= devinfo.rec_count else (devinfo.rec_count % page_size)
                res = DataBodyResponse(count)
                self._talk(req, res)

                for rec in res.records:
                    data_list.append((no, base_time, rec/10.0))
                    no += 1
                    base_time += dt
                if callback is not None:
                    callback(data_list)
                    data_list = []
        finally:
            self._ser.close()
            time.sleep(self.wait_time)

        return data_list

    def get_data_header(self, target_station_no):
        """
        :rtype: DataHeaderResponse
        """
        try:
            self._ser.open()
            req = DataHeaderRequest(target_station_no)
            res = self._talk(req, DataHeaderResponse())
        finally:
            self._ser.close()
            time.sleep(self.wait_time)

        return res

    def set_clock(self, station_no, set_time=None):
        """
        :type station_no: int
        :type set_time: datetime
        :rtype:ClockSetResponse
        """
        try:
            self._ser.open()
            if set_time is None:
                set_time = datetime.now()
            req = ClockSetRequest(station_no, set_time)
            res = ClockSetResponse()
            self._talk(req, res)
        finally:
            self._ser.close()
            time.sleep(self.wait_time)
        return res

    def set_device_number(self, station_no, device_number):
        """
        :type station_no: int
        :type device_number: string
        :rtype:DevNumResponse
        """
        try:
            self._ser.open()
            req = DevNumRequest(station_no)
            req.device_number = device_number
            res = self._talk(req, DevNumResponse())
        finally:
            self._ser.close()
            time.sleep(self.wait_time)

        return res

    def set_user_info(self, station_no, user_info):
        """
        :type station_no: int
        :type user_info: string
        :rtype: UserInfo
        """
        try:
            self._ser.open()
            req = UserInfoRequest(station_no)
            req.user_info = user_info
            res = self._talk(req, UserInfoResponse())
        finally:
            self._ser.close()
            time.sleep(self.wait_time)

        return res

    def raw_send(self, request_bytes, response_length):
        request = RequestMessage()
        request.to_bytes = lambda : request_bytes

        response = ResponseMessage()

        response.msg = None
        def __read(ser):
            response.msg = ser.read(response_length)

        response.read = __read

        try:
            self._ser.open()
            self._talk(request, response)
        finally:
            self._ser.close()
            time.sleep(self.wait_time)

        return response.msg

    def get_latest(self, callback=None, page_size=None):
        """
        :type devinfo: DevInfoResponse
        :rtype:list[(int,datetime,float)]
        """
        devinfo = self.get_devinfo()
        header = self.get_data_header(devinfo.station_no)

        if page_size is None:
            if devinfo.model_no == 40: # RC-4
                page_size = 100
            elif devinfo.model_no == 50: #RC-5
                page_size = 500
            else:
                raise ValueError("Unknowm model_no (%d). can't decide page_size", devinfo.model_no)

        page = int(math.ceil(header.rec_count / float(page_size)))
        dt = timedelta(hours=devinfo.rec_interval.hour,
                       minutes=devinfo.rec_interval.minute,
                       seconds=devinfo.rec_interval.second)


        base_time = devinfo.start_time + dt * (header.rec_count-1)

        no = header.rec_count
        try:
            self._ser.open()

            p = page - 1
            req = DataBodyRequest(devinfo.station_no, p)
            count = page_size if (p+1) * page_size <= devinfo.rec_count else (devinfo.rec_count % page_size)

            res = DataBodyResponse(count)
            self._talk(req, res)

            rec = res.records[-1]
            latest = (no, base_time, rec/10.0)
            if callback is not None:
                callback(latest)
        finally:
            self._ser.close()
            time.sleep(self.wait_time)

        return latest


