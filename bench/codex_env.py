"""Per-invocation Codex home: authentication only, no host customizations."""
from contextlib import contextmanager
import os
from pathlib import Path
import tempfile


# Match codex_harness's transport allowlist; never log environment values.
ENV_KEYS = ("PATH", "OPENAI_API_KEY", "CODEX_API_KEY", "HTTPS_PROXY", "HTTP_PROXY",
            "ALL_PROXY", "NO_PROXY", "https_proxy", "http_proxy", "all_proxy", "no_proxy",
            "SSL_CERT_FILE", "SSL_CERT_DIR", "REQUESTS_CA_BUNDLE", "CURL_CA_BUNDLE",
            "NODE_EXTRA_CA_CERTS")


@contextmanager
def isolated_codex_env():
    # Resolve the host location before replacing HOME. Do not open/copy auth.
    auth = Path.home() / ".codex" / "auth.json"
    with tempfile.TemporaryDirectory(prefix="mrb-codex-home-") as home:
        codex = Path(home) / ".codex"
        codex.mkdir()
        (codex / "auth.json").symlink_to(auth)
        env = {k: os.environ[k] for k in ENV_KEYS if k in os.environ}
        env.update(HOME=home, CODEX_HOME=str(codex), SHELL="/bin/bash", LANG="C.UTF-8", TMPDIR="/tmp")
        yield env
