'''Phone number normalization, shared between forms.py and the data
migration that standardizes existing records (see migrations/0015_*).
Kept dependency-free (no model imports) so the migration can import it
safely.'''

import re

US_PHONE_DIGITS = 10


def normalize_us_phone(raw):
    '''"555.123.4567" / "15551234567" / "(555) 123-4567" -> "(555) 123-4567".
    Raises ValueError if the text doesn't reduce to a 10-digit US number.'''
    digits = re.sub(r'\D', '', raw or '')
    if len(digits) == 11 and digits.startswith('1'):
        digits = digits[1:]
    if len(digits) != US_PHONE_DIGITS:
        raise ValueError('Enter a 10-digit US phone number.')
    return f'({digits[0:3]}) {digits[3:6]}-{digits[6:10]}'
