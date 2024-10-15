from typing import Optional, List
from presidio_analyzer import Pattern, PatternRecognizer, RecognizerResult
import re
import logging

logger = logging.getLogger("presidio-analyzer")

class SpainPassportRecognizer(PatternRecognizer):
    logger.info("Initializing Spain Passport Recognizer...")

    # Define patterns for Spain Passport Numbers (8-9 alphanumeric characters)
    PATTERNS = [
        Pattern(
            "Spain Passport Number - Low Confidence",
            r"\b[A-Za-z0-9]{8,9}\b",  # 8-9 alphanumeric characters
            0.4  # Initial confidence score for low confidence match
        ),
    ]

    # Context keywords related to Spain passport
    CONTEXT_KEYWORDS = [
        "passport", "passport number", "número de pasaporte", "spanish passport", "pasaporte"
    ]

    # Date-related keywords and regex pattern for dates
    DATE_KEYWORDS = ["date", "fecha", "expedition date", "fecha de expedición"]
    DATE_PATTERN = r"\b(?:\d{2}-\d{2}-\d{4}|\d{2}/\d{2}/\d{4})\b"  # Match dd-mm-yyyy or dd/mm/yyyy formats

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "en",  # Supports English and Spanish
        supported_entity: str = "SPAIN_PASSPORT",
    ):
        patterns = patterns if patterns else self.PATTERNS
        context = context if context else self.CONTEXT_KEYWORDS
        super().__init__(
            supported_entity=supported_entity,
            patterns=patterns,
            context=context,
            supported_language=supported_language,
        )

    def analyze(
        self, text: str, entities: List[str], nlp_artifacts=None
    ) -> List[RecognizerResult]:
        results = super().analyze(text, entities, nlp_artifacts)
        for result in results:
            lower_text = text.lower()

            # Check if passport keywords are present
            has_keyword = any(keyword in lower_text for keyword in self.CONTEXT_KEYWORDS)

            # Check if date keyword or date pattern is present
            has_date_keyword = any(date_kw in lower_text for date_kw in self.DATE_KEYWORDS)
            has_date_pattern = re.search(self.DATE_PATTERN, text) is not None

            if has_keyword and (has_date_keyword or has_date_pattern):
                result.score = min(result.score + 0.6, 1.0)  # High confidence
            elif has_keyword:
                result.score = min(result.score + 0.4, 1.0)  # Medium confidence
            else:
                result.score = result.score  # Low confidence (default)

        return results
