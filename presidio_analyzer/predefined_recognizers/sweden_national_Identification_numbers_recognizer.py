from typing import Optional, List
from presidio_analyzer import Pattern, PatternRecognizer, RecognizerResult
import logging
import re

logger = logging.getLogger("presidio-analyzer")

class SwedenNationalIDRecognizer(PatternRecognizer):
    logger.info("Initializing Sweden National Identification Number Recognizer...")

    # Define patterns for Swedish National Identification Numbers
    PATTERNS = [
        Pattern(
            "Sweden National ID - 10 or 12 digits",
            r"\b\d{2}?\d{6}[-+]?(\d{4})\b",  # Optional two digits, 6 digits YYMMDD, optional delimiter, and 4 digits
            0.5  # Initial confidence score for the pattern match
        ),
        Pattern(
            "Sweden National ID - 10 or 12 digits",
            r"\b(?:19|20)?[0-9]{2}(?:0[1-9]|1[0-2])(?:0[1-9]|[12][0-9]|3[01])[-+]?[0-9]{4}\b",  # Optional two digits, 6 digits YYMMDD, optional delimiter, and 4 digits
            1.0  # Initial confidence score for the pattern match
        )
    ]

    # Context keywords for Swedish National ID
    CONTEXT = [
        "id no", "id number", "id#", "identification no", "identification number",
        "identifikationsnumret#", "identifikationsnumret", "identitetshandling",
        "identity document", "identity no", "identity number", "id-nummer", "personal id",
        "personnummer#", "personnummer", "skatteidentifikationsnummer"
    ]

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "sv",  # Supports Swedish and English
        supported_entity: str = "SWEDEN_NATIONAL_ID",
    ):
        patterns = patterns if patterns else self.PATTERNS
        context = context if context else self.CONTEXT
        super().__init__(
            supported_entity=supported_entity,
            patterns=patterns,
            context=context,
            supported_language=supported_language,
        )

    def analyze(
        self, text: str, entities: List[str], nlp_artifacts=None
    ) -> List[RecognizerResult]:
        logger.info(f"Analyzing text for Swedish National ID: {text}")
        results = super().analyze(text, entities, nlp_artifacts)
        for result in results:
            national_id = text[result.start:result.end]
            logger.debug(f"Detected National ID: {national_id}, Confidence: {result.score}")

            # Remove delimiters for checksum validation
            cleaned_national_id = re.sub(r"[-+]", "", national_id)

            # Perform Luhn checksum validation
            if self._is_valid_checksum(cleaned_national_id):
                logger.info(f"Checksum valid for National ID: {national_id}")
                result.score = 0.7  # Medium confidence if checksum passes
                if any(keyword in text.lower() for keyword in self.CONTEXT):
                    logger.info(f"Context keywords found for National ID: {national_id}, setting high confidence.")
                    result.score = 1.0  # High confidence if context keywords are present
            else:
                logger.warning(f"Invalid checksum for National ID: {national_id}")
                result.score = 0.0  # Invalid ID
        return results

    def _is_valid_checksum(self, national_id: str) -> bool:
        """
        Validate the checksum using Luhn's algorithm (Modulus 10).
        Only the last 10 digits are considered for validation.
        """
        national_id = national_id[-10:]  # Consider the last 10 digits for validation
        sum_ = 0
        alternate = False

        for digit in reversed(national_id):
            num = int(digit)
            if alternate:
                num *= 2
                if num > 9:
                    num -= 9
            sum_ += num
            alternate = not alternate

        return sum_ % 10 == 0
