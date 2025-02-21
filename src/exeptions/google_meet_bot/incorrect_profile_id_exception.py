class IncorrectProfileIdException(ValueError):
    def __init__(self, profile_id: int, count_profiles: int):
        super().__init__(f"Неверно указан id профиля. Значение id профиля (profile_id = {profile_id}) не должно превышать количество профилей в директории (count_profiles = {count_profiles})")
