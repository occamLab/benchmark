# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: april_tag.proto

from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='april_tag.proto',
  package='',
  syntax='proto3',
  serialized_options=None,
  create_key=_descriptor._internal_create_key,
  serialized_pb=b'\n\x0f\x61pril_tag.proto\"=\n\x11\x41prilTagTimestamp\x12\x11\n\ttimestamp\x18\x01 \x01(\x01\x12\x15\n\rtagCenterPose\x18\x02 \x03(\x02\"\xf5\x01\n\x0c\x41prilTagData\x12\x30\n\x0cmappingPhase\x18\x01 \x01(\x0b\x32\x1a.AprilTagData.MappingPhase\x12:\n\x11localizationPhase\x18\x02 \x01(\x0b\x32\x1f.AprilTagData.LocalizationPhase\x1a\x38\n\x0cMappingPhase\x12(\n\x0cmeasurements\x18\x01 \x03(\x0b\x32\x12.AprilTagTimestamp\x1a=\n\x11LocalizationPhase\x12(\n\x0cmeasurements\x18\x01 \x03(\x0b\x32\x12.AprilTagTimestampb\x06proto3'
)




_APRILTAGTIMESTAMP = _descriptor.Descriptor(
  name='AprilTagTimestamp',
  full_name='AprilTagTimestamp',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='timestamp', full_name='AprilTagTimestamp.timestamp', index=0,
      number=1, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='tagCenterPose', full_name='AprilTagTimestamp.tagCenterPose', index=1,
      number=2, type=2, cpp_type=6, label=3,
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
  serialized_start=19,
  serialized_end=80,
)


_APRILTAGDATA_MAPPINGPHASE = _descriptor.Descriptor(
  name='MappingPhase',
  full_name='AprilTagData.MappingPhase',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='measurements', full_name='AprilTagData.MappingPhase.measurements', index=0,
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
  serialized_start=209,
  serialized_end=265,
)

_APRILTAGDATA_LOCALIZATIONPHASE = _descriptor.Descriptor(
  name='LocalizationPhase',
  full_name='AprilTagData.LocalizationPhase',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='measurements', full_name='AprilTagData.LocalizationPhase.measurements', index=0,
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
  serialized_start=267,
  serialized_end=328,
)

_APRILTAGDATA = _descriptor.Descriptor(
  name='AprilTagData',
  full_name='AprilTagData',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='mappingPhase', full_name='AprilTagData.mappingPhase', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='localizationPhase', full_name='AprilTagData.localizationPhase', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[_APRILTAGDATA_MAPPINGPHASE, _APRILTAGDATA_LOCALIZATIONPHASE, ],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=83,
  serialized_end=328,
)

_APRILTAGDATA_MAPPINGPHASE.fields_by_name['measurements'].message_type = _APRILTAGTIMESTAMP
_APRILTAGDATA_MAPPINGPHASE.containing_type = _APRILTAGDATA
_APRILTAGDATA_LOCALIZATIONPHASE.fields_by_name['measurements'].message_type = _APRILTAGTIMESTAMP
_APRILTAGDATA_LOCALIZATIONPHASE.containing_type = _APRILTAGDATA
_APRILTAGDATA.fields_by_name['mappingPhase'].message_type = _APRILTAGDATA_MAPPINGPHASE
_APRILTAGDATA.fields_by_name['localizationPhase'].message_type = _APRILTAGDATA_LOCALIZATIONPHASE
DESCRIPTOR.message_types_by_name['AprilTagTimestamp'] = _APRILTAGTIMESTAMP
DESCRIPTOR.message_types_by_name['AprilTagData'] = _APRILTAGDATA
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

AprilTagTimestamp = _reflection.GeneratedProtocolMessageType('AprilTagTimestamp', (_message.Message,), {
  'DESCRIPTOR' : _APRILTAGTIMESTAMP,
  '__module__' : 'april_tag_pb2'
  # @@protoc_insertion_point(class_scope:AprilTagTimestamp)
  })
_sym_db.RegisterMessage(AprilTagTimestamp)

AprilTagData = _reflection.GeneratedProtocolMessageType('AprilTagData', (_message.Message,), {

  'MappingPhase' : _reflection.GeneratedProtocolMessageType('MappingPhase', (_message.Message,), {
    'DESCRIPTOR' : _APRILTAGDATA_MAPPINGPHASE,
    '__module__' : 'april_tag_pb2'
    # @@protoc_insertion_point(class_scope:AprilTagData.MappingPhase)
    })
  ,

  'LocalizationPhase' : _reflection.GeneratedProtocolMessageType('LocalizationPhase', (_message.Message,), {
    'DESCRIPTOR' : _APRILTAGDATA_LOCALIZATIONPHASE,
    '__module__' : 'april_tag_pb2'
    # @@protoc_insertion_point(class_scope:AprilTagData.LocalizationPhase)
    })
  ,
  'DESCRIPTOR' : _APRILTAGDATA,
  '__module__' : 'april_tag_pb2'
  # @@protoc_insertion_point(class_scope:AprilTagData)
  })
_sym_db.RegisterMessage(AprilTagData)
_sym_db.RegisterMessage(AprilTagData.MappingPhase)
_sym_db.RegisterMessage(AprilTagData.LocalizationPhase)


# @@protoc_insertion_point(module_scope)