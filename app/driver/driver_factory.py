from app.driver.shelly import Shelly
from app.driver.types.device import Default
from app.driver.default_data_scanner import DefaultDataScanner
from app.driver.default_nfc_reader import DefaultNfcReader
from app.driver.as1620 import AS1620

DRIVERS = {
	"shelly_http": Shelly,
	"default_datascanner": DefaultDataScanner,
	"default_nfcreader": DefaultNfcReader,
	"as1620": AS1620,
	"default": Default
}

def driver_factory(driver_type: str, **kwargs):
	print(driver_type)
	if driver_type in DRIVERS:
		return DRIVERS[driver_type](**kwargs)
	else:
		return DRIVERS["default"](**kwargs)

# TODO: load into DB and co
def load_drivers():
	pass