import asyncio

from mtgprices.errors import FetchError
from mtgprices.jobs import JobManager, JobStatus
from mtgprices.repository import KEEP_FINISHED_JOBS


def run_job(repo, worker, payloads, errors=(), concurrency=3):
    async def run():
        manager = JobManager(repo, concurrency=concurrency)
        manager.register("test", worker)
        job_id = manager.start("test", "Тест", payloads, errors)
        await manager.wait_all()
        return manager.get(job_id)

    return asyncio.run(run())


def test_job_counts_successes_and_errors(repo):
    async def worker(item):
        await asyncio.sleep(0)
        if item % 3 == 0:
            raise FetchError(f"bad {item}")
        if item == 4:
            raise RuntimeError("unexpected")

    job = run_job(repo, worker, list(range(1, 10)), errors=["строка 1: мусор"])
    assert job.status == JobStatus.FINISHED
    assert (job.total, job.done, job.succeeded) == (10, 10, 5)
    assert job.errors == ["строка 1: мусор", "bad 3", "Внутренняя ошибка при обработке 4", "bad 6", "bad 9"]


def test_payloads_roundtrip_through_json(repo):
    seen = []

    async def worker(item):
        seen.append(item)

    run_job(repo, worker, [{"quantity": 2, "url": "https://x"}, 5])
    assert sorted(seen, key=str) == [5, {"quantity": 2, "url": "https://x"}]


def test_concurrency_limit(repo):
    active = 0
    peak = 0

    async def worker(item):
        nonlocal active, peak
        active += 1
        peak = max(peak, active)
        await asyncio.sleep(0.01)
        active -= 1

    run_job(repo, worker, list(range(10)), concurrency=2)
    assert peak == 2


def test_cancel_stops_remaining_items(repo):
    processed = []

    async def run():
        manager = JobManager(repo, concurrency=1)
        gate = asyncio.Event()

        async def worker(item):
            processed.append(item)
            await gate.wait()

        manager.register("test", worker)
        job_id = manager.start("test", "t", list(range(100)))
        while not processed:
            await asyncio.sleep(0)
        assert [job.id for job in manager.running()] == [job_id]
        manager.cancel(job_id)
        gate.set()
        await manager.wait_all()
        return manager, manager.get(job_id)

    manager, job = asyncio.run(run())
    assert job.status == JobStatus.CANCELLED
    assert (job.done, job.total) == (1, 100)
    assert processed == [0]
    assert manager.running() == []


def test_interrupted_job_resumes_after_restart(repo):
    """Остановка сервера посреди задачи: необработанные элементы продолжаются при следующем запуске."""
    first_run = []

    async def stop_midway():
        manager = JobManager(repo, concurrency=1)
        gate = asyncio.Event()

        async def worker(item):
            first_run.append(item)
            if item == 2:
                await gate.wait()  # «зависший» запрос в момент остановки

        manager.register("test", worker)
        job_id = manager.start("test", "t", [0, 1, 2, 3, 4])
        while 2 not in first_run:
            await asyncio.sleep(0)
        await manager.shutdown()
        return job_id

    job_id = asyncio.run(stop_midway())
    assert repo.get_job(job_id).status == JobStatus.RUNNING
    assert [seq for seq, _ in repo.pending_job_items(job_id)] == [2, 3, 4]

    second_run = []

    async def restart():
        manager = JobManager(repo)

        async def worker(item):
            second_run.append(item)

        manager.register("test", worker)
        assert manager.resume() == 1
        await manager.wait_all()
        return manager.get(job_id)

    job = asyncio.run(restart())
    assert sorted(second_run) == [2, 3, 4]
    assert (job.status, job.done, job.succeeded) == (JobStatus.FINISHED, 5, 5)


def test_resume_without_worker_cancels_job(repo):
    repo.create_job("old", "removed-kind", "t", [1], [])

    async def run():
        return JobManager(repo).resume()

    assert asyncio.run(run()) == 0
    assert repo.get_job("old").status == JobStatus.CANCELLED


def test_empty_job_finishes(repo):
    async def worker(item):
        raise AssertionError("не должен вызываться")

    job = run_job(repo, worker, [], errors=["e"])
    assert (job.status, job.done, job.total) == (JobStatus.FINISHED, 1, 1)


def test_old_jobs_are_forgotten(repo):
    async def worker(item):
        pass

    async def run():
        manager = JobManager(repo)
        manager.register("test", worker)
        ids = []
        for _ in range(KEEP_FINISHED_JOBS + 5):
            ids.append(manager.start("test", "t", [1]))
            await manager.wait_all()
        return manager, ids

    manager, ids = asyncio.run(run())
    assert manager.get(ids[0]) is None
    assert manager.get(ids[-1]) is not None
