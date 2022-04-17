try:
  import machine
  import usocket as socket
  import camera
  import ubinascii
  use_camera = True
  import utime as time
  import ujson
except:
  use_camera = False
  import time
  import socket

import time

p12 = machine.Pin(12)
pwm12 = machine.PWM(p12)


if use_camera:
  ## ESP32-CAM (default configuration) - https://bit.ly/2Ndn8tN
  #camera.init(0, format=camera.JPEG, fb_location=camera.PSRAM)
  #camera.init(0, format=camera.JPEG, fb_location=camera.PSRAM)
  camera.init(0, format=camera.JPEG, framesize=camera.FRAME_240X240, xclk_freq=camera.XCLK_10MHz, fb_location=camera.PSRAM)
  #print(dir(camera))

  # The parameters: format=camera.JPEG, xclk_freq=camera.XCLK_10MHz are standard for all cameras.
  # You can try using a faster xclk (20MHz), this also worked with the esp32-cam and m5camera
  # but the image was pixelated and somehow green.

  ## Other settings:
  # flip up side down
  #camera.flip(1)
  # left / right
  ##camera.mirror(1)

  # framesize
  # The options are the following:
  # FRAME_96X96 FRAME_QQVGA FRAME_QCIF FRAME_HQVGA FRAME_240X240
  # FRAME_QVGA FRAME_CIF FRAME_HVGA FRAME_VGA FRAME_SVGA
  # FRAME_XGA FRAME_HD FRAME_SXGA FRAME_UXGA FRAME_FHD
  # FRAME_P_HD FRAME_P_3MP FRAME_QXGA FRAME_QHD FRAME_WQXGA
  # FRAME_P_FHD FRAME_QSXGA
  # Check this link for more information: https://bit.ly/2YOzizz

  # special effects
  ##camera.speffect(camera.EFFECT_NONE)
  # The options are the following:
  # EFFECT_NONE (default) EFFECT_NEG EFFECT_BW EFFECT_RED EFFECT_GREEN EFFECT_BLUE EFFECT_RETRO

  # white balance
  ##camera.whitebalance(camera.WB_NONE)
  # The options are the following:
  # WB_NONE (default) WB_SUNNY WB_CLOUDY WB_OFFICE WB_HOME

  # saturation
  ##camera.saturation(0)
  # -2,2 (default 0). -2 grayscale 

  # brightness
  ##camera.brightness(0)
  # -2,2 (default 0). 2 brightness

  # contrast
  ##camera.contrast(0)
  #-2,2 (default 0). 2 highcontrast

  # quality
  ##camera.quality(10)
  # 10-63 lower number means higher quality



while True:
  time.sleep(0.1)
  print('getaddrinfo...')
  ai = socket.getaddrinfo("192.168.15.110", 5984)
  addr = ai[0][-1]
  time.sleep(0.1)
  
  s = socket.socket()
  s.connect(addr)
  time.sleep(0.1)

  s_cmd = socket.socket()
  s_cmd.settimeout(0.1)
  s_cmd.connect(addr)
  time.sleep(0.1)
  payload = bytes('GET /teste/_changes?feed=continuous&include_docs=true&since=now&heartbeat=2000&filter=_doc_ids&doc_ids=["cmd"] HTTP/1.1\r\n\r\n', 'utf-8')
  s_cmd.send(payload)

  while True:
    buf = camera.capture()

    if buf:
      try:
        doc_id = 'img_'+str(time.time_ns())
        payload = bytes('PUT /teste/{}/img.jpeg HTTP/1.1\r\nHost: 192.168.15.110:5984\r\nContent-Type: image/jpeg\r\nContent-Length: {}\r\n\r\n'.format(doc_id, len(buf)), 'utf-8')+buf
        s.send(payload)
        #print(s.recv(4096))
        #time.sleep(0.1)
      except Exception as e:
        s.close()
        s_cmd.close()
        break

    try:
      buf = s_cmd.recv(4096)
      # convert correct line feed
      data = ujson.loads([x for x in buf.decode('utf-8').split('\n') if len(x) and x[0] == '{'][0])
      print(data)

      if 'p12_pwm_freq' in data['doc']:
        time.sleep(0.1)
        if data['doc']['p12_pwm_freq']:
          pwm12.freq(data['doc']['p12_pwm_freq'])
          pass
        else:
          pwm12.freq(5000)

    except Exception as e:
      #print(dir(s_cmd))
      pass
