from threading import Lock
import requests
from app.db.session import get_session
from app.db.models import SysValues
from sqlmodel import select
from app.driver.types.nfc_reader import NfcData


nfc_lock = Lock()
latest_nfc_data = None

def set_latest_nfc_data(data: NfcData):
	global latest_nfc_data
	latest_nfc_data = data
	try:
		if(data.uid == None or data.uid == ''): return
		
		with get_session() as session:
			webhookData = session.exec(select(SysValues).where(SysValues.name == "WEBHOOK_NFC")).first()
			if(webhookData == None): return
			try:
				base_url = str(webhookData.value)
				if not base_url.startswith(("http://", "https://")):
					print("[WEBHOOK ERROR] Invalid URL schema in webhookData.value")
					return
				
				hook = base_url + data.toUrlQuery()
				requests.get(hook, timeout=2, headers={"Connection": "close"})
				print(f"Full webhook URL: {hook}")
			except Exception as e:
				print("[WEBHOOK ERROR] " + e)
	except Exception as e:
		print(e)

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