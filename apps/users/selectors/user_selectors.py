from apps.users.models import User


def get_user(user_id: int):
    """
    Get a user by ID
    """
    return User.objects.filter(id=user_id).first()


def get_user_by_username(username: str):
    """
    Get a user by username
    """
    return User.objects.filter(username=username).first()


def list_users():
    """
    List all users
    """
    return User.objects.all()