from __future__ import annotations

import asyncio

import async_sum
import multiprocessing_sum
import threading_sum

N = 100_000_000  # 10^8
WORKERS = 4


def main() -> None:
    print(f"Подсчёт суммы 1..{N:,} ({WORKERS} подзадачи)".replace(",", " "))
    print("Выполняется ...\n")

    # Каждый подход возвращает (сумма, время).
    results: list[tuple[str, int, float]] = []

    total, elapsed = threading_sum.run(N, WORKERS)
    results.append(("threading", total, elapsed))

    total, elapsed = multiprocessing_sum.run(N, WORKERS)
    results.append(("multiprocessing", total, elapsed))

    total, elapsed = asyncio.run(async_sum.run(N, WORKERS))
    results.append(("async", total, elapsed))

    # Базовое время — threading, относительно него считаем ускорение.
    base_time = next(t for name, _, t in results if name == "threading")

    header = f"| {'Подход':<16} | {'Время, с':>10} | {'Сумма':>21} |"
    sep = "|" + "-" * 18 + "|" + "-" * 12 + "|" + "-" * 23 + "|"
    print(header)
    print(sep)
    for name, total, elapsed in results:
        print(f"| {name:<16} | {elapsed:>10.4f} | {total:>20,} |".replace(",", " "))

    fastest = min(results, key=lambda r: r[2])
    print(f"\nСамый быстрый подход: {fastest[0]} ({fastest[2]:.4f} c)")


if __name__ == "__main__":
    # Защита __main__ обязательна для multiprocessing на Windows.
    main()
