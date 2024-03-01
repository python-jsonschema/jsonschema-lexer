"""
Contains the main functionality of the JSONSchemaLexer.
"""

import jsonschema

from typing import Any, ClassVar

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

    def get_dialect_keywords(self, dialect_url: str | None) -> list[str]:
        match dialect_url:
            case '"https://json-schema.org/draft/2020-12/schema"':
                return list(jsonschema.Draft202012Validator.VALIDATORS.keys()) + [
                    "$schema", "$id"
                ]
            case '"https://json-schema.org/draft/2019-09/schema"':
                return list(jsonschema.Draft201909Validator.VALIDATORS.keys()) + [
                    "$schema", "$id"
                ]
            case '"http://json-schema.org/draft-07/schema#"':
                return list(jsonschema.Draft7Validator.VALIDATORS.keys()) + ["$schema", "$id"]
            case '"http://json-schema.org/draft-06/schema#"':
                return list(jsonschema.Draft6Validator.VALIDATORS.keys()) + ["$schema", "$id"]
            case '"http://json-schema.org/draft-04/schema#"':
                return list(jsonschema.Draft4Validator.VALIDATORS.keys()) + ["$schema", "id"]
            case '"http://json-schema.org/draft-03/schema#"':
                return list(jsonschema.Draft3Validator.VALIDATORS.keys()) + ["$schema", "id"]
            case _:
                return []

    def get_dialect_identifier(self, dialect: str | None):
        match dialect:
            case '"https://json-schema.org/draft/2020-12/schema"':
                return '"$id"'
            case '"https://json-schema.org/draft/2019-09/schema"':
                return '"$id"'
            case '"http://json-schema.org/draft-07/schema#"':
                return '"$id"'
            case '"http://json-schema.org/draft-06/schema#"':
                return '"$id"'
            case '"http://json-schema.org/draft-04/schema#"':
                return '"id"'
            case '"https://json-schema.org/draft-03/schema"':
                return '"id"'
            case _:
                return None

    def _find_rightmost_token_index(
        self, syntax_stack: list[tuple[int, str]], token: str | None
    ):
        for i in range(len(syntax_stack) - 1, -1, -1):
            if syntax_stack[i][1] == token:
                return i
        return None

    def _find_key_value_from_json(self, tokens: list[tuple[int, Any, str]], index: int):
        for i in range(index, len(tokens), 1):
            if tokens[i][1] is Token.String.Double:
                return tokens[i][2]
        return None

    def _get_nearest_valid_dialect(
        self,
        tokens: list[tuple[int, Any, str]],
        syntax_stack: list[tuple[int, str]],
        index: int | None = None,
    ) -> str | None:
        if not index:
            index = len(syntax_stack) - 1

        nearest_schema_index = self._find_rightmost_token_index(
            syntax_stack[: index + 1], '"$schema"'
        )
        if nearest_schema_index:
            dialect = self._find_key_value_from_json(tokens, nearest_schema_index)
            identifier = self.get_dialect_identifier(dialect)
            is_dialect_valid = (
                True
                if identifier or syntax_stack[nearest_schema_index][0] == 0
                else False
            )
            nearest_identifier_index = self._find_rightmost_token_index(
                syntax_stack[: index + 1], identifier
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
                    tokens, syntax_stack, nearest_identifier_index - 1
                )
            elif is_dialect_valid and syntax_stack[-1][1] not in ('"$id"', '"id"'):
                return self._get_nearest_valid_dialect(
                    tokens, syntax_stack, nearest_schema_index - 1
                )

        return None

    def _parse_token_tuple(
        self, token_tuple: tuple[int, Any, str], keywords: list[str]
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
                    self.get_dialect_keywords(dialect),
                )

    def get_tokens_unprocessed(self, text: str): # type: ignore[reportUnknownParameterType]
        """
        Add token classes to it according to JSON Schema.
        """
        json_tokens: list[tuple[int, Any, str]] = list(super().get_tokens_unprocessed(text)) # type: ignore[reportUnknownParameterType]
        yield from self.map_tokens_by_schema(json_tokens)
        