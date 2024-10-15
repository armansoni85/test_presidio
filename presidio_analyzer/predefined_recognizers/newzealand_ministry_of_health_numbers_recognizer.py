from typing import Optional, List
from presidio_analyzer import Pattern, PatternRecognizer, RecognizerResult
import logging
import re

logger = logging.getLogger("presidio-analyzer")

class NewZealandHealthNumberRecognizer(PatternRecognizer):
    # Define patterns for both old and new formats
    PATTERNS = [
        # Old format: 3 letters (A-H, J-N, P-Z) + 4 digits
        Pattern(
            "NZ Health Number - Old Format", 
            r"\b[A-HJ-NP-Z]{3}\d{4}\b",  # Regex for old format (3 letters + 4 digits)
            0.5  # Medium confidence base score
        ),
        # New format: 3 letters (A-H, J-N, P-Z) + 2 digits + 1 letter + 1 digit
        Pattern(
            "NZ Health Number - New Format", 
            r"\b[A-HJ-NP-Z]{3}\d{2}[A-HJ-NP-Z]\d\b",  # Regex for new format (3 letters + 2 digits + 1 letter + 1 digit)
            0.5  # Medium confidence base score
        )
    ]

    # Context keywords for health numbers
    CONTEXT = ["health number", "nhi number", "nhi", "ministry of health", "new zealand health number", "nz health number", "health id", "medical number", "medical record", "health system", "national health identifier"]

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "en",
        supported_entity: str = "NZ_Health_Number",
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
        logger.info(f"Analyzing text for New Zealand Health Number: {text}")
        results = super().analyze(text, entities, nlp_artifacts)
        
        for result in results:
            number = text[result.start:result.end]
            logger.debug(f"Detected Health Number: {number}")
            if self._is_valid_checksum(number):
                logger.info(f"Checksum valid for health number: {number}")
                result.score = 0.7  # Medium confidence if checksum passes
                if any(keyword in text.lower() for keyword in self.CONTEXT):
                    logger.info(f"Context keywords found for health number: {number}, setting high confidence.")
                    result.score = 1.0  # High confidence if context keywords are present
            else:
                logger.warning(f"Invalid checksum for health number: {number}")
                result.score = 0.0  # Invalid number due to checksum failure

        return results

    def _is_valid_checksum(self, number: str) -> bool:
        """
        Validate the checksum for the given health number using Modulus 11.
        The validation works for both old and new formats.
        Reference: https://en.wikipedia.org/wiki/NHI_Number
        """
        logger.debug(f"Validating checksum for health number: {number}")
        weights = [7, 6, 5, 4, 3, 2]  # Modulus 11 weights for the first 6 digits
        letters_to_digits = {chr(i): i - 55 for i in range(65, 91) if chr(i) not in ['I', 'O']}  # A-Z to 1-9 mapping

        try:
            # OLD format: ABC1234 -> ABC are letters, 1234 are digits
            # NEW format: DEF12G7 -> DEF are letters, 12 are digits, G is a letter, 7 is a digit
            if len(number) == 7:  # Old format
                logger.debug("Old format detected")
                digits = [letters_to_digits[char.upper()] for char in number[:3]]  # Convert the first 3 letters
                digits += [int(digit) for digit in number[3:7]]  # Add the last 4 digits
            
            elif len(number) == 8:  # New format
                logger.debug("New format detected")
                digits = [letters_to_digits[char.upper()] for char in number[:3]]  # Convert the first 3 letters
                digits += [int(digit) for digit in number[3:5]]  # Add the 2 digits
                digits.append(letters_to_digits[number[5].upper()])  # Convert the letter to a digit
                digits.append(int(number[6]))  # Add the last check digit
            
            else:
                logger.error(f"Invalid format length for number: {number}")
                return False

            logger.debug(f"Digits after conversion: {digits}")

            # Calculate the weighted sum of the digits
            total_sum = sum(d * w for d, w in zip(digits[:6], weights))
            logger.debug(f"Total sum for checksum: {total_sum}")

            # Calculate Modulus 11
            check_digit = digits[6]  # The last digit is the check digit
            return (total_sum + check_digit) % 11 == 0  # Modulus 11 check

        except (KeyError, ValueError) as e:
            logger.error(f"Failed to calculate checksum for number: {number}, error: {e}")
            return False
