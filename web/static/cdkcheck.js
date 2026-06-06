/* gpt_signup_hybrid — Check CDK tab logic */
(() => {
  'use strict';

  const state = {
    jobs: new Map(),
    order: [],
    activeJobId: null,
    maxConcurrent: 5,
  };

  const $ = (id) => document.getElementById(id);
  const dom = {
    keysInput: $('cdkcheck-keys-input'),
    btnRun: $('cdkcheck-btn-run'),
    btnStopAll: $('cdkcheck-btn-stop-all'),
    btnClearInput: $('cdkcheck-btn-clear-input'),
    btnClearDone: $('cdkcheck-btn-clear-done'),
    btnClearCancelled: $('cdkcheck-btn-clear-cancelled'),
    btnCopyLive: $('cdkcheck-btn-copy-live'),
    btnCopyDead: $('cdkcheck-btn-copy-dead'),
    comboCount: $('cdkcheck-combo-count'),
    jobTimeout: $('cdkcheck-job-timeout'),
    jobList: $('cdkcheck-job-list'),
    jobSummary: $('cdkcheck-job-summary'),
    logPane: $('cdkcheck-log-pane'),
    logTarget: $('cdkcheck-log-target'),
    livePane: $('cdkcheck-live-pane'),
    deadPane: $('cdkcheck-dead-pane'),
    liveCount: $('cdkcheck-live-count'),
    deadCount: $('cdkcheck-dead-count'),
  };

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
    return fetch(path, { ...opts, headers }).then((r) => {
      if (!r.ok) return r.text().then((t) => { throw new Error(`HTTP ${r.status}: ${t}`); });
      return r.json();
    });
  }

  function updateCount() {
    const count = dom.keysInput.value.split('\n').filter((l) => {
      const s = l.trim();
      return s && !s.startsWith('#');
    }).length;
    dom.comboCount.textContent = `${count} key${count === 1 ? '' : 's'}`;
  }

  function quotaText(job) {
    if (job.quota) return job.quota;
    if (job.total != null && job.remaining != null) {
      const used = job.used != null ? job.used : (job.total - job.remaining);
      return `${used}/${job.total}`;
    }
    return '';
  }

  function renderResultPanes() {
    const live = [];
    const dead = [];
    state.order.forEach((id) => {
      const job = state.jobs.get(id);
      if (!job) return;
      if (job.status === 'live') {
        live.push(`${job.cdk_key}|LIVE (còn ${job.remaining}/${job.total})`);
      } else if (job.status === 'dead') {
        dead.push(`${job.cdk_key}|DEAD (${quotaText(job)})`);
      } else if (job.status === 'error') {
        dead.push(`${job.cdk_key}|ERROR (${job.error || 'unknown'})`);
      }
    });
    dom.livePane.textContent = live.length ? live.join('\n') : 'No live CDK yet.';
    dom.deadPane.textContent = dead.length ? dead.join('\n') : 'No dead CDK yet.';
    if (dom.liveCount) dom.liveCount.textContent = live.length ? `(${live.length})` : '';
    if (dom.deadCount) dom.deadCount.textContent = dead.length ? `(${dead.length})` : '';
  }

  function renderJobs() {
    if (state.order.length === 0) {
      dom.jobList.innerHTML = '<div class="empty">Paste CDK keys and click Check CDK.</div>';
      dom.jobSummary.textContent = '0 total';
      renderResultPanes();
      return;
    }

    const stats = { queued: 0, running: 0, live: 0, dead: 0, error: 0, cancelled: 0 };
    const html = state.order.map((id, idx) => {
      const job = state.jobs.get(id);
      if (!job) return '';
      stats[job.status] = (stats[job.status] || 0) + 1;
      const cls = state.activeJobId === id ? 'job is-active' : 'job';

      const actions = [];
      if (job.status === 'error' || job.status === 'dead') {
        actions.push(
          `<button class="icon-btn" data-action="retry" data-id="${escHtml(id)}" title="Re-check">${window.GptUi.icon('retry')}</button>`,
        );
      }
      actions.push(
        `<button class="icon-btn icon-danger" data-action="remove" data-id="${escHtml(id)}" title="Remove">${window.GptUi.icon('remove')}</button>`,
      );

      let meta = '';
      if (job.status === 'live') {
        meta = `<div class="job-meta status-success" style="font-weight:600;padding-left:0.5rem;">LIVE · còn ${escHtml(job.remaining)}/${escHtml(job.total)} lượt</div>`;
      } else if (job.status === 'dead') {
        meta = `<div class="job-meta status-error" style="padding-left:0.5rem;">DEAD · đã hết lượt (${escHtml(quotaText(job))})</div>`;
      } else if (job.status === 'error') {
        meta = `<div class="job-meta status-error" style="padding-left:0.5rem;">${escHtml(job.error || 'error')}</div>`;
      }

      // map status → class màu (live=success, dead=error)
      const statusCls = job.status === 'live' ? 'status-success'
        : (job.status === 'dead' ? 'status-error' : `status-${escHtml(job.status)}`);
      const statusLabel = job.status === 'live' ? 'LIVE'
        : (job.status === 'dead' ? 'DEAD' : job.status);

      return `
        <div class="${cls}" data-id="${escHtml(id)}">
          <div class="job-index">${idx + 1}</div>
          <div class="job-status ${statusCls}">${escHtml(statusLabel)}</div>
          <div class="job-main">
            <div class="job-email" title="${escHtml(job.cdk_key)}">${escHtml(job.cdk_key)}</div>
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
      stats.live ? `${stats.live} live` : '',
      stats.dead ? `${stats.dead} dead` : '',
      stats.error ? `${stats.error} error` : '',
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
    dom.logTarget.textContent = job.cdk_key;
    api(`/api/cdkcheck/jobs/${jobId}`).then((data) => {
      dom.logPane.textContent = (data.log_lines || []).join('\n');
      dom.logPane.scrollTop = dom.logPane.scrollHeight;
    }).catch((err) => {
      dom.logPane.textContent = `[error] ${err.message}`;
    });
  }

  function applySnapshot(jobs) {
    state.order = jobs.map((j) => j.id);
    state.jobs.clear();
    jobs.forEach((j) => state.jobs.set(j.id, j));
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
    const es = window.GptUi.authEventSource('/api/cdkcheck/events');
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
          api('/api/cdkcheck/jobs').then((r) => applySnapshot(r.jobs || [])).catch(console.error);
        }
      } catch (err) {
        console.error('CDK check SSE parse error', err);
      }
    };
    es.onerror = () => {
      es.close();
    };
    return es;
  }

  dom.jobList.addEventListener('click', (event) => {
    const actionBtn = event.target.closest('[data-action]');
    if (actionBtn) {
      const action = actionBtn.dataset.action;
      const id = actionBtn.dataset.id;
      event.stopPropagation();
      if (action === 'retry') {
        api(`/api/cdkcheck/jobs/${id}/retry`, { method: 'POST' }).catch((err) => alert(err.message));
      } else if (action === 'remove') {
        // Optimistic: xóa khỏi UI ngay, không chờ SSE event
        api(`/api/cdkcheck/jobs/${id}`, { method: 'DELETE' })
          .then(() => applyRemove(id))
          .catch((err) => alert(err.message));
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
    const cdk_keys = dom.keysInput.value.trim();
    if (!cdk_keys) {
      alert('Paste CDK keys first.');
      return;
    }
    // Phản hồi tức thì: nút chuyển trạng thái "Checking..."
    const origLabel = dom.btnRun.textContent;
    dom.btnRun.disabled = true;
    dom.btnRun.textContent = 'Checking…';
    try {
      const res = await api('/api/cdkcheck/jobs', {
        method: 'POST',
        body: JSON.stringify({ cdk_keys }),
      });
      // Hiển thị jobs NGAY (không chờ SSE) — đảm bảo UI phản hồi dù SSE chết.
      try {
        const snap = await api('/api/cdkcheck/jobs');
        applySnapshot(snap.jobs || []);
      } catch (e) { /* ignore */ }
      if (window.GptUi.showToast) {
        window.GptUi.showToast(`Đang check ${res.added || 0} CDK…`, 'success');
      }
    } catch (err) {
      if (window.GptUi.showToast) window.GptUi.showToast('Error: ' + err.message, 'error');
      else alert('Error: ' + err.message);
    } finally {
      dom.btnRun.disabled = false;
      dom.btnRun.textContent = origLabel;
    }
  });

  dom.btnStopAll.addEventListener('click', () => {
    api('/api/cdkcheck/jobs/stop-all', { method: 'POST' })
      .then(() => {
        // Refresh ngay từ server (không chờ SSE)
        api('/api/cdkcheck/jobs').then((r) => applySnapshot(r.jobs || [])).catch(() => {});
      })
      .catch((err) => alert(err.message));
  });

  dom.btnClearInput.addEventListener('click', () => {
    dom.keysInput.value = '';
    updateCount();
  });

  dom.btnClearDone.addEventListener('click', () => {
    api('/api/cdkcheck/jobs/clear-finished', { method: 'POST' })
      .then((r) => {
        // Optimistic: tự xóa job đã xong khỏi UI ngay, không chờ SSE event
        // (phòng SSE connection bị ngắt sau khi server restart).
        const finished = new Set(['live', 'dead', 'error']);
        state.order = state.order.filter((id) => {
          const j = state.jobs.get(id);
          if (j && finished.has(j.status)) {
            state.jobs.delete(id);
            return false;
          }
          return true;
        });
        renderJobs();
        if (window.GptUi.showToast) {
          window.GptUi.showToast(`Đã xóa ${r.removed || 0} CDK`, 'info');
        }
      })
      .catch((err) => alert(err.message));
  });

  dom.btnClearCancelled.addEventListener('click', () => {
    api('/api/cdkcheck/jobs/clear-cancelled', { method: 'POST' })
      .then((r) => {
        // Optimistic: xóa job cancelled khỏi UI ngay
        state.order = state.order.filter((id) => {
          const j = state.jobs.get(id);
          if (j && j.status === 'cancelled') {
            state.jobs.delete(id);
            return false;
          }
          return true;
        });
        renderJobs();
        if (window.GptUi.showToast) {
          window.GptUi.showToast(`Đã xóa ${r.removed || 0} CDK cancelled`, 'info');
        }
      })
      .catch((err) => alert(err.message));
  });

  dom.btnCopyLive.addEventListener('click', () => window.GptUi.copyText(dom.livePane.textContent));
  dom.btnCopyDead.addEventListener('click', () => window.GptUi.copyText(dom.deadPane.textContent));

  dom.jobTimeout.addEventListener('change', async () => {
    const val = parseInt(dom.jobTimeout.value, 10);
    if (isNaN(val) || val < 10 || val > 600) return;
    try {
      await api('/api/cdkcheck/config', {
        method: 'POST',
        body: JSON.stringify({ job_timeout: val }),
      });
    } catch (err) { console.error(err); }
  });

  dom.keysInput.addEventListener('input', updateCount);
  updateCount();
  // Đăng ký SSE vào manager — chỉ mở khi tab Check CDK active (tránh đầy quota
  // 6 connection/origin của browser khi nhiều tab cùng mở SSE).
  if (window.GptUi && window.GptUi.registerTabSSE) {
    window.GptUi.registerTabSSE('cdkcheck', connectSSE);
  } else {
    connectSSE();
  }

  function _isActive() {
    const el = document.getElementById('tab-cdkcheck');
    return el && el.classList.contains('active');
  }

  // Cập nhật duration cho job đang chạy (mỗi giây) — chỉ khi tab active
  setInterval(() => {
    if (!_isActive()) return;
    let hasRunning = false;
    for (const [, job] of state.jobs) {
      if (job.status === 'running' && job.started_at) {
        hasRunning = true;
        job.duration = (Date.now() / 1000) - job.started_at;
      }
    }
    if (hasRunning) renderJobs();
  }, 1000);

  // Polling fallback: mỗi 2.5s đồng bộ jobs từ server (chỉ khi tab active).
  // Đảm bảo UI luôn cập nhật kể cả khi SSE bị ngắt.
  setInterval(() => {
    if (!_isActive()) return;
    api('/api/cdkcheck/jobs')
      .then((r) => {
        const jobs = r.jobs || [];
        let changed = jobs.length !== state.order.length;
        if (!changed) {
          for (const j of jobs) {
            const cur = state.jobs.get(j.id);
            if (!cur || cur.status !== j.status) { changed = true; break; }
          }
        }
        if (changed) applySnapshot(jobs);
      })
      .catch(() => { /* bỏ qua */ });
  }, 2500);
})();
