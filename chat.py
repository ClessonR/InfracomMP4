from tkinter import messagebox, scrolledtext, simpledialog
import classes.client as client
import classes.server as server
import tkinter as tk
import sys

PORT = 30303

class P2PChat(tk.Frame):
    def __init__(self, master=None):
        global PORT
        
        master.wm_title("P2P Chat")
        
        tk.Frame.__init__(self, master)
        self.pack(fill=tk.BOTH, expand=1)
        self.create_interface()
        
        if messagebox.askyesno("", "Voce vai ser o host?"):
            self.chat = server.Server(PORT)
            
            # ip
            self.ip_entry.delete(0, tk.END)
            self.ip_entry.insert(0, self.chat.host_ip)
            self.ip_entry.config(state='readonly')
            
            # port
            self.port_entry.delete(0, tk.END)
            self.port_entry.insert(0, self.chat.host_port)
            self.port_entry.config(state='readonly')

        # else bota um botão de conectar
        else:
            self.chat = None
            self.connect_btn.pack(side=tk.LEFT)

        # enviar msg com enter
        master.bind('<Return>', self.send_msg)
        master.bind('<KP_Enter>', self.send_msg)
        self.display_new_msg()

    def conn_to_host(self):
        host_ip = self.ip_entry.get()
        port_entry_val = self.port_entry.get()

        try:
            self.chat = client.Client(host_ip, int(port_entry_val))
            self.connect_btn.pack_forget()
            self.ip_entry.config(state='readonly')
            self.port_entry.config(state='readonly')
        except Exception as e:
            msg = "SERVER: Erro: Verifique o IP e Port."
            self.display_msg(msg)

    def create_interface(self):
        global PORT

        # Barrinha de Mudar de nome
        menubar = tk.Menu(self)
        menubar.add_command(label="Mudar de nome", \
                         command=self.new_name)

        self.master.config(menu=menubar)

        # IP / Port
        ip_port_frame = tk.Frame(self, relief=tk.RAISED, bd=1)
        ip_port_frame.pack(side=tk.TOP, fill=tk.X)

        # IP Frame
        ip_frame = tk.Frame(ip_port_frame)
        ip_frame.pack(side=tk.LEFT)
        
        ip_label = tk.Label(ip_frame, text="ip:")
        ip_label.pack(side=tk.LEFT)
              
        ip_max_len = 15
        ip_entry = tk.Entry(ip_frame, width=ip_max_len)
        ip_entry.pack(side=tk.LEFT)
        ip_entry.insert(0, '') 
        self.ip_entry = ip_entry

        # Port Frame
        port_frame = tk.Frame(ip_port_frame)
        port_frame.pack(side=tk.LEFT)

        port_label = tk.Label(port_frame, text="port:")
        port_label.pack(side=tk.LEFT)

        port_max_len = 5
        port_entry = tk.Entry(port_frame, width=port_max_len)
        port_entry.pack(side=tk.LEFT)
        port_entry.insert(0, PORT)
        self.port_entry = port_entry
       
        # caixa de msg 
        msg_frame = tk.Frame(self)
        msg_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        msg_window = scrolledtext.ScrolledText(msg_frame, height=30, width=80)
        msg_window.pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        msg_window.config(state=tk.DISABLED)
        self.msg_window = msg_window

        # barrinha de enviar mensagem
        msg_entry_frame = tk.Frame(msg_frame, relief=tk.RAISED, bd=1)
        msg_entry_frame.pack(side=tk.BOTTOM, fill=tk.X)

        msg_entry = tk.Entry(msg_entry_frame)
        msg_entry.pack(side=tk.LEFT, fill=tk.X, expand=1)
        msg_entry.focus()
        self.msg_entry = msg_entry
        
        # botão de enviar mensagem
        send_btn = tk.Button(msg_entry_frame)
        send_btn["text"] = "Send"
        send_btn["command"] = self.send_msg
        send_btn.pack(side=tk.RIGHT)

        # botão de conectar
        connect_btn = tk.Button(ip_port_frame)
        connect_btn["text"] = "Conectar"
        connect_btn["command"] = self.conn_to_host
        self.connect_btn = connect_btn

        master = self.master
        master.update()
        temporary_menubar_height = 30
        min_height = master.winfo_height() + temporary_menubar_height
        master.minsize(master.winfo_width(), min_height)

    def new_name(self):
        new_name = simpledialog.askstring("Mudar nome", "Nome novo")
        if new_name is not None:
        	if self.chat is not None:
        		self.chat.send_msg("/nc " + new_name)

    def display_new_msg(self):
        if self.chat is not None:
            msgs = self.chat.take_msgs()
            for msg in msgs:
            	self.msg_window.config(state=tk.NORMAL)
            	self.msg_window.insert(tk.END, "%s\n" % msg)
            	self.msg_window.yview(tk.END)
            	self.msg_window.config(state=tk.DISABLED)
        self.master.after(100, self.display_new_msg)

    def send_msg(self, event=None):
        if self.chat is not None:
            msg = self.msg_entry.get()
            self.msg_entry.delete(0, tk.END)
            self.chat.send_msg(msg)

root = tk.Tk()
p2p_chat = P2PChat(master=root)
p2p_chat.mainloop()