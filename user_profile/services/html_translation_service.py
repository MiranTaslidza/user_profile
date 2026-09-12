from bs4 import BeautifulSoup
from bs4.element import NavigableString

from .translation_service import TranslationService


class HTMLTranslationService:

    SKIP_TAGS = {
        "script",
        "style",
        "code",
        "pre",
        "noscript",
        "svg",
    }

    @classmethod
    def translate_html(
        cls,
        html: str,
        user,
    ) -> str:

        if not html:
            return html

        soup = BeautifulSoup(
            html,
            "html.parser",
        )

        text_nodes = []

        for node in soup.find_all(string=True):

            if not isinstance(node, NavigableString):
                continue

            parent = node.parent

            if parent is None:
                continue

            if parent.name in cls.SKIP_TAGS:
                continue

            text = str(node)

            if not text.strip():
                continue

            text_nodes.append(node)

        if not text_nodes:
            return html

        texts = [
            str(node).strip()
            for node in text_nodes
        ]

        translations = TranslationService.translate_many_for_user(
            texts=texts,
            user=user,
        )

        for node, translation in zip(
            text_nodes,
            translations,
        ):
            original = str(node)

            leading_space = original[
                :len(original) - len(original.lstrip())
            ]

            trailing_space = original[
                len(original.rstrip()):
            ]

            node.replace_with(
                f"{leading_space}"
                f"{translation.translated_text}"
                f"{trailing_space}"
            )

        return str(soup)