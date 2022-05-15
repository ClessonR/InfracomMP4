import classes.saved_data as sd
import threading
import socket
import sys

class User():
    def __init__(self, sock, ip, port, name=None):
        self.sock = sock
        self.ip = ip
        self.port = port
        if name is None:
            self.name = "No Name (yet)"
        else:
            self.name = name

class Server(sd.saved_data):

    def __init__(self, port):
        super().__init__()

        self._s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ip = socket.gethostbyname(socket.gethostname())
        while True:
            try:
                self._s.bind((ip, port))
                break
            except:
                port += 1

        self.users = {}
        self.host_user = User(self._s, ip, port, "Host")
        self.system_user = User(self._s, ip, port, "SERVER")
       
        self._lock = threading.Lock()
        th = threading.Thread(target=self.get_users)
        th.start()

    @property
    def host_ip(self):
        return self.host_user.ip

    @property
    def host_port(self):
        return self.host_user.port
   
    def get_users(self):
        while True:
            try:
                self._s.listen(5)
                sock, addr = self._s.accept() 

                user = User(sock, addr[0], addr[1])
                
                msg = user.name + " entrou na conversa"
                with self._lock:
                    self.users[sock] = user
                    self.send_msg_as_sys_to_all(msg)
                
                th = threading.Thread(target=self.handler, kwargs={'sock': sock})
                th.start()
            except Exception as e:
                    break

    def send_msg(self, msg):
        if not msg:
            return
        
        msg_type = self.msg_type(msg)
        
        with self._lock:
            if msg_type == 2:
                self.change_name(self.host_user, msg[4:])
            else:
                self.send_msg_as_user_to_all(msg, self.host_user)

    def send_msg_as_sys_to_user(self, msg, to_user):
        if not msg:
            return

        msg = self.format_msg(msg, self.system_user)
        msg += '.'

        if to_user is self.host_user:
            self.msg_queue.put(msg)
        else:
            to_user.sock.sendall(msg.encode())


    

    def send_msg_as_sys_to_all(self, msg):
        if not msg:
            return

        msg = self.format_msg(msg, self.system_user)
        msg += '.'
        
        for user in self.users.values():
            try:
                user.sock.sendall(msg.encode())
            except Exception as e:
                self.send_msg_as_sys_to_user(repr(e), self.host_user)

        self.msg_queue.put(msg)

    def send_msg_as_user_to_all(self, msg, as_user):
        if not msg:
            return

        msg = self.format_msg(msg, as_user)
        for user in self.users.values():
            try:
                user.sock.sendall(msg.encode())
            except Exception as e:
                self.send_msg_as_sys_to_user(repr(e), self.host_user)

        self.msg_queue.put(msg)

    def format_msg(self, msg, as_user):
        return as_user.name + msg

    def handler(self, sock):
        while True:
            try:
                msg = sock.recv(1024)
                msg = msg.decode()
                msg_type = self.msg_type(msg)

                with self._lock:
                    user = self.users[sock]
                    if msg_type == 1:
                        user.sock.close()
                        del self.users[user.sock]
                        break
                    elif msg_type == 2:
                        self.change_name(user, msg[4:])
                    else:
                        self.send_msg_as_user_to_all(msg, user)
            except Exception as e:
                    break

    def msg_type(self, msg):
        if not msg:
            return 1

        if len(msg) >= 5 and msg[:4] == "/nc ":
            return 2

        return 3

    def change_name(self, requested_user, new_user_name):
        new_user_name = new_user_name.replace(' ', '')
        sys_msg = 'O usuario ' + requested_user.name
        requested_user.name = new_user_name
        sys_msg += ' mudou de nome para ' + new_user_name
        self.send_msg_as_sys_to_all(sys_msg)