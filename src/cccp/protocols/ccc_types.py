#!/usr/bin/env python

# This file is part of Interact-IV's CCCP Library.
# Interact-IV.com (c) 2013
#
# Contact: softeam@interact-iv.com
# Authors:
#    - PEMO <pemo@interact-iv.com>

t_uint_32 = 1
t_int_32 = 2
t_real = 3
t_boolean = 4
t_string = 5
t_date = 6
t_uint_64 = 8
t_ecma_expression = 9
t_ecma_instruction = 10
t_uint_8 = 30
t_uint_16 = 31
t_data = 32
t_object = 33
t_any_object = 34
t_uint_64 = 8
t_list = 50
t_internal_reference = 70
t_external_reference = 71
t_direct_reference = 72
t_inherited_uint_32 = 101
t_inherited_int_32 = 102
t_inherited_real = 103
t_inherited_boolean = 104
t_inherited_string = 105
t_inherited_date = 106
t_inherited_uint_64 = 107
t_inherited_internal_reference = 170
t_default = {
    1:0,
    2:0,
    3:0.0,
    4:False,
    5:"",
    6:"" ,
    8:0,
    9:"" ,
    10:"" ,
    50:None ,
    70:None ,
    71:0 ,
    72:None ,
    101:0 ,
    102:0 ,
    103:0.0 ,
    104:False,
    105:"" ,
    106:"" ,
    107:0 ,
    170:None
    }
t_names = {
    1:"t_uint_32",
    2:"t_int_32",
    3:"t_real" ,
    4:"t_boolean",
    5:"t_string",
    6:"t_date" ,
    8:"t_uint_64",
    9:"t_ecma_expression" ,
    10:"t_ecma_instruction" ,
    50:"t_list" ,
    70:"t_internal_reference" ,
    71:"t_external_reference" ,
    72:"t_direct_reference" ,
    101:"t_inherited_uint_32" ,
    102:"t_inherited_int_32" ,
    103:"t_inherited_real" ,
    104:"t_inherited_boolean",
    105:"t_inherited_string" ,
    106:"t_inherited_date" ,
    107:"t_inherited_uint_64" ,
    170:"t_inherited_internal_reference"
    }

