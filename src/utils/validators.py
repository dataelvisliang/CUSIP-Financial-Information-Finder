"""Validation utilities for CUSIP pipeline"""
import re
from typing import Tuple


def validate_cusip(cusip: str) -> Tuple[bool, str]:
    """
    Validate CUSIP format

    Args:
        cusip: CUSIP string to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not cusip:
        return False, "CUSIP cannot be empty"

    cusip = cusip.strip().upper()

    if len(cusip) != 9:
        return False, f"CUSIP must be 9 characters (got {len(cusip)})"

    if not re.match(r'^[0-9A-Z]{9}$', cusip):
        return False, "CUSIP must contain only alphanumeric characters"

    if not re.match(r'^[0-9A-Z]{8}[0-9]$', cusip):
        return False, "CUSIP must have 8 alphanumeric characters followed by 1 digit"

    return True, ""


def format_cusip(cusip: str) -> str:
    """
    Format CUSIP to standard format

    Args:
        cusip: CUSIP string

    Returns:
        Formatted CUSIP
    """
    return cusip.strip().upper()
