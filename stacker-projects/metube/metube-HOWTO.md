# MeTube — Stacker Deploy HOWTO

Single container: `alexta69/metube:latest`. YouTube downloader with web UI.

## Setup

```bash
stacker config setup server --ip <SERVER_IP> --user root --key ~/.ssh/id_ed25519
```

## Deploy

```bash
stacker deploy --target server --force-rebuild
```

## Access

Open `http://<SERVER_IP>:8081/` in a browser.

Paste a YouTube URL and click Download.

## Notes

- Port: 8081
- Downloads: `metube_downloads` volume
- State: `metube_state` volume
- Uses yt-dlp + aria2c internally
