import pytest
from cfg.errors import ConfigError
from cfg.loader import get, load

TEXT = """\
root = /srv
[app]
dir = ${.root}/app
log = ${dir}/log/${name}.log
name = web
[a.b]
c = deep
[ref]
x = ${a.b.c}-${app.name}
price = $$5 and $${x}
"""


def test_resolution():
    c = load(TEXT)
    assert get(c, "app.dir") == "/srv/app"
    assert get(c, "app.log") == "/srv/app/log/web.log"
    assert get(c, "ref.x") == "deep-web"
    assert get(c, "ref.price") == "$5 and ${x}"
    assert get(c, "root") == "/srv"


def test_unknown_reference_message_and_line():
    with pytest.raises(ConfigError) as e:
        load("[db]\nhost = h\n\nurl = pg://${db.hostt}:1\n")
    assert "unknown reference: db.hostt" in str(e.value) and e.value.line == 4
    with pytest.raises(ConfigError) as e:
        load("[s]\nk = ${nosuch.key}\n")
    assert "nosuch.key" in str(e.value)


def test_cycle_message_exact():
    with pytest.raises(ConfigError) as e:
        load("[a]\nstart = ${x}\nx = ${y}\ny = ${b.z}\n[b]\nz = ok ${a.x}\n")
    msg = str(e.value)
    assert msg.endswith("reference cycle: a.x -> a.y -> b.z -> a.x"), msg
    assert e.value.line == 2


def test_self_cycle_and_unnamed_section():
    with pytest.raises(ConfigError) as e:
        load("k = ${k}\n")
    assert str(e.value).endswith("reference cycle: .k -> .k")


@pytest.mark.parametrize("bad", ["x = a$b\n", "x = ${y\ny = 1\n", "x = $\n"])
def test_bad_dollar(bad):
    with pytest.raises(ConfigError):
        load(bad)


def test_parser_unchanged():
    with pytest.raises(ConfigError) as e:
        load("[a]\nx = 1\nx = 2\n")
    assert e.value.line == 3
    assert load("[s]\nv = plain text = fine\n")["s"]["v"] == "plain text = fine"
