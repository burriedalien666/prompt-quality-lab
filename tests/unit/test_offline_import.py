import os
import subprocess
import sys
from types import SimpleNamespace

import prompt_ops.core as core


def test_offline_cli_import_does_not_require_dspy_or_litellm():
    source = (
        "import builtins\n"
        "real_import = builtins.__import__\n"
        "def blocked(name, *args, **kwargs):\n"
        "    if name == 'dspy' or name.startswith('dspy.'):\n"
        "        raise ModuleNotFoundError('blocked dspy')\n"
        "    if name == 'litellm' or name.startswith('litellm.'):\n"
        "        raise ModuleNotFoundError('blocked litellm')\n"
        "    return real_import(name, *args, **kwargs)\n"
        "builtins.__import__ = blocked\n"
        "from prompt_ops.core.quality import normalize_text\n"
        "from prompt_ops.interfaces.cli import cli\n"
        "assert normalize_text(' OK ') == 'ok'\n"
        "assert cli.name == 'cli'\n"
    )
    env = dict(os.environ)
    env["PYTHONPATH"] = os.path.abspath("src")

    result = subprocess.run([sys.executable, "-c", source], env=env, text=True)

    assert result.returncode == 0, result.stderr


def test_core_keeps_lazy_submodule_attributes_resolvable(monkeypatch):
    sentinel = SimpleNamespace(name="prompt_strategies")
    real_import = core.importlib.import_module
    core.__dict__.pop("prompt_strategies", None)

    def fake_import(name):
        if name == "prompt_ops.core.prompt_strategies":
            return sentinel
        return real_import(name)

    monkeypatch.setattr(core.importlib, "import_module", fake_import)

    assert core.prompt_strategies is sentinel
