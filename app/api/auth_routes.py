from typing import Union, List
from uuid import UUID
from fastapi import APIRouter, status
from app.api.response import IHCApiResponse
import asyncio

router = APIRouter()
pending_requests = []

@router.get("/wait-for-card")
async def request_wait_for_card(timeout: int = 1000):
	from app.state.nfc import get_and_pop_latest_nfc_data, pop_latest_nfc_data

	# TODO: select wich reader
	print("Waiting for NFC card...")
	check_interval = 0.2
	waited = 0

	pop_latest_nfc_data()

	while waited < timeout:
		card_uid = get_and_pop_latest_nfc_data()
		if card_uid:
			return IHCApiResponse(message="success").add_data(key="uid", value=card_uid).to_dict()
		await asyncio.sleep(check_interval)
		waited += check_interval

	return IHCApiResponse(message="timeout").to_dict()