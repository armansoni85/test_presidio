from typing import Optional, List
from presidio_analyzer import Pattern, PatternRecognizer, RecognizerResult
import logging
import re

logger = logging.getLogger("presidio-analyzer")

class CanadaPIPEDARecognizer(PatternRecognizer):
    logger.info("Initializing Canada PIPEDA Recognizer...")

    # Define patterns for Canada SIN (used as PIPEDA)
    PATTERNS = [
        Pattern(
            "Canada PIPEDA - SIN Pattern",
            r"\b\d{3}-\d{3}-\d{3}\b",  # Pattern for Canada SIN formatted as 3 digits-3 digits-3 digits
            0.7  # Initial confidence score for the pattern match
        ),
        Pattern(
            "Canada PIPEDA - Unformatted SIN Pattern",
            r"\b\d{9}\b",  # Pattern for unformatted SIN (9 digits)
            0.6  # Medium confidence for unformatted SIN
        )
    ]

    # Context keywords for PIPEDA-related terms
    CONTEXT = [
        "pipeda", "personal information", "personal data", "protection", "electronic documents", "privacy"
    ]

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "en",  # Supports English
        supported_entity: str = "CANADA_PIPEDA",
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
        logger.info(f"Analyzing text for Canada PIPEDA: {text}")
        results = super().analyze(text, entities, nlp_artifacts)

        for result in results:
            pipeda_number = text[result.start:result.end]
            logger.debug(f"Detected PIPEDA Number: {pipeda_number}, Confidence: {result.score}")

            # Check if any PIPEDA-related terms are nearby
            nearby_text = text[max(0, result.start - 100):min(len(text), result.end + 100)].lower()
            if any(keyword in nearby_text for keyword in self.CONTEXT):
                logger.info(f"Context keywords found near PIPEDA Number: {pipeda_number}, increasing confidence.")
                result.score = 1.0  # High confidence if PIPEDA context found
            else:
                result.score = 0.7  # Medium confidence for pattern match only
            
        return results
