# In a file called custom_filters.py

from django import template

register = template.Library()

@register.filter
def format_account_number(account_number):
    return ' '.join([account_number[i:i+4] for i in range(0, len(account_number), 4)])

@register.filter
def xaf_currency(number):
    """
    Format a number to XAF currency format.
    Example: 1000000 -> 1,000,000 XAF
    """
    formatted_number = "{:,.0f}".format(float(number))  # Format number with thousands separator
    return f"{formatted_number} XAF"

@register.filter
def starts_with(input_string, prefix):
    return input_string.startswith(prefix)
