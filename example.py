
import elitech
import datetime
import sys

port = sys.argv[1]
print("PORT: {}".format(port))
device = elitech.Device(port)
device.debug = True
device.init()

# get devinfo
devinfo = device.get_devinfo()
for k,v in vars(devinfo).items():
    print("{}={}".format(k, v))

# get data
body = device.get_data()
for elm in body:
    print("{0}\t{1:%Y-%m-%d %H:%M:%S}\t{2:.1f}".format(*elm))

# update param
#param_put = devinfo.to_param_put()
#param_put.rec_interval = datetime.time(0, 0, 10)
#param_put.stop_button = elitech.StopButton.ENABLE
#param_put_res = device.update(param_put)
#print(param_put_res.msg)

# get devinfo
#print(vars(device.get_devinfo()))
