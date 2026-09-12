class LanguageService:

    DEFAULT_LANGUAGE = "en"

    @classmethod
    def get_user_language(cls, user) -> str:

        if not user or not user.is_authenticated:
            return cls.DEFAULT_LANGUAGE

        try:
            language = user.profile.language
        except AttributeError:
            return cls.DEFAULT_LANGUAGE

        if not language:
            return cls.DEFAULT_LANGUAGE

        return language