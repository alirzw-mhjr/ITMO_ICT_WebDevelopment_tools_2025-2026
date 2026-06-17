# Задача 1. Подсчёт суммы чисел с помощью threading.

import threading
import time

TARGET = 10_000_000_000_000  # 10^13
THREADS = 4


def calculate_sum(start: int, end: int, results: list[int], index: int) -> None:
    """Считает сумму целых чисел на отрезке [start, end] и кладёт её в results."""
    total = 0
    for number in range(start, end + 1):
        total += number
    results[index] = total


def run(n: int = TARGET, workers: int = THREADS) -> tuple[int, float]:
    """Запускает подсчёт суммы 1..n в `workers` потоках. Возвращает (сумма, время)."""
    chunk = n // workers
    results = [0] * workers
    threads: list[threading.Thread] = []

    start_time = time.perf_counter()
    for i in range(workers):
        start = i * chunk + 1
        end = n if i == workers - 1 else (i + 1) * chunk
        thread = threading.Thread(target=calculate_sum, args=(start, end, results, i))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    total = sum(results)
    elapsed = time.perf_counter() - start_time
    return total, elapsed


if __name__ == "__main__":
    total, elapsed = run()
    print(f"[threading] потоков: {THREADS}")
    print(f"[threading] сумма 1..{TARGET} = {total}")
    print(f"[threading] время выполнения: {elapsed:.4f} c")
