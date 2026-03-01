from fastapi import APIRouter
from app.api.response import IHCApiResponse
from app.db.config_controller import get_sysvalue, get_sysvalue_all
from app.core.utils import get_resource_path

router = APIRouter()
pending_requests = []

@router.get("/state")
async def rq_config_get_list_all():
	import tomllib
	TOML_PATH = get_resource_path("pyproject.toml")
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

@router.post("/set")
async def rq_config_set_value(data: dict):
	name = data.get("name")
	value = data.get("value")
	from app.db.config_controller import set_sysvalue
	set_sysvalue(name, value)
	return IHCApiResponse(message="success").api_response()

@router.post("/delete")
def req_config_delete(data: dict):
	if "name" not in data:
		return IHCApiResponse(message="error").add_error(key="config", value="Missing Config name").api_response()
	
	name = data.get("name")
	from app.db.config_controller import delete_sysvalue
	delete_sysvalue(name)
	IHCApiResponse(message="success").api_response()

@router.get("/restart/threads")
async def rq_config_restart_threads():
	from app.core.threadrunner import restart_threads, start_threading
	restart_threads()
	await start_threading()
	return IHCApiResponse(message="success").api_response()