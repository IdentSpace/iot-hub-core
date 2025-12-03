from typing import Union, List
from fastapi import APIRouter, status
from app.api.response import IHCApiResponse
from app.db.config_controller import get_sysvalue, get_sysvalue_all
from pathlib import Path
import asyncio

router = APIRouter()
pending_requests = []

@router.get("/state")
async def rq_config_get_list_all():
	import tomllib
	import subprocess
	ROOT_DIR = Path(__file__).parent.parent.parent
	TOML_PATH = ROOT_DIR / "pyproject.toml"
	
	with open(TOML_PATH, "rb") as f:
		config = tomllib.load(f)

	state = {
				"version": config["project"]["version"],
				"os": "TODO",
				"temp": "TODO",
			}

	return IHCApiResponse().add_data("state", state).to_dict()

@router.get("/list")
async def rq_config_get_list_all():
	value = get_sysvalue_all()
	return IHCApiResponse().add_data("config", value).to_dict()

@router.get("/get/{configName}")
async def rq_config_get_list(configName:str):
	value = get_sysvalue(configName)
	return IHCApiResponse().add_data(configName, value).to_dict()


@router.post("/set/{configName}")
async def rq_config_set_value():
	return IHCApiResponse(message="not implemented").to_dict()