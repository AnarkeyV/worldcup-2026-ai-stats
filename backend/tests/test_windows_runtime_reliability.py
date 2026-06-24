from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
WINDOWS_SCRIPTS = PROJECT_ROOT / "scripts" / "windows"


def read_script(name: str) -> str:
    return (WINDOWS_SCRIPTS / name).read_text()


def test_read_only_runtime_status_script_exists():
    script_path = WINDOWS_SCRIPTS / "get-worldcup-runtime-status.ps1"

    assert script_path.exists()

    script_text = script_path.read_text()

    assert "Read-only runtime status" in script_text
    assert "docker compose ps" in script_text
    assert "http://127.0.0.1:11434/api/tags" in script_text
    assert "Get-ScheduledTask" in script_text


def test_read_only_runtime_status_script_does_not_repair_or_reconfigure_runtime():
    script_text = read_script("get-worldcup-runtime-status.ps1")

    blocked_commands = (
        "docker compose up",
        "docker compose restart",
        "docker restart",
        "Start-Service",
        "Restart-Service",
        "Stop-Service",
        "Start-Process",
        "Stop-Process",
        "Register-ScheduledTask",
        "Set-ScheduledTask",
        "Start-ScheduledTask",
        "Stop-ScheduledTask",
        "Invoke-RestMethod -Method Post",
    )

    for command in blocked_commands:
        assert command not in script_text


def test_startup_and_watchdog_keep_cloudflared_report_only():
    for script_name in (
        "start-worldcup-runtime.ps1",
        "watch-worldcup-runtime.ps1",
    ):
        script_text = read_script(script_name)

        assert "function Report-CloudflaredService" in script_text
        assert "Cloudflared automation is report-only" in script_text
        assert "Start-Service cloudflared" not in script_text
        assert "Restart-Service cloudflared" not in script_text


def test_startup_and_watchdog_report_ai_without_launching_ollama():
    for script_name in (
        "start-worldcup-runtime.ps1",
        "watch-worldcup-runtime.ps1",
    ):
        script_text = read_script(script_name)

        assert "function Report-AiHealth" in script_text
        assert "Ollama automation is report-only" in script_text
        assert "ollama.exe" not in script_text
        assert "ollama serve" not in script_text


def test_watchdog_keeps_existing_container_recovery_scope():
    script_text = read_script("watch-worldcup-runtime.ps1")

    assert "function Restart-UnhealthyContainers" in script_text
    assert '"worldcup-postgres"' in script_text
    assert '"worldcup-backend"' in script_text
    assert '"worldcup-dashboard"' in script_text
    assert "docker restart $Container" in script_text


def test_runtime_task_registration_documents_report_only_boundaries():
    script_text = read_script("register-worldcup-runtime-tasks.ps1")

    assert "Cloudflared and Ollama checks are report-only." in script_text
    assert "repairs unhealthy Docker containers" in script_text

def test_read_only_runtime_status_checks_public_health_status_and_version_consistency():
    script_text = read_script("get-worldcup-runtime-status.ps1")

    assert '$PublicHealth.status -eq "healthy"' in script_text
    assert "Public health response is not healthy." in script_text
    assert "Version consistency" in script_text
    assert "Local and public backend versions differ." in script_text
    assert "$script:LocalBackendVersion -ne $script:PublicBackendVersion" in script_text

