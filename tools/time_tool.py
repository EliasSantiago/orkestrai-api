"""
Time Tool - Shared tool for time-related operations.

This tool can be used by any agent to get current time information.
"""

from datetime import datetime
import pytz


def get_current_time(timezone: str) -> dict:
    """
    Returns the current time in the specified timezone.
    
    Args:
        timezone: Timezone name (required)
                 Examples: "America/Sao_Paulo", "UTC", "America/New_York"
                 If not provided, defaults to "America/Sao_Paulo"
        
    Returns:
        dict with current time information
        
    Example:
        >>> get_current_time("America/Sao_Paulo")
        {'timezone': 'America/Sao_Paulo', 'time': '2024-11-04 00:30:00', 'status': 'success'}
    """
    try:
        # Use default timezone if empty string or None
        if not timezone or timezone.strip() == "":
            timezone = "America/Sao_Paulo"
        
        # Obtém o timezone
        tz = pytz.timezone(timezone)
        
        # Obtém a hora atual no timezone especificado
        current_time = datetime.now(tz)
        
        # Formata a hora
        formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
        formatted_time_12h = current_time.strftime("%I:%M %p")
        
        return {
            'status': 'success',
            'timezone': timezone,
            'time': formatted_time,
            'time_12h': formatted_time_12h,
            'day_of_week': current_time.strftime("%A"),
            'date': current_time.strftime("%Y-%m-%d"),
        }
    
    except pytz.exceptions.UnknownTimeZoneError:
        return {
            'status': 'error',
            'error': f'Timezone "{timezone}" não encontrado',
            'available_timezones': 'Use timezones como "America/Sao_Paulo", "UTC", "America/New_York"'
        }
    except Exception as e:
        return {
            'status': 'error',
            'error': f'Erro ao obter hora: {str(e)}'
        }

