from typing import Optional, List
from presidio_analyzer import Pattern, PatternRecognizer, RecognizerResult
import logging
import re

logger = logging.getLogger("presidio-analyzer")

class EUVATRecognizer(PatternRecognizer):
    logger.info("Initializing EU VAT Recognizer...")

    # Define patterns for VAT numbers used in different EU countries
    # This is a general pattern that can cover multiple VAT formats
    PATTERNS = [
        Pattern(
            "EU VAT - General Pattern",
            r"\b[A-Z]{2}[- ]?\d{8,12}\b",  # General pattern: 2-letter country code, optional space or hyphen, 8-12 digits
            0.5  # Initial confidence score for the pattern match
        )
    ]

    # Context keywords for VAT numbers in various EU countries
    CONTEXT = [
        "vat", "value added tax", "vat number", "vat identification", 
        "tva", "moms", "número de iva", "n° tva", "identificación de iva",
        "ustid", "btw", "iva", "mva"
    ]

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "en",  # Supports multiple languages for EU countries
        supported_entity: str = "EU_VAT",
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
        logger.info(f"Analyzing text for EU VAT: {text}")
        results = super().analyze(text, entities, nlp_artifacts)

        for result in results:
            vat_number = text[result.start:result.end]
            logger.debug(f"Detected VAT Number: {vat_number}, Confidence: {result.score}")

            # Check if any VAT-related terms are nearby
            nearby_text = text[max(0, result.start - 100):min(len(text), result.end + 100)]
            if any(keyword in nearby_text.lower() for keyword in self.CONTEXT):
                logger.info(f"Context keywords found near VAT Number: {vat_number}, setting high confidence.")
                result.score = 1.0  # High confidence if VAT keywords are within 100 characters
            else:
                result.score = 0.5  # Medium confidence if no keywords are found
            
        return results
