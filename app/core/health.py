class HealthCheck:
	def __init__(self, name: str, status: str):
		self.name = name
		self.status = status

	def getThreads(self):
		import threading
		return [thread.name for thread in threading.enumerate()]

	def to_dict(self):
		return {
			"name": self.name,
			"status": self.status
		}