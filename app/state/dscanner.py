from threading import Lock
import requests
from app.driver.types.data_scanner import DataScannerData
from app.db.session import get_session
from app.db.models import SysValues
from sqlmodel import select

dscanner_lock = Lock()
# TODO: Refactor to array
latest_nfc_data = None

def set_latest_dscanner_data(data: DataScannerData):
	global latest_dscanner_data
	latest_dscanner_data = data
	try:
		with get_session() as session:
			webhookData = session.exec(select(SysValues).where(SysValues.name == "WEBHOOK_DATASCANNER")).first()
			if(webhookData == None): return
			try:
				requests.get(webhookData.value + data.toUrlQuery(), timeout=2)
			except Exception as e:
				print("[WEBHOOK ERROR] ")
	except Exception as e:
		print(e)


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