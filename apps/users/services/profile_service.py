from apps.users.selectors.user_selectors import get_user


class ProfileService:
    @staticmethod
    def get_profile(user):
        return get_user(user.id)

    @staticmethod
    def update_profile(user, data):
        user.first_name = data.get("first_name", user.first_name)
        user.last_name = data.get("last_name", user.last_name)
        user.phone_number = data.get("phone_number", user.phone_number)
        user.avatar_url = data.get("avatar_url", user.avatar_url)
        user.save()
        return user
