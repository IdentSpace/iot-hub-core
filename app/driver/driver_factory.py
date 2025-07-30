from app.devices.shelly import ShellyDevice
from app.devices.base import Default

DRIVERS = {
	"shelly_http": ShellyDevice,
	"default": Default
}

def driver_factory(driver_type: str, **kwargs):
	if driver_type in DRIVERS:
		return DRIVERS[driver_type](**kwargs)
	else:
		return DRIVERS["default"](**kwargs)