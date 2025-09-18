from threading import Lock

dscanner_lock = Lock()
# TODO: Refactor to array
latest_nfc_data = None

def set_latest_dscanner_data(data):
	global latest_dscanner_data
	latest_dscanner_data = data

def pop_latest_dscanner_data():
	global latest_dscanner_data
	with dscanner_lock:
		latest_dscanner_data = None

def get_and_pop_latest_dscanner_data():
	global latest_dscanner_data
	try:
		with dscanner_lock:
			# Pop the latest dscanner data and return it
			to_return = latest_dscanner_data
			latest_dscanner_data = None
			return to_return
	except Exception as e:
		print(f"Error getting dscanner data from queue: {e}")
		return None