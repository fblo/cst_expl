#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of Interact-IV's CCCP Library.
# Interact-IV.com (c) 2014
#
# Contact: softeam@interact-iv.com
# Authors:
#    - GRIC <gric@interact-iv.com>

import mock

from cccp.protocols.deserializer import Deserializer, DeserializeMethod
from cccp.protocols.errors import DeserializerError
from twisted.trial import unittest

class DeserializerTestCase(unittest.TestCase):
    def setUp(self):
        self.data = [23, 0, 0, 0, 99, 111, 109, 46, 99, 111, 110, 115, 105, 115, 116, 101, 110, 116, 46, 112, 114, 111, 116, 111, 99, 111, 108, 19, 0, 0, 0, 99, 111, 109, 46, 99, 111, 110, 115, 105, 115, 116, 101, 110, 116, 46, 104, 101, 97, 100, 28, 0, 0, 0, 99, 111, 109, 46, 99, 111, 110, 115, 105, 115, 116, 101, 110, 116, 46, 99, 99, 101, 110, 116, 101, 114, 46, 97, 108, 101, 114, 116, 28, 0, 0, 0, 99, 111, 109, 46, 99, 111, 110, 115, 105, 115, 116, 101, 110, 116, 46, 99, 99, 101, 110, 116, 101, 114, 46, 99, 99, 120, 109, 108, 17, 0, 0, 0, 99, 111, 109, 46, 99, 111, 110, 115, 105, 115, 116, 101, 110, 116, 46, 100, 98, 32, 0, 0, 0, 99, 111, 109, 46, 99, 111, 110, 115, 105, 115, 116, 101, 110, 116, 46, 99, 99, 101, 110, 116, 101, 114, 46, 100, 98, 95, 108, 111, 103, 103, 101, 114, 35, 0, 0, 0, 99, 111, 109, 46, 99, 111, 110, 115, 105, 115, 116, 101, 110, 116, 46, 99, 99, 101, 110, 116, 101, 114, 46, 100, 98, 95, 108, 111, 103, 103, 101, 114, 95, 100, 98, 31, 0, 0, 0, 99, 111, 109, 46, 99, 111, 110, 115, 105, 115, 116, 101, 110, 116, 46, 99, 99, 101, 110, 116, 101, 114, 46, 100, 105, 115, 112, 97, 116, 99, 104, 34, 0, 0, 0, 99, 111, 109, 46, 99, 111, 110, 115, 105, 115, 116, 101, 110, 116, 46, 99, 99, 101, 110, 116, 101, 114, 46, 100, 105, 115, 112, 97, 116, 99, 104, 95, 100, 98, 29, 0, 0, 0, 99, 111, 109, 46, 99, 111, 110, 115, 105, 115, 116, 101, 110, 116, 46, 99, 99, 101, 110, 116, 101, 114, 46, 101, 110, 103, 105, 110, 101, 23, 0, 0, 0, 99, 111, 109, 46, 99, 111, 110, 115, 105, 115, 116, 101, 110, 116, 46, 101, 120, 112, 108, 111, 114, 101, 114, 23, 0, 0, 0, 99, 111, 109, 46, 99, 111, 110, 115, 105, 115, 116, 101, 110, 116, 46, 108, 105, 99, 101, 110, 99, 101, 115, 27, 0, 0, 0, 99, 111, 109, 46, 99, 111, 110, 115, 105, 115, 116, 101, 110, 116, 46, 99, 99, 101, 110, 116, 101, 114, 46, 108, 111, 97, 100, 19, 0, 0, 0, 99, 111, 109, 46, 99, 111, 110, 115, 105, 115, 116, 101, 110, 116, 46, 109, 97, 105, 108, 23, 0, 0, 0, 99, 111, 109, 46, 99, 111, 110, 115, 105, 115, 116, 101, 110, 116, 46, 109, 121, 115, 113, 108, 95, 119, 115, 17, 0, 0, 0, 99, 111, 109, 46, 99, 111, 110, 115, 105, 115, 116, 101, 110, 116, 46, 110, 115, 27, 0, 0, 0, 99, 111, 109, 46, 99, 111, 110, 115, 105, 115, 116, 101, 110, 116, 46, 99, 99, 101, 110, 116, 101, 114, 46, 111, 111, 99, 99, 27, 0, 0, 0, 99, 111, 109, 46, 99, 111, 110, 115, 105, 115, 116, 101, 110, 116, 46, 99, 99, 101, 110, 116, 101, 114, 46, 111, 111, 105, 100, 26, 0, 0, 0, 99, 111, 109, 46, 99, 111, 110, 115, 105, 115, 116, 101, 110, 116, 46, 99, 99, 101, 110, 116, 101, 114, 46, 111, 111, 118, 28, 0, 0, 0, 99, 111, 109, 46, 99, 111, 110, 115, 105, 115, 116, 101, 110, 116, 46, 99, 99, 101, 110, 116, 101, 114, 46, 112, 114, 111, 120, 121, 29, 0, 0, 0, 99, 111, 109, 46, 99, 111, 110, 115, 105, 115, 116, 101, 110, 116, 46, 99, 99, 101, 110, 116, 101, 114, 46, 113, 117, 101, 117, 101, 115, 29, 0, 0, 0, 99, 111, 109, 46, 99, 111, 110, 115, 105, 115, 116, 101, 110, 116, 46, 114, 101, 100, 105, 114, 101, 99, 116, 95, 112, 114, 111, 120, 121, 26, 0, 0, 0, 99, 111, 109, 46, 99, 111, 110, 115, 105, 115, 116, 101, 110, 116, 46, 99, 99, 101, 110, 116, 101, 114, 46, 115, 99, 101, 32, 0, 0, 0, 99, 111, 109, 46, 99, 111, 110, 115, 105, 115, 116, 101, 110, 116, 46, 99, 99, 101, 110, 116, 101, 114, 46, 115, 99, 104, 101, 100, 117, 108, 101, 114, 32, 0, 0, 0, 99, 111, 109, 46, 99, 111, 110, 115, 105, 115, 116, 101, 110, 116, 46, 99, 99, 101, 110, 116, 101, 114, 46, 115, 99, 114, 105, 112, 116, 105, 110, 103, 34, 0, 0, 0, 99, 111, 109, 46, 99, 111, 110, 115, 105, 115, 116, 101, 110, 116, 46, 99, 99, 101, 110, 116, 101, 114, 46, 115, 116, 97, 116, 115, 95, 109, 121, 115, 113, 108, 20, 0, 0, 0, 99, 111, 109, 46, 99, 111, 110, 115, 105, 115, 116, 101, 110, 116, 46, 115, 116, 111, 114, 101, 32, 0, 0, 0, 99, 111, 109, 46, 99, 111, 110, 115, 105, 115, 116, 101, 110, 116, 46, 99, 99, 101, 110, 116, 101, 114, 46, 115, 121, 110, 116, 104, 101, 115, 105, 115, 19, 0, 0, 0, 99, 111, 109, 46, 99, 111, 110, 115, 105, 115, 116, 101, 110, 116, 46, 116, 114, 101, 101, 26, 0, 0, 0, 99, 111, 109, 46, 99, 111, 110, 115, 105, 115, 116, 101, 110, 116, 46, 99, 99, 101, 110, 116, 101, 114, 46, 116, 116, 115, 27, 0, 0, 0, 99, 111, 109, 46, 99, 111, 110, 115, 105, 115, 116, 101, 110, 116, 46, 99, 99, 101, 110, 116, 101, 114, 46, 118, 111, 105, 112, 12, 0, 0, 0, 111, 114, 103, 46, 119, 51, 46, 99, 99, 120, 109, 108, 14, 0, 0, 0, 111, 114, 103, 46, 119, 51, 46, 103, 114, 97, 109, 109, 97, 114, 11, 0, 0, 0, 111, 114, 103, 46, 119, 51, 46, 110, 108, 115, 109, 11, 0, 0, 0, 111, 114, 103, 46, 119, 51, 46, 115, 115, 109, 108, 11, 0, 0, 0, 111, 114, 103, 46, 119, 51, 46, 118, 120, 109, 108, 13, 0, 0, 0, 111, 114, 103, 46, 119, 51, 46, 120, 102, 111, 114, 109, 115, 11, 0, 0, 0, 111, 114, 103, 46, 120, 109, 108, 115, 111, 97, 112, 0, 0, 0, 0, 0, 1, 0, 0, 0, 5, 0, 0, 131, 0, 0, 0, 0, 1, 0, 50, 0, 1, 0, 0, 0, 4, 0, 0, 131, 0, 0, 0, 0, 1, 0, 5, 0, 22, 0, 0, 0, 99, 111, 110, 115, 105, 115, 116, 101, 110, 116, 95, 49, 47, 72, 101, 97, 100, 95, 77, 97, 105, 110, 2, 0, 5, 0, 19, 0, 0, 0, 49, 57, 50, 46, 49, 54, 56, 46, 49, 48, 46, 53, 49, 58, 50, 48, 48, 48, 48, 3, 0, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.des = Deserializer(self.data)

    def test_init(self):
        self.assertEquals(self.des.data, self.data)
        self.assertEquals(self.des.src, 0)

    def test_skip_pathes_no_path(self):
        self.des.deserialize_string = mock.MagicMock(return_value = None)
        self.des.deserialize_uint_32 = mock.MagicMock()
        self.des.skip_pathes()
        self.assertEquals(self.des.deserialize_uint_32.called, False)
        self.assertEquals(self.des.deserialize_string.called, True)

    def side_effect_skip_pathes(self):
        if self._called != 2:
            self._called += 1
            return 1
        else:
            return None

    def test_skip_pathes_have_path(self):
        self._called = 0
        self.des.deserialize_string = mock.MagicMock(side_effect = self.side_effect_skip_pathes)
        self.des.deserialize_uint_32 = mock.MagicMock()
        self.des.skip_pathes()
        self.assertEquals(self.des.deserialize_uint_32.called, False)
        self.assertEquals(self.des.deserialize_string.call_count, 3)

    def test_deserialize_cdep_objects_no_arg(self):
        self.des.skip_pathes = mock.MagicMock()
        self.des.deserialize_body = mock.MagicMock()

        self.des.deserialize_cdep_objects()

        self.assertEquals(self.des.create_all_fields, False)
        self.assertEquals(self.des.skip_pathes.called, True)
        self.assertEquals(self.des.deserialize_body.called, True)

    def test_deserialize_cdep_object_with_arg(self):
        self.des.skip_pathes = mock.MagicMock()
        self.des.deserialize_body = mock.MagicMock()

        self.des.deserialize_cdep_objects(True)

        self.assertEquals(self.des.create_all_fields, True)
        self.assertEquals(self.des.skip_pathes.called, True)
        self.assertEquals(self.des.deserialize_body.called, True)

    def test_deserialize_body_same_len(self):
        self.des.src = 1160
        result = self.des.deserialize_body()
        self.assertEquals(result, None)

    def test_deserialize_body_different_len(self):
        self.des.deserialize_uint_32 = mock.MagicMock()
        self.des.deserialize_uint_8 = mock.MagicMock(return_value = 0)
        self.des.deserialize_object = mock.MagicMock()
        self.des.deserialize_body()

        self.assertEquals(self.des.deserialize_uint_8.called, True)
        self.assertEquals(self.des.deserialize_uint_32.called, True)
        self.assertEquals(self.des.deserialize_object.called, True)

    @mock.patch("cccp.protocols.deserializer.classes")
    def test_deserialize_object_raise(self, mock_classes):
        mock_classes.all_classes_by_id = mock.MagicMock()
        mock_classes.all_classes_by_id.has_key = mock.MagicMock(return_value = False)
        self.des.deserialize_uint_32 = mock.MagicMock()
        self.assertRaises(DeserializerError, self.des.deserialize_object)

    @mock.patch("cccp.protocols.deserializer.classes")
    @mock.patch("cccp.protocols.deserializer.new_object")
    def test_deserialize_object(self, mock_object, mock_classes):
        object = mock.MagicMock()

        mock_object.return_value = object
        mock_classes.all_classes_by_id = {"class_id": ("class_name", "class_field_by_id", "class_namespace")}

        self.des.deserialize_uint_32 = mock.MagicMock(return_value = "class_id")
        self.des.deserialize_content = mock.MagicMock()

        self.des.deserialize_object()

        self.assertEquals(self.des.deserialize_uint_32.call_count, 2)
        self.des.deserialize_content.assert_called_once_with(object, "class_field_by_id")
