"""
JSON Schema Lexer tests
"""

from pygments.token import Token
import pytest

from jsonschema_lexer import JSONSchemaLexer

dialects = [
    "http://json-schema.org/draft-03/schema#",
    "http://json-schema.org/draft-04/schema#",
    "http://json-schema.org/draft-06/schema#",
    "http://json-schema.org/draft-07/schema#",
    "https://json-schema.org/draft/2019-09/schema",
    "https://json-schema.org/draft/2020-12/schema",
]


@pytest.fixture()
def lexer():
    return JSONSchemaLexer()


def assert_single_token(lexer, s, token):
    """
    Assert a given string generates only one token.
    """
    tokens = list(lexer.get_tokens_unprocessed(s))
    assert len(tokens) == 1
    assert s == tokens[0][2]
    assert token == tokens[0][1]


def assert_tokens(lexer, string, expected_tokens):
    """
    Assert a given string generates the expected tokens.
    """
    tokens = list(lexer.get_tokens_unprocessed(string))
    parsed_tokens = [t[1] for t in tokens]
    assert parsed_tokens == expected_tokens


def test_data_type_tokens(lexer):
    for data_type in lexer.data_types:
        assert_single_token(lexer, data_type, Token.Name.Decorator)


def test_default_schema_support():
    for dialect in dialects:
        dialect = f'"{dialect}"'
        lexer = JSONSchemaLexer(dialect)
        assert lexer.default_dialect == dialect


def test_keyword_tokens():
    for dialect in dialects:
        lexer = JSONSchemaLexer(dialect)
        dialect = f'"{dialect}"'
        for keyword in lexer.keywords[dialect]:
            if keyword == "$schema":
                continue
            sample_json_schema = f"""
            {{
                "{keyword}":"test"
            }}
            """.strip()
            assert_tokens(
                lexer,
                sample_json_schema,
                [
                    Token.Punctuation,
                    Token.Text.Whitespace,
                    Token.Keyword,
                    Token.Punctuation,
                    Token.Literal.String.Double,
                    Token.Text.Whitespace,
                    Token.Punctuation,
                ],
            )


def test_no_schema_with_default():
    dialect = '"https://json-schema.org/draft/2020-12/schema"'
    lexer = JSONSchemaLexer(dialect)
    test_json_schema = """
    {
    "prefixItems": [true], // <- a keyword
    }
    """.strip()
    assert_tokens(
        lexer,
        test_json_schema,
        [
            Token.Punctuation,
            Token.Text.Whitespace,
            Token.Keyword,
            Token.Punctuation,
            Token.Text.Whitespace,
            Token.Punctuation,
            Token.Keyword.Constant,
            Token.Punctuation,
            Token.Text.Whitespace,
            Token.Comment.Single,
            Token.Text.Whitespace,
            Token.Punctuation,
        ],
    )


def test_no_schema_without_default(lexer):
    test_json_schema = """
    {
    "prefixItems": [true], // <- not a keyword
    }
    """.strip()
    assert_tokens(
        lexer,
        test_json_schema,
        [
            Token.Punctuation,
            Token.Text.Whitespace,
            Token.Name.Tag,
            Token.Punctuation,
            Token.Text.Whitespace,
            Token.Punctuation,
            Token.Keyword.Constant,
            Token.Punctuation,
            Token.Text.Whitespace,
            Token.Comment.Single,
            Token.Text.Whitespace,
            Token.Punctuation,
        ],
    )


def test_draft202012_schema(lexer):
    test_json_schema = """
    {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "prefixItems": [true], // <- a keyword
    "additionalItems": false, // <- not a keyword
    }
    """.strip()
    assert_tokens(
        lexer,
        test_json_schema,
        [
            Token.Punctuation,
            Token.Text.Whitespace,
            Token.Keyword,
            Token.Punctuation,
            Token.Text.Whitespace,
            Token.Literal.String.Double,
            Token.Punctuation,
            Token.Text.Whitespace,
            Token.Keyword,
            Token.Punctuation,
            Token.Text.Whitespace,
            Token.Punctuation,
            Token.Keyword.Constant,
            Token.Punctuation,
            Token.Text.Whitespace,
            Token.Comment.Single,
            Token.Text.Whitespace,
            Token.Name.Tag,
            Token.Punctuation,
            Token.Text.Whitespace,
            Token.Keyword.Constant,
            Token.Punctuation,
            Token.Text.Whitespace,
            Token.Comment.Single,
            Token.Text.Whitespace,
            Token.Punctuation,
        ],
    )


