try:
  import socket
except: 
  import usocket as socket
import config
class FrictionMonitor:
  def __init__(self):
    self.HOST  = config.central_host["ip"]
    self.PORT = config.central_host["port"]
    self.max_rec_bytes = config.central_host["bytes"]
    self.module_number = '3'
    self.high_friction = False

  def query_friction_value(self):
    try:
      s = socket.socket()
      # print("Created socket!")
      s.connect(socket.getaddrinfo(self.HOST, self.PORT)[0][-1])
      print("Made connection!")
      b = self.module_number.encode('utf-8')
      # print("Encoded!")
      s.sendall(b)
      # print("Sent request!")
      data = s.recv(self.max_rec_bytes)
      # print("Received data!")
      counter = 0
      max_rec_bytes = len(data)
      data = data.decode("utf-8")
      # print("Decoded data!")
      while counter < max_rec_bytes:
        if data[counter] == '\0':
          print("Character = " + data[counter])
          data = data[:counter]
          break
        counter += 1
      
      if data == 'high_friction':
        self.high_friction = True

      elif data == 'low_friction':
        self.high_friction = False
      
      print('Received ', data)
      s.close()
      return True

    except Exception as e:
      print("Could not connect to central control server")
      print("Exception = " , e)
      return False
    
    


