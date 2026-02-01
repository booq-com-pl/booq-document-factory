import sys
from pathlib import Path


def load_config_toml(path: str | None = None) -> dict:
    try:
        import tomllib  # py311+
    except Exception as exc:  # pragma: no cover
        raise RuntimeError("TOML requires Python 3.11+ (tomllib)") from exc

    config_path = Path(path) if path else Path("config.toml")
    if not config_path.exists():
        return {}

    raw = config_path.read_text(encoding="utf-8")
    return tomllib.loads(raw)


def main() -> int:
    config = load_config_toml()
    splibrary = (config.get("splibrary") or {})
    url = splibrary.get("url")
    if url:
        print(f"SharePoint library URL: {url}")
    else:
        print("SharePoint library URL not configured.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
