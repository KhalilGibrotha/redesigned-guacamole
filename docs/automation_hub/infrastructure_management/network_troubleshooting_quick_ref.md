# Network Troubleshooting Quick Reference

This is a direct markdown file for quick reference during network troubleshooting.

## Common Network Issues

### DNS Problems
- Check `/etc/resolv.conf`
- Test with `nslookup` or `dig`
- Verify DNS server connectivity

### Connectivity Issues
```bash
# Basic connectivity tests
ping 8.8.8.8
traceroute google.com
netstat -tuln
ss -tuln
```

### Port Testing
```bash
# Test specific ports
telnet hostname 80
nc -zv hostname 443
nmap -p 80,443 hostname
```

## Useful Commands

| Command | Purpose |
|---------|---------|
| `ip addr show` | Show IP addresses |
| `ip route show` | Show routing table |
| `iptables -L` | List firewall rules |
| `systemctl status networking` | Check network service |

## Quick Fixes

1. **Restart networking**: `sudo systemctl restart networking`
2. **Flush DNS cache**: `sudo systemctl restart systemd-resolved`
3. **Reset network interface**: `sudo ip link set eth0 down && sudo ip link set eth0 up`

*This file demonstrates direct markdown in nested sections.*
