from pathlib import Path

from app.config import Settings


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def read_env_example_value(key: str) -> str | None:
    env_example = PROJECT_ROOT / ".env.example"

    for line in env_example.read_text().splitlines():
        if line.startswith(f"{key}="):
            return line.split("=", 1)[1]

    return None


def test_version_file_matches_backend_default_version():
    version_file = PROJECT_ROOT / "VERSION"
    version = version_file.read_text().strip()

    assert version == Settings.model_fields["app_version"].default


def test_env_example_app_version_matches_backend_default_version():
    assert read_env_example_value("APP_VERSION") == Settings.model_fields["app_version"].default


def test_env_example_uses_current_llama_setting_names():
    env_text = (PROJECT_ROOT / ".env.example").read_text()

    assert "LLAMA_BASE_URL=" in env_text
    assert "LLAMA_MODEL=" in env_text
    assert "LLAMA_TIMEOUT_SECONDS=" in env_text
    assert "OLLAMA_BASE_URL=" not in env_text
    assert "OLLAMA_MODEL=" not in env_text


def test_root_docker_compose_file_exists():
    compose_file = PROJECT_ROOT / "docker-compose.yml"

    assert compose_file.exists()


def test_ci_validates_docker_builds():
    ci_file = PROJECT_ROOT / ".github" / "workflows" / "ci.yml"
    ci_text = ci_file.read_text()

    assert "docker-build" in ci_text
    assert "Docker Build Validation" in ci_text
    assert "docker build -t worldcup-backend:test ./backend" in ci_text
    assert "docker build -t worldcup-dashboard:test ./dashboard" in ci_text
    assert "cp .env.example .env" in ci_text
    assert "docker compose -f docker-compose.yml config" in ci_text
