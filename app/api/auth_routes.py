from typing import Union, List
from uuid import UUID
from fastapi import APIRouter, status
from app.api.response import IHCApiResponse
import asyncio
from pydantic import BaseModel

router = APIRouter()
pending_requests = []

class AuthUsername(BaseModel):
	username: str
	password: str
	# TODO: with expire wish


# TODO: Implement
@router.post("/login")
def req_auth(auth: AuthUsername):
	from app.auth.authentification import Auth

	token = Auth.loginByUsername(auth.username, auth.password)

	if(token == None):
		response = IHCApiResponse(message="error").add_error(key="auth", value="can not login").set_status_code(400)
		return response.api_response()

	response = IHCApiResponse(message="success").add_data(key="access_token", value=token)
	response.add_data(key="expire_at", value=None)
	return response.api_response()


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