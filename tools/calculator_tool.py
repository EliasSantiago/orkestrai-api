"""
Calculator Tool - Shared tool for mathematical calculations.

This tool can be used by any agent to perform calculations.
"""

import math
import re


def calculator(expression: str) -> dict:
    """
    Calculates a mathematical expression safely.
    
    Args:
        expression: Mathematical expression as a string (e.g., "25 * 4 + 10")
        
    Returns:
        dict with 'result' (float) and 'expression' (str)
        
    Example:
        >>> calculator("25 * 4 + 10")
        {'result': 110.0, 'expression': '25 * 4 + 10', 'status': 'success'}
    """
    try:
        # Remove espaços e valida entrada
        expression = expression.strip()
        
        # Sanitiza a expressão - permite apenas números, operadores e parênteses
        if not re.match(r'^[0-9+\-*/().\s]+$', expression):
            return {
                'status': 'error',
                'error': 'Expressão inválida. Use apenas números e operadores básicos (+, -, *, /, parênteses)',
                'expression': expression
            }
        
        # Avalia a expressão de forma segura
        # Usa eval com namespace limitado apenas a funções matemáticas seguras
        safe_dict = {
            "__builtins__": {},
            "abs": abs,
            "round": round,
            "min": min,
            "max": max,
            "sum": sum,
            "pow": pow,
            "math": math,
        }
        
        result = eval(expression, safe_dict)
        
        return {
            'status': 'success',
            'result': float(result),
            'expression': expression
        }
    
    except ZeroDivisionError:
        return {
            'status': 'error',
            'error': 'Divisão por zero não é permitida',
            'expression': expression
        }
    except Exception as e:
        return {
            'status': 'error',
            'error': f'Erro ao calcular: {str(e)}',
            'expression': expression
        }

