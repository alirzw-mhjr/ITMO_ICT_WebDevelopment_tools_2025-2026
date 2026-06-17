# Задача 2. Сравнение всех трёх подходов парсинга в одной таблице.


from __future__ import annotations

import asyncio

import async_parser
import multiprocessing_parser
import threading_parser
from parser_utils import load_urls


def _run_quiet(func) -> float:
    # Выполняет func, подавляя её печать, и возвращает результат (время)
    return func()


def main() -> None:
    url_count = len(load_urls())
    print(f"Парсинг {url_count} URL тремя способами. Выполняется, подождите...\n")

    results: list[tuple[str, float]] = []

    # threading и multiprocessing возвращают время напрямую.
    results.append(("threading", _run_quiet(threading_parser.run)))
    results.append(("multiprocessing", _run_quiet(multiprocessing_parser.run)))
    # async.run — корутина, запускаем через asyncio.run.
    results.append(("async", _run_quiet(lambda: asyncio.run(async_parser.run()))))

    # Базовое время — threading, относительно него считаем ускорение.
    base_time = next(t for name, t in results if name == "threading")

    header = f"| {'Подход':<16} | {'Время, с':>10} | {'Ускорение':>10} | {'URL':>5} |"
    sep = "|" + "-" * 18 + "|" + "-" * 12 + "|" + "-" * 12 + "|" + "-" * 7 + "|"
    print(header)
    print(sep)
    for name, elapsed in results:
        speedup = base_time / elapsed if elapsed else float("inf")
        print(f"| {name:<16} | {elapsed:>10.4f} | {speedup:>9.2f}x | {url_count:>5} |")

    fastest = min(results, key=lambda r: r[1])
    print(f"\nСамый быстрый подход: {fastest[0]} ({fastest[1]:.4f} c)")


if __name__ == "__main__":
    main()
