#!/usr/bin/env python

# This file is part of Interact-IV's CCCP Library.
# Interact-IV.com (c) 2013
#
# Contact: softeam@interact-iv.com
# Authors:
#    - PEMO <pemo@interact-iv.com>

from __future__ import print_function
import sys, struct
from socket import socket, AF_INET, SOCK_STREAM
from os import O_NDELAY
from select import poll, POLLIN, POLLOUT
from fcntl import fcntl, F_SETFL
from threading import Thread, Event, currentThread
from Queue import Queue
from time import sleep
from cccp.protocols.serializer import SerializeMethod
from cccp.protocols.deserializer import DeserializeMethod


CCC_REQUEST_TIMEOUT = 1


class CDEPSocket(Thread):
    server_address = "127.0.0.1"
    server_port = 20000

    _socket = None
    _poll = None

    _continue = True

    def step(self):
        try:
            return self._step_queue.get(True, CCC_REQUEST_TIMEOUT)
        except:
            print("Response timeout")
            return None

    def step_done(self, step_result):
        self._step_queue.put(step_result)

    def __init__(self, client, address, port, module_id):
        Thread.__init__(self)
        self.server_address = address
        self.server_port = port
        self.module_id = module_id
        self.client = client
        self._queue = Queue()
        self._step_queue = Queue()

    def connect(self):
        self._socket = socket(AF_INET, SOCK_STREAM)
        fcntl(self._socket.fileno(), F_SETFL, O_NDELAY)
        self._poll = poll()
        self._socket.connect_ex((self.server_address, self.server_port))
        self._poll.register(self._socket.fileno(), POLLIN | POLLOUT)

    def disconnect(self):
        self._poll.unregister(self._socket.fileno())
        self._socket.close()

    def run(self):
        self.connect()
        while self._continue:
            result = self._poll.poll()
            for _, event in result:
                if event & POLLIN != 0:
                    self.read_ready()
                if event & POLLOUT != 0:
                    if not self._queue.empty():
                        self.write_ready()
        sleep(3)
        self.disconnect()

    def stop(self):
        self._queue.join()
        self._continue = False

    def write_ready(self):
        buffer = self._queue.get()
        size = len(buffer)
        written = 0
        while written < size:
            written += self._socket.send(buffer[written:])
        self._queue.task_done()

    def read_ready(self):
        buffer = []
        received = self._socket.recv(4096)
        buffer += struct.unpack("B" * len(received), received)
        while len(buffer) >= 8:
            size = buffer[0]
            size += buffer[1] << 8
            size += buffer[2] << 16
            size += buffer[3] << 24
            if size > len(buffer):
                return

            d = DeserializeMethod(buffer[0:size], self.module_id)
            method_name, method_args = d.deserialize()

            f = getattr(self.client, "on_" + method_name, None)
            if f is not None:
                f(*method_args)
            else:
                print("TODO : on_" + method_name)

            del buffer[0:size]

    def send(self, *args):
        s = SerializeMethod(self.module_id, args)
        data = s.serialize()
        size = len(data)
        data[0] = size & 0xFF
        data[1] = (size >> 8) & 0xFF
        data[2] = (size >> 16) & 0xFF
        data[3] = (size >> 24) & 0xFF
        self._queue.put(struct.pack("B" * len(data), *data))
