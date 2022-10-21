import ast
import codecs
from ast import (
    Add,
    BinOp,
    Call,
    ListComp,
    Load,
    Name,
    Slice,
    Starred,
    Store,
    Subscript,
    comprehension,
)
from contextlib import suppress
from io import BytesIO
from tokenize import tokenize, untokenize
from typing import Dict, List, Tuple, Union

TARGET_PATTERN = ["[", ":", ":", ":", "]"]


def index(l: list, target: str, count: int = 0) -> List[int]:
    indices = [i for i, value in enumerate(l) if value == target]

    if count:
        return indices[count:]
    else:
        return indices


def pairs_are_equal(l: list) -> bool:
    if l and len(index(l, "[")) == len(index(l, "]")):
        return True
    else:
        return False


def check_pattern(string: str) -> bool:
    marked_list, is_marked = [], False

    for token in tokenize(BytesIO(string.encode("utf-8")).readline):
        _, tok_val, _, _, _ = token
        if "[" == tok_val or ":" == tok_val or "]" == tok_val:
            marked_list.append(tok_val)

    if TARGET_PATTERN == marked_list:
        return True
    else:
        return False


def set_tree_parents(tree: ast.AST) -> None:
    for node in ast.walk(tree):
        for child_node in ast.iter_child_nodes(node):
            child_node.parent = node  # type: ignore


def new_list_expr(string: str) -> ast.AST:
    name_of_list, rest = string.split("[")
    start, stop, _, step = rest.strip("]").split(":")

    node = Starred(
        value=Subscript(
            value=ListComp(
                elt=Subscript(
                    value=Name(id=f"{name_of_list}", ctx=Load()),
                    slice=Slice(
                        lower=Name(id="index", ctx=Load()),
                        upper=BinOp(
                            left=Name(id="index", ctx=Load()),
                            op=Add(),
                            right=Name(id=f"{stop}", ctx=Load()),
                        ),
                    ),
                    ctx=Load(),
                ),
                generators=[
                    comprehension(
                        target=Name(id="index", ctx=Store()),
                        iter=Call(
                            func=Name(id="range", ctx=Load()),
                            args=[
                                Name(id=f"{start}", ctx=Load()),
                                Call(
                                    func=Name(id="len", ctx=Load()),
                                    args=[
                                        Name(id=f"{name_of_list}", ctx=Load())
                                    ],
                                    keywords=[],
                                ),
                                Name(id=f"{stop}", ctx=Load()),
                            ],
                            keywords=[],
                        ),
                        ifs=[],
                        is_async=0,
                    )
                ],
            ),
            slice=Slice(upper=Name(id=f"{step}", ctx=Load())),
            ctx=Load(),
        ),
    )

    return node


class ModifyExpression(ast.NodeTransformer):
    def __init__(self) -> None:
        super().__init__()
        self.nodes: Dict[int, str] = {}

    def visit_Constant(self, node: ast.AST) -> ast.AST:
        if id(node) in self.nodes:
            new_node = new_list_expr(
                node.value.replace("__unpack", self.nodes[id(node)])  # type: ignore
            )
            return new_node
        else:
            return node

    def visit_Name(self, node: ast.AST) -> ast.AST:
        with suppress(AttributeError):
            if node.parent.slice.value.startswith("__unpack"):  # type: ignore
                self.nodes[id(node.parent.slice)] = node.id  # type: ignore
                node.id = ""  # type: ignore
        return node


def modify_notation(source: str, new_line: bool = False) -> str:
    token_list, marked_list, patterns, is_marked = [], [], [], False
    unmodified_source = source

    if source.startswith("#coding: sublist"):
        _, source = source.split("#coding: sublist")

    for token in tokenize(BytesIO(source.encode("utf-8")).readline):
        _, tok_val, _, _, _ = token

        if "[" == tok_val:
            marked_list.append("[")
            is_marked = True
        if is_marked:
            if ":" == tok_val:
                marked_list.append(tok_val)
            token_list.append(token)
        if "]" == tok_val:
            marked_list.append("]")
            is_marked = False

        if pairs_are_equal(marked_list) and marked_list[-1] == "]":
            if "".join(TARGET_PATTERN) in "".join(marked_list):
                string = untokenize(token_list)

                # if the line contains more than one target pattern
                left, right = string.count("["), string.count("]")
                if left > 2:
                    count = right if left > right else left
                    for first, last in (
                        index(string, "[", -count),
                        index(string, "]", -count),
                    ):
                        pattern = string[first : last + 1]
                        if check_pattern(pattern):
                            patterns.append(pattern)
                else:
                    first, last = (
                        index(string, "[")[-1],
                        index(string, "]")[-1],
                    )
                    patterns.append(string[first : last + 1])

            marked_list.clear()
            token_list.clear()

    for pattern in set(patterns):
        source = source.replace(pattern, f"['__unpack{pattern}']")

    if unmodified_source == source:
        return unmodified_source
    else:
        tree = ast.parse(source)
        set_tree_parents(tree)
        output = ast.unparse(
            ast.fix_missing_locations(ModifyExpression().visit(tree))
        )

        if new_line:
            return f"\n{output}"
        else:
            return output


class Codec(codecs.Codec):
    def encode(self, input: str, errors: str = "strict") -> Tuple[bytes, int]:
        if errors != "strict":
            raise UnicodeError(f"{errors} is an unsupported error handler.")

        if not input:
            return b"", 0

        output = modify_notation(input).encode()
        return output, len(output)

    def decode(
        self,
        input: Union[bytes, memoryview],
        errors: str = "strict",
        new_line: bool = False,
    ) -> Tuple[str, int]:
        if errors != "strict":
            raise UnicodeError(f"{errors} is an unsupported error handler.")

        if not input:
            return "", 0

        if isinstance(input, memoryview):
            input = input.tobytes()

        output = modify_notation(input.decode(), new_line)
        return output, len(output)


class IncrementalEncoder(codecs.IncrementalEncoder):
    def encode(self, input: str, final: bool = False) -> bytes:
        output, length_of_output = Codec().encode(input)
        return output


class IncrementalDecoder(codecs.IncrementalDecoder):
    def decode(self, input: bytes, final: bool = False) -> str:
        output, length_of_output = Codec().decode(input, new_line=True)
        return output


class StreamWriter(Codec, codecs.StreamWriter):
    pass


class StreamReader(Codec, codecs.StreamReader):
    pass


def search_func(encoding: str) -> Union[None, codecs.CodecInfo]:
    if encoding == "sublist":
        return codecs.CodecInfo(
            name="sublist",
            encode=Codec().encode,
            decode=Codec().decode,
            incrementalencoder=IncrementalEncoder,
            incrementaldecoder=IncrementalDecoder,
            streamwriter=StreamWriter,
            streamreader=StreamReader,
        )
    else:
        return None


codecs.register(search_func)
