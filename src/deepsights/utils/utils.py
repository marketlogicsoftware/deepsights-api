import concurrent.futures


##############################################
def run_in_parallel(fun, args, max_workers=5):
    """
    Executes the given function in parallel using multiple threads.

    Args:
        fun (callable): The function to be executed in parallel.
        args (iterable): The arguments to be passed to the function.
        max_workers (int, optional): The maximum number of worker threads to use. Defaults to 5.

    Returns:
        list: A list of results returned by the function for each argument.
    """
    results = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_arg = {executor.submit(fun, arg): arg for arg in args}
        for future in concurrent.futures.as_completed(future_to_arg):
            results.append(future.result())

    return results
