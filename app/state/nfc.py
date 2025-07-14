from threading import Lock

nfc_lock = Lock()
latest_nfc_data = None

def set_latest_nfc_data(data):
	global latest_nfc_data
	latest_nfc_data = data

def pop_latest_nfc_data():
	global latest_nfc_data
	with nfc_lock:
		latest_nfc_data = None

def get_and_pop_latest_nfc_data():
	global latest_nfc_data
	try:
		with nfc_lock:
			# Pop the latest NFC data and return it
			to_return = latest_nfc_data
			latest_nfc_data = None
			return to_return
	except Exception as e:
		print(f"Error getting NFC data from queue: {e}")
		return None