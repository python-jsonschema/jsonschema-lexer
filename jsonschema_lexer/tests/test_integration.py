"""
    JSON Schema Lexer tests
"""

import pytest

from pygments.token import Token
from jsonschema_lexer.lexer import JSONSchemaLexer

# Test helpers.

@pytest.fixture
def lexer():
    yield JSONSchemaLexer()


@pytest.fixture
def data_types():
    yield JSONSchemaLexer().parsed_data_types


@pytest.fixture
def keywords():
    yield JSONSchemaLexer().parsed_keywords


def assert_single_token(lexer, s, token):
    """Show that a given string generates only one token."""
    tokens = list(lexer.get_tokens_unprocessed(s))
    assert len(tokens) == 1 and s==tokens[0][2] and token==tokens[0][1]


def assert_tokens(lexer, string, expected_tokens):
    """Show that a given string generates the expected tokens."""
    tokens = list(lexer.get_tokens_unprocessed(string))
    parsed_tokens = [t[1] for t in tokens]
    assert parsed_tokens == expected_tokens


# Tests

def test_it_imports():
    import jsonschema_lexer  # noqa: F401


def test_data_type_tokens(lexer, data_types):
    for data_type in data_types:
        assert_single_token(lexer, data_type, Token.Name.Decorator)


def test_keyword_tokens(lexer, keywords):
    for keyword in keywords:
        sample_json_schema = f"""
        {{
            {keyword}:"test"
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
