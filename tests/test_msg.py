# coding: utf8

__author__ = 'civic'

import unittest
from io import BytesIO

from elitech.msg import (
    _bin,
    _datetime_unpack,
    _interval_unpack,
    _interval_pack,
    _append_checksum,
)
from elitech.msg import *
from six import (
    b,
)

class TestFunctions(unittest.TestCase):
    def test_bin(self):
        self.assertEqual(_bin("01 02 FF AB"), b'\x01\x02\xFF\xAB')
        self.assertEqual(_bin("01"), b'\x01')

    def test_datetime_unpack(self):
        self.assertEqual(_datetime_unpack(b'\x07\xDF\x05\x0E\x07\x38\x0E'), datetime(2015, 5, 14, 7, 56, 14))

    def test_interval_unpack(self):
        self.assertEqual(_interval_unpack(b'\x01\x02\x03'), time(1, 2, 3))

    def test_interval_pack(self):
        self.assertEqual(_interval_pack(time(1, 2,3 )), b'\x01\x02\x03')

    def test_append_checksum(self):
        self.assertEqual(_append_checksum(b'\x01\x02\x03'), b'\x01\x02\x03\x06')
        self.assertEqual(_append_checksum(b'\xF0\x0A\x09'), b'\xF0\x0A\x09\x03')

class TestMessages(unittest.TestCase):
    def test_InitRequest(self):
        self.assertEqual(InitRequest().to_bytes(), _bin("CC 00 0A 00 D6"))

    def test_InitResponse(self):
        res = InitResponse()
        res.read(BytesIO(_bin("01 02 03")))
        self.assertEqual(res.msg, b'\x01\x02\x03')

    def test_DevInfoRequest(self):
        self.assertEqual(DevInfoRequest().to_bytes(), _bin("CC 00 06 00 D2"))

    def test_DevInfoResponse(self):
        res = DevInfoResponse()
        res.read(BytesIO(_bin("55 02 01 28 0A 00 00 1E 02 58 FE D4 07 DF 05 0E "
                              "16 2F 04 02 07 DF 05 0E 07 38 0E 13 64 00 09 07 "
                              "DF 05 0E 16 2F 36 52 43 2D 34 20 44 61 74 61 20 "
                              "4C 6F 67 67 65 72 00 00 00 00 00 00 00 00 00 00 "
                              "00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 "
                              "00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 "
                              "00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 "
                              "00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 "
                              "00 00 00 00 00 00 00 00 00 00 39 39 30 30 31 31 "
                              "32 32 33 33 11 31 00 31 F1 00 00 00 00 00 00 B3"
                              )))
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

    def test_to_param_put(self):
        res = DevInfoResponse()
        res.read(BytesIO(_bin("55 02 01 28 0A 00 00 1E 02 58 FE D4 07 DF 05 0E "
                              "16 2F 04 02 07 DF 05 0E 07 38 0E 13 64 00 09 07 "
                              "DF 05 0E 16 2F 36 52 43 2D 34 20 44 61 74 61 20 "
                              "4C 6F 67 67 65 72 00 00 00 00 00 00 00 00 00 00 "
                              "00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 "
                              "00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 "
                              "00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 "
                              "00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 "
                              "00 00 00 00 00 00 00 00 00 00 39 39 30 30 31 31 "
                              "32 32 33 33 11 31 00 31 F1 00 00 00 00 00 00 B3"
                              )))
        param_put = res.to_param_put()
        self.assertEqual(param_put.rec_interval, time(0, 0, 30))
        self.assertEqual(param_put.target_station_no, 2)
        self.assertEqual(param_put.update_station_no, 2)
        self.assertEqual(param_put.rec_interval, time(0, 0, 30))
        self.assertEqual(param_put.upper_limit, 60.0)
        self.assertEqual(param_put.lower_limit, -30.0)
        self.assertEqual(param_put.stop_button, StopButton.ENABLE)
        self.assertEqual(param_put.delay, 1.5)
        self.assertEqual(param_put.tone_set, ToneSet.NONE)
        self.assertEqual(param_put.alarm, AlarmSetting.NONE)
        self.assertEqual(param_put.temp_unit, TemperatureUnit.C)
        self.assertEqual(param_put.temp_calibration, -1.5)

    def test_ParamPutRequest(self):
        req = ParamPutRequest(2)
        req.rec_interval = time(0, 0, 30)
        req.update_station_no = 2
        req.stop_button = StopButton.ENABLE
        req.delay = 0
        req.temp_calibration = -1.5

        self.assertEqual(req.to_bytes(), _bin("33 02 05 00 00 00 1E 02 58 FE D4 02 13 00 31 00 "
                                               "31 F1 00 00 00 00 00 00 EC"))

    def test_ParamPutResponse(self):
        res = ParamPutResponse()
        res.read(BytesIO(_bin("01 02 03")))
        self.assertTrue(res.msg, b'\x01\x02\x03')

    def test_DataHeaderRequest(self):
        req = DataHeaderRequest(123)
        self.assertEqual(req.to_bytes(), _bin("33 7B 01 00 AF"))

    def test_DataHeaderResponse(self):
        res = DataHeaderResponse()
        res.read(BytesIO(_bin("55 0B 76 07 DF 05 0E 17 04 35 1F")))
        self.assertEqual(res.rec_count, 2934)
        self.assertEqual(res.start_time, datetime(2015, 5, 14, 23, 4, 53))

    def test_DataBodyRequest(self):
        req = DataBodyRequest(123, 5)
        self.assertEqual(req.to_bytes(), _bin("33 7B 02 05 B5"))

    def test_DataBodyResponse(self):
        res = DataBodyResponse(10)
        res.read(BytesIO(_bin("55 00 01 FF FF 00 03 00 04 00 05 00 06 00 07 00 08 00 09 00 0A 8C")))
        self.assertEqual(len(res.records), 10)
        self.assertEqual(res.records, (1, -1, 3, 4, 5, 6, 7, 8, 9, 10))

if __name__ == '__main__':
    unittest.main()
