# IoT Hub Core

!!! Fresh and under development

- a Python core library to manage devices such as Shelly, Sonoff, and other supported IoT brands.
- users can integrate their own UI by interacting with the core library through HTTP or WebSocket APIs

## Tested Driver

| Device   | Connection | Usage   |
|----------|------------|---------|
| Automatic Systems AS1620 | Network  | Parking Barrier

## Install

Global installation of packages
```
pip3 install -r requirements.txt
```

Local environment
```
python3 -m venv venv
source venv/bin/activate
```

## Run
wget ... prepare-install.sh
...

```
systemctl start iot-hub-core
python ./run.py
```

## Build Windows Client
python -m PyInstaller --onefile --add-data "app;app" --hidden-import fastapi --hidden-import uvicorn --hidden-import sqlmodel --hidden-import requests --hidden-import aiosqlite .\run.build.py

## Milestones
1) Controll different device types with shellys over http
2) Rolles and Cans
3) Over shelly websockets
4) Add support for additional IoT brands and device typesMilestones
5) Implement hooks
6) Watch and Sync

## Shortcuts
```
lsusb
lsusb -d <usbvendorpid> -v


systemctl status iot-hub-core
journalctl -u iot-hub-core -f
```

## Maintainer
IdentSpace

## Partners
2G Konzept DudoPark
