from datetime import datetime


def get_reference() -> str:
    """
    Generate a unique reference ID for payment transactions

    Format: eT{YYMMDD}.{HHMMSS}.{microseconds}
    Example: eT251022.143025.123456

    Returns:
        str: Unique reference ID
    """
    reference = datetime.now().strftime("%y%m%d.%H%M%S.%f")
    return f"eT{reference}"


def convert_arzeka_payment_status(status):
    if status == "COMPLETED":
        return "completed"
    elif status == "PENDING":
        return "pending"
    elif status == "INCOMPLETE":
        return "failed"
    else:
        return "pending"
