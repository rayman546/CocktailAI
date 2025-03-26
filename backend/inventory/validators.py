"""
Custom validators for inventory models.
"""

from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from datetime import date, datetime, time
import re


def no_future_date_validator(value):
    """
    Validates that a date is not in the future.
    
    Args:
        value: The date or datetime to validate
        
    Raises:
        ValidationError: If the date is in the future
    """
    if not value:
        return
        
    today = timezone.now().date()
    
    # If value is a datetime, convert it to date
    if isinstance(value, datetime):
        value = value.date()
        
    if value > today:
        raise ValidationError(
            _('%(value)s is in the future. This field cannot accept future dates.'),
            params={'value': value},
        )


def date_not_before_validator(base_date_field):
    """
    Returns a validator that validates a date is not before the specified field.
    
    Args:
        base_date_field: The name of the field to compare against
        
    Returns:
        A validator function
    """
    def validate(value, instance):
        if not value:
            return
            
        base_date = getattr(instance, base_date_field, None)
        if not base_date:
            return
            
        # Convert datetime to date if needed
        if isinstance(value, datetime):
            value = value.date()
        if isinstance(base_date, datetime):
            base_date = base_date.date()
            
        if value < base_date:
            raise ValidationError(
                _('%(value)s cannot be before %(base_date)s.'),
                params={'value': value, 'base_date': base_date},
            )
            
    return validate


def date_before_today_validator(value):
    """
    Validates that a date is before or equal to today.
    
    Args:
        value: The date or datetime to validate
        
    Raises:
        ValidationError: If the date is after today
    """
    if not value:
        return
        
    today = timezone.now().date()
    
    # If value is a datetime, convert it to date
    if isinstance(value, datetime):
        value = value.date()
        
    if value > today:
        raise ValidationError(
            _('%(value)s is after today. This field must be today or earlier.'),
            params={'value': value},
        )


def phone_number_validator(value):
    """
    Validates that a string is a valid phone number.
    Accepts formats with optional country code, optional parentheses, optional hyphens or spaces.
    
    Args:
        value: The phone number string to validate
        
    Raises:
        ValidationError: If the phone number is not valid
    """
    if not value:
        return
    
    # Remove all non-digit characters for counting
    digits = re.sub(r'\D', '', value)
    
    # Check if we have a reasonable number of digits (7-15 covers most international formats)
    if len(digits) < 7 or len(digits) > 15:
        raise ValidationError(
            _('%(value)s is not a valid phone number. Must have between 7 and 15 digits.'),
            params={'value': value},
        )
    
    # Validate common formats: international, US/CA, or other local
    pattern = r'^(\+\d{1,3}[\s.-]?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}$'
    if not re.match(pattern, value):
        raise ValidationError(
            _('%(value)s is not a valid phone number format.'),
            params={'value': value},
        )


def currency_validator(min_value=0, max_value=None):
    """
    Returns a validator that validates a decimal field is within the specific range for currency.
    
    Args:
        min_value: Minimum allowed value (default: 0)
        max_value: Maximum allowed value (optional)
        
    Returns:
        A validator function
    """
    def validate(value):
        if value is None:
            return
            
        if value < min_value:
            raise ValidationError(
                _('Value cannot be less than %(min)s.'),
                params={'min': min_value},
            )
            
        if max_value is not None and value > max_value:
            raise ValidationError(
                _('Value cannot be greater than %(max)s.'),
                params={'max': max_value},
            )
    
    return validate


def non_negative_decimal_validator(value):
    """
    Validates that a decimal value is not negative.
    
    Args:
        value: The decimal value to validate
        
    Raises:
        ValidationError: If the value is negative
    """
    if value is None:
        return
        
    if value < 0:
        raise ValidationError(
            _('%(value)s cannot be negative.'),
            params={'value': value},
        )


def email_validator(value):
    """
    Validates that a string is a valid email address.
    
    Args:
        value: The email string to validate
        
    Raises:
        ValidationError: If the email is not valid
    """
    if not value:
        return
        
    # Simple regex for email validation
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, value):
        raise ValidationError(
            _('%(value)s is not a valid email address.'),
            params={'value': value},
        ) 