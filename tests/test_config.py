from melaps_cli import config


def test_save_and_load_roundtrip(tmp_path):
    path = tmp_path / "config.toml"
    config.save("sk_test_abc", path=path)
    assert config.load(path)["api_key"] == "sk_test_abc"
    assert oct(path.stat().st_mode)[-3:] == "600"
