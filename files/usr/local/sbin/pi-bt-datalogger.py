#!/usr/bin/env python3
# --------------------------------------------------------------------------
# This script implements the datalogger service.
#
# The server waits for incoming connections, creates a new thread for the
# client and dumps all incoming data to a file.
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/pi-bt-datalogger
#
# --------------------------------------------------------------------------

import bluetooth
import threading, uuid

server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
server_sock.bind(("", bluetooth.PORT_ANY))
server_sock.listen(1)

port = server_sock.getsockname()[1]

uuid = str(uuid.uuid4())
bluetooth.advertise_service(
  server_sock, "rfcomm-server", service_id=uuid,
  service_classes=[uuid, bluetooth.SERIAL_PORT_CLASS],
  profiles=[bluetooth.SERIAL_PORT_PROFILE],
  )
client_threads = {}
stop_event = threading.Event()

# --- serve client   ------------------------------------------------

def serve_client(info,sock):
  """ serve single client """

  try:
    while True:
      data = client_sock.recv(128)
      if stop_event.is_set() or not data:
        break
      print("Received", data)
  except:
    pass
  finally:
    print("Disconnected.")
    try:
      sock.close()
    except:
      pass
    finally:
      if not stop_event.is_set():
        del client_threads[info]

# --- main program   ------------------------------------------------

if __name__ == '__main__':
  try:
    while True:
      print("Waiting for connection on RFCOMM channel",port)
      client_sock, client_info = server_sock.accept()
      print("Accepted connection from", client_info)
      t = threading.Thread(target=serve_client,
                           args=(client_info,client_sock))
      client_threads[client_info] = t
      t.start()

  except:
    pass

  try:
    stop_event.set()
    server_sock.close()
  except:
    pass
  map(threading.Thread.join,client_threads.values())
  print("All done.")
