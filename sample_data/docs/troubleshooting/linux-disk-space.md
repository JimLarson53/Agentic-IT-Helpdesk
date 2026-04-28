# Troubleshooting Note: Linux Disk Space Pressure

Document type: Troubleshooting note
Applies to: Ubuntu Server, Debian, RHEL-compatible systems

## Issue

Linux hosts can become unstable when the root filesystem is full. Common symptoms include failed package updates, services failing to write logs, and applications returning unexpected errors.

## Safe Diagnostics

Use `df -h` to inspect filesystem usage. Use `du -sh /var/log/*` to identify large log directories when the affected path is `/var/log`. Use `journalctl --disk-usage` to inspect journal size.

## Safe Remediation Guidance

Prefer application-specific cleanup procedures. Do not remove arbitrary system files. For journald, use organization-approved retention settings rather than deleting files directly. Escalate before removing data from production systems.

## Verification

After cleanup, verify that disk usage is below the operational threshold and restart only the affected service if required by the runbook.
