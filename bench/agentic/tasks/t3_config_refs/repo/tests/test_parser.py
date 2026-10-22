import pytest
from cfg.errors import ConfigError
from cfg.loader import get, load


def test_sections_and_keys():
    c = load("name = app\n# comment\n[db]\nhost = localhost\nport= 5432\n")
    assert get(c, "name") == "app" and get(c, "db.host") == "localhost" and get(c, "db.port") == "5432"


def test_duplicate_key_reports_line():
    with pytest.raises(ConfigError) as e:
        load("[a]\nx = 1\n\nx = 2\n")
    assert e.value.line == 4
