import random
import time
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import wraps
from multiprocessing import Pool, Process, Queue, cpu_count

WORKERS = cpu_count()


def timer(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__} выполнилась за {end - start:.4f} секунд")

        return result

    return wrapper


def generate_data(n: int) -> list[int]:
    return [random.randint(10000000, 99) for _ in range(n)]


def process_number(number: int) -> int:
    if number < 2:
        return 1
    return number * process_number(number - 1)


@timer
def process_with_threads(data: list[int], max_workers=WORKERS) -> list[int]:
    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(process_number, num) for num in data]
        for future in as_completed(futures):
            results.append(future.result())
    return results


@timer
def process_with_pool(data: list[int], max_workers=WORKERS) -> list[int]:
    with Pool(processes=max_workers) as pool:
        return pool.map(process_number, data)


def worker(input_queue: Queue, output_queue: Queue) -> None:
    while True:
        num = input_queue.get()
        if num is None:
            break
        result = process_number(num)
        output_queue.put((num, result))


@timer
def process_with_processes(data: list[int]) -> list[int]:
    input_queue = Queue()
    output_queue = Queue()

    workers = WORKERS
    processes = []

    for _ in range(workers):
        p = Process(target=worker, args=(input_queue, output_queue))
        p.start()
        processes.append(p)

    for number in data:
        input_queue.put(number)

    for _ in range(workers):
        input_queue.put(None)

    results = []
    for _ in range(len(data)):
        results.append(output_queue.get())

    for p in processes:
        p.join()

    return [res for _, res in results]


if __name__ == "__main__":
    data = generate_data(1000)

    results_threads = process_with_threads(data)
    results_pool = process_with_pool(data)
    results_queue = process_with_processes(data)
    print(results_queue)
