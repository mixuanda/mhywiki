#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import mimetypes
import sys
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Lock
from urllib.parse import parse_qs, unquote, urlparse

import content_cms
import content_entities
import textmap_shards


ROOT_DIR = Path(__file__).resolve().parent.parent
SITE_DIR = ROOT_DIR / "site"

LEGACY_REPO = content_entities.ContentRepository()
CMS_REPO = content_cms.UniversalCMSRepository()
REPO_LOCK = Lock()


def _response_charset_type(path: Path, default_ctype: str) -> str:
    ext = path.suffix.lower()
    if ext == ".html":
        return "text/html; charset=utf-8"
    if ext == ".js":
        return "application/javascript; charset=utf-8"
    if ext == ".css":
        return "text/css; charset=utf-8"
    if ext == ".json":
        return "application/json; charset=utf-8"
    if ext in {".txt", ".xml"}:
        return f"{default_ctype}; charset=utf-8"
    return default_ctype


ADMIN_HTML = """<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>HomDGCat 全站内容后台</title>
  <style>
    :root {
      --bg: #f7f4ec;
      --panel: #fffdf7;
      --ink: #1e242a;
      --line: #d9d0c2;
      --muted: #616c76;
      --accent: #b45f2f;
      --accent-2: #2f6d89;
      --ok: #267a2f;
      --bad: #b13434;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      color: var(--ink);
      background:
        radial-gradient(1200px 520px at -5% -20%, #f6d5ba 0%, transparent 50%),
        radial-gradient(1200px 560px at 105% -20%, #cfe3ea 0%, transparent 55%),
        var(--bg);
      font-family: "Avenir Next", "PingFang SC", "Microsoft YaHei", sans-serif;
    }
    .wrap {
      max-width: 1520px;
      margin: 18px auto;
      padding: 0 12px;
    }
    .head {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      gap: 12px;
      margin-bottom: 10px;
    }
    h1 {
      margin: 0;
      font-size: 28px;
      letter-spacing: .2px;
    }
    .sub {
      margin: 6px 0 0;
      color: var(--muted);
      font-size: 13px;
      line-height: 1.45;
    }
    .btns {
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
      justify-content: flex-end;
    }
    button, .btn {
      border: 1px solid var(--line);
      background: #fff;
      color: var(--ink);
      border-radius: 10px;
      font-size: 12px;
      padding: 8px 11px;
      text-decoration: none;
      cursor: pointer;
    }
    .pri {
      border: 0;
      color: #fff;
      background: linear-gradient(135deg, var(--accent), #cf7745);
    }
    .sec {
      border: 0;
      color: #fff;
      background: linear-gradient(135deg, var(--accent-2), #4990aa);
    }
    .danger {
      border: 0;
      color: #fff;
      background: linear-gradient(135deg, #8b2323, var(--bad));
    }
    .layout {
      display: grid;
      grid-template-columns: 360px 420px 1fr;
      gap: 10px;
    }
    .card {
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 12px;
      overflow: hidden;
      min-height: 70vh;
    }
    .bar {
      padding: 10px;
      border-bottom: 1px solid var(--line);
      background: #fff7e8;
      display: flex;
      gap: 8px;
      align-items: center;
      flex-wrap: wrap;
    }
    .bar b {
      font-size: 13px;
    }
    .ctrl {
      display: flex;
      gap: 7px;
      flex-wrap: wrap;
      margin-left: auto;
      align-items: center;
    }
    select, input[type="text"], textarea {
      border: 1px solid #cfc1ab;
      border-radius: 8px;
      background: #fff;
      color: #16202a;
      padding: 7px 8px;
      font: inherit;
      width: 100%;
    }
    .ctrl select, .ctrl input {
      width: auto;
      min-width: 110px;
      font-size: 12px;
    }
    .pane {
      max-height: calc(70vh - 48px);
      overflow: auto;
      padding: 8px;
    }
    .source-group {
      margin-bottom: 8px;
      border: 1px solid #e4d9c6;
      border-radius: 9px;
      background: #fff;
      overflow: hidden;
    }
    .source-group h4 {
      margin: 0;
      padding: 8px;
      font-size: 12px;
      background: #fff6e4;
      border-bottom: 1px solid #eadfcf;
      color: #3e4852;
    }
    .source-item,
    .record-item {
      border-bottom: 1px solid #eee3d3;
      padding: 8px;
      cursor: pointer;
    }
    .source-item:last-child,
    .record-item:last-child {
      border-bottom: 0;
    }
    .source-item:hover,
    .record-item:hover {
      background: #fff4de;
    }
    .source-item.active,
    .record-item.active {
      background: #ffe7c4;
      border-left: 4px solid var(--accent);
      padding-left: 4px;
    }
    .name {
      font-size: 13px;
      font-weight: 600;
      line-height: 1.35;
      word-break: break-all;
    }
    .meta {
      margin-top: 3px;
      color: var(--muted);
      font-size: 11px;
      line-height: 1.35;
    }
    .readonly {
      color: var(--bad);
      font-weight: 600;
    }
    .f {
      margin-bottom: 10px;
    }
    .f label {
      display: block;
      margin-bottom: 4px;
      font-size: 12px;
      font-weight: 600;
    }
    textarea {
      min-height: 110px;
      resize: vertical;
    }
    .editor {
      padding: 10px;
      max-height: calc(70vh - 110px);
      overflow: auto;
    }
    .editor-toolbar {
      padding: 9px 10px;
      border-top: 1px solid var(--line);
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
      background: #fff;
      align-items: center;
    }
    .status {
      margin-top: 10px;
      border: 1px solid #d8cdc1;
      border-radius: 10px;
      background: #fff;
      padding: 8px 10px;
      color: #4e5965;
      font-size: 12px;
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
    }
    pre#log {
      margin: 10px 0 0;
      background: #12161a;
      color: #e3edf5;
      border-radius: 10px;
      border: 1px solid #293038;
      min-height: 160px;
      max-height: 30vh;
      overflow: auto;
      padding: 10px;
      font-size: 12px;
      line-height: 1.45;
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace;
    }
    .ok { color: var(--ok); }
    .bad { color: var(--bad); }
    .hint {
      padding: 8px;
      font-size: 12px;
      color: var(--muted);
    }
    @media (max-width: 1250px) {
      .layout { grid-template-columns: 1fr; }
      .card { min-height: 45vh; }
      .pane { max-height: calc(45vh - 48px); }
      .editor { max-height: calc(45vh - 110px); }
    }
  </style>
</head>
<body>
  <div class="wrap">
    <div class="head">
      <div>
        <h1>HomDGCat 全站可视化内容后台</h1>
        <p class="sub">CH+EN 文本内容统一管理。支持角色/武器/任务/怪物/活动/TextMap 等数据源。<br>保存自动备份，支持回滚。TextMap 分片存在时会自动聚合回 `GI.json/SR.json`。</p>
      </div>
      <div class="btns">
        <a class="btn sec" href="/index/" target="_blank" rel="noopener">打开网站预览</a>
        <button id="btnReloadAll">刷新数据源</button>
        <button id="btnRebuildIndex">重建索引</button>
        <button class="danger" id="btnUndo">回滚最近一次保存</button>
      </div>
    </div>

    <div class="layout">
      <section class="card">
        <div class="bar">
          <b>数据源目录</b>
          <div class="ctrl">
            <select id="fGame">
              <option value="">全部游戏</option>
              <option value="gi">原神</option>
              <option value="sr">星铁</option>
              <option value="global">全局</option>
            </select>
            <select id="fLocale">
              <option value="">全部语言</option>
              <option value="CH">CH</option>
              <option value="EN">EN</option>
              <option value="CH+EN">CH+EN</option>
            </select>
            <input id="fSourceQ" type="text" placeholder="筛选文件/模块" />
          </div>
        </div>
        <div id="sourcePane" class="pane"></div>
      </section>

      <section class="card">
        <div class="bar">
          <b id="recordsTitle">记录列表</b>
          <div class="ctrl">
            <input id="recordQ" type="text" placeholder="搜索当前数据源" />
            <button id="btnPrevPage">上一页</button>
            <button id="btnNextPage">下一页</button>
          </div>
        </div>
        <div id="recordPane" class="pane"></div>
        <div class="hint" id="recordPager">请选择左侧数据源</div>
      </section>

      <section class="card">
        <div class="bar">
          <b id="editorTitle">编辑器</b>
          <div class="ctrl">
            <button id="btnPreviewDiff">预览差异</button>
            <button class="pri" id="btnSaveForm">保存字段模式</button>
            <button class="sec" id="btnSaveRaw">保存原始JSON</button>
          </div>
        </div>
        <div class="editor" id="editorPane">
          <div class="hint">请选择数据源与记录后开始编辑。</div>
        </div>
        <div class="editor-toolbar">
          <input id="globalQ" type="text" placeholder="全局搜索（跨数据源）" />
          <button id="btnGlobalSearch">执行全局搜索</button>
          <button id="btnUseGlobalResult">将首条结果载入编辑器</button>
        </div>
      </section>
    </div>

    <div class="status" id="status"></div>
    <pre id="log">后台已启动，等待操作...</pre>
  </div>

<script>
const state = {
  game: '',
  locale: '',
  sourceQ: '',
  sources: [],
  selectedSourceId: '',
  records: [],
  selectedRecordId: '',
  recordQ: '',
  page: 1,
  pageSize: 50,
  total: 0,
  currentRecord: null,
  globalResults: []
};

const els = {
  fGame: document.getElementById('fGame'),
  fLocale: document.getElementById('fLocale'),
  fSourceQ: document.getElementById('fSourceQ'),
  sourcePane: document.getElementById('sourcePane'),
  recordPane: document.getElementById('recordPane'),
  recordQ: document.getElementById('recordQ'),
  recordsTitle: document.getElementById('recordsTitle'),
  recordPager: document.getElementById('recordPager'),
  editorPane: document.getElementById('editorPane'),
  editorTitle: document.getElementById('editorTitle'),
  status: document.getElementById('status'),
  log: document.getElementById('log'),
  btnPrevPage: document.getElementById('btnPrevPage'),
  btnNextPage: document.getElementById('btnNextPage'),
  btnReloadAll: document.getElementById('btnReloadAll'),
  btnRebuildIndex: document.getElementById('btnRebuildIndex'),
  btnUndo: document.getElementById('btnUndo'),
  btnPreviewDiff: document.getElementById('btnPreviewDiff'),
  btnSaveForm: document.getElementById('btnSaveForm'),
  btnSaveRaw: document.getElementById('btnSaveRaw'),
  globalQ: document.getElementById('globalQ'),
  btnGlobalSearch: document.getElementById('btnGlobalSearch'),
  btnUseGlobalResult: document.getElementById('btnUseGlobalResult')
};

function esc(s) {
  return String(s || '')
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;');
}

function setLog(text, cls) {
  els.log.className = cls || '';
  els.log.textContent = text || '';
  els.log.scrollTop = els.log.scrollHeight;
}

async function api(url, opt = {}) {
  const res = await fetch(url, {
    headers: {'Content-Type': 'application/json'},
    ...opt
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.error || `HTTP ${res.status}`);
  return data;
}

function sourceGroupKey(src) {
  return `${src.game || 'global'} / ${src.locale || 'N/A'} / ${src.category || '-'}`;
}

function renderSourcePane() {
  els.sourcePane.innerHTML = '';
  if (!state.sources.length) {
    els.sourcePane.innerHTML = '<div class="hint">没有匹配的数据源。</div>';
    return;
  }

  const groups = {};
  for (const src of state.sources) {
    const k = sourceGroupKey(src);
    if (!groups[k]) groups[k] = [];
    groups[k].push(src);
  }

  const keys = Object.keys(groups).sort();
  for (const key of keys) {
    const wrap = document.createElement('div');
    wrap.className = 'source-group';
    wrap.innerHTML = `<h4>${esc(key)}</h4>`;
    for (const src of groups[key]) {
      const div = document.createElement('div');
      div.className = 'source-item' + (src.id === state.selectedSourceId ? ' active' : '');
      div.innerHTML = `
        <div class="name">${esc(src.id)}</div>
        <div class="meta">
          format=${esc(src.format)} | records=${esc(String(src.record_count))} | size=${esc(String(src.size_bytes))}<br>
          ${src.editable ? '可编辑' : '<span class="readonly">只读</span>'}
          ${src.readonly_reason ? ` | ${esc(src.readonly_reason)}` : ''}
        </div>
      `;
      div.addEventListener('click', async () => {
        state.selectedSourceId = src.id;
        state.page = 1;
        state.selectedRecordId = '';
        state.currentRecord = null;
        renderSourcePane();
        await loadRecords();
      });
      wrap.appendChild(div);
    }
    els.sourcePane.appendChild(wrap);
  }
}

function renderRecords() {
  els.recordPane.innerHTML = '';
  if (!state.selectedSourceId) {
    els.recordPane.innerHTML = '<div class="hint">请先选择左侧数据源。</div>';
    return;
  }
  if (!state.records.length) {
    els.recordPane.innerHTML = '<div class="hint">当前页没有记录。</div>';
    return;
  }
  for (const row of state.records) {
    const div = document.createElement('div');
    div.className = 'record-item' + (row.record_id === state.selectedRecordId ? ' active' : '');
    div.innerHTML = `
      <div class="name">${esc(row.title)} <span style="color:#6a7480">#${esc(row.record_id)}</span></div>
      <div class="meta">${esc(row.summary || '')}</div>
    `;
    div.addEventListener('click', async () => {
      state.selectedRecordId = row.record_id;
      renderRecords();
      await loadRecord();
    });
    els.recordPane.appendChild(div);
  }
  const start = (state.page - 1) * state.pageSize + 1;
  const end = Math.min(state.total, state.page * state.pageSize);
  els.recordPager.textContent = `第 ${state.page} 页 | ${start}-${end} / ${state.total}`;
}

function renderEditor() {
  if (!state.currentRecord) {
    els.editorTitle.textContent = '编辑器';
    els.editorPane.innerHTML = '<div class="hint">请选择记录后编辑。</div>';
    return;
  }

  const item = state.currentRecord;
  els.editorTitle.textContent = `${item.title || 'record'} (#${item.record_id || ''})`;

  const fieldsHtml = (item.fields || []).map((f) => {
    const id = `fld_${f.key}`;
    const label = `<label for="${esc(id)}">${esc(f.label || f.key)}</label>`;
    if (f.type === 'textarea') {
      return `<div class="f">${label}<textarea id="${esc(id)}" data-key="${esc(f.key)}">${esc(f.value || '')}</textarea></div>`;
    }
    return `<div class="f">${label}<input id="${esc(id)}" data-key="${esc(f.key)}" type="text" value="${esc(f.value || '')}" /></div>`;
  }).join('');

  els.editorPane.innerHTML = `
    <div class="hint">字段模式：修改顶层标量字段。复杂结构请用原始JSON模式。</div>
    ${fieldsHtml || '<div class="hint">该记录没有可直接表单编辑的字段。</div>'}
    <div class="f">
      <label for="rawJson">原始 JSON</label>
      <textarea id="rawJson" style="min-height:240px;">${esc(item.raw_json || '')}</textarea>
    </div>
  `;
}

function collectFields() {
  const out = {};
  els.editorPane.querySelectorAll('[data-key]').forEach((el) => {
    out[el.getAttribute('data-key')] = el.value;
  });
  return out;
}

function currentSource() {
  return state.sources.find(x => x.id === state.selectedSourceId) || null;
}

async function loadStatus() {
  const data = await api('/__admin/api/status');
  const c = data.counts || {};
  const cms = data.cms || {};
  const shard = data.textmap_shards || {};
  const giShard = shard.gi || {};
  const srShard = shard.sr || {};
  els.status.innerHTML = `
    <span>站点: ${esc(data.site_dir)}</span>
    <span>备份: ${esc(String(data.backups?.count || 0))}</span>
    <span>最近备份: ${esc(data.backups?.latest || '-')}</span>
    <span>CMS数据源: ${esc(String(cms.sources || 0))}</span>
    <span>可编辑源: ${esc(String(cms.editable_sources || 0))}</span>
    <span>SR角色: ${esc(String(c.sr_characters || 0))}</span>
    <span>GI角色: ${esc(String(c.gi_characters || 0))}</span>
    <span>SR武器: ${esc(String(c.sr_weapons || 0))}</span>
    <span>GI武器: ${esc(String(c.gi_weapons || 0))}</span>
    <span>GI分片: ${esc(String(giShard.shard_count || 0))}</span>
    <span>SR分片: ${esc(String(srShard.shard_count || 0))}</span>
  `;
}

async function loadSources() {
  const game = encodeURIComponent(state.game);
  const locale = encodeURIComponent(state.locale);
  const q = encodeURIComponent(state.sourceQ);
  const data = await api(`/__admin/api/v2/sources?game=${game}&locale=${locale}&q=${q}`);
  state.sources = data.sources || [];

  if (!state.selectedSourceId || !state.sources.some(x => x.id === state.selectedSourceId)) {
    state.selectedSourceId = state.sources.length ? state.sources[0].id : '';
    state.selectedRecordId = '';
    state.currentRecord = null;
  }

  renderSourcePane();
  await loadRecords();
}

async function loadRecords() {
  renderEditor();
  if (!state.selectedSourceId) {
    state.records = [];
    state.total = 0;
    renderRecords();
    return;
  }
  const sourceId = encodeURIComponent(state.selectedSourceId);
  const q = encodeURIComponent(state.recordQ);
  const page = encodeURIComponent(String(state.page));
  const pageSize = encodeURIComponent(String(state.pageSize));
  const data = await api(`/__admin/api/v2/records?source_id=${sourceId}&q=${q}&page=${page}&page_size=${pageSize}`);
  state.records = data.records || [];
  state.total = Number(data.total || 0);
  els.recordsTitle.textContent = `记录列表 (${state.selectedSourceId})`;

  if (!state.selectedRecordId || !state.records.some(x => x.record_id === state.selectedRecordId)) {
    state.selectedRecordId = state.records.length ? state.records[0].record_id : '';
  }

  renderRecords();
  await loadRecord();
}

async function loadRecord() {
  if (!state.selectedSourceId || !state.selectedRecordId) {
    state.currentRecord = null;
    renderEditor();
    return;
  }
  const sourceId = encodeURIComponent(state.selectedSourceId);
  const recordId = encodeURIComponent(state.selectedRecordId);
  const data = await api(`/__admin/api/v2/record?source_id=${sourceId}&record_id=${recordId}`);
  state.currentRecord = data.record || null;
  renderEditor();
}

async function saveRecord(mode) {
  if (!state.selectedSourceId || !state.selectedRecordId) {
    setLog('没有选中记录。', 'bad');
    return;
  }
  const src = currentSource();
  if (!src) {
    setLog('当前数据源不存在。', 'bad');
    return;
  }
  if (!src.editable) {
    setLog(`当前数据源只读: ${src.readonly_reason || 'unknown'}`, 'bad');
    return;
  }
  const body = {
    source_id: state.selectedSourceId,
    record_id: state.selectedRecordId,
    mode,
    fields: collectFields(),
    raw_json: (document.getElementById('rawJson')?.value || '')
  };
  const data = await api('/__admin/api/v2/record/save', {
    method: 'POST',
    body: JSON.stringify(body)
  });
  setLog(data.message || '保存成功。', 'ok');
  await loadStatus();
  await loadRecords();
}

async function previewDiff() {
  if (!state.selectedSourceId || !state.selectedRecordId) {
    setLog('没有选中记录。', 'bad');
    return;
  }
  const body = {
    source_id: state.selectedSourceId,
    record_id: state.selectedRecordId,
    mode: 'raw',
    fields: collectFields(),
    raw_json: (document.getElementById('rawJson')?.value || '')
  };
  const data = await api('/__admin/api/v2/record/preview-diff', {
    method: 'POST',
    body: JSON.stringify(body)
  });
  if (!data.changed) {
    setLog('没有检测到变更。', 'ok');
    return;
  }
  setLog(data.diff || '(diff 为空)', '');
}

async function doUndo() {
  const data = await api('/__admin/api/v2/undo', {
    method: 'POST',
    body: '{}'
  });
  setLog(data.message || '已回滚。', data.code === 0 ? 'ok' : 'bad');
  await loadStatus();
  await loadSources();
}

async function rebuildIndex() {
  const data = await api('/__admin/api/v2/rebuild-index', {
    method: 'POST',
    body: '{}'
  });
  setLog(`索引重建完成: ok=${data.ok || 0}, failed=${data.failed || 0}`, 'ok');
  await loadStatus();
  await loadSources();
}

async function reloadAll() {
  await api('/__admin/api/reload', {
    method: 'POST',
    body: '{}'
  });
  setLog('已重新加载所有数据。', 'ok');
  await loadStatus();
  await loadSources();
}

async function globalSearch() {
  const q = (els.globalQ.value || '').trim();
  if (!q) {
    setLog('请输入全局搜索关键词。', 'bad');
    return;
  }
  const data = await api('/__admin/api/v2/search-global', {
    method: 'POST',
    body: JSON.stringify({q, limit: 80})
  });
  state.globalResults = data.results || [];
  if (!state.globalResults.length) {
    setLog('全局搜索无结果。', '');
    return;
  }
  const lines = state.globalResults.slice(0, 20).map((x, i) => `${i + 1}. [${x.source_id}] ${x.record_id} | ${x.title}`);
  setLog(`找到 ${state.globalResults.length} 条结果:\n` + lines.join('\n'), '');
}

async function useGlobalFirst() {
  if (!state.globalResults.length) {
    setLog('没有可用的全局搜索结果。', 'bad');
    return;
  }
  const first = state.globalResults[0];
  state.selectedSourceId = first.source_id;
  state.selectedRecordId = first.record_id;
  renderSourcePane();
  await loadRecords();
}

let sourceTimer = null;
els.fSourceQ.addEventListener('input', () => {
  clearTimeout(sourceTimer);
  sourceTimer = setTimeout(async () => {
    state.sourceQ = els.fSourceQ.value.trim();
    await loadSources();
  }, 220);
});

let recordTimer = null;
els.recordQ.addEventListener('input', () => {
  clearTimeout(recordTimer);
  recordTimer = setTimeout(async () => {
    state.recordQ = els.recordQ.value.trim();
    state.page = 1;
    await loadRecords();
  }, 220);
});

els.fGame.addEventListener('change', async () => {
  state.game = els.fGame.value;
  await loadSources();
});

els.fLocale.addEventListener('change', async () => {
  state.locale = els.fLocale.value;
  await loadSources();
});

els.btnPrevPage.addEventListener('click', async () => {
  if (state.page <= 1) return;
  state.page -= 1;
  await loadRecords();
});

els.btnNextPage.addEventListener('click', async () => {
  if (state.page * state.pageSize >= state.total) return;
  state.page += 1;
  await loadRecords();
});

els.btnSaveForm.addEventListener('click', async () => {
  try {
    await saveRecord('form');
  } catch (e) {
    setLog(`保存失败: ${e.message}`, 'bad');
  }
});

els.btnSaveRaw.addEventListener('click', async () => {
  try {
    await saveRecord('raw');
  } catch (e) {
    setLog(`保存失败: ${e.message}`, 'bad');
  }
});

els.btnPreviewDiff.addEventListener('click', async () => {
  try {
    await previewDiff();
  } catch (e) {
    setLog(`预览失败: ${e.message}`, 'bad');
  }
});

els.btnUndo.addEventListener('click', async () => {
  try {
    await doUndo();
  } catch (e) {
    setLog(`回滚失败: ${e.message}`, 'bad');
  }
});

els.btnRebuildIndex.addEventListener('click', async () => {
  try {
    await rebuildIndex();
  } catch (e) {
    setLog(`重建索引失败: ${e.message}`, 'bad');
  }
});

els.btnReloadAll.addEventListener('click', async () => {
  try {
    await reloadAll();
  } catch (e) {
    setLog(`刷新失败: ${e.message}`, 'bad');
  }
});

els.btnGlobalSearch.addEventListener('click', async () => {
  try {
    await globalSearch();
  } catch (e) {
    setLog(`全局搜索失败: ${e.message}`, 'bad');
  }
});

els.btnUseGlobalResult.addEventListener('click', async () => {
  try {
    await useGlobalFirst();
  } catch (e) {
    setLog(`载入结果失败: ${e.message}`, 'bad');
  }
});

(async function boot() {
  try {
    await loadStatus();
    await loadSources();
  } catch (e) {
    setLog(`初始化失败: ${e.message}`, 'bad');
  }
})();
</script>
</body>
</html>
"""


