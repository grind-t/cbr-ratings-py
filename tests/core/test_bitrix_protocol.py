from cbr_ratings._core.search.bitrix_protocol import parse_csrf_token, serialize_fields


def test_serializes_simple_fields():
    assert (
        serialize_fields({"foo": "bar", "baz": 42}) == "fields[foo]=bar&fields[baz]=42"
    )


def test_serializes_array_field():
    assert (
        serialize_fields({"arr": [1, 2, 3]})
        == "fields[arr][0]=1&fields[arr][1]=2&fields[arr][2]=3"
    )


def test_skips_none_values():
    assert serialize_fields({"foo": None, "bar": "baz"}) == "fields[bar]=baz"


def test_serializes_empty_mapping():
    assert serialize_fields({}) == ""


def test_serializes_special_characters():
    assert (
        serialize_fields({"a": "c&d", "b": "g h"}) == "fields[a]=c%26d&fields[b]=g%20h"
    )


def test_encodes_cyrillic():
    assert serialize_fields({"a": "АКРА"}) == "fields[a]=%D0%90%D0%9A%D0%A0%D0%90"


def test_serializes_with_custom_prefix():
    assert serialize_fields({"foo": "bar"}, "custom") == "custom[foo]=bar"


def test_parses_csrf_token():
    html = '<script>{"bitrix_sessid": "abc123"}</script>'

    assert parse_csrf_token(html) == "abc123"


def test_csrf_token_is_none_when_absent():
    assert parse_csrf_token("<html></html>") is None
