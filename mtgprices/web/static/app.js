"use strict";

// Подтверждение опасных действий: <form data-confirm="Текст?">
document.addEventListener("submit", (event) => {
  const message = event.target.dataset.confirm;
  if (message && !window.confirm(message)) {
    event.preventDefault();
  }
});

// Прогресс фоновых задач. Без JS страница тоже работает: прогресс виден после перезагрузки.
const STATUS_TEXT = { running: "идёт", finished: "готово", cancelled: "остановлено" };

function renderJob(panel, job) {
  panel.querySelector("[data-role=status]").textContent = STATUS_TEXT[job.status] || job.status;
  const progress = panel.querySelector("[data-role=progress]");
  progress.max = job.total || 1;
  progress.value = job.done;
  panel.querySelector("[data-role=counts]").textContent =
    `Обработано ${job.done} из ${job.total}, успешно ${job.succeeded}, ошибок ${job.errors.length}`;
  const list = panel.querySelector("[data-role=errors]");
  list.replaceChildren(...job.errors.map((text) => {
    const item = document.createElement("li");
    item.textContent = text;
    return item;
  }));
}

function watchJob(panel) {
  const id = panel.dataset.jobId;
  const poll = async () => {
    let job;
    try {
      const response = await fetch(`/api/jobs/${encodeURIComponent(id)}`, { cache: "no-store" });
      if (!response.ok) return;
      job = await response.json();
    } catch {
      setTimeout(poll, 3000);
      return;
    }
    renderJob(panel, job);
    if (job.status === "running") {
      setTimeout(poll, 1000);
    } else {
      // Перезагружаем, чтобы показать новые карты и цены
      window.location.reload();
    }
  };
  setTimeout(poll, 500);
}

document.querySelectorAll(".job[data-status=running]").forEach(watchJob);
