# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: google_cloud_anchor.proto

from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='google_cloud_anchor.proto',
  package='',
  syntax='proto3',
  serialized_options=None,
  create_key=_descriptor._internal_create_key,
  serialized_pb=b'\n\x19google_cloud_anchor.proto\"\xc7\x01\n\x12\x43loudAnchorResolve\x12\x11\n\ttimestamp\x18\x01 \x01(\x01\x12\x17\n\x0f\x63loudAnchorName\x18\x02 \x01(\t\x12\x1f\n\x17resolvedCloudAnchorName\x18\x03 \x01(\t\x12\x19\n\x11\x61nchorTranslation\x18\x04 \x03(\x02\x12\x17\n\x0f\x61nchorRotMatrix\x18\x05 \x03(\x02\x12\x18\n\x10\x61rkitTranslation\x18\x06 \x03(\x02\x12\x16\n\x0e\x61rkitRotMatrix\x18\x07 \x03(\x02\"L\n\x0f\x43loudAnchorHost\x12\x17\n\x0f\x63loudAnchorName\x18\x01 \x01(\t\x12 \n\x18\x61nchorHostRotationMatrix\x18\x02 \x03(\x02\"\x98\x02\n\x15GoogleCloudAnchorData\x12\x39\n\x0cmappingPhase\x18\x01 \x01(\x0b\x32#.GoogleCloudAnchorData.MappingPhase\x12\x43\n\x11localizationPhase\x18\x02 \x01(\x0b\x32(.GoogleCloudAnchorData.LocalizationPhase\x1a\x39\n\x0cMappingPhase\x12)\n\x0f\x63loudAnchorHost\x18\x01 \x01(\x0b\x32\x10.CloudAnchorHost\x1a\x44\n\x11LocalizationPhase\x12/\n\x12\x63loudAnchorResolve\x18\x01 \x03(\x0b\x32\x13.CloudAnchorResolveb\x06proto3'
)




_CLOUDANCHORRESOLVE = _descriptor.Descriptor(
  name='CloudAnchorResolve',
  full_name='CloudAnchorResolve',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='timestamp', full_name='CloudAnchorResolve.timestamp', index=0,
      number=1, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='cloudAnchorName', full_name='CloudAnchorResolve.cloudAnchorName', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='resolvedCloudAnchorName', full_name='CloudAnchorResolve.resolvedCloudAnchorName', index=2,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='anchorTranslation', full_name='CloudAnchorResolve.anchorTranslation', index=3,
      number=4, type=2, cpp_type=6, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='anchorRotMatrix', full_name='CloudAnchorResolve.anchorRotMatrix', index=4,
      number=5, type=2, cpp_type=6, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='arkitTranslation', full_name='CloudAnchorResolve.arkitTranslation', index=5,
      number=6, type=2, cpp_type=6, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='arkitRotMatrix', full_name='CloudAnchorResolve.arkitRotMatrix', index=6,
      number=7, type=2, cpp_type=6, label=3,
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
  serialized_start=30,
  serialized_end=229,
)


_CLOUDANCHORHOST = _descriptor.Descriptor(
  name='CloudAnchorHost',
  full_name='CloudAnchorHost',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='cloudAnchorName', full_name='CloudAnchorHost.cloudAnchorName', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='anchorHostRotationMatrix', full_name='CloudAnchorHost.anchorHostRotationMatrix', index=1,
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
  serialized_start=231,
  serialized_end=307,
)


_GOOGLECLOUDANCHORDATA_MAPPINGPHASE = _descriptor.Descriptor(
  name='MappingPhase',
  full_name='GoogleCloudAnchorData.MappingPhase',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='cloudAnchorHost', full_name='GoogleCloudAnchorData.MappingPhase.cloudAnchorHost', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
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
  serialized_start=463,
  serialized_end=520,
)

_GOOGLECLOUDANCHORDATA_LOCALIZATIONPHASE = _descriptor.Descriptor(
  name='LocalizationPhase',
  full_name='GoogleCloudAnchorData.LocalizationPhase',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='cloudAnchorResolve', full_name='GoogleCloudAnchorData.LocalizationPhase.cloudAnchorResolve', index=0,
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
  serialized_start=522,
  serialized_end=590,
)

