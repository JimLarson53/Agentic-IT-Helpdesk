# KB: Windows VPN Error 809

Document type: Internal KB article
Applies to: Windows 10, Windows 11, remote access VPN

## Problem

Users connecting to the corporate VPN may receive error 809 when UDP traffic required for the VPN tunnel is blocked or when the VPN client profile points to an outdated gateway name.

## Symptoms

- Windows VPN client reports: "The network connection between your computer and the VPN server could not be established."
- The user can browse public websites but cannot connect to internal resources.
- Other users on different networks may connect successfully.

## Resolution

Confirm the user is on a stable internet connection. Ask the user to disconnect from guest Wi-Fi or captive portals. Verify the configured VPN server name is `vpn.example.test`. If the server name is old, update the VPN profile through the approved device management policy.

For low-risk diagnostics, support staff may ask the user to run `Resolve-DnsName vpn.example.test` in PowerShell and confirm that DNS returns an address. Staff may also check Windows Event Viewer under RasClient for recent VPN failure entries.

## Escalation

Escalate to network engineering when multiple users report error 809 from different networks or when DNS for `vpn.example.test` does not resolve.
