from pygments.lexer import include, RegexLexer
from pygments.token import Token


def _get_regex_from_options(options: list[str]) -> str:
    """
    Constructs a regular expression pattern allowing any string from the options list.

    Args:
        options (list[str]): List of options to be included in the regex pattern.

    Returns:
        str: Regular expression pattern constructed from the options.
    """
    options = ['"' + option + '"' for option in options]
    regex_str = "(" + "|".join(options) + ")"
    return regex_str


class JSONSchemaLexer(RegexLexer):
    """
    Lexer for JSON Schema syntax highlighting.
    """

    name = "JSON Schema Lexer"

    data_types = ["object", "integer", "string", "number", "array", "boolean", "null"]
    core_keywords = [
        r"\$schema",
        r"\$id",
        r"\$ref",
        r"\$defs",
        r"\$comment",
        r"\$dynamicAnchor",
        r"\$dynamicRef",
        r"\$anchor",
        r"\$vocabulary",
    ]
    applicator_keywords = [
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
    meta_data_keywords = [
        "title",
        "description",
        "default",
        "deprecated",
        "examples",
        "readOnly",
        "writeOnly",
    ]
    validation_keywords = [
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
    other_keywords = [
        "format",
        "unevaluatedItems",
        "unevaluatedProperties",
        "contentEncoding",
        "contentMediaType",
        "contentSchema",
        "format_assertion",
    ]

    tokens = {
        "whitespace": [
            (r"\s+", Token.Whitespace),
        ],
        "data_types": [
            # Used Literal type here to differentiate the highlighted color of data types from other keywords
            (_get_regex_from_options(data_types), Token.Literal),
        ],
        "core_keywords": [
            (
                _get_regex_from_options(core_keywords),
                Token.Keyword.Reserved,
                "objectattribute",
            ),
        ],
        "applicator_keywords": [
            (
                _get_regex_from_options(applicator_keywords),
                Token.Keyword.Reserved,
                "objectattribute",
            ),
        ],
        "validation_keywords": [
            (
                _get_regex_from_options(validation_keywords),
                Token.Keyword.Reserved,
                "objectattribute",
            ),
        ],
        "meta_data_keywords": [
            (
                _get_regex_from_options(meta_data_keywords),
                Token.Keyword.Reserved,
                "objectattribute",
            ),
        ],
        "other_keywords": [
            (
                _get_regex_from_options(other_keywords),
                Token.Keyword.Reserved,
                "objectattribute",
            ),
        ],
        "keywords": [
            include("core_keywords"),
            include("applicator_keywords"),
            include("validation_keywords"),
            include("meta_data_keywords"),
            include("other_keywords"),
        ],
        # represents a simple terminal value
        "simplevalue": [
            include("data_types"),
            (r"(true|false)", Token.Number),
            (r"-?(?:0|[1-9]\d*)(?:\.\d+)?(?:[eE][+-]?\d+)?", Token.Number.Integer),
            ('"(\\|"|[^"])*"', Token.String.Double),
        ],
        # the right hand side of an object, after the attribute name
        "objectattribute": [
            include("value"),
            (r":", Token.Punctuation),
            # comma terminates the attribute but expects more
            (r",", Token.Punctuation, "#pop"),
            # a closing bracket terminates the entire object, so pop twice
            (r"}", Token.Punctuation, ("#pop", "#pop")),
        ],
        # a json object - { attr, attr, ... }
        "objectvalue": [
            include("whitespace"),
            include("keywords"),
            (r'"(\\\\|\\"|[^"])*"', Token.Name.Tag, "objectattribute"),
            (r"}", Token.Punctuation, "#pop"),
        ],
        # json array - [ value, value, ... }
        "arrayvalue": [
            include("whitespace"),
            include("value"),
            (r",", Token.Punctuation),
            (r"]", Token.Punctuation, "#pop"),
        ],
        # a json value - either a simple value or a complex value (object or array)
        "value": [
            include("whitespace"),
            include("simplevalue"),
            (r"{", Token.Punctuation, "objectvalue"),
            (r"\[", Token.Punctuation, "arrayvalue"),
        ],
        # the root of a json document whould be a value
        "root": [
            include("value"),
        ],
    }