_GOOGLECLOUDANCHORDATA = _descriptor.Descriptor(
  name='GoogleCloudAnchorData',
  full_name='GoogleCloudAnchorData',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='mappingPhase', full_name='GoogleCloudAnchorData.mappingPhase', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='localizationPhase', full_name='GoogleCloudAnchorData.localizationPhase', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[_GOOGLECLOUDANCHORDATA_MAPPINGPHASE, _GOOGLECLOUDANCHORDATA_LOCALIZATIONPHASE, ],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=310,
  serialized_end=590,
)

_GOOGLECLOUDANCHORDATA_MAPPINGPHASE.fields_by_name['cloudAnchorHost'].message_type = _CLOUDANCHORHOST
_GOOGLECLOUDANCHORDATA_MAPPINGPHASE.containing_type = _GOOGLECLOUDANCHORDATA
_GOOGLECLOUDANCHORDATA_LOCALIZATIONPHASE.fields_by_name['cloudAnchorResolve'].message_type = _CLOUDANCHORRESOLVE
_GOOGLECLOUDANCHORDATA_LOCALIZATIONPHASE.containing_type = _GOOGLECLOUDANCHORDATA
_GOOGLECLOUDANCHORDATA.fields_by_name['mappingPhase'].message_type = _GOOGLECLOUDANCHORDATA_MAPPINGPHASE
_GOOGLECLOUDANCHORDATA.fields_by_name['localizationPhase'].message_type = _GOOGLECLOUDANCHORDATA_LOCALIZATIONPHASE
DESCRIPTOR.message_types_by_name['CloudAnchorResolve'] = _CLOUDANCHORRESOLVE
DESCRIPTOR.message_types_by_name['CloudAnchorHost'] = _CLOUDANCHORHOST
DESCRIPTOR.message_types_by_name['GoogleCloudAnchorData'] = _GOOGLECLOUDANCHORDATA
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

CloudAnchorResolve = _reflection.GeneratedProtocolMessageType('CloudAnchorResolve', (_message.Message,), {
  'DESCRIPTOR' : _CLOUDANCHORRESOLVE,
  '__module__' : 'google_cloud_anchor_pb2'
  # @@protoc_insertion_point(class_scope:CloudAnchorResolve)
  })
_sym_db.RegisterMessage(CloudAnchorResolve)

CloudAnchorHost = _reflection.GeneratedProtocolMessageType('CloudAnchorHost', (_message.Message,), {
  'DESCRIPTOR' : _CLOUDANCHORHOST,
  '__module__' : 'google_cloud_anchor_pb2'
  # @@protoc_insertion_point(class_scope:CloudAnchorHost)
  })
_sym_db.RegisterMessage(CloudAnchorHost)

GoogleCloudAnchorData = _reflection.GeneratedProtocolMessageType('GoogleCloudAnchorData', (_message.Message,), {

  'MappingPhase' : _reflection.GeneratedProtocolMessageType('MappingPhase', (_message.Message,), {
    'DESCRIPTOR' : _GOOGLECLOUDANCHORDATA_MAPPINGPHASE,
    '__module__' : 'google_cloud_anchor_pb2'
    # @@protoc_insertion_point(class_scope:GoogleCloudAnchorData.MappingPhase)
    })
  ,

  'LocalizationPhase' : _reflection.GeneratedProtocolMessageType('LocalizationPhase', (_message.Message,), {
    'DESCRIPTOR' : _GOOGLECLOUDANCHORDATA_LOCALIZATIONPHASE,
    '__module__' : 'google_cloud_anchor_pb2'
    # @@protoc_insertion_point(class_scope:GoogleCloudAnchorData.LocalizationPhase)
    })
  ,
  'DESCRIPTOR' : _GOOGLECLOUDANCHORDATA,
  '__module__' : 'google_cloud_anchor_pb2'
  # @@protoc_insertion_point(class_scope:GoogleCloudAnchorData)
  })
_sym_db.RegisterMessage(GoogleCloudAnchorData)
_sym_db.RegisterMessage(GoogleCloudAnchorData.MappingPhase)
_sym_db.RegisterMessage(GoogleCloudAnchorData.LocalizationPhase)


# @@protoc_insertion_point(module_scope)