from typing import Optional, List
from presidio_analyzer import Pattern, PatternRecognizer, RecognizerResult
import logging
import re

logger = logging.getLogger("presidio-analyzer")

class SwedenIBANRecognizer(PatternRecognizer):
    logger.info("Initializing Sweden IBAN Recognizer...")

    # Define patterns for Sweden IBAN Numbers
    PATTERNS = [
        Pattern(
            "Sweden IBAN - Medium Confidence",
            r"\bSE\d{2}\d{3}\d{17}\b",  # Pattern for SE followed by 22 digits (2 check digits, 3 bank code, 17 account digits)
            0.5  # Medium confidence score for the pattern match
        )
    ]

    # Context keywords for IBAN
    CONTEXT = [
        "IBAN", "Sweden IBAN", "international bank account number", "bankkonto", "kontonummer", 
        "nummer IBAN", "IBAN nummer", "bank code", "bank identifier"
    ]

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "sv",  # Supports Swedish and English
        supported_entity: str = "SWEDEN_IBAN",
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
        logger.info(f"Analyzing text for Sweden IBAN: {text}")
        results = super().analyze(text, entities, nlp_artifacts)
        
        for result in results:
            iban_number = text[result.start:result.end]
            logger.debug(f"Detected IBAN: {iban_number}, Confidence: {result.score}")

            # Check if any IBAN-related terms exist in the nearby text
            nearby_text = text[max(0, result.start - 100):min(len(text), result.end + 100)]
            if any(keyword in nearby_text.lower() for keyword in self.CONTEXT):
                logger.info(f"Context keywords found near IBAN: {iban_number}, increasing confidence.")
                result.score = 1.0  # Increase confidence to high if context keywords are found
            else:
                result.score = 0.5  # Medium confidence for pattern match only
            
        return results
