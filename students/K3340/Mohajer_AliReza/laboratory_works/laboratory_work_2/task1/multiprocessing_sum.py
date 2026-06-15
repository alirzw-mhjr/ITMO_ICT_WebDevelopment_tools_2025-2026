"""Задача 1. Подсчёт суммы чисел с помощью multiprocessing.

Сумма всех чисел от 1 до N разбивается на несколько диапазонов, каждый из
которых обсчитывается в отдельном процессе (multiprocessing). У каждого
процесса свой интерпретатор Python и свой GIL, поэтому вычисления реально
выполняются параллельно на разных ядрах процессора. На CPU-bound задаче это
даёт настоящее ускорение, ограниченное числом физических ядер.
"""

from __future__ import annotations

import multiprocessing
import time

TARGET = 10_000_000_000_000  # 10^13
PROCESSES = 4


def calculate_sum(bounds: tuple[int, int]) -> int:
    """Считает сумму целых чисел на отрезке [start, end]."""
    start, end = bounds
    total = 0
    for number in range(start, end + 1):
        total += number
    return total


def run(n: int = TARGET, workers: int = PROCESSES) -> tuple[int, float]:
    """Запускает подсчёт суммы 1..n в `workers` процессах. Возвращает (сумма, время)."""
    chunk = n // workers
    ranges: list[tuple[int, int]] = []
    for i in range(workers):
        start = i * chunk + 1
        end = n if i == workers - 1 else (i + 1) * chunk
        ranges.append((start, end))

    start_time = time.perf_counter()
    with multiprocessing.Pool(processes=workers) as pool:
        partials = pool.map(calculate_sum, ranges)
    total = sum(partials)
    elapsed = time.perf_counter() - start_time
    return total, elapsed


if __name__ == "__main__":
    total, elapsed = run()
    print(f"[multiprocessing] процессов: {PROCESSES}")
    print(f"[multiprocessing] сумма 1..{TARGET} = {total}")
    print(f"[multiprocessing] время выполнения: {elapsed:.4f} c")
