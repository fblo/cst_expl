#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of Interact-IV's CCCP Library.
# Interact-IV.com (c) 2017
#
# Contact: softeam@interact-iv.com
# Authors:
#    - GRIC <gric@interact-iv.com>

from struct import unpack, pack

from twisted.internet.protocol import Protocol

from cccp.protocols.deserializer import DeserializeMethod
from cccp.protocols.errors import DeserializerError
from cccp.protocols.errors import SerializerError
from cccp.protocols.serializer import SerializeMethod

from ivcommons.log import Log

log = Log("cccp.async.protocol")


class CCCProtocol(Protocol):
    def __init__(self, factory):
        """
            Here we set some default variables.
            :param factory: The factory used to communicate with.
            :type factory: IVReconnectingClientFactory
        """
        self.log = getattr(factory, 'log', log)
        self.buffer = []
        self.version = 1234
        self.compression_supported = True
        self.setup = False
        self.factory = factory

    def connectionMade(self):
        self.sendMessage(
            self.factory.module_id, self.version, self.compression_supported
        )

    def dataReceived(self, data):
        self.buffer += unpack("B" * len(data), data)
        while len(self.buffer) >= 8:
            size = self.buffer[0]
            size += self.buffer[1] << 8
            size += self.buffer[2] << 16
            size += self.buffer[3] << 24

            if size > len(self.buffer):
                return

            try:
                deserializer = DeserializeMethod(
                    self.buffer[0:size], self.factory.module_id
                )
                (method_name, method_args) = deserializer.deserialize()

            except DeserializerError:
                self.log.error(
                    'Deserialization error : Event ignored %s' % (
                        str(self.buffer[0:size]),
                    )
                )
                del self.buffer[0:size]
                return

            del self.buffer[0:size]
            self.call_factory_method(method_name, method_args)

    def sendMessage(self, *args):
        data = self.serialize(args)
        self.transport.write(data)

    def serialize(self, data):
        try:
            serializer = SerializeMethod(self.factory.module_id, data)
            data = serializer.serialize()

        except SerializerError:
            self.log.error("Serialization error : Bad data %s" % (data,))
            return None

        size = len(data)
        data[0] = size & 0xFF
        data[1] = (size >> 8) & 0xFF
        data[2] = (size >> 16) & 0xFF
        data[3] = (size >> 24) & 0xFF
        data = pack("B" * len(data), *data)
        return data

    def call_factory_method(self, method_name, method_args):
        if not hasattr(self.factory, "on_%s" % method_name):
            self.log.info('Event not handled: %s, %s' % (
                          method_name, method_args))
            return

        fn = getattr(self.factory, "on_%s" % method_name)
        if not callable(fn):
            return

        try:
            fn(*method_args)
        except Exception as e:
            self.log.error("Call error: %s(%s)" % (method_name, method_args))
            self.log.error(str(e))
