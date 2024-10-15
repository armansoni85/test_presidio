import re
from presidio_analyzer import Pattern, PatternRecognizer, RecognizerResult
from typing import List, Optional, Dict

class AllCreditCardNumberRecognizer(PatternRecognizer):
    """
    Recognizer to detect various credit card numbers and validate using Luhn 10 algorithm.
    """

    # Patterns for detecting credit card numbers
    PATTERNS: Dict[str, List[Pattern]] = {
        'American Express': [
            Pattern(name="American Express (high)", regex=r'\b3[47]\d{2} \d{6} \d{5}\b', score=1.0),
            Pattern(name="American Express (high)", regex=r'\b3[47]\d{2}-\d{6}-\d{5}\b', score=1.0),
            Pattern(name="American Express (high)", regex=r'\b3[47]\d{13}\b', score=1.0),
            Pattern(name="American Express (medium_high)", regex=r'\b3[47]\d{2} \d{6} \d{5}\b', score=0.8),
            Pattern(name="American Express (medium)", regex=r'\b3[47]\d{2} \d{6} \d{5}\b', score=0.6),
        ],
        'China UnionPay': [
            Pattern(name="China UnionPay (high)", regex=r'\b622\d{13,16}\b', score=1.0),
            Pattern(name="China UnionPay (high)", regex=r'\b603601\d{10}\b', score=1.0),
            Pattern(name="China UnionPay (high)", regex=r'\b603265\d{10}\b', score=1.0),
            Pattern(name="China UnionPay (high)", regex=r'\b621977\d{10}\b', score=1.0),
            Pattern(name="China UnionPay (high)", regex=r'\b603708\d{10}\b', score=1.0),
            Pattern(name="China UnionPay (high)", regex=r'\b602969\d{10}\b', score=1.0),
            Pattern(name="China UnionPay (high)", regex=r'\b601428\d{10}\b', score=1.0),
            Pattern(name="China UnionPay (high)", regex=r'\b603367\d{10}\b', score=1.0),
            Pattern(name="China UnionPay (high)", regex=r'\b603694\d{10}\b', score=1.0),
        ],
        'Diner\'s Club': [
            Pattern(name="Diner's Club (high)", regex=r'\b30[0-5]\d-\d{6}-\d{4}\b', score=1.0),
            Pattern(name="Diner's Club (high)", regex=r'\b30[0-5]\d \d{6} \d{4}\b', score=1.0),
            Pattern(name="Diner's Club (high)", regex=r'\b30[0-5]\d{11}\b', score=1.0),
            Pattern(name="Diner's Club (high)", regex=r'\b3[689]\d{2}-\d{6}-\d{4}\b', score=1.0),
            Pattern(name="Diner's Club (high)", regex=r'\b3[689]\d{2} \d{6} \d{4}\b', score=1.0),
            Pattern(name="Diner's Club (high)", regex=r'\b3[689]\d{12}\b', score=1.0),
        ],
        'Discover': [
            Pattern(name="Discover (high)", regex=r'\b6011-\d{4}-\d{4}-\d{4}\b', score=1.0),
            Pattern(name="Discover (high)", regex=r'\b6011 \d{4} \d{4} \d{4}\b', score=1.0),
            Pattern(name="Discover (high)", regex=r'\b6011\d{12}\b', score=1.0),
            Pattern(name="Discover (high)", regex=r'\b64[4-9]\d-\d{4}-\d{4}-\d{4}\b', score=1.0),
            Pattern(name="Discover (high)", regex=r'\b64[4-9]\d \d{4} \d{4} \d{4}\b', score=1.0),
            Pattern(name="Discover (high)", regex=r'\b64[4-9]\d{13}\b', score=1.0),
            Pattern(name="Discover (high)", regex=r'\b65\d{2}-\d{4}-\d{4}-\d{4}\b', score=1.0),
            Pattern(name="Discover (high)", regex=r'\b65\d{2} \d{4} \d{4} \d{4}\b', score=1.0),
            Pattern(name="Discover (high)", regex=r'\b65\d{14}\b', score=1.0),
        ],
        'JCB': [
            Pattern(name="JCB (high)", regex=r'\b352[89]-\d{4}-\d{4}-\d{4}\b', score=1.0),
            Pattern(name="JCB (high)", regex=r'\b352[89] \d{4} \d{4} \d{4}\b', score=1.0),
            Pattern(name="JCB (high)", regex=r'\b352[89]\d{12}\b', score=1.0),
            Pattern(name="JCB (high)", regex=r'\b35[3-8]\d-\d{4}-\d{4}-\d{4}\b', score=1.0),
            Pattern(name="JCB (high)", regex=r'\b35[3-8]\d \d{4} \d{4} \d{4}\b', score=1.0),
            Pattern(name="JCB (high)", regex=r'\b35[3-8]\d{14}\b', score=1.0),
        ],
        'Kohl\'s': [
            Pattern(name="Kohl's (high)", regex=r'\b(4391|4392|4393|4394|4395|4396|4397|4398|4399)-\d{4}-\d{4}-\d{4}\b', score=1.0),
            Pattern(name="Kohl's (high)", regex=r'\b(4391|4392|4393|4394|4395|4396|4397|4398|4399) \d{4} \d{4} \d{4}\b', score=1.0),
            Pattern(name="Kohl's (high)", regex=r'\b(4391|4392|4393|4394|4395|4396|4397|4398|4399)\d{12}\b', score=1.0),
        ],
        'Mastercard': [
            Pattern(name="Mastercard (high)", regex=r'\b5[1-5]\d{4}-\d{4}-\d{4}-\d{4}\b', score=1.0),
            Pattern(name="Mastercard (high)", regex=r'\b5[1-5] \d{4} \d{4} \d{4}\b', score=1.0),
            Pattern(name="Mastercard (high)", regex=r'\b5[1-5]\d{15}\b', score=1.0),
            Pattern(name="Mastercard (high)", regex=r'\b2[2-7]\d{14}\b', score=1.0),
        ],
        'VISA': [
            Pattern(name="VISA (high)", regex=r'\b4\d{3}-\d{4}-\d{4}-\d{4}\b', score=1.0),
            Pattern(name="VISA (high)", regex=r'\b4\d{12}\d{4}\b', score=1.0),
            Pattern(name="VISA (medium_high)", regex=r'\b4\d{3} \d{4} \d{4} \d{4}\b', score=0.8),
            Pattern(name="VISA (medium)", regex=r'\b4\d{3} \d{4} \d{4}\b', score=0.6),
        ]
    }

    IGNORED_PATTERNS: Dict[str, List[str]] = {
        'American Express': [
            r'3400([- ]?)000000([- ]?)00009',
            r'3411([- ]?)111111([- ]?)11111',
            r'3434([- ]?)343434([- ]?)34343',
            r'3456([- ]?)789012([- ]?)34564',
            r'3456([- ]?)400000([- ]?)55123',
            r'3468([- ]?)276304([- ]?)35344',
            r'3700([- ]?)000000([ -]?)00002',
            r'3700([- ]?)002000([ -]?)00000',
            r'3704([- ]?)072699([ -]?)09809',
            r'3705([- ]?)560193([ -]?)09221',
            r'3714([- ]?)496353([ -]?)98431',
            r'3742([- ]?)000000([ -]?)00004',
            r'3756([- ]?)400000([ -]?)55123',
            r'3764([- ]?)622809([ -]?)21451',
            r'3777([- ]?)527498([ -]?)96404',
            r'3782([- ]?)822463([ -]?)10005',
            r'3787([- ]?)344936([ -]?)11827',
            r'3793([- ]?)123456([ -]?)78901',
        ],
        'China UnionPay': [
            r'6213([- ]?)145678([- ]?)90123',
            r'6214([- ]?)500123([- ]?)45678',
            r'6222([- ]?)000000([- ]?)00000',
            r'6222([- ]?)000000([- ]?)00001',
            r'6223([- ]?)040506([- ]?)07080',
            r'6224([- ]?)060708([- ]?)09010',
            r'6227([- ]?)890123([- ]?)45678',
            r'6230([- ]?)111111([- ]?)22222',
            r'6231([- ]?)233344([- ]?)55555',
            r'6250([- ]?)987654([- ]?)32100',
            r'6262([- ]?)222222([- ]?)22222',
            r'6263([- ]?)111111([- ]?)00000',
        ],
        'Diner\'s Club': [
            r'3000([- ]?)000000([- ]?)00004',
            r'3001([- ]?)111111([- ]?)11111',
            r'3050([- ]?)000000([- ]?)00000',
            r'3051([- ]?)555555([- ]?)55555',
            r'3052([- ]?)999999([- ]?)99999',
            r'3053([- ]?)123456([- ]?)78901',
            r'3054([- ]?)000000([- ]?)00000',
            r'3055([- ]?)654321([- ]?)09876',
            r'3056([- ]?)789012([- ]?)34567',
            r'3057([- ]?)890123([- ]?)45678',
            r'3058([- ]?)678901([- ]?)23456',
            r'3059([- ]?)456789([- ]?)12345',
            r'3060([- ]?)543210([- ]?)98765',
            r'3061([- ]?)234567([- ]?)89012',
            r'3062([- ]?)789012([- ]?)34567',
        ],
        'Discover': [
            r'6011([- ]?)0000([- ]?)0000([- ]?)0004',
            r'6011([- ]?)1111([- ]?)2222([- ]?)3333',
            r'6011([- ]?)3333([- ]?)4444([- ]?)5555',
            r'6011([- ]?)6666([- ]?)7777([- ]?)8888',
            r'6011([- ]?)0000([- ]?)1111([- ]?)2222',
            r'6011([- ]?)3333([- ]?)4444([- ]?)5555',
            r'6011([- ]?)6666([- ]?)7777([- ]?)8888',
            r'6011([- ]?)9999([- ]?)0000([- ]?)1111',
            r'6011([- ]?)2222([- ]?)3333([- ]?)4444',
            r'6011([- ]?)5555([- ]?)6666([- ]?)7777',
            r'6011([- ]?)8888([- ]?)9999([- ]?)0000',
        ],
        'JCB': [
            r'3528([- ]?)1234([- ]?)5678([- ]?)9012',
            r'3528([- ]?)2345([- ]?)6789([- ]?)0123',
            r'3528([- ]?)3456([- ]?)7890([- ]?)1234',
            r'3528([- ]?)4567([- ]?)8901([- ]?)2345',
            r'3528([- ]?)5678([- ]?)9012([- ]?)3456',
            r'3528([- ]?)6789([- ]?)0123([- ]?)4567',
            r'3528([- ]?)7890([- ]?)1234([- ]?)5678',
            r'3528([- ]?)8901([- ]?)2345([- ]?)6789',
            r'3528([- ]?)9012([- ]?)3456([- ]?)7890',
            r'3530([- ]?)1234([- ]?)5678([- ]?)9012',
            r'3530([- ]?)2345([- ]?)6789([- ]?)0123',
            r'3530([- ]?)3456([- ]?)7890([- ]?)1234',
        ],
        'Kohl\'s': [
            r'4391([- ]?)0000([- ]?)0000([- ]?)0000',
            r'4391([- ]?)1234([- ]?)5678([- ]?)9012',
            r'4391([- ]?)2345([- ]?)6789([- ]?)0123',
            r'4391([- ]?)3456([- ]?)7890([- ]?)1234',
            r'4391([- ]?)4567([- ]?)8901([- ]?)2345',
            r'4391([- ]?)5678([- ]?)9012([- ]?)3456',
            r'4391([- ]?)6789([- ]?)0123([- ]?)4567',
            r'4391([- ]?)7890([- ]?)1234([- ]?)5678',
            r'4391([- ]?)8901([- ]?)2345([- ]?)6789',
            r'4391([- ]?)9012([- ]?)3456([- ]?)7890',
        ],
        'Mastercard': [
            r'5111([- ]?)1111([- ]?)1111([- ]?)1111',
            r'5111([- ]?)2222([- ]?)3333([- ]?)4444',
            r'5111([- ]?)5555([- ]?)6666([- ]?)7777',
            r'5111([- ]?)8888([- ]?)9999([- ]?)0000',
            r'5111([- ]?)1111([- ]?)1111([- ]?)1111',
            r'5111([- ]?)0000([- ]?)0000([- ]?)0000',
            r'5111([- ]?)2222([- ]?)2222([- ]?)2222',
            r'5111([- ]?)3333([- ]?)3333([- ]?)3333',
            r'5111([- ]?)4444([- ]?)4444([- ]?)4444',
            r'5111([- ]?)5555([- ]?)5555([- ]?)5555',
        ],
    }

    CONTEXT_TERMS: List[str] = [
        'credit card', 'card number', 'CCN',
        'card verification', 'card identification number', 'cvn',
        'cid', 'cvc2', 'cvv2', 'pin block'
    ]

    def __init__(self, supported_language: Optional[str] = None):
        # Initialize the parent class with appropriate entity type and patterns
        patterns = [pattern for pattern_list in self.PATTERNS.values() for pattern in pattern_list]
        super().__init__(supported_entity="CREDIT_CARD", patterns=patterns, context=self.CONTEXT_TERMS, supported_language=supported_language)
        
        # Set ignored patterns for the recognizer
        self.ignored_patterns = [re.compile(pattern) for sublist in self.IGNORED_PATTERNS.values() for pattern in sublist]


    def analyze(self, text: str, entities: List[str], nlp_artifacts=None) -> List[RecognizerResult]:
        """
        Analyze text to detect credit card numbers using regex patterns and Luhn algorithm validation.
        
        :param text: The input text to analyze.
        :param entities: The entities to look for (e.g., 'CREDIT_CARD').
        :param nlp_artifacts: Additional NLP artifacts (unused here).
        :return: A list of RecognizerResult objects.
        """
        results = []
        for card_type, pattern_list in self.PATTERNS.items():
            for pattern in pattern_list:
                # Find all matches for the current pattern
                matches = re.finditer(pattern.regex, text)
                for match in matches:
                    start, end = match.start(), match.end()
                    matched_text = text[start:end]
                    if not self._is_ignored(card_type, matched_text) and self._is_valid_credit_card(matched_text):
                        results.append(RecognizerResult(entity_type="CREDIT_CARD", start=start, end=end, score=pattern.score))

        return results

    def _is_ignored(self, card_type: str, matched_text: str) -> bool:
        """
        Check if the matched text matches any of the ignored patterns for the given card type.
        
        :param card_type: The type of the credit card.
        :param matched_text: The matched credit card number.
        :return: True if the matched text should be ignored; False otherwise.
        """
        if card_type in self.IGNORED_PATTERNS:
            for ignored_pattern in self.IGNORED_PATTERNS[card_type]:
                if re.fullmatch(ignored_pattern, matched_text):
                    return True
        return False

    def _is_valid_credit_card(self, card_number: str) -> bool:
        """
        Validate the credit card number using the Luhn algorithm.
        
        :param card_number: The credit card number to validate.
        :return: True if valid; False otherwise.
        """
        # Remove spaces and dashes
        card_number = re.sub(r"[\s-]", "", card_number)
        if not card_number.isdigit():
            return False
        
        # Implement Luhn algorithm
        sum_digits = 0
        num_digits = len(card_number)
        odd_even = num_digits & 1

        for count in range(num_digits):
            digit = int(card_number[count])
            if not ((count & 1) ^ odd_even):
                digit = digit * 2
            if digit > 9:
                digit = digit - 9
            sum_digits += digit
        
        return (sum_digits % 10) == 0