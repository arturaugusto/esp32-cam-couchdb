import machine
from machine import Pin
import usocket as socket
import camera
import utime as time
import ujson
from config import jwt
from boot import do_connect
import ussl as ssl

# p12 = machine.Pin(12)
# p13 = machine.Pin(13)
# p15 = machine.Pin(15)
# p14 = machine.Pin(14)

# pwm_dict = {
#   12: machine.PWM(p12),
#   13: machine.PWM(p13),
#   15: machine.PWM(p15),
#   14: machine.PWM(p14)
# }

dig_dict = {
  4: machine.Pin(4, mode=Pin.OUT),
  12: machine.Pin(12, mode=Pin.OUT),
  13: machine.Pin(13, mode=Pin.OUT),
  15: machine.Pin(15, mode=Pin.OUT),
  14: machine.Pin(14, mode=Pin.OUT)
}

for k in dig_dict.keys():
  dig_dict[k].init()




## ESP32-CAM (default configuration) - https://bit.ly/2Ndn8tN
#camera.init(0, format=camera.JPEG, fb_location=camera.PSRAM)
#camera.init(0, format=camera.JPEG, fb_location=camera.PSRAM)
camera.init(0, format=camera.JPEG, xclk_freq=camera.XCLK_10MHz, fb_location=camera.PSRAM)

# framesize
# The options are the following:
# FRAME_96X96 FRAME_QQVGA FRAME_QCIF FRAME_HQVGA FRAME_240X240
# FRAME_QVGA FRAME_CIF FRAME_HVGA FRAME_VGA FRAME_SVGA
# FRAME_XGA FRAME_HD FRAME_SXGA FRAME_UXGA FRAME_FHD
# FRAME_P_HD FRAME_P_3MP FRAME_QXGA FRAME_QHD FRAME_WQXGA
# FRAME_P_FHD FRAME_QSXGA
# Check this link for more information: https://bit.ly/2YOzizz
camera.framesize(camera.FRAME_240X240)

# quality
#camera.quality(40)
# 10-63 lower number means higher quality


while True:
  try:
    print('getaddrinfo...')
    ai = socket.getaddrinfo("couchdatabase.xyz", 443)
    print("Address infos:", ai)
    addr = ai[0][-1]
    
    s = socket.socket()
    s.connect(addr)
    s.settimeout(3)
    s = ssl.wrap_socket(s)

    socket_cmd_non_ssl = socket.socket()
    socket_cmd_non_ssl.connect(addr)
    socket_cmd = ssl.wrap_socket(socket_cmd_non_ssl)
    payload = bytes('GET /_couch/teste/_changes?feed=continuous&include_docs=true&since=now&heartbeat=2000&filter=_doc_ids&doc_ids=["cmd"] HTTP/1.1\r\nAuthorization: Bearer {}\r\n\r\n'.format(jwt), 'utf-8')
    socket_cmd_non_ssl.settimeout(0.1)
    socket_cmd.write(payload)
    
    time.sleep(0.1)

    while True:
      print('capturing frame...')
      buf = camera.capture()
      print('capture done.')
      time.sleep(0.1)
      if buf:
        try:
          doc_id = 'img_'+str(time.time_ns())
          payload = bytes('PUT /_couch/teste/{}/img.jpeg?batch=ok HTTP/1.1\r\nHost: couchdatabase.xyz\r\nAuthorization: Bearer {}\r\nContent-Type: image/jpeg\r\nContent-Length: {}\r\n\r\n'.format(doc_id, jwt, len(buf)), 'utf-8')+buf
          #s.send(payload)
          print('sending data...')
          s.write(payload)
          print('send done.')

          print('waiting ok response...')
          while True:
            buf = s.readline()
            if '"ok":true' in buf:
              #print(buf)
              break
          print('waiting ok done.')
          #time.sleep(0.1)
        except Exception as e:
          print('error sending frame')
          print(e)
          s.close()
          socket_cmd.close()
          do_connect()
          break

      # read cmd doc
      try:
        print('reading cmd...')
        #buf = socket_cmd.read(4096)
        while True:
          buf = socket_cmd.readline()
          if '"doc":{"_id":"cmd"' in buf:
            break

        # convert correct line feed
        data = ujson.loads([x for x in buf.decode('utf-8').split('\n') if len(x) and x[0] == '{'][0])
        print(data)
        
        """
        `data['doc']` have this structure:
        
        pwm = [
          {'io': 12, 'f': 100, 'on': True}, # `on` can be True (turn on), False (turn off) or None (do nothing)
          {'io': 13, 'f': 200, 'on': True}
        ]
        """
        
        if 'pwm' in data['doc']:
          for c in data['doc']['pwm']:
            pwm_dict[c['io']].freq(c['f'])
        
        if 'dig' in data['doc']:
          for c in data['doc']['dig']:
            dig_dict[c['io']].value(c['on'])
        print('read done.')
      except Exception as e:
        print('read failed.')
        #print('err2')
        print(e)
        #print(dir(socket_cmd))
        pass
  except Exception as e:
    print(e)
    pass
