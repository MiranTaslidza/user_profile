class PageTranslationClient {

    static SKIPPED_TAGS = new Set([
        "SCRIPT",
        "STYLE",
        "NOSCRIPT",
        "CODE",
        "PRE",
        "SVG",
        "TEXTAREA",
        "OPTION",
    ]);

    static MAX_BATCH_SIZE = 128;

    static TRANSLATABLE_ATTRIBUTES = [
    "placeholder",
    "title",
    "alt",
    "aria-label",
];

    static getCsrfToken() {
        const cookie = document.cookie
            .split("; ")
            .find(row => row.startsWith("csrftoken="));

        if (!cookie) {
            return null;
        }

        return decodeURIComponent(
            cookie.split("=")[1]
        );
    }

    static shouldSkipNode(node) {

        const parent = node.parentElement;

        if (!parent) {
            return true;
        }

        if (this.SKIPPED_TAGS.has(parent.tagName)) {
            return true;
        }

        if (parent.closest("[data-no-translate]")) {
            return true;
        }

        if (parent.isContentEditable) {
            return true;
        }

        return false;
    }

    static collectTextNodes(root = document.body) {

        if (!root) {
            return [];
        }

        const walker = document.createTreeWalker(
            root,
            NodeFilter.SHOW_TEXT
        );

        const textNodes = [];

        let node;

        while ((node = walker.nextNode())) {

            if (this.shouldSkipNode(node)) {
                continue;
            }

            const text = node.nodeValue.trim();

            if (!text) {
                continue;
            }

            textNodes.push({
                node: node,
                text: text,
            });
        }

        return textNodes;
    }

    static collectAttributeNodes(root = document.body) {

    if (!root) {
        return [];
    }

    const attributeNodes = [];

    const elements = root.querySelectorAll("*");

    for (const element of elements) {

        if (this.SKIPPED_TAGS.has(element.tagName)) {
            continue;
        }

        if (element.closest("[data-no-translate]")) {
            continue;
        }

        for (const attribute of this.TRANSLATABLE_ATTRIBUTES) {

            if (!element.hasAttribute(attribute)) {
                continue;
            }

            const value = element
                .getAttribute(attribute)
                ?.trim();

            if (!value) {
                continue;
            }

            attributeNodes.push({
                element: element,
                attribute: attribute,
                text: value,
            });
        }

        if (
            element.tagName === "INPUT" &&
            ["button", "submit", "reset"].includes(
                element.type
            )
        ) {

            const value = element.value?.trim();

            if (value) {
                attributeNodes.push({
                    element: element,
                    attribute: "value",
                    text: value,
                });
                }
            }
        }

        return attributeNodes;
    }

static getUniqueTexts(items) {

    return [
        ...new Set(
            items.map(item => item.text)
        ),
    ];
}

    static createBatches(texts) {

        const batches = [];

        for (
            let start = 0;
            start < texts.length;
            start += this.MAX_BATCH_SIZE
        ) {
            batches.push(
                texts.slice(
                    start,
                    start + this.MAX_BATCH_SIZE
                )
            );
        }

        return batches;
    }

    static async requestBatch(
        endpoint,
        texts
    ) {

        const csrfToken = this.getCsrfToken();

        const response = await fetch(
            endpoint,
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrfToken ?? "",
                },

                credentials: "same-origin",

                body: JSON.stringify({
                    texts: texts,
                }),
            }
        );

        if (!response.ok) {
            throw new Error(
                `Translation request failed: ${response.status}`
            );
        }

        const data = await response.json();

        if (!Array.isArray(data.translations)) {
            throw new Error(
                "Invalid translation response."
            );
        }

        return data.translations;
    }

    static async requestTranslations(
        endpoint,
        texts
    ) {

        if (!texts.length) {
            return [];
        }

        const batches = this.createBatches(texts);

        const translations = [];

        for (const batch of batches) {

            const batchTranslations =
                await this.requestBatch(
                    endpoint,
                    batch
                );

            translations.push(
                ...batchTranslations
            );
        }

        return translations;
    }

    static applyTranslations(
        textNodes,
        uniqueTexts,
        translations
    ) {

        const translationMap = new Map();

        uniqueTexts.forEach((text, index) => {

            const translation = translations[index];

            if (!translation) {
                return;
            }

            translationMap.set(
                text,
                translation.translated_text
            );
        });

        for (const item of textNodes) {

            const translatedText =
                translationMap.get(item.text);

            if (!translatedText) {
                continue;
            }

            const originalValue =
                item.node.nodeValue;

            const leadingWhitespace =
                originalValue.match(/^\s*/)?.[0] ?? "";

            const trailingWhitespace =
                originalValue.match(/\s*$/)?.[0] ?? "";

            item.node.nodeValue =
                `${leadingWhitespace}${translatedText}${trailingWhitespace}`;
        }
    }

    static applyAttributeTranslations(
    attributeNodes,
    translationMap
) {

    for (const item of attributeNodes) {

        const translatedText =
            translationMap.get(item.text);

        if (!translatedText) {
            continue;
        }

        if (item.attribute === "value") {
            item.element.value = translatedText;
            continue;
        }

        item.element.setAttribute(
            item.attribute,
            translatedText
        );
    }
}
static async translatePage(
    endpoint
) {

    const textNodes =
        this.collectTextNodes();

    const attributeNodes =
        this.collectAttributeNodes();

    const allItems = [
        ...textNodes,
        ...attributeNodes,
    ];

    if (!allItems.length) {
        return;
    }

    const uniqueTexts =
        this.getUniqueTexts(allItems);

    if (!uniqueTexts.length) {
        return;
    }

    try {

        const translations =
            await this.requestTranslations(
                endpoint,
                uniqueTexts
            );

        const translationMap = new Map();

        uniqueTexts.forEach((text, index) => {

            const translation =
                translations[index];

            if (!translation) {
                return;
            }

            translationMap.set(
                text,
                translation.translated_text
            );
        });

        for (const item of textNodes) {

            const translatedText =
                translationMap.get(item.text);

            if (!translatedText) {
                continue;
            }

            const originalValue =
                item.node.nodeValue;

            const leadingWhitespace =
                originalValue.match(/^\s*/)?.[0] ?? "";

            const trailingWhitespace =
                originalValue.match(/\s*$/)?.[0] ?? "";

            item.node.nodeValue =
                `${leadingWhitespace}${translatedText}${trailingWhitespace}`;
        }

        this.applyAttributeTranslations(
            attributeNodes,
            translationMap
        );

    } catch (error) {

        console.error(
            "Page translation failed:",
            error
        );
    }
}
}


window.PageTranslationClient =
    PageTranslationClient;


document.addEventListener(
    "DOMContentLoaded",
    () => {

        PageTranslationClient.translatePage(
            "/api/translate/"
        );

    }
);