# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: lidar.proto

from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='lidar.proto',
  package='',
  syntax='proto3',
  serialized_options=None,
  create_key=_descriptor._internal_create_key,
  serialized_pb=b'\n\x0blidar.proto\"@\n\x0eLidarTimestamp\x12\x11\n\ttimestamp\x18\x01 \x01(\x01\x12\r\n\x05lidar\x18\x02 \x03(\x02\x12\x0c\n\x04\x63onf\x18\x03 \x03(\r\"\xe6\x01\n\tLidarData\x12-\n\x0cmappingPhase\x18\x01 \x01(\x0b\x32\x17.LidarData.MappingPhase\x12\x37\n\x11localizationPhase\x18\x02 \x01(\x0b\x32\x1c.LidarData.LocalizationPhase\x1a\x35\n\x0cMappingPhase\x12%\n\x0cmeasurements\x18\x01 \x03(\x0b\x32\x0f.LidarTimestamp\x1a:\n\x11LocalizationPhase\x12%\n\x0cmeasurements\x18\x01 \x03(\x0b\x32\x0f.LidarTimestampb\x06proto3'
)




_LIDARTIMESTAMP = _descriptor.Descriptor(
  name='LidarTimestamp',
  full_name='LidarTimestamp',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='timestamp', full_name='LidarTimestamp.timestamp', index=0,
      number=1, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='lidar', full_name='LidarTimestamp.lidar', index=1,
      number=2, type=2, cpp_type=6, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='conf', full_name='LidarTimestamp.conf', index=2,
      number=3, type=13, cpp_type=3, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=15,
  serialized_end=79,
)


_LIDARDATA_MAPPINGPHASE = _descriptor.Descriptor(
  name='MappingPhase',
  full_name='LidarData.MappingPhase',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='measurements', full_name='LidarData.MappingPhase.measurements', index=0,
      number=1, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=199,
  serialized_end=252,
)

_LIDARDATA_LOCALIZATIONPHASE = _descriptor.Descriptor(
  name='LocalizationPhase',
  full_name='LidarData.LocalizationPhase',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='measurements', full_name='LidarData.LocalizationPhase.measurements', index=0,
      number=1, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=254,
  serialized_end=312,
)

_LIDARDATA = _descriptor.Descriptor(
  name='LidarData',
  full_name='LidarData',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='mappingPhase', full_name='LidarData.mappingPhase', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='localizationPhase', full_name='LidarData.localizationPhase', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[_LIDARDATA_MAPPINGPHASE, _LIDARDATA_LOCALIZATIONPHASE, ],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=82,
  serialized_end=312,
)

_LIDARDATA_MAPPINGPHASE.fields_by_name['measurements'].message_type = _LIDARTIMESTAMP
_LIDARDATA_MAPPINGPHASE.containing_type = _LIDARDATA
_LIDARDATA_LOCALIZATIONPHASE.fields_by_name['measurements'].message_type = _LIDARTIMESTAMP
_LIDARDATA_LOCALIZATIONPHASE.containing_type = _LIDARDATA
_LIDARDATA.fields_by_name['mappingPhase'].message_type = _LIDARDATA_MAPPINGPHASE
_LIDARDATA.fields_by_name['localizationPhase'].message_type = _LIDARDATA_LOCALIZATIONPHASE
DESCRIPTOR.message_types_by_name['LidarTimestamp'] = _LIDARTIMESTAMP
DESCRIPTOR.message_types_by_name['LidarData'] = _LIDARDATA
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

LidarTimestamp = _reflection.GeneratedProtocolMessageType('LidarTimestamp', (_message.Message,), {
  'DESCRIPTOR' : _LIDARTIMESTAMP,
  '__module__' : 'lidar_pb2'
  # @@protoc_insertion_point(class_scope:LidarTimestamp)
  })
_sym_db.RegisterMessage(LidarTimestamp)

LidarData = _reflection.GeneratedProtocolMessageType('LidarData', (_message.Message,), {

  'MappingPhase' : _reflection.GeneratedProtocolMessageType('MappingPhase', (_message.Message,), {
    'DESCRIPTOR' : _LIDARDATA_MAPPINGPHASE,
    '__module__' : 'lidar_pb2'
    # @@protoc_insertion_point(class_scope:LidarData.MappingPhase)
    })
  ,

  'LocalizationPhase' : _reflection.GeneratedProtocolMessageType('LocalizationPhase', (_message.Message,), {
    'DESCRIPTOR' : _LIDARDATA_LOCALIZATIONPHASE,
    '__module__' : 'lidar_pb2'
    # @@protoc_insertion_point(class_scope:LidarData.LocalizationPhase)
    })
  ,
  'DESCRIPTOR' : _LIDARDATA,
  '__module__' : 'lidar_pb2'
  # @@protoc_insertion_point(class_scope:LidarData)
  })
_sym_db.RegisterMessage(LidarData)
_sym_db.RegisterMessage(LidarData.MappingPhase)
_sym_db.RegisterMessage(LidarData.LocalizationPhase)


# @@protoc_insertion_point(module_scope)
