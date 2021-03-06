import os
import textwrap

import jinja2
import platform
import pytest
import sys

from conda_devenv.devenv import render_jinja


def test_jinja_root():
    assert render_jinja(
        "{{root}}",
        filename="path/to/file",
        is_included=False,
    ) == os.path.abspath("path/to")


def test_jinja_os(monkeypatch):
    template = textwrap.dedent("""\
        {% if os.environ['ENV_VARIABLE'] == '1' -%}
        variable is set
        {%- else -%}
        variable is not set
        {%- endif %}
    """).strip()

    assert render_jinja(template, filename="", is_included=False) == "variable is not set"

    monkeypatch.setenv('ENV_VARIABLE', '1')
    assert render_jinja(template, filename="", is_included=False) == "variable is set"

    monkeypatch.setenv('ENV_VARIABLE', '2')
    assert render_jinja(template, filename="", is_included=False) == "variable is not set"


def test_jinja_sys(monkeypatch):
    template = textwrap.dedent("""\
        {% if sys.platform.startswith('linux') -%}
        linux!
        {%- elif sys.platform.startswith('win') -%}
        windows!
        {%- else -%}
        others!
        {%- endif %}
    """).strip()

    monkeypatch.setattr(sys, 'platform', 'linux')
    assert render_jinja(template, filename="", is_included=False) == "linux!"

    monkeypatch.setattr(sys, 'platform', 'windows')
    assert render_jinja(template, filename="", is_included=False) == "windows!"

    monkeypatch.setattr(sys, 'platform', 'darwin')
    assert render_jinja(template, filename="", is_included=False) == "others!"


def test_jinja_platform(monkeypatch):
    template = "{{ platform.python_revision() }}"
    assert render_jinja(template, filename="", is_included=False) == platform.python_revision()


def test_jinja_invalid_template():
    with pytest.raises(jinja2.exceptions.TemplateSyntaxError):
        render_jinja(
            textwrap.dedent("""\
                {%- if os.environ['ENV_VARIABLE'] == '1' %}
                {% %}
            """),
            filename="",
            is_included=False,
        )