def test_draft201909_schema(lexer):
    test_json_schema = """
    {
    "$schema": "https://json-schema.org/draft/2019-09/schema",
    "$recursiveRef": "test", // <- a keyword
    "$dynamicRef": "test", // <- not a keyword
    }
    """.strip()
    assert_tokens(
        lexer,
        test_json_schema,
        [
            Token.Punctuation,
            Token.Text.Whitespace,
            Token.Keyword,
            Token.Punctuation,
            Token.Text.Whitespace,
            Token.Literal.String.Double,
            Token.Punctuation,
            Token.Text.Whitespace,
            Token.Keyword,
            Token.Punctuation,
            Token.Text.Whitespace,
            Token.Literal.String.Double,
            Token.Punctuation,
            Token.Text.Whitespace,
            Token.Comment.Single,
            Token.Text.Whitespace,
            Token.Name.Tag,
            Token.Punctuation,
            Token.Text.Whitespace,
            Token.Literal.String.Double,
            Token.Punctuation,
            Token.Text.Whitespace,
            Token.Comment.Single,
            Token.Text.Whitespace,
            Token.Punctuation,
        ],
    )


def test_draft07_schema(lexer):
    test_json_schema = """
    {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "prefixItems": [true], // <- not a keyword
    "additionalItems": false, // <- a keyword
    }
    """.strip()
    assert_tokens(
        lexer,
        test_json_schema,
        [
            Token.Punctuation,
            Token.Text.Whitespace,
            Token.Keyword,
            Token.Punctuation,
            Token.Text.Whitespace,
            Token.Literal.String.Double,
            Token.Punctuation,
            Token.Text.Whitespace,
            Token.Name.Tag,
            Token.Punctuation,
            Token.Text.Whitespace,
            Token.Punctuation,
            Token.Keyword.Constant,
            Token.Punctuation,
            Token.Text.Whitespace,
            Token.Comment.Single,
            Token.Text.Whitespace,
            Token.Keyword,
            Token.Punctuation,
            Token.Text.Whitespace,
            Token.Keyword.Constant,
            Token.Punctuation,
            Token.Text.Whitespace,
            Token.Comment.Single,
            Token.Text.Whitespace,
            Token.Punctuation,
        ],
    )


def test_draft06_schema(lexer):
    test_json_schema = """
    {
    "$schema": "http://json-schema.org/draft-06/schema#",
    "const": "test", // <- a keyword
    "propertyNames": "test", // <- a keyword
    }
    """.strip()
    assert_tokens(
        lexer,
        test_json_schema,
        [
            Token.Punctuation,
            Token.Text.Whitespace,
            Token.Keyword,
            Token.Punctuation,
            Token.Text.Whitespace,
            Token.Literal.String.Double,
            Token.Punctuation,
            Token.Text.Whitespace,
            Token.Keyword,
            Token.Punctuation,
            Token.Text.Whitespace,
            Token.Literal.String.Double,
            Token.Punctuation,
            Token.Text.Whitespace,
            Token.Comment.Single,
            Token.Text.Whitespace,
            Token.Keyword,
            Token.Punctuation,
            Token.Text.Whitespace,
            Token.Literal.String.Double,
            Token.Punctuation,
            Token.Text.Whitespace,
            Token.Comment.Single,
            Token.Text.Whitespace,
            Token.Punctuation,
        ],
    )


