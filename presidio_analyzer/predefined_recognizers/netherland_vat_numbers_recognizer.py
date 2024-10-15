from presidio_analyzer import PatternRecognizer, Pattern, RecognizerResult
from typing import List, Optional
import re

class NetherlandsVATRecognizer(PatternRecognizer):
    # Define the pattern for Netherlands VAT numbers: 9 digits, 'B', and 3 digits (total 14 alphanumeric characters)
    PATTERNS = [
        Pattern("Netherlands VAT Number", r"\b\d{9}B\d{2}\b", 0.5)  # Medium confidence by default
    ]

    # Keywords related to Netherlands VAT numbers
    CONTEXT_KEYWORDS = [
        "btw", "vat number", "vat id", "Netherlands VAT", "BTW-nummer", "btw-id", 
        "btw nummer", "btw identificatienummer"
    ]

    def __init__(self, supported_language: Optional[str] = None):
        super().__init__(
            supported_entity="NETHERLANDS_VAT_NUMBER",
            supported_language=supported_language,
            patterns=self.PATTERNS,
            context=self.CONTEXT_KEYWORDS
        )

    def enhance_confidence(self, text: str, pattern_result: RecognizerResult) -> RecognizerResult:
        """
        Enhance confidence based on proximity to context keywords.
        """
        context_window = 50  # Number of characters before and after the detected VAT number
        start, end = pattern_result.start, pattern_result.end
        surrounding_text = text[max(0, start - context_window):min(len(text), end + context_window)].lower()

        # Check for context keywords
        context_present = any(keyword.lower() in surrounding_text for keyword in self.CONTEXT_KEYWORDS)

        # Adjust confidence based on the presence of context
        if context_present:
            pattern_result.score = 0.9  # High confidence if keywords are present
        else:
            pattern_result.score = 0.5  # Medium confidence if no keywords are present

        return pattern_result

    def validate_checksum(self, vat_number: str) -> bool:
        """
        Validate the first 9 digits of the Netherlands VAT number using the Modulus 11 checksum.
        """
        if len(vat_number) != 14 or vat_number[9] != 'B':
            return False
        
        digits = vat_number[:9]
        if not digits.isdigit():
            return False
        
        # Perform Modulus 11 checksum validation on the first 9 digits
        total_sum = 0
        for index, digit in enumerate(digits):
            total_sum += int(digit) * (9 - index)  # Multiply by position weight (9, 8, ..., 1)

        checksum_valid = total_sum % 11 == 0
        return checksum_valid

    def analyze(self, text: str, entities: List[str], nlp_artifacts=None) -> List[RecognizerResult]:
        """
        Override the analyze method to enhance results with contextual information and checksum validation.
        """
        results = super().analyze(text, entities, nlp_artifacts)

        # Iterate over results and apply checksum validation and confidence enhancement
        enhanced_results = []
        for result in results:
            vat_number = text[result.start:result.end]
            
            if self.validate_checksum(vat_number):
                result = self.enhance_confidence(text, result)
            else:
                result.score = 0.0  # Invalid VAT number due to failed checksum
            
            enhanced_results.append(result)

        return enhanced_results
