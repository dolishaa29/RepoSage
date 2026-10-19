import json
import pytest
from test_bugs import read_config


def test_read_config_valid_json(tmp_path):
    config_file = tmp_path / "config.json"
    data = {"host": "localhost", "port": 8080, "debug": True}
    config_file.write_text(json.dumps(data))

    assert read_config(str(config_file)) == data


def test_read_config_does_not_eval_code(tmp_path):
    config_file = tmp_path / "config.txt"
    # A payload that would execute arbitrary code if eval() were used
    config_file.write_text("__import__('os').system('echo pwned')")

    with pytest.raises(json.JSONDecodeError):
        read_config(str(config_file))
