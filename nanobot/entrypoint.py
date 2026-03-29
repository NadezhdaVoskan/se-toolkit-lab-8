import json
import os
import tempfile
from pathlib import Path
from typing import Any


APP_DIR = Path(__file__).resolve().parent
CONFIG_PATH = APP_DIR / "config.json"
WORKSPACE_PATH = APP_DIR / "workspace"


def require_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"Environment variable {name} is required")
    return value


def set_nested(mapping: dict[str, Any], path: list[str], value: Any) -> None:
    current: dict[str, Any] = mapping
    for key in path[:-1]:
        next_value = current.get(key)
        if not isinstance(next_value, dict):
            next_value = {}
            current[key] = next_value
        current = next_value
    current[path[-1]] = value


def load_config() -> dict[str, Any]:
    with CONFIG_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


def resolve_config(config: dict[str, Any]) -> dict[str, Any]:
    provider_name = config.get("agents", {}).get("defaults", {}).get("provider")
    if not provider_name:
        raise RuntimeError("agents.defaults.provider is missing in config.json")

    set_nested(config, ["agents", "defaults", "model"], require_env("LLM_API_MODEL"))
    set_nested(config, ["gateway", "host"], require_env("NANOBOT_GATEWAY_CONTAINER_ADDRESS"))
    set_nested(config, ["gateway", "port"], int(require_env("NANOBOT_GATEWAY_CONTAINER_PORT")))

    set_nested(config, ["providers", provider_name, "apiKey"], require_env("LLM_API_KEY"))
    set_nested(
        config,
        ["providers", provider_name, "apiBase"],
        require_env("LLM_API_BASE_URL"),
    )

    mcp_servers = config.setdefault("tools", {}).setdefault("mcpServers", {})
    lms_server = mcp_servers.setdefault("lms", {})
    lms_server["env"] = {
        "NANOBOT_LMS_BACKEND_URL": require_env("NANOBOT_LMS_BACKEND_URL"),
        "NANOBOT_LMS_API_KEY": require_env("NANOBOT_LMS_API_KEY"),
    }

    channels = config.setdefault("channels", {})
    webchat = channels.setdefault("webchat", {})
    webchat["enabled"] = True
    webchat["host"] = require_env("NANOBOT_WEBCHAT_CONTAINER_ADDRESS")
    webchat["port"] = int(require_env("NANOBOT_WEBCHAT_CONTAINER_PORT"))
    webchat["access_key"] = require_env("NANOBOT_ACCESS_KEY")
    webchat.setdefault("allow_from", ["*"])

    return config


def write_resolved_config(config: dict[str, Any]) -> Path:
    temp_file = tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        suffix=".json",
        prefix="nanobot-config-",
        delete=False,
    )
    with temp_file:
        json.dump(config, temp_file, indent=2)
        temp_file.write("\n")
    return Path(temp_file.name)


def main() -> None:
    config = load_config()
    resolved_config_path = write_resolved_config(resolve_config(config))
    os.execvp(
        "nanobot",
        [
            "nanobot",
            "gateway",
            "--config",
            str(resolved_config_path),
            "--workspace",
            str(WORKSPACE_PATH),
        ],
    )


if __name__ == "__main__":
    main()
