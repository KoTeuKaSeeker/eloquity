class NoUserProfilesFoundException(FileNotFoundError):
    def __init__(self, profile_path: str):
        super().__init__(f"Не найдено ни одного профиля пользователя. Возможно указана не верная директория профилей: {profile_path}")