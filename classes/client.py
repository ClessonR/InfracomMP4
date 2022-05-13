import classes.saved_data as sd 
import threading
import socket


class Client(sd.saved_data):
    def __init__(self, host_ip, port):
        super().__init__()

        self._s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._s.settimeout(5)
        self._s.connect((host_ip, port))
        self._s.settimeout(None)

        th = threading.Thread(target=self.end_func, kwargs={'sock':self._s})
        th.start()

    def end_func(self, sock):
        while True:
            try:
                msg = sock.recv(1024)
                msg = msg.decode()
                if not msg:
                    msg = "SISTEMA_LOCAL: Host disconectou."
                    self.msg_queue.put(msg)
                    break

                self.msg_queue.put(msg)
            except Exception as e:
                    break

    def send_msg(self, msg):
        if not msg:
            return

        try:
            if self._s is not None:
                self._s.sendall(msg.encode())
            else:
                self.msg_queue.put(msg)
        except Exception as e:
            msg = "SISTEMA_LOCAL: " + repr(e)
            self.msg_queue.put(msg)