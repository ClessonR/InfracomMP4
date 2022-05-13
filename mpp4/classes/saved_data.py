import queue

class saved_data:
    def __init__(self):
        self.msg_queue = queue.Queue()

    def take_msgs(self):
        msgs = []
        while not self.msg_queue.empty():
            try:
                msg = self.msg_queue.get(block=False)
                msgs.append(msg)
            except queue.Empty():
                return msgs
        return msgs