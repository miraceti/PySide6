import configparser
import os
import sys
from pathlib import Path

def get_base_dir():
    """Retourne le dossier racine de l'application"""
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).parent
    else:
        return Path(__file__).resolve().parents[1]

def load_config():
    config = configparser.ConfigParser()
    base_dir = get_base_dir()

    config_path = base_dir / "config" / "config.ini"

    # Cas exe
    if not config_path.exists():
        config_path = base_dir / "config.ini"

    if not config_path.exists():
        print("⚠️ config.ini introuvable :", config_path)
        return {}

    config.read(config_path, encoding="utf-8")

    # Conversion types
    cfg = {}

    # PARAMS
    cfg['lots_path'] = config.get("PARAMS", "lots_path", fallback="")
    cfg['dsn'] = config.get("PARAMS", "dsn", fallback="dsn_null")
    # cfg['dsn'] = config.getint("PARAMS", "dsn", fallback="dsn_null")
    #cfg['enable_logging'] = config.getboolean("PARAMS", "enable_logging", fallback=False)

    return cfg
