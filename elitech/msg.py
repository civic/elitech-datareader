__author__ = 'civic'

from struct import unpack, pack
from datetime import datetime, time
from enum import Enum
import six

def _bin(s):
    """
    :rtype: bytes
    """
    return bytes([int(b, 16) for b in s.split(" ")])

def _intarray2bytes(int_array):
    return bytes(int_array)

if six.PY2:
    def py2bin(s):
        return "".join([chr(int(b, 16)) for b in s.split(" ")])
    def py2intarray2bytes(int_array):
        return "".join([chr(b) for b in int_array])

    _bin = py2bin
    _intarray2bytes = py2intarray2bytes

def _datetime_unpack(date_bytes):
    """
    :rtype: datetime
    """
    try:
        return datetime(*unpack(">h5b", date_bytes))
    except ValueError:
        return None

def _datetime_pack(dt):
    """
    :type dt: datetime
    :rtype: bytes
    """
    return _intarray2bytes([(dt.year&0xFF00)>>8, dt.year&0x00FF, dt.month, dt.day, dt.hour, dt.minute, dt.second])

def _interval_unpack(time_bytes):
    """
    :rtype: time
    """
    try:
        return time(*unpack(">3b", time_bytes))
    except Exception:
        return None

def _interval_pack(t):
    """
    :param t: time.time
    :return: bytes
    """
    return _intarray2bytes([t.hour, t.minute, t.second])


def _append_checksum(byte_array):
    if six.PY2:
        checksum = sum([ord(c) for c in byte_array]) % 0x100
    else:
        checksum = sum(byte_array) % 0x100

    return byte_array + _intarray2bytes([checksum])


class TemperatureUnit(Enum):
    C = 0x31
    F = 0x13


class ToneSet(Enum):
    PERMIT = 0x13
    NONE = 0x31


class StopButton(Enum):
    ENABLE = 0x13
    DISABLE = 0x31


class AlarmSetting(Enum):
    NONE = 0x00
    T3 = 0x03
    T10 = 0x0A


class WorkStatus(Enum):
    NOT_START = 0x00
    START = 0x01
    STOP = 0x02
    DELAY_START = 0x03


class RequestMessage:
    def to_bytes(self):
        pass


class ResponseMessage:
    def read(self, ser):
        """
        :type ser: serial.Serial
        """
        pass


class InitRequest(RequestMessage):
    def to_bytes(self):
        return _bin("CC 00 0A 00 D6")


class InitResponse(ResponseMessage):
    """
    :type msg: bytes
    """

    def __init__(self):
        self.msg = None

    def read(self, ser):
        """
        :type ser: serial.Serial
        """
        self.msg = ser.read(3)


class DevInfoRequest(RequestMessage):

    def to_bytes(self):
        return _bin("CC 00 06 00 D2")