class Handler(BaseHTTPRequestHandler):
    server_version = "HomDGCatLocalAdmin/3.0"

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)

        if path in {"/__admin", "/__admin/"}:
            self._send_html(ADMIN_HTML)
            return

        if path == "/__admin/api/status":
            with REPO_LOCK:
                payload = {
                    "site_dir": str(SITE_DIR),
                    "backups": content_cms.backup_status(),
                    "counts": {
                        "sr_characters": len(LEGACY_REPO.characters["sr"]),
                        "gi_characters": len(LEGACY_REPO.characters["gi"]),
                        "sr_weapons": len(LEGACY_REPO.weapons["sr"]),
                        "gi_weapons": len(LEGACY_REPO.weapons["gi"]),
                    },
                    "cms": {
                        "sources": len(CMS_REPO.sources),
                        "editable_sources": sum(1 for s in CMS_REPO.sources.values() if s.editable),
                    },
                    "textmap_shards": textmap_shards.status(),
                }
            self._send_json(payload)
            return

        if path == "/__admin/api/catalog":
            game = (query.get("game", ["sr"])[0] or "sr").strip().lower()
            kind = (query.get("kind", ["character"])[0] or "character").strip().lower()
            q = (query.get("q", [""])[0] or "").strip()
            with REPO_LOCK:
                items = LEGACY_REPO.list_items(kind=kind, game=game, query=q)
            self._send_json({"items": items})
            return

        if path == "/__admin/api/item":
            game = (query.get("game", ["sr"])[0] or "sr").strip().lower()
            kind = (query.get("kind", ["character"])[0] or "character").strip().lower()
            item_id = (query.get("id", [""])[0] or "").strip()
            if not item_id:
                self._send_json({"error": "Missing id"}, HTTPStatus.BAD_REQUEST)
                return
            try:
                with REPO_LOCK:
                    item = LEGACY_REPO.get_item(kind=kind, game=game, item_id=item_id)
            except Exception as exc:
                self._send_json({"error": str(exc)}, HTTPStatus.BAD_REQUEST)
                return
            self._send_json({"item": item})
            return

        if path == "/__admin/api/v2/sources":
            game = (query.get("game", [""])[0] or "").strip().lower()
            locale = (query.get("locale", [""])[0] or "").strip().upper()
            q = (query.get("q", [""])[0] or "").strip()
            with REPO_LOCK:
                sources = CMS_REPO.list_sources(game=game, locale=locale, q=q)
            self._send_json({"sources": sources})
            return

        if path == "/__admin/api/v2/records":
            source_id = (query.get("source_id", [""])[0] or "").strip()
            q = (query.get("q", [""])[0] or "").strip()
            page_raw = (query.get("page", ["1"])[0] or "1").strip()
            page_size_raw = (query.get("page_size", ["50"])[0] or "50").strip()
            if not source_id:
                self._send_json({"error": "Missing source_id"}, HTTPStatus.BAD_REQUEST)
                return
            try:
                page = int(page_raw)
                page_size = int(page_size_raw)
                with REPO_LOCK:
                    payload = CMS_REPO.list_records(
                        source_id=source_id,
                        q=q,
                        page=page,
                        page_size=page_size,
                    )
            except Exception as exc:
                self._send_json({"error": str(exc)}, HTTPStatus.BAD_REQUEST)
                return
            self._send_json(payload)
            return

        if path == "/__admin/api/v2/record":
            source_id = (query.get("source_id", [""])[0] or "").strip()
            record_id = (query.get("record_id", [""])[0] or "").strip()
            if not source_id or not record_id:
                self._send_json({"error": "Missing source_id or record_id"}, HTTPStatus.BAD_REQUEST)
                return
            try:
                with REPO_LOCK:
                    record = CMS_REPO.get_record(source_id=source_id, record_id=record_id)
            except Exception as exc:
                self._send_json({"error": str(exc)}, HTTPStatus.BAD_REQUEST)
                return
            self._send_json({"record": record})
            return

        self._serve_site(path, head_only=False)

    def do_HEAD(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path
        if path in {"/__admin", "/__admin/"}:
            raw = ADMIN_HTML.encode("utf-8")
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(raw)))
            self.end_headers()
            return
        self._serve_site(path, head_only=True)

    def do_POST(self) -> None:
        path = urlparse(self.path).path

        if path == "/__admin/api/reload":
            try:
                with REPO_LOCK:
                    LEGACY_REPO.refresh()
                    CMS_REPO.refresh_registry()
            except Exception as exc:
                self._send_json({"error": str(exc)}, HTTPStatus.BAD_REQUEST)
                return
            self._send_json({"message": "reloaded"})
            return

        if path == "/__admin/api/item":
            body = self._read_json()
            game = str(body.get("game", "sr")).strip().lower()
            kind = str(body.get("kind", "character")).strip().lower()
            item_id = str(body.get("id", "")).strip()
            fields = body.get("fields", {})
            if not item_id:
                self._send_json({"error": "Missing id"}, HTTPStatus.BAD_REQUEST)
                return
            if not isinstance(fields, dict):
                self._send_json({"error": "fields must be object"}, HTTPStatus.BAD_REQUEST)
                return
            try:
                with REPO_LOCK:
                    backup_name = LEGACY_REPO.save_item(
                        kind=kind,
                        game=game,
                        item_id=item_id,
                        fields={k: str(v) for k, v in fields.items()},
                    )
                    CMS_REPO.refresh_registry()
            except Exception as exc:
                self._send_json({"error": str(exc)}, HTTPStatus.BAD_REQUEST)
                return
            self._send_json({"message": f"保存成功，备份: {backup_name}"})
            return

        if path == "/__admin/api/undo":
            try:
                with REPO_LOCK:
                    message = content_cms.undo_backup()
                    LEGACY_REPO.refresh()
                    CMS_REPO.refresh_registry()
            except Exception as exc:
                self._send_json({"code": 1, "message": str(exc)}, HTTPStatus.BAD_REQUEST)
                return
            self._send_json({"code": 0, "message": message})
            return

        if path == "/__admin/api/v2/record/save":
            body = self._read_json()
            source_id = str(body.get("source_id", "")).strip()
            record_id = str(body.get("record_id", "")).strip()
            mode = str(body.get("mode", "form")).strip().lower() or "form"
            fields = body.get("fields", {})
            raw_json = str(body.get("raw_json", ""))
            if not source_id or not record_id:
                self._send_json({"error": "Missing source_id or record_id"}, HTTPStatus.BAD_REQUEST)
                return
            if not isinstance(fields, dict):
                self._send_json({"error": "fields must be object"}, HTTPStatus.BAD_REQUEST)
                return
            try:
                with REPO_LOCK:
                    payload = CMS_REPO.save_record(
                        source_id=source_id,
                        record_id=record_id,
                        fields=fields,
                        raw_json=raw_json,
                        mode=mode,
                    )
                    LEGACY_REPO.refresh()
                    CMS_REPO.refresh_registry()
            except Exception as exc:
                self._send_json({"error": str(exc)}, HTTPStatus.BAD_REQUEST)
                return
            self._send_json(payload)
            return

        if path == "/__admin/api/v2/record/preview-diff":
            body = self._read_json()
            source_id = str(body.get("source_id", "")).strip()
            record_id = str(body.get("record_id", "")).strip()
            mode = str(body.get("mode", "form")).strip().lower() or "form"
            fields = body.get("fields", {})
            raw_json = str(body.get("raw_json", ""))
            if not source_id or not record_id:
                self._send_json({"error": "Missing source_id or record_id"}, HTTPStatus.BAD_REQUEST)
                return
            if not isinstance(fields, dict):
                self._send_json({"error": "fields must be object"}, HTTPStatus.BAD_REQUEST)
                return
            try:
                with REPO_LOCK:
                    payload = CMS_REPO.preview_record_diff(
                        source_id=source_id,
                        record_id=record_id,
                        fields=fields,
                        raw_json=raw_json,
                        mode=mode,
                    )
            except Exception as exc:
                self._send_json({"error": str(exc)}, HTTPStatus.BAD_REQUEST)
                return
            self._send_json(payload)
            return

        if path == "/__admin/api/v2/search-global":
            body = self._read_json()
            q = str(body.get("q", "")).strip()
            limit = int(body.get("limit", 200) or 200)
            try:
                with REPO_LOCK:
                    payload = CMS_REPO.search_global(q=q, limit=limit)
            except Exception as exc:
                self._send_json({"error": str(exc)}, HTTPStatus.BAD_REQUEST)
                return
            self._send_json(payload)
            return

        if path == "/__admin/api/v2/undo":
            body = self._read_json()
            backup_id = str(body.get("backup_id", "")).strip() or None
            try:
                with REPO_LOCK:
                    message = content_cms.undo_backup(backup_id=backup_id)
                    LEGACY_REPO.refresh()
                    CMS_REPO.refresh_registry()
            except Exception as exc:
                self._send_json({"code": 1, "message": str(exc)}, HTTPStatus.BAD_REQUEST)
                return
            self._send_json({"code": 0, "message": message})
            return

        if path == "/__admin/api/v2/rebuild-index":
            try:
                with REPO_LOCK:
                    payload = CMS_REPO.rebuild_index()
                    LEGACY_REPO.refresh()
                    CMS_REPO.refresh_registry()
            except Exception as exc:
                self._send_json({"error": str(exc)}, HTTPStatus.BAD_REQUEST)
                return
            self._send_json(payload)
            return

        self._send_json({"error": "Not found"}, HTTPStatus.NOT_FOUND)

    def _serve_site(self, path: str, head_only: bool = False) -> None:
        if not SITE_DIR.exists():
            self._send_text("site/ directory not found.", HTTPStatus.NOT_FOUND)
            return

        if path == "/":
            self._redirect("/index/")
            return
        if path == "/home":
            self._redirect("/index/")
            return

        rel = unquote(path).lstrip("/")
        target = (SITE_DIR / rel).resolve()
        site_root = SITE_DIR.resolve()
        if site_root not in target.parents and target != site_root:
            self._send_text("Invalid path", HTTPStatus.BAD_REQUEST)
            return

        if target.is_dir():
            target = target / "index.html"
        elif not target.is_file() and (target / "index.html").is_file():
            target = target / "index.html"

        if not target.exists() or not target.is_file():
            self._send_text("404 Not Found", HTTPStatus.NOT_FOUND)
            return

        guessed = mimetypes.guess_type(str(target))[0] or "application/octet-stream"
        ctype = _response_charset_type(target, guessed)

        try:
            raw = target.read_bytes()
        except OSError:
            self._send_text("500 Internal Server Error", HTTPStatus.INTERNAL_SERVER_ERROR)
            return

        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        if not head_only:
            self._safe_write(raw)

    def _read_json(self) -> dict:
        length = int(self.headers.get("Content-Length", "0") or 0)
        raw = self.rfile.read(length) if length > 0 else b"{}"
        try:
            data = json.loads(raw.decode("utf-8"))
            return data if isinstance(data, dict) else {}
        except Exception:
            return {}

    def _send_json(self, payload: dict, status: HTTPStatus = HTTPStatus.OK) -> None:
        raw = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self._safe_write(raw)

    def _send_html(self, html: str) -> None:
        raw = html.encode("utf-8")
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self._safe_write(raw)

    def _send_text(self, text: str, status: HTTPStatus = HTTPStatus.OK) -> None:
        raw = text.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self._safe_write(raw)

    def _safe_write(self, raw: bytes) -> None:
        try:
            self.wfile.write(raw)
        except (BrokenPipeError, ConnectionResetError, OSError):
            return

    def _redirect(self, location: str) -> None:
        self.send_response(HTTPStatus.FOUND)
        self.send_header("Location", location)
        self.end_headers()

    def log_message(self, fmt: str, *args) -> None:
        return


def main() -> int:
    parser = argparse.ArgumentParser(description="HomDGCat local visual backend")
    parser.add_argument("--port", type=int, default=9000)
    args = parser.parse_args()

    server = ThreadingHTTPServer(("0.0.0.0", args.port), Handler)
    print("=" * 60)
    print("HomDGCat Local Visual Backend")
    print("=" * 60)
    print(f"Website: http://localhost:{args.port}/index/")
    print(f"Admin:   http://localhost:{args.port}/__admin")
    print("Press Ctrl+C to stop")
    print("=" * 60)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
