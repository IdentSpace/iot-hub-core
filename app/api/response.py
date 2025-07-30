class IHCApiResponse:
	def __init__(self, message: str = None):
		self.status_code = 200
		self.message = message
		self.data = dict()
		self.errors = dict()

	def add_data(self, key: str, value):
		self.data[key] = value
		return self

	def add_error(self, key: str, value):
		self.errors[key] = value
		return self
	
	def set_status_code(self, code: int):
		self.status_code = code
		return self

	def to_dict(self):
		return {
			"message": self.message,
			"data": self.data,
			"errors": self.errors
		}
	
	def api_response(self):
		from fastapi.responses import JSONResponse
		return JSONResponse(
			status_code=self.status_code,
			content=self.to_dict()
		)