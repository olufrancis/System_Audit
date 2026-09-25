import os
import stat
import subprocess
import sys
from datetime import datetime


def parse_auth_logs(log_path: str) -> int:
    """Parses authentication logs to flag failed SSH login attempts."""
    failed_attempts = 0
    if not os.path.exists(log_path):
        print(f"Warning: Log path {log_path} not found. Skipping log parse.")
        return 0

    with open(log_path, "r") as file:
        for line in file:
            if "Failed password" in line or "authentication failure" in line:
                failed_attempts += 1
    return failed_attempts


def audit_file_permissions(file_paths: list[str]) -> list[str]:
    """Audits file paths to ensure they are not world-writable."""
    insecure_files = []
    for path in file_paths:
        if os.path.exists(path):
            st = os.stat(path)
            # Check if others have write permission
            if st.st_mode & stat.S_IWOTH:
                insecure_files.append(path)
    return insecure_files


def check_system_processes() -> int:
    """Executes a subshell command to count running active background daemons."""
    try:
        # Added the missing closing parenthesis here
        result = subprocess.run(
            ["ps", "-e", "--no-headers"], capture_output=True, text=True
        )
        process_count = len(result.stdout.strip().split("\n"))
        return process_count
    except Exception as e:
        print(f"Error querying process table: {e}")
        return 0


if __name__ == "__main__":
    log_file = sys.argv[1] if len(sys.argv) > 1 else "/var/log/auth.log"
    critical_files = ["/etc/passwd", "/etc/shadow", "main.py"]

    print(f"=== LINUX SYSTEM AUDIT REPORT [{datetime.utcnow().isoformat()}] ===")
    failed_logins = parse_auth_logs(log_file)
    print(f"[+] Failed Logins Detected: {failed_logins}")

    insecure = audit_file_permissions(critical_files)
    if insecure:
        print(f"[!] INSECURE WORLD-WRITABLE FILES FOUND: {insecure}")
    else:
        print("[+] File Permission Audit: SECURE")

    total_procs = check_system_processes()
    print(f"[+] Active Process Count: {total_procs}")
