# SmartCam

Control legacy Samsung SmartCam cameras (SNH-P6410BN and compatible models) that are no longer officially supported. Features GUI and CLI interfaces with full camera control, WiFi setup, and RTSP streaming.

[Join the /r/AbandonedIoT subreddit to restore the functionality of deprecated / bricked IoT devices](https://reddit.com/r/AbandonedIoT)

## Quick Start

Factory reset your camera by powering the camera on, waiting for the LED to stablize, and hold the RESET button for 10-15 seconds until the LED flashes.

Once you are done, the username and password combo should be:

Usernames:

- `admin` - (SNH-P6410BN confirmed)
- `root`

Passwords:

- `<empty>` - (SNH-P6410BN confirmed)
- `1111111`
- `4321`
- `4321abcd`
- `1234`

```bash
# Install dependencies
pip install -r requirements.txt

# Run CLI (interactive)
python3 cli.py

# CLI with commands
python3 cli.py --info
python3 cli.py --streams

# Run (crappy) GUI
python3 gui.py
```

## RTSP Streaming

View camera streams with VLC or ffplay:

```bash
vlc "rtsp://admin:password@192.168.1.200:554/profile5/media.smp"
ffplay -rtsp_transport tcp -i "rtsp://admin:password@192.168.1.200:554/profile5/media.smp"
```

## License

MIT
