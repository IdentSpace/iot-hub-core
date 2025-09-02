from app.driver.shelly import Shelly
from app.devices.base import Default

DRIVERS = {
	"shelly_http": Shelly,
	"default": Default
}

def driver_factory(driver_type: str, **kwargs):
	if driver_type in DRIVERS:
		return DRIVERS[driver_type](**kwargs)
	else:
		return DRIVERS["default"](**kwargs)
	

# TODO: load into DB and co
def load_drivers():
	pass