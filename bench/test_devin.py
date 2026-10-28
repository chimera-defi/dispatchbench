"""Devin lane stop detection; mocked subprocess, no network."""
import subprocess
from unittest.mock import patch

import pytest

from bench import run as R

UPGRADE = "Error: Upgrade to Pro to access this model (https://devin.ai/pricing)"


def run(code, out, err):
    with patch.object(R.subprocess, "run") as call:
        call.return_value = subprocess.CompletedProcess([], code, out, err)
        return R.call_devin("swe-1-6-slow", "default", "p", "/tmp"), call


@pytest.mark.parametrize("code,out,err", [(1, "", UPGRADE), (0, "Usage limit reached", ""), (1, "", "boom")])
def test_stop(code, out, err):
    with pytest.raises(R.DevinStop) as e:
        run(code, out, err)
    assert e.value.res["is_error"] and e.value.res["outcome"] == "harness_error"
    assert (err or out) in e.value.res["error"]


def test_normal_and_command():
    (row, raw), call = run(0, "```python\ndef f(): pass\n```", "")
    assert not row["is_error"] and row["cost_usd"] is None and row["in_tok"] is None
    assert call.call_args.args[0] == [R.DEVIN, "--model", "swe-1-6-slow", "--permission-mode", "auto", "-p", "p"]