class DevInfoResponse(ResponseMessage):
    """
    :type station_no: int
    :type model_no: int
    :type rec_interval: time
    :type upper_limit: float
    :type lower_limit: float
    :type last_online: datetime
    :type work_sts: WorkStatus
    :type start_time: datetime
    :type stop_button: StopButton
    :type rec_count: int
    :type current:datetime
    :type user_info:str
    :type dev_num:str
    :type delay: float
    :type tone_set: ToneSet
    :type alarm: AlarmSetting
    :type temp_unit: TemperatureUnit
    :type temp_calibration: float
    """

    def __init__(self):
        self.station_no = None
        self.rec_interval = None
        self.model_no = None
        self.upper_limit = None
        self.lower_limit = None
        self.last_online = None
        self.work_sts = None
        self.start_time = None
        self.stop_button = None
        self.rec_count = None
        self.current = None
        self.user_info = None
        self.dev_num = None
        self.delay = None
        self.tone_set = None
        self.alarm = None
        self.temp_unit = None
        self.temp_calibration = None

    def read(self, ser):
        """
        :type ser: serial.Serial
        """
        res = ser.read(160)

        (_, station_no, _, model_no, _, rec_interval, upper_limit, lower_limit, last_online, work_sts,
         start_time, stp_btn, _, rec_count, current, user_info, dev_num, delay, tone_set,
         alarm, temp_unit, temp_calib, _) = unpack(
            '>1s'
            'B'  # station no
            '1s'
            'B'  # model_no
            '1s'
            '3s'  # record interval hh mm ss
            'h'  # upper limit
            'h'  # lower limit
            '7s'  # last_online
            'b'  # work_status
            '7s'  # start_time
            'b'  # stopbutton permit=0x13, prohibit=0x31
            'b'
            'h'  # record_count
            '7s'  # current_time
            '100s'  # info
            '10s'  # device number
            'b'  # delaytime
            'b'  # tone set
            'b'  # alarm
            'b'  # temp unit
            'b'  # temp calibration
            '7s',
            res)

        self.station_no = station_no
        self.model_no = model_no
        self.rec_interval = _interval_unpack(rec_interval)
        self.upper_limit = upper_limit / 10.0
        self.lower_limit = lower_limit / 10.0
        self.last_online = _datetime_unpack(last_online)
        self.work_sts = WorkStatus(work_sts)
        self.start_time = _datetime_unpack(start_time)
        self.stop_button = StopButton(stp_btn)
        self.rec_count = rec_count
        self.current = _datetime_unpack(current)
        try:
            self.user_info = user_info.decode("utf-8").rstrip("\x00")
        except UnicodeDecodeError as e:
            self.user_info = ""
        try:
            self.dev_num = dev_num.decode("utf-8").rstrip('\0x00')
        except UnicodeDecodeError as e:
            self.dev_num = ""

        if delay in [0x00, 0x01, 0x10, 0x11, 0x20, 0x21]:
            self.delay = int(delay / 16.0) + 0.5 * (delay % 16)
        else:
            self.delay = 0.0

        try:
            self.tone_set = ToneSet(tone_set)
        except ValueError:
            self.tone_set = ToneSet.NONE

        try:
            self.alarm = AlarmSetting(alarm)
        except ValueError:
            self.alarm = AlarmSetting.NONE

        try:
            self.temp_unit = TemperatureUnit(temp_unit)
        except ValueError:
            self.temp_unit = TemperatureUnit.C

        self.temp_calibration = temp_calib / 10.0

    def to_param_put(self):
        """
        convert dev_info to ParamPutRequest message.
        :rtype : ParamPutRequest
        """
        req = ParamPutRequest(self.station_no)
        req.rec_interval = self.rec_interval or time(0, 0, 30)
        req.upper_limit = self.upper_limit
        req.lower_limit = self.lower_limit
        req.update_station_no = self.station_no
        req.stop_button = self.stop_button
        req.delay = self.delay
        req.tone_set = self.tone_set
        req.alarm = self.alarm
        req.temp_unit = self.temp_unit
        req.temp_calibration = self.temp_calibration

        return req


class ParamPutRequest(RequestMessage):
    """
    :type target_station_no: int
    :type rec_interval: time
    :type upper_limit: float
    :type lower_limit: float
    :type update_station_no: int
    :type stop_button: StopButton
    :type delay: float
    :type tone_set: ToneSet
    :type alarm: AlarmSetting
    :type temp_unit: TemperatureUnit
    :type temp_calibration: float
    """

    def __init__(self, target_station_no):
        self.target_station_no = target_station_no
        self.rec_interval = time(0, 10, 0)

        self.upper_limit = 60.0
        self.lower_limit = -30.0
        self.update_station_no = 1

        self.stop_button = StopButton.DISABLE
        self.delay = 0
        self.tone_set = ToneSet.NONE
        self.alarm = AlarmSetting.NONE
        self.temp_unit = TemperatureUnit.C
        self.temp_calibration = 0

    def to_bytes(self):
        write_bytes = pack(
            ">b"  # 0x33
            "B"  # target station no
            "2s"  # 0x0500
            "3s"  # record interval
            "h"  # upper limit
            "h"  # lower limit
            "B"  # update station no
            "b"  # stopbutton permit=0x13, prohibit=0x31
            "b"  # delaytime
            "b"  # tone set
            "b"  # alarm
            'b'  # temp unit
            'b'  # temp calibration
            "6s",
            0x33,
            self.target_station_no,
            _bin('05 00'),
            _interval_pack(self.rec_interval),
            int(self.upper_limit * 10.0),
            int(self.lower_limit * 10.0),
            self.update_station_no,
            self.stop_button.value,
            int(self.delay) * 16 + (5 if (self.delay % 1 != 0) else 0),
            self.tone_set.value,
            self.alarm.value,
            self.temp_unit.value,
            int(self.temp_calibration * 10.0),
            _bin('00 00 00 00 00 00'),
        )

        ba = _append_checksum(write_bytes)
        return ba


