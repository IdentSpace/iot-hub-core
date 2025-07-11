class IHCApiResponse:
	def __init__(self, message: str = None):
		self.message = message
		self.data = dict()
		self.errors = dict()

	def add_data(self, key: str, value):
		self.data[key] = value
		return self

	def add_error(self, key: str, value):
		self.errors[key] = value
		return self

	def to_dict(self):
		return {
			"message": self.message,
			"data": self.data,
			"errors": self.errors
		}