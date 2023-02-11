from functools import wraps
import time
from typing import Callable, Any


def async_timed():
    
    def wrapper(func: Callable) -> Callable:
        
        @wraps(func)  # for save name of function
        async def wrapped(*args, **kwargs) -> Any:
            
            start = time.time()
            try:
                return await func(*args, **kwargs)
            
            finally:
                total = round(time.time() - start, 3)
                print(f'Work duration:\t{total} s.')
                
        return wrapped
    
    return wrapper
