=======================
``jsonschema-lexer``
=======================

|PyPI| |Pythons| |CI|

.. |PyPI| image:: https://img.shields.io/pypi/v/jsonschema-lexer.svg
  :alt: PyPI version
  :target: https://pypi.org/project/jsonschema-lexer/

.. |Pythons| image:: https://img.shields.io/pypi/pyversions/jsonschema-lexer.svg
  :alt: Supported Python versions
  :target: https://pypi.org/project/jsonschema-lexer/

.. |CI| image:: https://github.com/python-jsonschema/jsonschema-lexer/workflows/CI/badge.svg
  :alt: Build status
  :target: https://github.com/python-jsonschema/jsonschema-lexer/actions?query=workflow%3ACI

Introduction
------------

`jsonschema-lexer` provides a lexer for syntax highlighting JSON Schema documents via `Pygments <https://pygments.org/>`_.

Usage
-----

Once installed, you can use it in your Python code to highlight JSON Schema documents.

Here's a simple example:

.. code-block:: python

  from jsonschema_lexer import JSONSchemaLexer

  from rich.console import Console
  from rich.syntax import Syntax

  console = Console()

  code = """
  {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "https://example.com/product.schema.json",
    "title": "Product",
    "description": "A product from Acme's catalog",
    "type": "object",
    "properties": {
      "productId": {
        "description": "The unique identifier for a product",
        "type": "integer"
      },
      "productName": {
        "description": "Name of the product",
        "type": "string"
      }
    }
  }
  """

  syntax = Syntax(code, lexer=JSONSchemaLexer(), background_color="default", word_wrap=True)
  console.print(syntax)
