from de_projekt import config


def test_data_dirs_exist():
    assert config.RAW_DIR.is_dir()
    assert config.PROCESSED_DIR.is_dir()
