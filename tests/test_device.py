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
        self.assertEqual(res.model_no, 40)
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
        devinfo.model_no = 40
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

    def test_get_data_body_2page_RC5(self):
        """ RC5の2ページのデータ取得が行われる(1ページあたり500件)
        """
        device = elitech.Device(None)

        def callback(length, ba):
            if ba[0] == 0xCC:
                # devinfo
                return _bin("55 01 01 32 0A 01 02 03 02 58 FE D4 07 DF 0A 01 "
                            "00 00 00 02 07 DF 0A 01 00 00 00 13 64 01 FE 07 "
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
                return _append_checksum(_bin("55 01 FE 07 DF 0A 01 00 00 00"))
            elif ba[0] == 0x33 and ba[2] == 0x02:
                # 温度データボディ
                if ba[3] == 0:
                    # 1ページ目500件
                    return _bin("55 00 00 00 01 00 02 00 03 00 04 00 05 00 06 00 07 00 08 00 09 00 0A 00 0B 00 0C 00 0D "
                                "00 0E 00 0F 00 10 00 11 00 12 00 13 00 14 00 15 00 16 00 17 00 18 00 19 00 1A 00 1B 00 "
                                "1C 00 1D 00 1E 00 1F 00 20 00 21 00 22 00 23 00 24 00 25 00 26 00 27 00 28 00 29 00 2A "
                                "00 2B 00 2C 00 2D 00 2E 00 2F 00 30 00 31 00 32 00 33 00 34 00 35 00 36 00 37 00 38 00 "
                                "39 00 3A 00 3B 00 3C 00 3D 00 3E 00 3F 00 40 00 41 00 42 00 43 00 44 00 45 00 46 00 47 "
                                "00 48 00 49 00 4A 00 4B 00 4C 00 4D 00 4E 00 4F 00 50 00 51 00 52 00 53 00 54 00 55 00 "
                                "56 00 57 00 58 00 59 00 5A 00 5B 00 5C 00 5D 00 5E 00 5F 00 60 00 61 00 62 00 63 00 64 "
                                "00 65 00 66 00 67 00 68 00 69 00 6A 00 6B 00 6C 00 6D 00 6E 00 6F 00 70 00 71 00 72 00 "
                                "73 00 74 00 75 00 76 00 77 00 78 00 79 00 7A 00 7B 00 7C 00 7D 00 7E 00 7F 00 80 00 81 "
                                "00 82 00 83 00 84 00 85 00 86 00 87 00 88 00 89 00 8A 00 8B 00 8C 00 8D 00 8E 00 8F 00 "
                                "90 00 91 00 92 00 93 00 94 00 95 00 96 00 97 00 98 00 99 00 9A 00 9B 00 9C 00 9D 00 9E "
                                "00 9F 00 A0 00 A1 00 A2 00 A3 00 A4 00 A5 00 A6 00 A7 00 A8 00 A9 00 AA 00 AB 00 AC 00 "
                                "AD 00 AE 00 AF 00 B0 00 B1 00 B2 00 B3 00 B4 00 B5 00 B6 00 B7 00 B8 00 B9 00 BA 00 BB "
                                "00 BC 00 BD 00 BE 00 BF 00 C0 00 C1 00 C2 00 C3 00 C4 00 C5 00 C6 00 C7 00 C8 00 C9 00 "
                                "CA 00 CB 00 CC 00 CD 00 CE 00 CF 00 D0 00 D1 00 D2 00 D3 00 D4 00 D5 00 D6 00 D7 00 D8 "
                                "00 D9 00 DA 00 DB 00 DC 00 DD 00 DE 00 DF 00 E0 00 E1 00 E2 00 E3 00 E4 00 E5 00 E6 00 "
                                "E7 00 E8 00 E9 00 EA 00 EB 00 EC 00 ED 00 EE 00 EF 00 F0 00 F1 00 F2 00 F3 00 F4 00 F5 "
                                "00 F6 00 F7 00 F8 00 F9 00 FA 00 FB 00 FC 00 FD 00 FE 00 FF 01 00 01 01 01 02 01 03 01 04 01 "
                                "05 01 06 01 07 01 08 01 09 01 0A 01 0B 01 0C 01 0D 01 0E 01 0F 01 10 01 11 01 12 01 13 "
                                "01 14 01 15 01 16 01 17 01 18 01 19 01 1A 01 1B 01 1C 01 1D 01 1E 01 1F 01 20 01 21 01 "
                                "22 01 23 01 24 01 25 01 26 01 27 01 28 01 29 01 2A 01 2B 01 2C 01 2D 01 2E 01 2F 01 30 "
                                "01 31 01 32 01 33 01 34 01 35 01 36 01 37 01 38 01 39 01 3A 01 3B 01 3C 01 3D 01 3E 01 "
                                "3F 01 40 01 41 01 42 01 43 01 44 01 45 01 46 01 47 01 48 01 49 01 4A 01 4B 01 4C 01 4D "
                                "01 4E 01 4F 01 50 01 51 01 52 01 53 01 54 01 55 01 56 01 57 01 58 01 59 01 5A 01 5B 01 "
                                "5C 01 5D 01 5E 01 5F 01 60 01 61 01 62 01 63 01 64 01 65 01 66 01 67 01 68 01 69 01 6A "
                                "01 6B 01 6C 01 6D 01 6E 01 6F 01 70 01 71 01 72 01 73 01 74 01 75 01 76 01 77 01 78 01 "
                                "79 01 7A 01 7B 01 7C 01 7D 01 7E 01 7F 01 80 01 81 01 82 01 83 01 84 01 85 01 86 01 87 "
                                "01 88 01 89 01 8A 01 8B 01 8C 01 8D 01 8E 01 8F 01 90 01 91 01 92 01 93 01 94 01 95 01 "
                                "96 01 97 01 98 01 99 01 9A 01 9B 01 9C 01 9D 01 9E 01 9F 01 A0 01 A1 01 A2 01 A3 01 A4 "
                                "01 A5 01 A6 01 A7 01 A8 01 A9 01 AA 01 AB 01 AC 01 AD 01 AE 01 AF 01 B0 01 B1 01 B2 01 "
                                "B3 01 B4 01 B5 01 B6 01 B7 01 B8 01 B9 01 BA 01 BB 01 BC 01 BD 01 BE 01 BF 01 C0 01 C1 "
                                "01 C2 01 C3 01 C4 01 C5 01 C6 01 C7 01 C8 01 C9 01 CA 01 CB 01 CC 01 CD 01 CE 01 CF 01 "
                                "D0 01 D1 01 D2 01 D3 01 D4 01 D5 01 D6 01 D7 01 D8 01 D9 01 DA 01 DB 01 DC 01 DD 01 DE "
                                "01 DF 01 E0 01 E1 01 E2 01 E3 01 E4 01 E5 01 E6 01 E7 01 E8 01 E9 01 EA 01 EB 01 EC 01 "
                                "ED 01 EE 01 EF 01 F0 01 F1 01 F2 01 F3 A3"
                                )
                elif ba[3] == 1:
                    # 2ページ目10件
                    return _bin("55 01 F4 01 F5 01 F6 01 F7 01 F8 01 F9 01 FA 01 FB 01 FC 01 FD BF")

            raise ValueError("invalid request data length")

        device._ser = DummySerial(None, callback=callback)

        devinfo = DevInfoResponse()
        devinfo.station_no = 1
        devinfo.rec_count = 510
        devinfo.rec_interval = time(1, 2, 3)
        devinfo.start_time = datetime(2015, 10, 1, 0, 0, 0)

        dt = timedelta(hours=1, minutes=2, seconds=3)

        res = device.get_data()
        self.assertEqual(len(res), 510)

        expect = []
        for n in range(510):
            expect.append((n+1, devinfo.start_time + dt*n, n / 10.0))

        self.assertEqual(res, expect)

    def test_set_clock(self):
        device = elitech.Device(None)

        device._ser = DummySerial(_bin("55 A3 F8"))
        res = device.set_clock(123, datetime(2015, 1, 2, 10, 20, 30))

        self.assertEqual(res.msg, _bin("55 A3 F8"))

    def test_set_device_number(self):
        device = elitech.Device(None)
        device._ser = DummySerial(_bin("01 02 03"))

        res = device.set_device_number(1, "1122334455")
        self.assertEqual(res.msg, _bin("01 02 03"))

    def test_set_user_info(self):
        device = elitech.Device(None)
        device._ser = DummySerial(_bin("01 02 03"))

        res = device.set_user_info(1, "1122334455")
        self.assertEqual(res.msg, _bin("01 02 03"))

    def test_raw_send(self):
        device = elitech.Device(None)
        device._ser = DummySerial(_bin("01 02 03"))
        res = device.raw_send(_bin('11 12 13'), 3)
        self.assertEqual(res, _bin("01 02 03"))

    def test_get_latest(self):
        """ 最新データ取得が行われる
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

        res = device.get_latest()

        expect = []
        for n in range(110):
            expect.append((n+1, devinfo.start_time + dt*n, n / 10.0))

        self.assertEqual(res, (110, devinfo.start_time + dt*109, 10.9))