def test_draft04_schema(lexer):
    test_json_schema = """
    {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "multipleOf": "test", // <- a keyword
    "divisibleBy": "test", // <- not a keyword
    }
    """.strip()
    assert_tokens(
        lexer,
        test_json_schema,
        [
            Token.Punctuation,
            Token.Text.Whitespace,
            Token.Keyword,
            Token.Punctuation,
            Token.Text.Whitespace,
            Token.Literal.String.Double,
            Token.Punctuation,
            Token.Text.Whitespace,
            Token.Keyword,
            Token.Punctuation,
            Token.Text.Whitespace,
            Token.Literal.String.Double,
            Token.Punctuation,
            Token.Text.Whitespace,
            Token.Comment.Single,
            Token.Text.Whitespace,
            Token.Name.Tag,
            Token.Punctuation,
            Token.Text.Whitespace,
            Token.Literal.String.Double,
            Token.Punctuation,
            Token.Text.Whitespace,
            Token.Comment.Single,
            Token.Text.Whitespace,
            Token.Punctuation,
        ],
    )


def test_draft03_schema(lexer):
    test_json_schema = """
    {
    "$schema": "http://json-schema.org/draft-03/schema#",
    "patternProperties": "test", // <- a keyword
    "optional": "test", // <- not a keyword
    }
    """.strip()
    assert_tokens(
        lexer,
        test_json_schema,
        [
            Token.Punctuation,
            Token.Text.Whitespace,
            Token.Keyword,
            Token.Punctuation,
            Token.Text.Whitespace,
            Token.Literal.String.Double,
            Token.Punctuation,
            Token.Text.Whitespace,
            Token.Keyword,
            Token.Punctuation,
            Token.Text.Whitespace,
            Token.Literal.String.Double,
            Token.Punctuation,
            Token.Text.Whitespace,
            Token.Comment.Single,
            Token.Text.Whitespace,
            Token.Name.Tag,
            Token.Punctuation,
            Token.Text.Whitespace,
            Token.Literal.String.Double,
            Token.Punctuation,
            Token.Text.Whitespace,
            Token.Comment.Single,
            Token.Text.Whitespace,
            Token.Punctuation,
        ],
    )


def test_nested_json_schema(lexer):
    test_json_schema = """
    {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "Product",
    "description": "A product from Acme's catalog",
    "type": "object",
    "properties": {
        "productId": {
        "description": "The unique identifier for a product",
        "type": "integer"
        }
    }
    }
    """.strip()
    assert_tokens(
        lexer,
        test_json_schema,
        [
            Token.Punctuation,
            Token.Text.Whitespace,
            Token.Keyword,
            Token.Punctuation,
            Token.Text.Whitespace,
            Token.Literal.String.Double,
            Token.Punctuation,
            Token.Text.Whitespace,
            Token.Keyword,
            Token.Punctuation,
            Token.Text.Whitespace,
            Token.Literal.String.Double,
            Token.Punctuation,
            Token.Text.Whitespace,
            Token.Keyword,
            Token.Punctuation,
            Token.Text.Whitespace,
            Token.Literal.String.Double,
            Token.Punctuation,
            Token.Text.Whitespace,
            Token.Keyword,
            Token.Punctuation,
            Token.Text.Whitespace,
            Token.Name.Decorator,
            Token.Punctuation,
            Token.Text.Whitespace,
            Token.Keyword,
            Token.Punctuation,
            Token.Text.Whitespace,
            Token.Punctuation,
            Token.Text.Whitespace,
            Token.Name.Tag,
            Token.Punctuation,
            Token.Text.Whitespace,
            Token.Punctuation,
            Token.Text.Whitespace,
            Token.Keyword,
            Token.Punctuation,
            Token.Text.Whitespace,
            Token.Literal.String.Double,
            Token.Punctuation,
            Token.Text.Whitespace,
            Token.Keyword,
            Token.Punctuation,
            Token.Text.Whitespace,
            Token.Name.Decorator,
            Token.Text.Whitespace,
            Token.Punctuation,
            Token.Text.Whitespace,
            Token.Punctuation,
            Token.Text.Whitespace,
            Token.Punctuation,
        ],
    )
