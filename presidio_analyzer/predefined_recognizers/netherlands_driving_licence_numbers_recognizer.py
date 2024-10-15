from typing import Optional, List
from presidio_analyzer import Pattern, PatternRecognizer, RecognizerResult
import logging

logger = logging.getLogger("presidio-analyzer")

class NetherlandsDriversLicenseRecognizer(PatternRecognizer):
    logger.info("Initializing Netherlands Driver's License Recognizer...")

    # Define patterns for Netherlands Driver's License Numbers (10 digits without spaces or delimiters)
    PATTERNS = [
        Pattern(
            "Netherlands Driver's License - High Confidence",
            r"\b\d{10}\b",  # Pattern for exactly 10 digits
            0.7  # Initial confidence score for the pattern match
        )
    ]

    # Context keywords for driver's license
    CONTEXT = [
        "rijbewijs", "driver's license", "licentienummer", "license number", 
        "drivers license", "nummer rijbewijs"
    ]

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "nl",  # Supports Dutch and English
        supported_entity: str = "NETHERLANDS_DRIVERS_LICENSE",
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
        logger.info(f"Analyzing text for Netherlands Driver's License: {text}")
        results = super().analyze(text, entities, nlp_artifacts)
        for result in results:
            license_number = text[result.start:result.end]
            logger.debug(f"Detected Driver's License Number: {license_number}, Confidence: {result.score}")
            # Adjust confidence based on context keywords
            if any(keyword in text.lower() for keyword in self.CONTEXT):
                logger.info(f"Context keywords found for Driver's License: {license_number}, setting high confidence.")
                result.score = 1.0  # High confidence if context keywords are present
            return results
