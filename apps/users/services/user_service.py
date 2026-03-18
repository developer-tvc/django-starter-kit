from apps.users.models import User,Role
from apps.users.selectors.user_selectors import get_user,list_users
class UserService:

    @staticmethod
    def list_users():
        return list_users()

    @staticmethod
    def create_user(username: str, password: str, first_name: str, last_name: str):
        user = User(username=username, email=username, first_name=first_name, last_name=last_name)
        user.set_password(password)
        user.save()
        return user

    @staticmethod
    def update_user(user_id: int, data: dict):
        user = get_user(user_id)
        if not user:
            return None

        for attr, value in data.items():
            setattr(user, attr, value)
        user.save()
        return user

    @staticmethod
    def delete_user(user_id: int):
        user = get_user(user_id)
        if not user:
            return None

        user.is_active = False  # soft delete for now
        user.save()
        return user