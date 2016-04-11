# coding: utf8

__author__ = 'civic'

import unittest
from io import BytesIO

from elitech.msg import (
    _bin,
    _datetime_unpack,
    _datetime_pack,
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

    def test_datetime_pack(self):
        self.assertEqual(_datetime_pack(datetime(2015,1,2,3,4,5)), b'\x07\xDF\x01\x02\x03\x04\x05')

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
        res.read(BytesIO(_bin("55 82 01 28 0A 00 00 1E 02 58 FE D4 07 DF 05 0E "
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
        self.assertEqual(res.station_no, 130)
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

    def test_DevInfoResponse_devnum_default_is_FF(self):
        res = DevInfoResponse()
        res.read(BytesIO(_bin("55 02 01 28 0A 00 00 1E 02 58 FE D4 07 DF 05 0E "
                              "16 2F 04 02 07 DF 05 0E 07 38 0E 13 64 00 09 07 "
                              "DF 05 0E 16 2F 36 52 43 2D 34 20 44 61 74 61 20 "
                              "4C 6F 67 67 65 72 00 00 00 00 00 00 00 00 00 00 "
                              "00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 "
                              "00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 "
                              "00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 "
                              "00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 "
                              "00 00 00 00 00 00 00 00 00 00 FF FF FF FF FF FF "
                              "FF FF FF FF 11 31 00 31 F1 00 00 00 00 00 00 B3"
                              )))
        self.assertEqual(res.dev_num, "")

    def test_DevInfoResponse_virgin_device(self):
        res = DevInfoResponse()
        res.read(BytesIO(_bin("55 02 01 28 0A FF FF FF 02 58 FE D4 07 DF 05 0E "
                              "16 2F 04 02 FF FF 05 0E 07 38 0E 13 64 00 09 07 "
                              "DF 05 0E 16 2F 36 FF FF FF FF FF FF FF FF FF FF "
                              "4C 6F 67 67 65 72 00 00 00 00 00 00 00 00 00 00 "
                              "00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 "
                              "00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 "
                              "00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 "
                              "00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 "
                              "00 00 00 00 00 00 00 00 00 00 FF FF FF FF FF FF "
                              "FF FF FF FF FF FF FF FF FF FF FF FF FF FF 00 B3"
                              )))
        self.assertIsNone(res.rec_interval)
        self.assertIsNone(res.start_time)

    def test_to_param_put(self):
        res = DevInfoResponse()
        res.read(BytesIO(_bin("55 82 01 28 0A 00 00 1E 02 58 FE D4 07 DF 05 0E "
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
        self.assertEqual(param_put.target_station_no, 130)
        self.assertEqual(param_put.update_station_no, 130)
        self.assertEqual(param_put.rec_interval, time(0, 0, 30))
        self.assertEqual(param_put.upper_limit, 60.0)
        self.assertEqual(param_put.lower_limit, -30.0)
        self.assertEqual(param_put.stop_button, StopButton.ENABLE)
        self.assertEqual(param_put.delay, 1.5)
        self.assertEqual(param_put.tone_set, ToneSet.NONE)
        self.assertEqual(param_put.alarm, AlarmSetting.NONE)
        self.assertEqual(param_put.temp_unit, TemperatureUnit.C)
        self.assertEqual(param_put.temp_calibration, -1.5)

    def test_to_param_put2(self):
        res = DevInfoResponse()
        res.read(BytesIO(_bin("55 02 01 28 0A FF FF FF 02 58 FE D4 07 DF 05 0E "
                              "16 2F 04 02 FF FF 05 0E 07 38 0E 13 64 00 09 07 "
                              "DF 05 0E 16 2F 36 FF FF FF FF FF FF FF FF FF FF "
                              "4C 6F 67 67 65 72 00 00 00 00 00 00 00 00 00 00 "
                              "00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 "
                              "00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 "
                              "00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 "
                              "00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 "
                              "00 00 00 00 00 00 00 00 00 00 FF FF FF FF FF FF "
                              "FF FF FF FF FF FF FF FF FF FF FF FF FF FF 00 B3"
                              )))
        param_put = res.to_param_put()
        self.assertEqual(param_put.rec_interval, time(0, 0, 30))
        self.assertEqual(param_put.target_station_no, 2)
        self.assertEqual(param_put.update_station_no, 2)
        self.assertEqual(param_put.upper_limit, 60.0)
        self.assertEqual(param_put.lower_limit, -30.0)
        self.assertEqual(param_put.stop_button, StopButton.ENABLE)
        self.assertEqual(param_put.delay, 0.0)
        self.assertEqual(param_put.tone_set, ToneSet.NONE)
        self.assertEqual(param_put.alarm, AlarmSetting.NONE)
        self.assertEqual(param_put.temp_unit, TemperatureUnit.C)
        self.assertEqual(param_put.temp_calibration, -0.1)

    def test_ParamPutRequest(self):
        req = ParamPutRequest(130)
        req.rec_interval = time(0, 0, 30)
        req.update_station_no = 130
        req.stop_button = StopButton.ENABLE
        req.delay = 0
        req.temp_calibration = -1.5

        self.assertEqual(req.to_bytes(), _bin("33 82 05 00 00 00 1E 02 58 FE D4 82 13 00 31 00 "
                                               "31 F1 00 00 00 00 00 00 EC"))

    def test_ParamPutResponse(self):
        res = ParamPutResponse()
        res.read(BytesIO(_bin("01 02 03")))
        self.assertTrue(res.msg, b'\x01\x02\x03')

    def test_DataHeaderRequest(self):
        req = DataHeaderRequest(130)
        self.assertEqual(req.to_bytes(), _bin("33 82 01 00 B6"))

    def test_DataHeaderResponse(self):
        res = DataHeaderResponse()
        res.read(BytesIO(_bin("55 0B 76 07 DF 05 0E 17 04 35 1F")))
        self.assertEqual(res.rec_count, 2934)
        self.assertEqual(res.start_time, datetime(2015, 5, 14, 23, 4, 53))

    def test_DataBodyRequest(self):
        req = DataBodyRequest(130, 131)
        self.assertEqual(req.to_bytes(), _bin("33 82 02 83 3A"))

    def test_DataBodyResponse(self):
        res = DataBodyResponse(10)
        res.read(BytesIO(_bin("55 00 01 FF FF 00 03 00 04 00 05 00 06 00 07 00 08 00 09 00 0A 8C")))
        self.assertEqual(len(res.records), 10)
        self.assertEqual(res.records, (1, -1, 3, 4, 5, 6, 7, 8, 9, 10))

    def test_ClockSetRequest(self):
        req = ClockSetRequest(130, datetime(2015, 5, 14, 23, 4, 53))
        self.assertEqual(req.to_bytes(), _bin("33 82 07 00 07 DF 05 0E 17 04 35 05"))

    def test_ClockSetResponse(self):
        res = ClockSetResponse()
        res.read(BytesIO(_bin("55 A3 F8")))
        self.assertEqual(res.msg, b'\x55\xA3\xF8')

    def test_DevNumRequest(self):
        req = DevNumRequest(130)
        req.device_number = "11223344"

        self.assertEqual(req.to_bytes(), _bin("33 82 0B 00 31 31 32 32 33 33 34 34 00 00 54"))

    def test_DevNumResponse(self):
        res = DevNumResponse()
        res.read(BytesIO(_bin("55 A7 FC")))
        self.assertEqual(res.msg, b'\x55\xA7\xFC')

    def test_UserInfoRequest(self):
        req = UserInfoRequest(1)
        req.user_info = "".join([str(n)+"____.____" for n in range(10)])

        self.assertEqual(req.to_bytes(), _bin("33 01 09 00 "
                                              "30 5F 5F 5F 5F 2E 5F 5F 5F 5F "
                                              "31 5F 5F 5F 5F 2E 5F 5F 5F 5F "
                                              "32 5F 5F 5F 5F 2E 5F 5F 5F 5F "
                                              "33 5F 5F 5F 5F 2E 5F 5F 5F 5F "
                                              "34 5F 5F 5F 5F 2E 5F 5F 5F 5F "
                                              "35 5F 5F 5F 5F 2E 5F 5F 5F 5F "
                                              "36 5F 5F 5F 5F 2E 5F 5F 5F 5F "
                                              "37 5F 5F 5F 5F 2E 5F 5F 5F 5F "
                                              "38 5F 5F 5F 5F 2E 5F 5F 5F 5F "
                                              "39 5F 5F 5F 5F 2E 5F 5F 5F 5F "
                                              "C6"
                                              ))

    def test_UserInfoResponse(self):
        res = UserInfoResponse()
        res.read(BytesIO(_bin("55 AB 00")))
        self.assertEqual(res.msg, b'\x55\xAB\x00')
if __name__ == '__main__':
    unittest.main()
