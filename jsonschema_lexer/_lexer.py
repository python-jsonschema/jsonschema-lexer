"""
Contains the main functionality of the JSONSchemaLexer.
"""

from importlib.resources import files
from pathlib import Path
from typing import Any, ClassVar
import json

from pygments.lexers.data import (  # type: ignore[reportMissingTypeStubs]
    JsonLexer,
)
from pygments.token import Token


class JSONSchemaLexer(JsonLexer):
    """
    A Pygments lexer for dialects of the JSON Schema specification.
    """

    name = "JSON Schema"
    url = "https://json-schema.org"
    aliases: ClassVar[list[str]] = ["jsonschema", "json-schema"]
    mimetypes: ClassVar[list[str]] = [
        "application/schema+json",
        "application/schema-instance+json",
    ]

    data_types: ClassVar[list[str]] = [
        '"object"',
        '"integer"',
        '"string"',
        '"number"',
        '"array"',
        '"boolean"',
        '"null"',
    ]
    keywords: ClassVar[dict[str | None, list[str]]] = {}
    identifier: ClassVar[dict[str | None, str]] = {}
    default_dialect = None

    def __init__(self, default_dialect: str | None = None):
        super().__init__()  # type: ignore[reportUnknownMemberType]
        self._populate_keywords_and_identifiers()
        if default_dialect and default_dialect[0] != '"':
            default_dialect = '"' + default_dialect

        if default_dialect and default_dialect[-1] != '"':
            default_dialect = default_dialect + '"'

        self.default_dialect = default_dialect

    def _populate_keywords_and_identifiers(self):
        dialect_files = files("jsonschema_lexer") / "data" / "keywords"
        if not dialect_files.is_dir():
            dialect_files = Path(__file__).parent / "data" / "keywords"
        for dialect_file in dialect_files.iterdir():
            with dialect_file.open() as file:
                json_content = json.load(file)
                dialect_name = f'"{json_content["dialect"]}"'
                self.keywords[dialect_name] = json_content["keywords"]
                self.identifier[dialect_name] = (
                    f'"{json_content["identifier"]}"'
                )

    def _find_rightmost_token_index(
        self,
        syntax_stack: list[tuple[int, str]],
        token: str | None,
    ):
        return next(
            (
                i
                for i, (_, t) in reversed(list(enumerate(syntax_stack)))
                if t == token
            ),
            None,
        )

    def _find_key_value_from_json(
        self,
        tokens: list[tuple[int, Any, str]],
        index: int,
    ):
        return next(
            (t[2] for t in tokens[index:] if t[1] is Token.String.Double),
            None,
        )

    def _get_nearest_valid_dialect(
        self,
        tokens: list[tuple[int, Any, str]],
        syntax_stack: list[tuple[int, str]],
        index: int | None = None,
    ) -> str | None:
        if not index:
            index = len(syntax_stack) - 1

        nearest_schema_index = self._find_rightmost_token_index(
            syntax_stack[: index + 1],
            '"$schema"',
        )
        if nearest_schema_index:
            dialect = self._find_key_value_from_json(
                tokens,
                nearest_schema_index,
            )
            identifier = self.identifier.get(dialect, None)
            is_dialect_valid = bool(
                identifier or syntax_stack[nearest_schema_index][0] == 0,
            )
            nearest_identifier_index = self._find_rightmost_token_index(
                syntax_stack[: index + 1],
                identifier,
            )
            if (
                nearest_identifier_index
                and identifier
                and syntax_stack[nearest_identifier_index][0]
                == syntax_stack[nearest_schema_index][0]
            ) or syntax_stack[nearest_schema_index][0] == 0:
                return dialect
            elif is_dialect_valid and nearest_identifier_index:
                return self._get_nearest_valid_dialect(
                    tokens,
                    syntax_stack,
                    nearest_identifier_index - 1,
                )
            elif is_dialect_valid and syntax_stack[-1][1] not in (
                '"$id"',
                '"id"',
            ):
                return self._get_nearest_valid_dialect(
                    tokens,
                    syntax_stack,
                    nearest_schema_index - 1,
                )

        if self.default_dialect:
            return self.default_dialect

        return None

    def _parse_token_tuple(
        self,
        token_tuple: tuple[int, Any, str],
        keywords: list[str],
    ):
        start, token, value = token_tuple
        keywords = ['"%s"' % keyword for keyword in (keywords)]
        if token is Token.Name.Tag and value in keywords:
            return start, Token.Keyword, value
        elif token is Token.String.Double and value in self.data_types:
            return start, Token.Name.Decorator, value
        else:
            return start, token, value

    def map_tokens_by_schema(self, tokens: list[tuple[int, Any, str]]):
        syntax_stack: list[tuple[int, str]] = []
        cur_depth = -1
        for start, token, value in tokens:
            if value == "{":
                cur_depth += 1

            syntax_stack.append((cur_depth, value))

            if value == "}":
                while syntax_stack.pop()[1] != "{":
                    continue
                yield self._parse_token_tuple((start, token, value), [])
            else:
                dialect = self._get_nearest_valid_dialect(tokens, syntax_stack)
                yield self._parse_token_tuple(
                    (start, token, value),
                    self.keywords.get(dialect, []),
                )

    def get_tokens_unprocessed(self, text: str):  # type: ignore[reportUnknownParameterType]
        """
        Add token classes to it according to JSON Schema.
        """
        json_tokens: list[tuple[int, Any, str]] = list(
            super().get_tokens_unprocessed(text),  # type: ignore[reportUnknownParameterType]
        )
        yield from self.map_tokens_by_schema(json_tokens)
