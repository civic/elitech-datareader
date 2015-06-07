# coding: utf8

__author__ = 'civic'

import unittest
import elitech

from elitech.msg import _bin, _append_checksum
from elitech.msg import *
from datetime import timedelta
from io import BytesIO
import six

class DummySerial:
    def __init__(self, res, callback=None):
        if res:
            self.buf = BytesIO(res)
        else:
            self.buf = None
            self.callback = callback

        self.ba = None

    def write(self, ba):
        self.ba = ba

    def read(self, length):
        if self.buf:
            return self.buf.read(length)
        else:
            if six.PY2:
                return self.callback(length, [int(ord(b)) for b in self.ba])
            else:
                return self.callback(length, self.ba)

    def open(self):
        pass
    def close(self):
        pass

class DeviceTest(unittest.TestCase):
    def test_init(self):
        device = elitech.Device(None)
        device._ser = DummySerial(_bin("01 02 03"))

        res = device.init()
        self.assertEqual(res.msg, _bin('01 02 03'))

    def test_get_devinfo(self):
        device = elitech.Device(None)
        device._ser = DummySerial(_bin("55 02 01 28 0A 00 00 1E 02 58 FE D4 07 DF 05 0E "
                              "16 2F 04 02 07 DF 05 0E 07 38 0E 13 64 00 09 07 "
                              "DF 05 0E 16 2F 36 52 43 2D 34 20 44 61 74 61 20 "
                              "4C 6F 67 67 65 72 00 00 00 00 00 00 00 00 00 00 "
                              "00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 "
                              "00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 "
                              "00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 "
                              "00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 "
                              "00 00 00 00 00 00 00 00 00 00 39 39 30 30 31 31 "
                              "32 32 33 33 11 31 00 31 F1 00 00 00 00 00 00 B3"
                              ))

        res = device.get_devinfo()
        self.assertEqual(res.station_no, 2)
        self.assertEqual(res.rec_interval, time(0, 0, 30))
        self.assertEqual(res.upper_limit, 60.0)
        self.assertEqual(res.lower_limit, -30.0)
        self.assertEqual(res.last_online, datetime(2015, 5, 14, 22, 47, 4))
        self.assertEqual(res.work_sts, WorkStatus.STOP)
        self.assertEqual(res.start_time, datetime(2015,5,14, 7,56,14))
        self.assertEqual(res.stop_button, StopButton.ENABLE)
        self.assertEqual(res.rec_count, 9)
        self.assertEqual(res.current, datetime(2015,5,14,22,47,54))
        self.assertEqual(res.user_info, "RC-4 Data Logger")
        self.assertEqual(res.dev_num, "9900112233")
        self.assertEqual(res.delay, 1.5)
        self.assertEqual(res.tone_set, ToneSet.NONE)
        self.assertEqual(res.alarm, AlarmSetting.NONE)
        self.assertEqual(res.temp_unit, TemperatureUnit.C)
        self.assertEqual(res.temp_calibration, -1.5)

    def test_update(self):
        device = elitech.Device(None)
        device._ser = DummySerial(_bin("01 02 03"))

        req = ParamPutRequest(1)
        res = device.update(req)
        self.assertEqual(res.msg, _bin("01 02 03"))

    def test_get_data_header(self):
        device = elitech.Device(None)
        device._ser = DummySerial(_bin("55 0B 76 07 DF 05 0E 17 04 35 1F"))
        res = device.get_data_header(1)

        self.assertEqual(res.rec_count, 2934)
        self.assertEqual(res.start_time, datetime(2015, 5, 14, 23, 4, 53))

    def test_get_data_body_1page(self):
        device = elitech.Device(None)
        def callback(length, ba):
            if ba[0] == 0xCC:
                # devinfo
                return _bin("55 01 01 28 0A 01 02 03 02 58 FE D4 07 DF 0A 01 "
                            "00 00 00 02 07 DF 0A 01 00 00 00 13 64 00 0A 07 "
                            "DF 05 0E 16 2F 36 52 43 2D 34 20 44 61 74 61 20 "
                            "4C 6F 67 67 65 72 00 00 00 00 00 00 00 00 00 00 "
                            "00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 "
                            "00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 "
                            "00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 "
                            "00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 "
                            "00 00 00 00 00 00 00 00 00 00 39 39 30 30 31 31 "
                            "32 32 33 33 11 31 00 31 F1 00 00 00 00 00 00 FF"
                            )
            elif ba[0] == 0x33 and ba[2] == 0x01:
                # 温度データヘッダ
                return _append_checksum(_bin("55 00 0A 07 DF 0A 01 00 00 00"))

            elif ba[0] == 0x33 and ba[2] == 0x02:
                # 温度データボディ
                if ba[3] == 0:
                    # 1ページ目10件
                    return _bin("55 00 01 FF FF 00 03 00 04 00 05 00 06 00 07 00 08 00 09 00 0A 8C")

            raise ValueError("invalid request data length")
        device._ser = DummySerial(None, callback=callback)

        devinfo = DevInfoResponse()
        devinfo.station_no = 1
        devinfo.rec_count = 10
        devinfo.rec_interval = time(1, 2, 3)
        devinfo.start_time = datetime(2015, 10, 1, 0, 0, 0)

        dt = timedelta(hours=1, minutes=2, seconds=3)

        res = device.get_data()
        self.assertEqual(len(res), 10)
        self.assertEqual(res, [
            (1, devinfo.start_time + dt*0, 0.1),
            (2, devinfo.start_time + dt*1, -0.1),
            (3, devinfo.start_time + dt*2, 0.3),
            (4, devinfo.start_time + dt*3, 0.4),
            (5, devinfo.start_time + dt*4, 0.5),
            (6, devinfo.start_time + dt*5, 0.6),
            (7, devinfo.start_time + dt*6, 0.7),
            (8, devinfo.start_time + dt*7, 0.8),
            (9, devinfo.start_time + dt*8, 0.9),
            (10, devinfo.start_time + dt*9, 1.0),
        ])

    def test_get_data_body_2page(self):
        """ 2ページのデータ取得が行われる
        """
        device = elitech.Device(None)

        def callback(length, ba):
            if ba[0] == 0xCC:
                # devinfo
                return _bin("55 01 01 28 0A 01 02 03 02 58 FE D4 07 DF 0A 01 "
                              "00 00 00 02 07 DF 0A 01 00 00 00 13 64 00 6E 07 "
                              "DF 05 0E 16 2F 36 52 43 2D 34 20 44 61 74 61 20 "
                              "4C 6F 67 67 65 72 00 00 00 00 00 00 00 00 00 00 "
                              "00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 "
                              "00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 "
                              "00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 "
                              "00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 "
                              "00 00 00 00 00 00 00 00 00 00 39 39 30 30 31 31 "
                              "32 32 33 33 11 31 00 31 F1 00 00 00 00 00 00 FF"
                              )
            elif ba[0] == 0x33 and ba[2] == 0x01:
                # 温度データヘッダ
                return _append_checksum(_bin("55 00 6E 07 DF 0A 01 00 00 00"))
            elif ba[0] == 0x33 and ba[2] == 0x02:
                # 温度データボディ
                if ba[3] == 0:
                    # 1ページ目100件
                    return _bin("55 00 00 00 01 00 02 00 03 00 04 00 05 00 06 00 07 00 08 00 09 00 0A 00 0B 00 0C 00 0D "
                                "00 0E 00 0F 00 10 00 11 00 12 00 13 00 14 00 15 00 16 00 17 00 18 00 19 00 1A 00 1B 00 "
                                "1C 00 1D 00 1E 00 1F 00 20 00 21 00 22 00 23 00 24 00 25 00 26 00 27 00 28 00 29 00 2A "
                                "00 2B 00 2C 00 2D 00 2E 00 2F 00 30 00 31 00 32 00 33 00 34 00 35 00 36 00 37 00 38 00 "
                                "39 00 3A 00 3B 00 3C 00 3D 00 3E 00 3F 00 40 00 41 00 42 00 43 00 44 00 45 00 46 00 47 "
                                "00 48 00 49 00 4A 00 4B 00 4C 00 4D 00 4E 00 4F 00 50 00 51 00 52 00 53 00 54 00 55 00 "
                                "56 00 57 00 58 00 59 00 5A 00 5B 00 5C 00 5D 00 5E 00 5F 00 60 00 61 00 62 00 63 AB")
                elif ba[3] == 1:
                    # 2ページ目10件
                    return _bin("55 00 64 00 65 00 66 00 67 00 68 00 69 00 6A 00 6B 00 6C 00 6D 6A")
            raise ValueError("invalid request data length")

        device._ser = DummySerial(None, callback=callback)

        devinfo = DevInfoResponse()
        devinfo.station_no = 1
        devinfo.rec_count = 110
        devinfo.rec_interval = time(1, 2, 3)
        devinfo.start_time = datetime(2015, 10, 1, 0, 0, 0)

        dt = timedelta(hours=1, minutes=2, seconds=3)

        res = device.get_data()
        self.assertEqual(len(res), 110)

        expect = []
        for n in range(110):
            expect.append((n+1, devinfo.start_time + dt*n, n / 10.0))

        self.assertEqual(res, expect)


