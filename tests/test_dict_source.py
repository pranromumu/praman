from framework.config.dict_source import DictSource


def test_get_config_returns_original_values():
    config = {
        "browser": "firefox",
        "timeout": 30000,
    }

    source = DictSource(config)

    assert source.get_config() == config


def test_get_config_returns_a_separate_top_level_dictionary():
    config = {
        "browser": "firefox",
        "timeout": 30000,
    }

    source = DictSource(config)
    result = source.get_config()

    assert result is not config

    result["browser"] = "webkit"
    result["headless"] = True

    assert config == {
        "browser": "firefox",
        "timeout": 30000,
    }