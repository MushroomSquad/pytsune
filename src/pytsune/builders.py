from types import UnionType
from typing import Union, Sequence
from pydantic import BaseModel
from google.protobuf.descriptor import (
    Descriptor,
    ServiceDescriptor,
    FieldDescriptor,
    EnumDescriptor,
)
from enum import IntEnum
from typing_extensions import get_args, get_origin
from pathlib import Path
import grpc

from .utils import protoc_compile, generate
from .models import (
    ProtoDefine,
    ProtoService,
    ProtoMethod,
    ProtoStruct,
    ProtoField,
    MethodMode,
)
from .mapping import _base_types
from .types import Empty


class ProtoBuilder:
    """Builder class for constructing proto definitions from services."""

    def __init__(self, package: str) -> None:
        """
        Initialize the ProtoBuilder with a package name.

        Args:
            package: The package name for the proto definition.
        """
        self._proto_define = ProtoDefine(
            package=package, services=[], messages={}, enums={}
        )

    def add_service(self, service: "Controller") -> "ProtoBuilder":
        """
        Add a service to the proto definition.

        Args:
            service: The Service instance to add.

        Returns:
            ProtoBuilder: Self, for method chaining.По встречи на 2-м этаже.
        """
        srv = ProtoService(name=service.name, methods=[])
        self._proto_define.services.append(srv)
        for name, method in service.methods.items():
            request = self.convert_message(method.request_model or Empty)
            response = self.convert_message(method.response_model or Empty)
            proto_method = ProtoMethod(
                name=name, request=request.name, response=response.name
            )
            if method.mode in {MethodMode.STREAM_UNARY, MethodMode.STREAM_STREAM}:
                proto_method.request = f"stream {proto_method.request}"
            if method.mode in {MethodMode.UNARY_STREAM, MethodMode.STREAM_STREAM}:
                proto_method.response = f"stream {proto_method.response}"
            srv.methods.append(proto_method)
        return self

    def get_proto(self) -> ProtoDefine:
        """
        Get the constructed proto definition.

        Returns:
            ProtoDefine: The complete proto definition object.
        """
        return self._proto_define

    def convert_message(self, schema: type[BaseModel]) -> ProtoStruct:
        """
        Convert a Pydantic model to a proto message structure.

        Args:
            schema: The Pydantic model to convert.

        Returns:
            ProtoStruct: The corresponding proto message structure.
        """
        if schema in self._proto_define.messages:
            return self._proto_define.messages[schema]
        message = ProtoStruct(name=generate(schema), fields=[])
        for i, (name, field) in enumerate(schema.model_fields.items(), 1):
            type_name = self._get_type_name(field.annotation)
            message.fields.append(ProtoField(name=name, type=type_name, index=i))
        self._proto_define.messages[schema] = message
        return message

    def convert_enum(self, schema: type[IntEnum]) -> ProtoStruct:
        """
        Convert an IntEnum to a proto enum structure.

        Args:
            schema: The IntEnum to convert.

        Returns:
            ProtoStruct: The corresponding proto enum structure.
        """
        if schema in self._proto_define.enums:
            return self._proto_define.enums[schema]
        enum_struct = ProtoStruct(
            name=schema.__name__,
            fields=[
                ProtoField(name=member.name, index=member.value) for member in schema
            ],
        )
        self._proto_define.enums[schema] = enum_struct
        return enum_struct

    def _get_type_name(self, type_: type) -> str:
        """
        Get the proto type name for a given Python type.

        Args:
            type_: The Python type to convert.

        Returns:
            str: The proto-compatible type name.

        Raises:
            ValueError: If the type is unsupported.
        """
        generate()


