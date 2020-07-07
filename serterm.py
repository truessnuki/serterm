from serial import Serial, SerialException
from argparse import ArgumentParser
from threading import Thread
from struct import pack, calcsize

stop_threads = False
formatting_enabled = True

# Rx/Tx-Header
# ==============================================================================
class MessageHeader:
	def __init__(self, byteorder, stream=0, size=0):
		self._streamsource = stream
		self._size = size

		if byteorder == "big":
			self.format = ">BI"
		elif byteorder == "little":
			self.format = "<BI"
		else:
			raise ValueError("Please define BYTEORDER")

	@property
	def bytes(self) -> bytes:
		return pack(self.format, self._streamsource, self._size)

	@property
	def size(self) -> int:
		return self._size

	@property
	def stream(self) -> int:
		return self._streamsource

	def __len__(self):
		return calcsize(self.format)

	def __str__(self):
		return self.stream.value + ":" + str(self._size)


# ==============================================================================
def sender_thread(conn: Serial):
	global stop_threads
	global formatting_enabled
	
	print("sender started")
	while not stop_threads:
		try:
		
			data = input()
			
			if len(data) == 0:
				continue
			
			if data == "exit":
				break
				
			if data == "ON":
				formatting_enabled = True
				continue
			
			if data == "OFF":
				formatting_enabled = False
				continue
		
			
			header = MessageHeader("little", ord("d"), len(data))
			
			msg = header.bytes + data.encode("utf-8")
			conn.write(msg)
		
		except Exception as ex:
			print(ex)
			break
		
	stop_threads = True
	

# ==============================================================================
def receiver_thread(conn: Serial):
	global stop_threads
	global formatting_enabled
	
	print("receiver started")
	while not stop_threads:
		try:
			# receive header
			header = MessageHeader("little")
			data = conn.read(len(header))
			
			if not formatting_enabled and len(data):
				print("{}".format(data), end="")
				continue
			
			if len(data) != len(header):
				continue
			
			streamsrc = data[0]
			msgsize = int.from_bytes(data[1:], "little")

			if msgsize > 80 or msgsize == 0:
				raise ValueError("invalid message size {}".format(msgsize))
				
			header = MessageHeader("little", streamsrc, msgsize)
			
			# receive message
			data = conn.read(header.size)
			
			if len(data) == 0:
				continue
				
			if msgsize == 2 and data.decode("utf-8") == "ok":
				continue

			print(data.decode("utf-8"), end="")
		
		except Exception as ex:
			print(ex)
			break
		
	stop_threads = True


# ==============================================================================
def main(port, baudrate):
	
	ser = Serial(port=port, baudrate=baudrate, timeout=1)
		
	print("opened Port {}".format(port))
	
	sender = Thread(target=sender_thread, args=(ser,))
	receiver = Thread(target=receiver_thread, args=(ser,))
	
	sender.start()
	receiver.start()
	
	sender.join()
	receiver.join()
	
	ser.close()
	
	exit(0)
	
	
# ==============================================================================
if __name__ == "__main__":
	
	parser = ArgumentParser(description="Helper programm to talk to the smartlock dispatcher via serial")
	parser.add_argument("port", type=str, help="Serial Port")
	parser.add_argument("baudrate", type=int, help="Baudrate")
	
	args = parser.parse_args()
	
	main(args.port, args.baudrate)