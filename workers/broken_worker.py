def intentionally_broken_function():
    print("Initiating Live-Fire Sequence...")
    # This will trigger a NameError
    result = 100 / this_variable_does_not_exist
    return result
