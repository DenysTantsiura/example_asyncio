from functools import wraps
import time
from typing import Callable, Any


def async_timed():
    
    def wrapper(func: Callable) -> Callable:
        
        @wraps(func)
        async def wrapped(*args, **kwargs) -> Any:
            
            start = time.time()
            try:
                return await func(*args, **kwargs)
            
            finally:
                total = time.time() - start
                print(f'{total=} s.')
                
        return wrapped
    
    return wrapper
