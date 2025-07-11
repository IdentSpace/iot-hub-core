from app.devices.shelly import ShellyDevice

DRIVERS = {
	"shelly_http": ShellyDevice
}

def driver_factory(driver_type: str, **kwargs):
	if driver_type in DRIVERS:
		return DRIVERS[driver_type](**kwargs)
	else:
		raise ValueError(f"Driver type '{driver_type}' is not recognized.")