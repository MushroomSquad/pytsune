from typing import Dict, List, Union, get_args, get_origin
from types import UnionType
from pathlib import Path
from typing import Sequence
import sys
import subprocess
from logzero import logger


def protoc_compile(
    proto: Path,
    python_out: str = ".",
    grpc_python_out: str = ".",
    proto_paths: Sequence[str] | None = None,
) -> None:
    """
    Compile a proto file into Python modules.

    Executes the protoc compiler to generate pb2 and pb2_grpc files.

    Args:
        proto: The Path to the proto file or directory.
        python_out: Directory for Python output files (default: ".").
        grpc_python_out: Directory for gRPC Python output files (default: ".").
        proto_paths: Optional list of include paths for protoc (default: None).

    Raises:
        FileNotFoundError: If the proto file or directory does not exist.
        RuntimeError: If the protoc compilation fails.
    """
    if not proto.exists():
        raise FileNotFoundError(f"Proto file or directory '{proto}' not found")
    if proto.is_file():
        proto_dir = proto.parent
    else:
        proto_dir = proto
    proto_files = [
        str(f) for f in proto_dir.iterdir() if f.is_file() and f.name.endswith(".proto")
    ]
    protoc_args = [
        sys.executable,
        "-m",
        "grpc_tools.protoc",
        f"--python_out={python_out}",
        f"--grpc_python_out={grpc_python_out}",
        "-I.",
    ]
    if proto_paths is not None:
        protoc_args.extend([f"-I{p}" for p in proto_paths])
    for file in proto_files:
        protoc_args.append(file)
    status_code = subprocess.call(protoc_args)
    if status_code != 0:
        logger.error(f"Command `{' '.join(protoc_args)}` [Err] {status_code=}")
        raise RuntimeError("Protobuf compilation failed")
    logger.info(f"Compiled {proto} success")


def map_simple_type(
    type_,
    origin,
    args,
):
    print("################")
    print("simple type")
    print(type_)
    print(origin)
    print(args)
    print("################\n")


def map_complex_type(): ...


def map_optional_type(
    type_,
    origin,
    args,
):
    print("################")
    print("optional type")
    print(type_)
    print(origin)
    print(args)
    print("################\n")


def map_union_type(
    type_,
    origin,
    args,
):
    print("################")
    print("union type")
    print(type_)
    print(origin)
    print(args)
    print("################\n")


def generate(
    type_,
):
    origin = get_origin(type_)
    args = get_args(type_)
    if origin is None:
        map_simple_type(type_, origin, args)
    elif origin in (Union, UnionType) and type(None) in args:
        map_optional_type(type_, origin, args)
    elif origin in (Union, UnionType) and type(None) not in args:
        map_union_type(type_, origin, args)
    elif origin in (list, List, dict, Dict):
        map_complex_type()
    else:
        raise ValueError(f"Unsupported type: {type_}")


def parse_model(model):
    model_name = model.__class__.__name__
    model_fields = model.model_fields
    print(model_name)
    for field_name, field in model_fields.items():
        generate(field.annotation)
