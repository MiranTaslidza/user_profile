from dataclasses import dataclass
from html import unescape
from google.cloud import translate_v2 as translate
from .language_service import LanguageService 

from hashlib import sha256

from django.conf import settings
from django.core.cache import cache


@dataclass(frozen=True)
class TranslationResult:
    translated_text: str
    detected_source_language: str | None


class TranslationService:

    _client = None
    
    CACHE_VERSION = "v1"

    CACHE_TIMEOUT = getattr(
        settings,
        "TRANSLATION_CACHE_TIMEOUT",
        60 * 60 * 24 * 30,
    )

    @classmethod
    def _get_client(cls):
        if cls._client is None:
            cls._client = translate.Client()

        return cls._client
    
    @classmethod
    def _build_cache_key(
        cls,
        text: str,
        target_language: str,
        source_language: str | None,
    ) -> str:

        source = source_language or "auto"

        value = (
            f"{cls.CACHE_VERSION}|"
            f"{source}|"
            f"{target_language}|"
            f"{text}"
        )

        digest = sha256(
            value.encode("utf-8")
        ).hexdigest()

        return f"translation:{digest}"

    @classmethod
    def translate_text(
        cls,
        text: str,
        target_language: str,
        source_language: str | None = None,
    ) -> TranslationResult:

        results = cls.translate_many(
            texts=[text],
            target_language=target_language,
            source_language=source_language,
        )

        return results[0]
    
    
    @classmethod
    def translate_many(
        cls,
        texts: list[str],
        target_language: str,
        source_language: str | None = None,
    ) -> list[TranslationResult]:

        if not texts:
            return []

        translations = [
            TranslationResult(
                translated_text=text,
                detected_source_language=source_language,
            )
            for text in texts
        ]

        non_empty_indexes = [
            index
            for index, text in enumerate(texts)
            if text and text.strip()
        ]

        if not non_empty_indexes:
            return translations

        cache_keys = {
            index: cls._build_cache_key(
                text=texts[index],
                target_language=target_language,
                source_language=source_language,
            )
            for index in non_empty_indexes
        }

        cached_values = cache.get_many(
            list(cache_keys.values())
        )

        missing_indexes = []

        for index in non_empty_indexes:

            cache_key = cache_keys[index]

            cached_result = cached_values.get(
                cache_key
            )

            if cached_result is None:
                missing_indexes.append(index)
                continue

            translations[index] = TranslationResult(
                translated_text=cached_result[
                    "translated_text"
                ],
                detected_source_language=cached_result.get(
                    "detected_source_language"
                ),
            )

        if not missing_indexes:
            return translations

        options = {
            "target_language": target_language,
            "format_": "text",
        }

        if source_language:
            options["source_language"] = source_language

        client = cls._get_client()

        batch_size = 128

        values_to_cache = {}

        for start in range(
            0,
            len(missing_indexes),
            batch_size,
        ):

            batch_indexes = missing_indexes[
                start:start + batch_size
            ]

            batch_values = [
                texts[index]
                for index in batch_indexes
            ]

            results = client.translate(
                values=batch_values,
                **options,
            )

            for index, result in zip(
                batch_indexes,
                results,
            ):

                translation = TranslationResult(
                    translated_text=unescape(
                        result["translatedText"]
                    ),
                    detected_source_language=result.get(
                        "detectedSourceLanguage",
                        source_language,
                    ),
                )

                translations[index] = translation

                values_to_cache[
                    cache_keys[index]
                ] = {
                    "translated_text": (
                        translation.translated_text
                    ),
                    "detected_source_language": (
                        translation.detected_source_language
                    ),
                }

        if values_to_cache:
            cache.set_many(
                values_to_cache,
                timeout=cls.CACHE_TIMEOUT,
            )

        return translations
    

    @classmethod
    def translate_for_user(
        cls,
        text: str,
        user,
        source_language: str | None = None,
    ) -> TranslationResult:

        # target_language = user.profile.language
        target_language = LanguageService.get_user_language(user)

        return cls.translate_text(
            text=text,
            target_language=target_language,
            source_language=source_language,
        )
        
    @classmethod
    def translate_many_for_user(
        cls,
        texts: list[str],
        user,
        source_language: str | None = None,
    ) -> list[TranslationResult]:

        target_language = LanguageService.get_user_language(user)

        return cls.translate_many(
            texts=texts,
            target_language=target_language,
            source_language=source_language,
        )