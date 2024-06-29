# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: gyro.proto

from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='gyro.proto',
  package='',
  syntax='proto3',
  serialized_options=None,
  create_key=_descriptor._internal_create_key,
  serialized_pb=b'\n\ngyro.proto\"g\n\rGyroTimestamp\x12\x11\n\ttimestamp\x18\x01 \x01(\x01\x12\x15\n\rxRotationRate\x18\x02 \x01(\x01\x12\x15\n\ryRotationRate\x18\x03 \x01(\x01\x12\x15\n\rzRotationRate\x18\x04 \x01(\x01\"\xe1\x01\n\x08GyroData\x12,\n\x0cmappingPhase\x18\x01 \x01(\x0b\x32\x16.GyroData.MappingPhase\x12\x36\n\x11localizationPhase\x18\x02 \x01(\x0b\x32\x1b.GyroData.LocalizationPhase\x1a\x34\n\x0cMappingPhase\x12$\n\x0cmeasurements\x18\x01 \x03(\x0b\x32\x0e.GyroTimestamp\x1a\x39\n\x11LocalizationPhase\x12$\n\x0cmeasurements\x18\x01 \x03(\x0b\x32\x0e.GyroTimestampb\x06proto3'
)




_GYROTIMESTAMP = _descriptor.Descriptor(
  name='GyroTimestamp',
  full_name='GyroTimestamp',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='timestamp', full_name='GyroTimestamp.timestamp', index=0,
      number=1, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='xRotationRate', full_name='GyroTimestamp.xRotationRate', index=1,
      number=2, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='yRotationRate', full_name='GyroTimestamp.yRotationRate', index=2,
      number=3, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='zRotationRate', full_name='GyroTimestamp.zRotationRate', index=3,
      number=4, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=float(0),
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
  serialized_start=14,
  serialized_end=117,
)


_GYRODATA_MAPPINGPHASE = _descriptor.Descriptor(
  name='MappingPhase',
  full_name='GyroData.MappingPhase',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='measurements', full_name='GyroData.MappingPhase.measurements', index=0,
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
  serialized_start=234,
  serialized_end=286,
)

_GYRODATA_LOCALIZATIONPHASE = _descriptor.Descriptor(
  name='LocalizationPhase',
  full_name='GyroData.LocalizationPhase',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='measurements', full_name='GyroData.LocalizationPhase.measurements', index=0,
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
  serialized_start=288,
  serialized_end=345,
)

_GYRODATA = _descriptor.Descriptor(
  name='GyroData',
  full_name='GyroData',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='mappingPhase', full_name='GyroData.mappingPhase', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='localizationPhase', full_name='GyroData.localizationPhase', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[_GYRODATA_MAPPINGPHASE, _GYRODATA_LOCALIZATIONPHASE, ],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=120,
  serialized_end=345,
)

_GYRODATA_MAPPINGPHASE.fields_by_name['measurements'].message_type = _GYROTIMESTAMP
_GYRODATA_MAPPINGPHASE.containing_type = _GYRODATA
_GYRODATA_LOCALIZATIONPHASE.fields_by_name['measurements'].message_type = _GYROTIMESTAMP
_GYRODATA_LOCALIZATIONPHASE.containing_type = _GYRODATA
_GYRODATA.fields_by_name['mappingPhase'].message_type = _GYRODATA_MAPPINGPHASE
_GYRODATA.fields_by_name['localizationPhase'].message_type = _GYRODATA_LOCALIZATIONPHASE
DESCRIPTOR.message_types_by_name['GyroTimestamp'] = _GYROTIMESTAMP
DESCRIPTOR.message_types_by_name['GyroData'] = _GYRODATA
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

GyroTimestamp = _reflection.GeneratedProtocolMessageType('GyroTimestamp', (_message.Message,), {
  'DESCRIPTOR' : _GYROTIMESTAMP,
  '__module__' : 'gyro_pb2'
  # @@protoc_insertion_point(class_scope:GyroTimestamp)
  })
_sym_db.RegisterMessage(GyroTimestamp)

GyroData = _reflection.GeneratedProtocolMessageType('GyroData', (_message.Message,), {

  'MappingPhase' : _reflection.GeneratedProtocolMessageType('MappingPhase', (_message.Message,), {
    'DESCRIPTOR' : _GYRODATA_MAPPINGPHASE,
    '__module__' : 'gyro_pb2'
    # @@protoc_insertion_point(class_scope:GyroData.MappingPhase)
    })
  ,

  'LocalizationPhase' : _reflection.GeneratedProtocolMessageType('LocalizationPhase', (_message.Message,), {
    'DESCRIPTOR' : _GYRODATA_LOCALIZATIONPHASE,
    '__module__' : 'gyro_pb2'
    # @@protoc_insertion_point(class_scope:GyroData.LocalizationPhase)
    })
  ,
  'DESCRIPTOR' : _GYRODATA,
  '__module__' : 'gyro_pb2'
  # @@protoc_insertion_point(class_scope:GyroData)
  })
_sym_db.RegisterMessage(GyroData)
_sym_db.RegisterMessage(GyroData.MappingPhase)
_sym_db.RegisterMessage(GyroData.LocalizationPhase)


# @@protoc_insertion_point(module_scope)
