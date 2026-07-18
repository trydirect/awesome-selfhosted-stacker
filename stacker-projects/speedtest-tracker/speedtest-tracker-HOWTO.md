# Speedtest Tracker — Stacker Deploy HOWTO

Single container: `lscr.io/linuxserver/speedtest-tracker:latest`. Internet speed monitoring with graphs.

## Setup

```bash
stacker config setup server --ip <SERVER_IP> --user root --key ~/.ssh/id_ed25519
```

## Deploy

```bash
stacker deploy --target server --force-rebuild
```

## Access

Open `http://<SERVER_IP>:8080/` in a browser.

Create an account on first visit.

## Notes

- Port: 8080
- Data: `speedtest_config` volume
- Runs automated speed tests on schedule
- Historical graphs and statistics
- Supports multiple speedtest servers
