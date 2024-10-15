from typing import Optional, List
from presidio_analyzer import Pattern, PatternRecognizer, RecognizerResult
import logging
import re

logger = logging.getLogger("presidio-analyzer")

class SpainSSNRecognizer(PatternRecognizer):
    logger.info("Initializing Spain Social Security Number Recognizer...")

    # Define patterns for Spanish Social Security Numbers (SSN)
    PATTERNS = [
        Pattern(
            "Spain SSN - High Confidence",
            r"(?:\b[0-6][0-9][ -]?[0-9]{8}[ -]?[0-9]{2}\b)",  # Pattern for 11-12 digits SSN format
            0.5  # Initial confidence score for the pattern match
        ),
        Pattern(
            "Spain SSN - Alternate Format",
            r"\b\d{2}/?\d{7,8}/?\d{2}\b",  # Alternate format for SSN: two digits, optional slash, 7-8 digits, optional slash, two digits
            0.5  # Initial confidence score for the pattern match
        )
    ]

    # Spanish and English context keywords for SSN
    CONTEXT = [
        "ssn", "ssn#", "socialsecurityno", "social security no", 
        "social security number", "número de la seguridad social"
    ]

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "es",  # Supports Spanish and English
        supported_entity: str = "SPAIN_SSN",
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
        logger.info(f"Analyzing text: {text}")
        results = super().analyze(text, entities, nlp_artifacts)
        for result in results:
            ssn = text[result.start:result.end]
            logger.debug(f"Detected SSN: {ssn}, Confidence: {result.score}")
            if self._is_valid_checksum(ssn):
                logger.info(f"Checksum valid for SSN: {ssn}")
                result.score = 0.7  # Medium confidence if checksum passes
                if any(keyword in text.lower() for keyword in self.CONTEXT):
                    logger.info(f"Context keywords found for SSN: {ssn}, setting high confidence.")
                    result.score = 1.0  # High confidence if checksum passes and context keywords are present
            else:
                logger.warning(f"Invalid checksum for SSN: {ssn}")
                result.score = 0.0  # Invalid SSN
        return results

    def _is_valid_checksum(self, ssn: str) -> bool:
        """
        Validate the checksum for the given Spanish SSN.
        The last two digits in the SSN represent the checksum.
        """
        logger.debug(f"Validating checksum for SSN: {ssn}")

        # Remove any non-numeric characters
        ssn_digits = re.sub(r"\D", "", ssn)
        logger.debug(f"SSN digits after removing non-numeric characters: {ssn_digits}")

        if len(ssn_digits) < 10:
            logger.error(f"SSN {ssn} does not contain enough digits for checksum validation.")
            return False

        # Extract the base number (first part) and the checksum (last two digits)
        base_number = ssn_digits[:-2]
        checksum = ssn_digits[-2:]
        logger.debug(f"Base number: {base_number}, Provided checksum: {checksum}")

        # Calculate expected checksum
        calculated_checksum = str(int(base_number) % 97).zfill(2)
        logger.debug(f"Calculated checksum: {calculated_checksum}")

        # Check if calculated checksum matches the provided checksum
        is_valid = checksum == calculated_checksum
        if is_valid:
            logger.info(f"Checksum for SSN {ssn} is valid.")
        else:
            logger.error(f"Checksum for SSN {ssn} is invalid. Expected {calculated_checksum}, but got {checksum}.")
        return is_valid
