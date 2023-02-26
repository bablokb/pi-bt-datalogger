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

def serve_client(bt_mac,sock):
  """ serve single client """

  first = True
  rest  = ""

  # read-loop with timeout
  sock.settimeout(5)
  while True:
    if stop_event.is_set():
      print("%s: stop event detected." % bt_mac)
      break
    try:
      data = client_sock.recv(1024)
    except bluetooth.btcommon.BluetoothError as bte:
      if bte.args[0] == "timed out":
        continue
      else:
        break

    # no data means sender closed connection
    if not data:
      print("%s: disconnected." % bt_mac)
      break
    data = (rest + data.decode("utf-8")).split()
    if first:
      first = False
    else:
      for line in data[:-1]:
        print("%s: %s" % (bt_mac,line),flush=True)
    rest = data[-1:] if len(data)>1 else ""

  # read-loop terminated
  try:
    sock.close()
  except:
    pass
  finally:
    if not stop_event.is_set():
      # no termination due to stop event: remove from thread-list
      del client_threads[bt_mac]

# --- main program   ------------------------------------------------

if __name__ == '__main__':
  try:
    print("Waiting for connection on RFCOMM channel",port)
    while True:
      client_sock, client_info = server_sock.accept()
      print("Accepted connection from", client_info)
      t = threading.Thread(target=serve_client,
                           args=(client_info[0],client_sock))
      client_threads[client_info[0]] = t
      t.start()

  except:
    pass

  try:
    stop_event.set()
    server_sock.close()
  except:
    pass
  map(threading.Thread.join,client_threads.values())
  print("datalogger finished")
