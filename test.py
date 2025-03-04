from typing import Dict, List, Optional
from pydantic import BaseModel

from fast_grpc import ControllerMeta
from fast_grpc import Controller
from src import ProtoBuilder


class TestModel(BaseModel):
    string_: str
    int_: int
    float_: float
    bool: bool
    list_: list
    List_: List
    dict_: dict
    Dict_: Dict
    list_str: list[str]
    List_str: List[str]
    dict_str: dict[str, str]
    Dict_str: Dict[str, str]
    Optional_: Optional[str]
    Optional_None: Optional[str] = None
    Optional_UnionType: str | None
    Union_: str | int
    Union_complex: str | dict[str, str]


class ServiceTest(
    metaclass=ControllerMeta,
    proto_path="protos/",
    middlewares=[],
    exceptions={},
):
    @staticmethod
    async def unary_unary(
        request: TestModel,
    ) -> TestModel:
        return TestModel()


def main():
    service = ServiceTest()
    path_name = f"{service.proto}:{service.name}"
    services = {}
    if path_name not in services:
        services[path_name] = Controller(
            name=service.name,
            proto=service.proto,
        )
    services[path_name].methods.update(service.methods)
    builders = {}
    for service in services.values():
        if not service.methods:
            continue
        if service.proto_path not in builders:
            builders[service.proto_path] = ProtoBuilder(package=service.proto_path.stem)
        builders[service.proto_path].add_service(service)
    for proto, builder in builders.items():
        proto_define = builder.get_proto()
        content = proto_define.render_proto_file()
        proto.parent.mkdir(parents=True, exist_ok=True)
        proto.write_text(content)


if __name__ == "__main__":
    main()
