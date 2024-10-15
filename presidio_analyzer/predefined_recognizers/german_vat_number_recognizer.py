import re
from presidio_analyzer import Pattern, PatternRecognizer, RecognizerResult
from typing import List, Optional


class GermanVATRecognizer(PatternRecognizer):
    """
    Recognizer to detect German Value Added Tax (VAT) Numbers.
    """

    # Patterns for detecting German VAT Numbers
    PATTERNS = [
        # Pattern for German VAT number format without separators
        Pattern(
            name="German VAT (9-digit format)",
            regex=r"(?:\b[1-9][0-9]{8}\b)",
            score=1.0,
        ),
        # Pattern for German VAT number format with optional slashes or spaces
        Pattern(
            name="German VAT (formatted with slashes or spaces)",
            regex=r"(?:\b[1-9][0-9]{2}/?[0-9]{4}/?[0-9]{4}\b)",
            score=1.0,
        ),
        # Pattern for German VAT number alphanumeric pattern
        Pattern(
            name="German VAT (11-character alphanumeric)",
            regex=r"\b[Dd][Ee][ ]?[0-9]{3}[ ,]?[0-9]{3}[ ,]?[0-9]{3}\b",
            score=1.0,
        ),
    ]

    CONTEXT = [
        "vat number", "vat no", "vat#", "vat# mehrwertsteuer",
        "mwst", "mehrwertsteuer identifikationsnummer", "mehrwertsteuer nummer"
    ]

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "de",
        supported_entity: str = "DE_Germany_VAT_Number",
    ):
        patterns = patterns if patterns else self.PATTERNS
        context = context if context else self.CONTEXT
        super().__init__(
            supported_entity=supported_entity,
            patterns=patterns,
            context=context,
            supported_language=supported_language,
        )

    def analyze(self, text: str, entities: List[str], nlp_artifacts=None) -> List[RecognizerResult]:
        results = super().analyze(text, entities, nlp_artifacts)

        # Apply context-based scoring and checksum validation
        for result in results:
            if self._has_context(text, result.start, result.end) and self._validate_checksum(text[result.start:result.end]):
                result.score = min(result.score + 0.15, 1.0)  # Boost score if context and checksum pass
            else:
                result.score = result.score * 0.5  # Reduce score if context or checksum fails

        return results

    def _validate_checksum(self, vat_number: str) -> bool:
        """Validate the checksum of the German VAT number."""
        # Implement the checksum logic here, if applicable.
        # Since the actual checksum logic isn't specified, assuming a placeholder validation.
        # Replace with actual checksum algorithm as required.
        return True  # Placeholder: Assume checksum is valid

    def _has_context(self, text: str, start: int, end: int) -> bool:
        """Check if there is relevant context around the detected pattern."""
        window_size = 300  # Number of characters to check before and after the detected pattern
        context_window = text[max(0, start - window_size): min(len(text), end + window_size)]
        context_found = any(context_word.lower() in context_window.lower() for context_word in self.CONTEXT)
        return context_found
