class Auth:

	def newToken(user_id: int):
		import secrets
		from app.db.models import ApiKey
		from app.db.session import get_session

		token = secrets.token_hex(40 // 2)

		with get_session() as session:
			api_key = ApiKey(user_id=user_id, key=token)
			session.add(api_key)
			session.commit()
			session.refresh(api_key)
			return token

		return None

	def loginByUsername(username, password):
		from app.db.models import User
		from app.db.session import get_session
		from sqlmodel import select

		with get_session() as session:
			user = session.exec(select(User).where((User.username == username) & (User.password == password))).first()
			if(user == None):
				return None

			return Auth.newToken(user.id)
		
		return None