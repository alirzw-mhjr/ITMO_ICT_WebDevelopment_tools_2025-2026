# Задача 1. Подсчёт суммы чисел с помощью async/await (asyncio).
import asyncio
import time

TARGET = 10_000_000_000_000  # 10^13
TASKS = 4


async def calculate_sum(start: int, end: int) -> int:
    """Корутина: считает сумму целых чисел на отрезке [start, end]."""
    total = 0
    for number in range(start, end + 1):
        total += number
    return total


async def run(n: int = TARGET, workers: int = TASKS) -> tuple[int, float]:
    """Запускает подсчёт суммы 1..n в `workers` корутинах. Возвращает (сумма, время)."""
    chunk = n // workers
    coros = []
    for i in range(workers):
        start = i * chunk + 1
        end = n if i == workers - 1 else (i + 1) * chunk
        coros.append(calculate_sum(start, end))

    start_time = time.perf_counter()
    partials = await asyncio.gather(*coros)
    total = sum(partials)
    elapsed = time.perf_counter() - start_time
    return total, elapsed


if __name__ == "__main__":
    total, elapsed = asyncio.run(run())
    print(f"[async] корутин: {TASKS}")
    print(f"[async] сумма 1..{TARGET} = {total}")
    print(f"[async] время выполнения: {elapsed:.4f} c")
