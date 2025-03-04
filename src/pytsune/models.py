from enum import Enum
from typing import Any
from jinja2 import Template

from pydantic import BaseModel


class MethodMode(Enum):
    """Enumeration of supported gRPC method modes.

    Defines the possible combinations of request and response types (unary or streaming).
    """

    UNARY_UNARY = "unary_unary"  # Single request, single response
    UNARY_STREAM = "unary_stream"  # Single request, streaming response
    STREAM_UNARY = "stream_unary"  # Streaming request, single response
    STREAM_STREAM = "stream_stream"  # Streaming request, streaming response


class ProtoField(BaseModel):
    """Represents a field in a proto message or enum."""

    name: str
    index: int
    type: str = ""

    @property
    def proto_string(self) -> str:
        """
        Generate the proto string representation of the field.

        Returns:
            str: A string in the format '<type> <name> = <index>'.
        """
        return f"{self.type} {self.name} = {self.index}".strip()


class ProtoStruct(BaseModel):
    """Represents a proto message or enum structure."""

    name: str
    fields: list[ProtoField]


class ProtoMethod(BaseModel):
    """Represents a method in a proto service."""

    name: str
    request: str
    response: str
    mode: MethodMode = MethodMode.UNARY_UNARY
    client_streaming: bool = False
    server_streaming: bool = False


class ProtoService(BaseModel):
    """Represents a proto service definition."""

    name: str
    methods: list[ProtoMethod]


class ProtoDefine(BaseModel):
    """Represents the complete proto file definition."""

    package: str
    services: list[ProtoService]
    messages: dict[Any, ProtoStruct]
    enums: dict[Any, ProtoStruct]

    def render(
        self,
        proto_template: str,
    ) -> str:
        """
        Render the proto definition using a Jinja2 template.

        Args:
            proto_template: The Jinja2 template string to render.

        Returns:
            str: The rendered proto file content.
        """
        template = Template(proto_template)
        return template.render(proto_define=self)

    def render_proto_file(
        self,
        template,
    ) -> str:
        """
        Render the proto file content using the PROTO_TEMPLATE.

        Returns:
            str: The rendered proto file content.
        """
        return self.render(template)

    def render_python_file(
        self,
        template,
    ) -> str:
        """
        Render the Python client code using the PYTHON_TEMPLATE.

        Returns:
            str: The rendered Python client code.
        """
        return self.render(template)
