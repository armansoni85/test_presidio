from typing import Optional, List
from presidio_analyzer import Pattern, PatternRecognizer, RecognizerResult
import logging
import re

logger = logging.getLogger("presidio-analyzer")

class NetherlandsNationalIDRecognizer(PatternRecognizer):
    logger.info("Initializing Netherlands National Identification Number Recognizer...")

    # Define patterns for Netherlands National Identification Numbers (9 digits without spaces or delimiters)
    PATTERNS = [
        Pattern(
            "Netherlands National ID - High Confidence",
            r"\b[0-9]{9}\b",  # Pattern for exactly 9 digits
            0.7  # Initial confidence score for the pattern match
        )
    ]

    # Context keywords for National Identification Number
    CONTEXT = [
        "burgerservicenummer", "national identification number", "bsn", 
        "national ID", "nummer", "ID number", "identificatienummer"
    ]

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "nl",  # Supports Dutch and English
        supported_entity: str = "NETHERLANDS_NATIONAL_ID",
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
        logger.info(f"Analyzing text for Netherlands National ID: {text}")
        results = super().analyze(text, entities, nlp_artifacts)
        for result in results:
            national_id = text[result.start:result.end]
            logger.debug(f"Detected National ID: {national_id}, Confidence: {result.score}")
            if self._is_valid_checksum(national_id):
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
        Validate the checksum for the given Netherlands National ID.
        The Modulus 11 algorithm is used for validation.
        """
        logger.debug(f"Validating checksum for National ID: {national_id}")
        total_sum = 0
        multiplier = 9

        for i in range(9):
            digit = int(national_id[i])
            total_sum += digit * multiplier
            multiplier -= 1

        # Modulus 11 check
        is_valid = total_sum % 11 == 0
        if is_valid:
            logger.info(f"Checksum for National ID {national_id} is valid.")
        else:
            logger.error(f"Checksum for National ID {national_id} is invalid.")
        return is_valid
