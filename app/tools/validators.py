from functools import wraps
from typing import Callable
import time

# Rate limiting storage
rate_limit_store = {}

def require_verification(func: Callable) -> Callable:
    """
    Decorator to ensure identity verification before sensitive operations
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Check if customer_id is verified in session
        # This is a simplified version - in production, use proper session management
        customer_id = kwargs.get('customer_id') or (args[0] if args else None)
        
        if not customer_id:
            raise ValueError("Customer ID required for this operation")
        
        # In a real app, check session/token for verification status
        # For now, we assume verification is handled by the agent
        return func(*args, **kwargs)
    
    return wrapper

def rate_limit(max_calls: int = 5, time_window: int = 60):
    """
    Rate limiting decorator to prevent abuse
    max_calls: Maximum number of calls allowed
    time_window: Time window in seconds
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            customer_id = kwargs.get('customer_id') or (args[0] if args else None)
            
            if not customer_id:
                return func(*args, **kwargs)
            
            current_time = time.time()
            key = f"{func.__name__}:{customer_id}"
            
            if key not in rate_limit_store:
                rate_limit_store[key] = []
            
            # Remove old timestamps outside the time window
            rate_limit_store[key] = [
                ts for ts in rate_limit_store[key] 
                if current_time - ts < time_window
            ]
            
            # Check if rate limit exceeded
            if len(rate_limit_store[key]) >= max_calls:
                raise Exception(f"Rate limit exceeded. Please try again later.")
            
            # Add current timestamp
            rate_limit_store[key].append(current_time)
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator

def confirm_irreversible_action(action_name: str) -> Callable:
    """
    Decorator for irreversible actions that require extra confirmation
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # In production, this would require explicit user confirmation
            # For now, we log the action as critical
            print(f"[CRITICAL ACTION] {action_name} - Requires confirmation")
            result = func(*args, **kwargs)
            print(f"[CRITICAL ACTION] {action_name} - Completed")
            return result
        
        return wrapper
    return decorator

class SecurityValidator:
    """Security validation utilities"""
    
    @staticmethod
    def validate_pin(pin: str) -> bool:
        """Validate PIN format"""
        return pin.isdigit() and len(pin) == 4
    
    @staticmethod
    def validate_customer_id(customer_id: str) -> bool:
        """Validate customer ID format"""
        return customer_id.startswith("CUST") and len(customer_id) == 8
    
    @staticmethod
    def sanitize_input(text: str) -> str:
        """Sanitize user input to prevent injection attacks"""
        # Basic sanitization - in production, use proper libraries
        dangerous_chars = ['<', '>', '"', "'", ';', '--']
        for char in dangerous_chars:
            text = text.replace(char, '')
        return text.strip()
