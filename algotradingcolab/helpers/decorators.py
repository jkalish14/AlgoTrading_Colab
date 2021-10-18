from timeit import default_timer as timer
import functools

def time_func_execution(func):
    def wrapper(*args, **kwargs):
        start_point = timer()
        __return_value = func(*args, **kwargs)
        end_point = timer()
        print(f"{func.__name__} took {end_point - start_point} seconds to run")
        return __return_value

    return wrapper
    