class ClientBuilder:
    """Builder class for constructing client-side proto definitions from descriptors."""

    def __init__(self, package: str) -> None:
        """
        Initialize the ClientBuilder with a package name.

        Args:
            package: The package name for the proto definition.
        """
        self._proto_define = ProtoDefine(
            package=package, services=[], messages={}, enums={}
        )
        self.pb2 = grpc.protos(self._proto_define.package)
        self._proto_package = self.pb2.DESCRIPTOR.package

    def get_proto(self) -> ProtoDefine:
        """
        Get the constructed proto definition from descriptors.

        Returns:
            ProtoDefine: The complete proto definition object.
        """
        for service in self.pb2.DESCRIPTOR.services_by_name.values():
            self.add_service(service)
        return self._proto_define

    def add_service(self, service: ServiceDescriptor) -> "ClientBuilder":
        """
        Add a service to the proto definition from a descriptor.

        Args:
            service: The ServiceDescriptor to add.

        Returns:
            ClientBuilder: Self, for method chaining.
        """
        srv = ProtoService(name=service.name, methods=[])
        self._proto_define.services.append(srv)
        for name, method in service.methods_by_name.items():
            request = self.convert_message(method.input_type)
            response = self.convert_message(method.output_type)
            proto_method = ProtoMethod(
                name=name,
                request=request.name,
                response=response.name,
                client_streaming=method.client_streaming,
                server_streaming=method.server_streaming,
            )
            if method.client_streaming and method.server_streaming:
                proto_method.mode = MethodMode.STREAM_STREAM
            elif method.client_streaming:
                proto_method.mode = MethodMode.STREAM_UNARY
            elif method.server_streaming:
                proto_method.mode = MethodMode.UNARY_STREAM
            else:
                proto_method.mode = MethodMode.UNARY_UNARY
            srv.methods.append(proto_method)
        return self

    def _gen_class_name(self, name: str) -> str:
        """
        Generate a class name from a fully qualified proto name.

        Args:
            name: The fully qualified proto name.

        Returns:
            str: A simplified class name with underscores instead of dots.
        """
        return "_".join(name.removeprefix(f"{self._proto_package}.").split("."))

    def convert_message(self, message: Descriptor) -> ProtoStruct:
        """
        Convert a proto message descriptor to a ProtoStruct.

        Args:
            message: The Descriptor of the proto message.

        Returns:
            ProtoStruct: The corresponding proto message structure.
        """
        if message in self._proto_define.messages:
            return self._proto_define.messages[message]
        name = self._gen_class_name(message.full_name)
        schema = ProtoStruct(name=name, fields=[])
        for i, field in enumerate(message.fields):
            type_name = self._get_type_name(field)
            schema.fields.append(ProtoField(name=field.name, type=type_name, index=i))
        self._proto_define.messages[message] = schema
        return schema

    def convert_enum(self, enum_meta: EnumDescriptor) -> ProtoStruct:
        """
        Convert a proto enum descriptor to a ProtoStruct.

        Args:
            enum_meta: The EnumDescriptor of the proto enum.

        Returns:
            ProtoStruct: The corresponding proto enum structure.
        """
        if enum_meta in self._proto_define.enums:
            return self._proto_define.enums[enum_meta]
        name = self._gen_class_name(enum_meta.full_name)
        enum_struct = ProtoStruct(
            name=name,
            fields=[
                ProtoField(name=name, index=value.index)
                for name, value in enum_meta.values_by_name.items()
            ],
        )
        self._proto_define.enums[enum_meta] = enum_struct
        return enum_struct

    def _get_type_name(self, field: FieldDescriptor) -> str:
        """
        Get the proto type name for a field descriptor.

        Args:
            field: The FieldDescriptor to convert.

        Returns:
            str: The proto-compatible type name.

        Raises:
            ValueError: If the field type is unsupported.
        """
        if field.message_type and field.message_type.GetOptions().map_entry:
            key_type = self._get_type_name(field.message_type.fields_by_name["key"])
            value_type = self._get_type_name(field.message_type.fields_by_name["value"])
            return f"dict[{key_type}, {value_type}]"

        def get_base_type() -> str:
            if field.type == FieldDescriptor.TYPE_MESSAGE:
                message = self.convert_message(field.message_type)
                return message.name
            elif field.type == FieldDescriptor.TYPE_ENUM:
                struct = self.convert_enum(field.enum_type)
                return struct.name

            type_map = {
                FieldDescriptor.TYPE_DOUBLE: "float",
                FieldDescriptor.TYPE_FLOAT: "float",
                FieldDescriptor.TYPE_INT64: "int",
                FieldDescriptor.TYPE_UINT64: "int",
                FieldDescriptor.TYPE_INT32: "int",
                FieldDescriptor.TYPE_FIXED64: "int",
                FieldDescriptor.TYPE_FIXED32: "int",
                FieldDescriptor.TYPE_UINT32: "int",
                FieldDescriptor.TYPE_SFIXED32: "int",
                FieldDescriptor.TYPE_SFIXED64: "int",
                FieldDescriptor.TYPE_SINT32: "int",
                FieldDescriptor.TYPE_SINT64: "int",
                FieldDescriptor.TYPE_BOOL: "bool",
                FieldDescriptor.TYPE_STRING: "str",
                FieldDescriptor.TYPE_BYTES: "bytes",
            }

            if field.type in type_map:
                return type_map[field.type]

            raise ValueError(f"Unsupported field type: {field.type}")

        base_type = get_base_type()
        if field.label == FieldDescriptor.LABEL_REPEATED:
            return f"list[{base_type}]"
        return base_type


def proto_to_python_client(proto_path: str, template) -> str:
    """
    Generate Python client code from a proto file.

    Compiles the proto file and builds a client-side proto definition.

    Args:
        proto_path: The path to the proto file.

    Returns:
        str: The generated Python client code.
    """
    protoc_compile(Path(proto_path))
    builder = ClientBuilder(proto_path)
    proto_define = builder.get_proto()
    return proto_define.render_python_file(template)
