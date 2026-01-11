#!/usr/bin/env python

# This file is part of Interact-IV's CCCP Library.
# Interact-IV.com (c) 2013
#
# Contact: softeam@interact-iv.com
# Authors:
#    - PEMO <pemo@interact-iv.com>

import socket, struct, select, fcntl
from datetime import datetime
from time import mktime,gmtime
from os import O_NDELAY
from cccp.protocols.serializer import SerializeMethod
from cccp.protocols.deserializer import DeserializeMethod

class CCSocket:
    server_address = "127.0.0.1"
    server_port = 20000
    socket = None
    connected = False

    def __init__(self, address, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        fcntl.fcntl(self.socket.fileno(), fcntl.F_SETFL, O_NDELAY)
        self.server_address = address
        self.server_port = port
    
    def start(self):
        self.connect()
    
    def connect(self):
        self.socket.connect_ex((self.server_address, self.server_port))
        cc_system.sockets[self.socket.fileno()] = self
        if self.has_to_write(): cc_system.polls.register(self.socket.fileno(), select.POLLIN | select.POLLOUT)
        else: cc_system.polls.register(self.socket.fileno(), select.POLLIN)
        self.connected = True
    
    def disconnect(self):
        self.connected = False
        cc_system.polls.unregister(self.socket.fileno())
        del cc_system.sockets[self.socket.fileno()]
        self.socket.close()
    
    def step(self):
        return cc_system.step()
    
    def step_result(self):
        return cc_system.step_result
    
    def step_done(self,step_result = None):
        cc_system.step_done(step_result)

class CDEPSocket(CCSocket):
    incoming_buffer = []
    outgoing_messages = []
    objects_with_all_fields = False
    
    def __init__(self, client, address, port, module_id):
        CCSocket.__init__(self,address, port)
        self.client = client
        self.module_id = module_id
    
    def has_to_write(self):
        return len(self.outgoing_messages) > 0
    
    def read_ready(self):
        received = self.socket.recv(4096)
        self.incoming_buffer += struct.unpack("B" * len(received), received)
        while len(self.incoming_buffer) >= 8:
            message_size = self.incoming_buffer[0]
            message_size += self.incoming_buffer[1] << 8
            message_size += self.incoming_buffer[2] << 16
            message_size += self.incoming_buffer[3] << 24
            if message_size > len(self.incoming_buffer): return
            d=DeserializeMethod(self.incoming_buffer[0:message_size], self.module_id)
            (method_name, method_args) = d.deserialize(self.objects_with_all_fields)
            of = getattr(self.client, "on_" + method_name, None)
            if of is not None: of(*method_args)
            f = getattr(self.client, method_name, None)
            if f is not None : f(*method_args)
            del self.incoming_buffer[0:message_size]

    def write_ready(self):
        while len(self.outgoing_messages) > 0:
            message = self.outgoing_messages[0]
            to_write = len(message)
            written = self.socket.send(message)
            if written != to_write:
                if written > 0: message[written:]
                return
            del self.outgoing_messages[0]
        if self.connected: cc_system.polls.register(self.socket.fileno(), select.POLLIN)
    
    def send(self, *args):
        if (len(self.outgoing_messages) == 0) and self.connected: cc_system.polls.register(self.socket.fileno(), select.POLLIN|select.POLLOUT)
        s = SerializeMethod(self.module_id, args)
        data = s.serialize()
        size = len(data)
        data[0] = size & 0xFF
        data[1] =(size >> 8) & 0xFF
        data[2] = (size >> 16) & 0xFF
        data[3] = (size >> 24) & 0xFF
        data = struct.pack("B" * len(data), *data)
        self.outgoing_messages.append(data)

class CCSystem:
    def __init__(self):
        self.system_ended = False
        self.sockets = {}
        self.polls = select.poll()
        self.step_result = None
    
    def step(self):
        self.waiting_step = True
        while self.waiting_step:
            time_to_wait = self.idle()
            result = self.polls.poll(int(time_to_wait * 1000))
            for pair in result:
                socket = self.sockets[pair[0]]
                if pair[1] & select.POLLIN != 0: socket.read_ready()
                if pair[1] & select.POLLOUT != 0: socket.write_ready()
        return self.step_result

    def step_done(self, step_result = None):
        self.step_result = step_result;
        self.waiting_step = False

    def idle(self):
        return 2

    def run(self):
        while not self.system_ended:
            time_to_wait = self.idle()
            result = self.polls.poll(int(time_to_wait * 1000))
            for pair in result:
                socket = self.sockets[pair[0]]
                if pair[1] & select.POLLIN != 0: socket.read_ready()
                if pair[1] & select.POLLOUT != 0: socket.write_ready()
