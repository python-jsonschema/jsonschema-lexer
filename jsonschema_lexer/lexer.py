"""
Contains the main functionality of the JSONSchemaLexer.
"""

from typing import ClassVar

from pygments.lexers.data import (  # type: ignore[reportMissingTypeStubs]
    JsonLexer,
)
from pygments.token import Token


class JSONSchemaLexer(JsonLexer):
    """
    For JSONSchema.
    """

    name = "JSON Schema Lexer"

    data_types: ClassVar[list[str]] = [
        "object",
        "integer",
        "string",
        "number",
        "array",
        "boolean",
        "null",
    ]
    core_keywords: ClassVar[list[str]] = [
        "$schema",
        "$id",
        "$ref",
        "$defs",
        "$comment",
        "$dynamicAnchor",
        "$dynamicRef",
        "$anchor",
        "$vocabulary",
    ]
    applicator_keywords: ClassVar[list[str]] = [
        "oneOf",
        "allOf",
        "anyOf",
        "if",
        "then",
        "else",
        "not",
        "properties",
        "patternProperties",
        "additionalProperties",
        "dependentSchemas",
        "propertyNames",
        "prefixItems",
        "contains",
        "items",
    ]
    meta_data_keywords: ClassVar[list[str]] = [
        "title",
        "description",
        "default",
        "deprecated",
        "examples",
        "readOnly",
        "writeOnly",
    ]
    validation_keywords: ClassVar[list[str]] = [
        "type",
        "enum",
        "const",
        "minLength",
        "maxLength",
        "pattern",
        "maximum",
        "exclusiveMinimum",
        "multipleOf",
        "exclusiveMaximum",
        "minimum",
        "dependentRequired",
        "minProperties",
        "maxProperties",
        "required",
        "minItems",
        "maxItems",
        "minContains",
        "maxContains",
        "uniqueItems",
    ]
    other_keywords: ClassVar[list[str]] = [
        "format",
        "unevaluatedItems",
        "unevaluatedProperties",
        "contentEncoding",
        "contentMediaType",
        "contentSchema",
        "format_assertion",
    ]

    parsed_keywords: ClassVar[list[str]] = [
        '"%s"' % keyword
        for keyword in (
            core_keywords
            + applicator_keywords
            + meta_data_keywords
            + validation_keywords
            + other_keywords
        )
    ]

    parsed_data_types: ClassVar[list[str]] = [
        '"%s"' % data_type for data_type in data_types
    ]

    def get_tokens_unprocessed(self, text: str):  # type: ignore[reportUnknownParameterType]
        """
        Add token classes to it according to JSON Schema.
        """
        for start, token, value in super().get_tokens_unprocessed(text):  # type: ignore[reportUnknownVariableType]
            if token is Token.Name.Tag and value in self.parsed_keywords:
                yield start, Token.Keyword, value
            elif (
                token is Token.String.Double
                and value in self.parsed_data_types
            ):
                yield start, Token.Name.Decorator, value
            else:
                yield start, token, value
