from datetime import datetime
from .types import (
    Uint32,
    Uint64,
    Int32,
    Int64,
    Double,
    BoolValue,
    BytesValue,
    DoubleValue,
    FloatValue,
    Int32Value,
    Int64Value,
    StringValue,
    UInt32Value,
    UInt64Value,
)

_base_types = {
    # base
    str: "string",
    int: "int32",
    float: "float",
    bool: "bool",
    datetime: "google.protobuf.Timestamp",
    #
    Uint32: "uint32",
    Uint64: "uint64",
    Int32: "int32",
    Int64: "int64",
    Double: "double",
}
_wrapper_types = {
    BoolValue: "google.protobuf.BoolValue",
    BytesValue: "google.protobuf.BytesValue",
    DoubleValue: "google.protobuf.DoubleValue",
    FloatValue: "google.protobuf.FloatValue",
    Int32Value: "google.protobuf.Int32Value",
    Int64Value: "google.protobuf.Int64Value",
    StringValue: "google.protobuf.StringValue",
    UInt32Value: "google.protobuf.UInt32Value",
    UInt64Value: "google.protobuf.UInt64Value",
}
"""Mapping of wrapper types to their proto equivalents."""
