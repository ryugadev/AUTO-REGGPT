/* gpt_signup_hybrid — Check Live tab logic */
(() => {
  'use strict';

  const MODE_CONFIG = {
    combo: {
      hint: 'One line per combo: email|password|2fa_secret',
      placeholder: 'email@hotmail.com|password123|DNPARKKMM5EYOPDG...\nemail2@outlook.com|pass456|I77PEBZQNEBE67SU...',
    },
    session_json: {
      hint: 'Paste one session JSON object (from /api/auth/session)',
      placeholder: '{\n  "accessToken": "eyJhbGci...",\n  "user": { "email": "user@example.com", ... },\n  ...\n}',
    },
    access_token: {
      hint: 'One raw accessToken (JWT) per line',
      placeholder: 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ...\neyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ...',
    },
  };

  const state = {
    jobs: new Map(),
    order: [],
    activeJobId: null,
    maxConcurrent: 1,
    mode: 'combo',
  };

  const $ = (id) => document.getElementById(id);
  const dom = {
    comboInput: $('checker-combo-input'),
    modeHint: $('checker-mode-hint'),
    btnRun: $('checker-btn-run'),
    btnStopAll: $('checker-btn-stop-all'),
    btnClearInput: $('checker-btn-clear-input'),
    btnClearDone: $('checker-btn-clear-done'),
    btnCopyPlus: $('checker-btn-copy-plus'),
    btnCopyFree: $('checker-btn-copy-free'),
    btnCopyError: $('checker-btn-copy-error'),
    comboCount: $('checker-combo-count'),
    jobTimeout: $('checker-job-timeout'),
    jobList: $('checker-job-list'),
    jobSummary: $('checker-job-summary'),
    logPane: $('checker-log-pane'),
    logTarget: $('checker-log-target'),
    plusPane: $('checker-plus-pane'),
    freePane: $('checker-free-pane'),
    errorPane: $('checker-error-pane'),
  };

  // ─── Mode switching ───
  const modeBtns = document.querySelectorAll('.checker-mode-btn');
  modeBtns.forEach((btn) => {
    btn.addEventListener('click', () => {
      modeBtns.forEach((b) => b.classList.remove('active'));
      btn.classList.add('active');
      state.mode = btn.dataset.mode;
      const cfg = MODE_CONFIG[state.mode];
      dom.modeHint.textContent = cfg.hint;
      dom.comboInput.placeholder = cfg.placeholder;
      updateComboCount();
    });
  });

  function escHtml(s) {
    return String(s).replace(/[&<>"']/g, (c) => ({
      '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;',
    }[c]));
  }

  function fmtDuration(secs) {
    if (secs == null) return '';
    if (secs < 60) return secs.toFixed(1) + 's';
    return Math.floor(secs / 60) + 'm' + Math.floor(secs % 60) + 's';
  }

  function api(path, opts = {}) {
    const headers = { 'Content-Type': 'application/json', ...(opts.headers || {}) };
    return fetch(path, {
      ...opts,
      headers,
    }).then((r) => {
      if (!r.ok) return r.text().then((t) => { throw new Error(`HTTP ${r.status}: ${t}`); });
      return r.json();
    });
  }

  function updateComboCount() {
    const text = dom.comboInput.value.trim();
    let count = 0;

    if (state.mode === 'combo' || state.mode === 'access_token') {
      count = text.split('\n').filter((line) => {
        const trimmed = line.trim();
        return trimmed && !trimmed.startsWith('#');
      }).length;
    } else if (state.mode === 'session_json') {
      count = text.length > 0 ? 1 : 0;
    }

    const label = state.mode === 'session_json' ? 'session' : 'item';
    dom.comboCount.textContent = `${count} ${label}${count === 1 ? '' : 's'}`;
  }

  function renderResultPanes() {
    const plusAccounts = [];
    const freeAccounts = [];
    const failedAccounts = [];

    state.order.forEach((id) => {
      const job = state.jobs.get(id);
      if (!job) return;

      const cred = job.password
        ? `${job.email}|${job.password}${job.secret ? '|' + job.secret : ''}`
        : job.email;

      if (job.status === 'success') {
        const isPlus = job.plan && job.plan.includes('plus');
        if (isPlus) {
          plusAccounts.push(`${cred}|Live Plus (${job.plan})`);
        } else {
          freeAccounts.push(`${cred}|Live Free (${job.plan || 'chatgptfreeplan'})`);
        }
      } else if (job.status === 'error') {
        failedAccounts.push(`${cred}|Die (${job.error || 'unknown error'})`);
      } else if (job.status === 'cancelled') {
        failedAccounts.push(`${cred}|Cancelled`);
      }
    });

    dom.plusPane.textContent = plusAccounts.length ? plusAccounts.join('\n') : 'No Live Plus accounts yet.';
    dom.freePane.textContent = freeAccounts.length ? freeAccounts.join('\n') : 'No Live Free accounts yet.';
    dom.errorPane.textContent = failedAccounts.length ? failedAccounts.join('\n') : 'No errors yet.';
  }

  function renderJobs() {
    if (state.order.length === 0) {
      dom.jobList.innerHTML = '<div class="empty">Paste input and click Check Live.</div>';
      dom.jobSummary.textContent = '0 total';
      renderResultPanes();
      return;
    }

    const stats = { queued: 0, running: 0, success: 0, error: 0, cancelled: 0 };
    const html = state.order.map((id, idx) => {
      const job = state.jobs.get(id);
      if (!job) return '';

      stats[job.status] = (stats[job.status] || 0) + 1;
      const cls = state.activeJobId === id ? 'job is-active' : 'job';

      const actions = [];
      if (job.status === 'running') {
        actions.push(
          `<button class="icon-btn icon-danger" data-action="stop" data-id="${escHtml(id)}" title="Stop">${window.GptUi.icon('stop')}</button>`,
        );
      } else if (job.status === 'error') {
        actions.push(
          `<button class="icon-btn" data-action="retry" data-id="${escHtml(id)}" title="Retry">${window.GptUi.icon('retry')}</button>`,
        );
      }
      actions.push(
        `<button class="icon-btn icon-danger" data-action="remove" data-id="${escHtml(id)}" title="Remove">${window.GptUi.icon('remove')}</button>`,
      );

      let meta = '';
      if (job.status === 'success' && job.plan) {
        const isPlus = job.plan.includes('plus');
        const planCls = isPlus ? 'status-success' : 'status-queued';
        meta = `<div class="job-meta ${planCls}" style="font-weight: 600; padding-left: 0.5rem;">Plan: ${escHtml(job.plan)}</div>`;
      } else if (job.error) {
        meta = `<div class="job-meta status-error" style="padding-left: 0.5rem;">${escHtml(job.error)}</div>`;
      }

      const modeTag = job.mode && job.mode !== 'combo' ? `<span class="muted">[${escHtml(job.mode)}]</span> ` : '';

      return `
        <div class="${cls}" data-id="${escHtml(id)}">
          <div class="job-index">${idx + 1}</div>
          <div class="job-status status-${escHtml(job.status)}">${escHtml(job.status)}</div>
          <div class="job-main">
            <div class="job-email" title="${escHtml(job.email)}">${modeTag}${escHtml(job.email)}</div>
            ${meta}
          </div>
          <div class="job-duration">${escHtml(fmtDuration(job.duration))}</div>
          <div class="job-actions">${actions.join('')}</div>
        </div>
      `;
    }).join('');

    dom.jobList.innerHTML = html;
    dom.jobSummary.textContent = [
      `${state.order.length} total`,
      stats.running ? `${stats.running} running` : '',
      stats.success ? `${stats.success} done` : '',
      stats.error ? `${stats.error} failed` : '',
    ].filter(Boolean).join(' · ');
    renderResultPanes();
  }

  function renderLog(jobId) {
    if (!jobId) {
      dom.logPane.textContent = '';
      dom.logTarget.textContent = '—';
      return;
    }

    const job = state.jobs.get(jobId);
    if (!job) return;

    dom.logTarget.textContent = job.email;
    api(`/api/checker/jobs/${jobId}`).then((data) => {
      dom.logPane.textContent = (data.log_lines || []).join('\n');
      dom.logPane.scrollTop = dom.logPane.scrollHeight;
    }).catch((err) => {
      dom.logPane.textContent = `[error] ${err.message}`;
    });
  }

  function applySnapshot(jobs) {
    state.order = jobs.map((job) => job.id);
    state.jobs.clear();
    jobs.forEach((job) => state.jobs.set(job.id, job));
    renderJobs();
    if (state.activeJobId && !state.jobs.has(state.activeJobId)) {
      state.activeJobId = null;
      renderLog(null);
    }
  }

  function applyJobUpdate(job) {
    if (!state.jobs.has(job.id)) state.order.push(job.id);
    state.jobs.set(job.id, job);
    renderJobs();
    if (state.activeJobId === job.id) renderLog(job.id);
  }

  function applyRemove(jobId) {
    state.jobs.delete(jobId);
    state.order = state.order.filter((id) => id !== jobId);
    if (state.activeJobId === jobId) {
      state.activeJobId = null;
      renderLog(null);
    }
    renderJobs();
  }

  function applyLog(jobId, line) {
    if (state.activeJobId !== jobId) return;
    dom.logPane.textContent += `${line}\n`;
    dom.logPane.scrollTop = dom.logPane.scrollHeight;
  }

  function connectSSE() {
    const es = window.GptUi.authEventSource('/api/checker/events');
    es.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === 'snapshot') {
          state.maxConcurrent = data.max_concurrent || state.maxConcurrent;
          if (data.job_timeout) dom.jobTimeout.value = data.job_timeout;
          applySnapshot(data.jobs || []);
        } else if (data.type === 'job') {
          applyJobUpdate(data.job);
        } else if (data.type === 'log') {
          applyLog(data.job_id, data.line);
        } else if (data.type === 'remove') {
          applyRemove(data.job_id);
        } else if (data.type === 'clear_finished') {
          api('/api/checker/jobs').then((response) => applySnapshot(response.jobs || [])).catch(console.error);
        }
      } catch (err) {
        console.error('Checker SSE parse error', err);
      }
    };
    es.onerror = () => {
      es.close();
      setTimeout(connectSSE, 3000);
    };
  }

  dom.jobList.addEventListener('click', (event) => {
    const actionBtn = event.target.closest('[data-action]');
    if (actionBtn) {
      const action = actionBtn.dataset.action;
      const id = actionBtn.dataset.id;
      event.stopPropagation();

      if (action === 'retry') {
        api(`/api/checker/jobs/${id}/retry`, { method: 'POST' }).catch((err) => alert(err.message));
      } else if (action === 'stop' || action === 'remove') {
        api(`/api/checker/jobs/${id}`, { method: 'DELETE' }).catch((err) => alert(err.message));
      }
      return;
    }

    const row = event.target.closest('.job');
    if (!row) return;
    state.activeJobId = row.dataset.id;
    renderJobs();
    renderLog(state.activeJobId);
  });

  dom.btnRun.addEventListener('click', async () => {
    const combos = dom.comboInput.value.trim();
    if (!combos) {
      alert('Paste input first.');
      return;
    }

    dom.btnRun.disabled = true;
    try {
      await api('/api/checker/jobs', {
        method: 'POST',
        body: JSON.stringify({ combos, mode: state.mode }),
      });
    } catch (err) {
      alert('Error: ' + err.message);
    } finally {
      dom.btnRun.disabled = false;
    }
  });

  dom.btnStopAll.addEventListener('click', () => {
    api('/api/checker/jobs/stop-all', { method: 'POST' }).catch((err) => alert(err.message));
  });

  dom.btnClearInput.addEventListener('click', () => {
    dom.comboInput.value = '';
    updateComboCount();
  });

  dom.btnClearDone.addEventListener('click', () => {
    api('/api/checker/jobs/clear-finished', { method: 'POST' }).catch((err) => alert(err.message));
  });

  dom.btnCopyPlus.addEventListener('click', () => {
    window.GptUi.copyText(dom.plusPane.textContent);
  });

  dom.btnCopyFree.addEventListener('click', () => {
    window.GptUi.copyText(dom.freePane.textContent);
  });

  dom.btnCopyError.addEventListener('click', () => {
    window.GptUi.copyText(dom.errorPane.textContent);
  });

  dom.jobTimeout.addEventListener('change', async () => {
    const val = parseInt(dom.jobTimeout.value, 10);
    if (isNaN(val) || val < 30 || val > 600) return;
    try {
      await api('/api/checker/config', {
        method: 'POST',
        body: JSON.stringify({ job_timeout: val }),
      });
    } catch (err) { console.error(err); }
  });

  dom.comboInput.addEventListener('input', updateComboCount);
  updateComboCount();
  connectSSE();

  setInterval(() => {
    let hasRunning = false;
    for (const [, job] of state.jobs) {
      if (job.status === 'running' && job.started_at) {
        hasRunning = true;
        job.duration = (Date.now() / 1000) - job.started_at;
      }
    }
    if (hasRunning) renderJobs();
  }, 1000);
})();