class ParamPutResponse(ResponseMessage):
    def __init__(self):
        self.msg = None

    def read(self, ser):
        """
        :type ser: serial.Serial
        """
        self.msg = ser.read(3)


class DataHeaderRequest(RequestMessage):
    def __init__(self, target_station_no):
        self.target_station_no = target_station_no

    def to_bytes(self):
        write_bytes = pack(
            ">b"    # 0x33
            "B"     # target station no
            "b"     # command: datahead 0x01
            "B",    # page number 0x00
            0x33, self.target_station_no, 0x01, 0x00)

        return _append_checksum(write_bytes)

class DataHeaderResponse(ResponseMessage):
    """
    :type rec_count: int
    :type start_time: datetime
    """
    def __init__(self):
        self.rec_count = 0
        self.start_time = None

    def read(self, ser):
        """
        :type ser: serial.Serial
        """
        res = ser.read(11)

        (_, rec_count, start_time, _) = unpack(
            '>1s'
            'h'  # record_count
            '7s'  # current_time
            'b',
            res)

        self.start_time = _datetime_unpack(start_time)
        self.rec_count = rec_count

class DataBodyRequest(RequestMessage):
    def __init__(self, target_station_no, page_num):
        self.target_station_no = target_station_no
        self.page_num = page_num

    def to_bytes(self):
        write_bytes = pack(
            ">b"    # 0x33
            "B"     # target station no
            "b"     # command databody 0x02
            "B",    # page number
            0x33, self.target_station_no, 0x02, self.page_num)

        return _append_checksum(write_bytes)

class DataBodyResponse(ResponseMessage):
    """
    :type count: int
    :type records: list
    :type start_time: datetime
    """
    def __init__(self, count):
        self.count = count
        self.records = None

    def read(self, ser):
        """
        :type ser: serial.Serial
        """
        res = ser.read(self.count * 2 + 2)  #data(2bytes)*count + (comand:0x55 + checksum)

        unpacked = unpack(
            '>1s'+('h'*self.count)+"b",
            res)

        self.records = unpacked[1:-1]

class ClockSetRequest(RequestMessage):
    def __init__(self, target_station_no, set_time=None):
        self.target_station_no = target_station_no
        self.set_time = set_time if set_time is not None else datetime.now()

    def to_bytes(self):
        write_bytes = pack(
            ">b"  # 0x33
            "B"  # target station no
            "2s"  # 0x0700
            "7s",  # set time
            0x33,
            self.target_station_no,
            _bin('07 00'),
            _datetime_pack(self.set_time),
            )

        ba = _append_checksum(write_bytes)
        return ba

class ClockSetResponse(ResponseMessage):
    """
    :type msg: bytes
    """

    def __init__(self):
        self.msg = None

    def read(self, ser):
        """
        :type ser: serial.Serial
        """
        self.msg = ser.read(3)

class DevNumRequest(RequestMessage):
    """
    :type target_station_no: int
    :type device_number: str
    """

    def __init__(self, target_station_no):
        self.target_station_no = target_station_no
        self.device_number = "1234567890"

    def to_bytes(self):
        write_bytes = pack(
            ">b"  # 0x33
            "B"  # target station no
            "2s"  # 0x0B00
            "10s",  # device_number
            0x33,
            self.target_station_no,
            _bin('0B 00'),
            self.device_number.encode("utf8")[:10],
            )

        ba = _append_checksum(write_bytes)
        return ba

class DevNumResponse(ResponseMessage):
    def __init__(self):
        self.msg = None

    def read(self, ser):
        """
        :type ser: serial.Serial
        """
        self.msg = ser.read(3)

class UserInfoRequest(RequestMessage):
    """
    :type target_station_no: int
    :type user_info: str
    """

    def __init__(self, target_station_no):
        self.target_station_no = target_station_no
        self.user_info = ""

    def to_bytes(self):
        write_bytes = pack(
            ">b"  # 0x33
            "B"  # target station no
            "2s"  # 0x0900
            "100s",  # device_number
            0x33,
            self.target_station_no,
            _bin('09 00'),
            self.user_info.encode("utf8")[:100],
        )

        ba = _append_checksum(write_bytes)
        return ba

class UserInfoResponse(ResponseMessage):
    def __init__(self):
        self.msg = None

    def read(self, ser):
        """
        :type ser: serial.Serial
        """
        self.msg = ser.read(3)
