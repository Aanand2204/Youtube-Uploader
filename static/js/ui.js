// JS UI Controller
import { CONFIG } from './constants.js';
import { Utils } from './utils.js';

export const UI = {
  get(id) { return document.getElementById(CONFIG.selectors[id]); },

  setFile(file) {
    const dz = this.get('dropZone');
    dz.classList.add('has-file');
    dz.querySelector('.drop-icon').textContent = '✅';
    dz.querySelector('.drop-title').textContent = 'Video selected';

    this.get('fileInfo').classList.add('visible');
    this.get('fileName').textContent = file.name;
    this.get('fileSize').textContent = Utils.formatBytes(file.size);

    const btn = this.get('uploadBtn');
    btn.disabled = false;
    this.get('btnText').textContent = '🚀  Upload & Publish to YouTube';
    
    this.hideError();
    this.resetSteps();
    this.get('resultSection').classList.remove('visible');
  },

  clearFile() {
    document.getElementById(CONFIG.selectors.fileInput).value = '';
    const dz = this.get('dropZone');
    dz.classList.remove('has-file');
    dz.querySelector('.drop-icon').textContent = '☁️';
    dz.querySelector('.drop-title').textContent = 'Drop your video here';
    
    this.get('fileInfo').classList.remove('visible');
    
    const btn = this.get('uploadBtn');
    btn.disabled = true;
    this.get('btnText').textContent = 'Select a video to upload';
    
    this.resetSteps();
    this.hideError();
  },

  resetSteps() {
    [1, 2, 3, 4].forEach(n => {
      const el = document.getElementById(`step-${n}`);
      el.className = 'step-card';
      document.getElementById(`step-${n}-status`).textContent = 'Waiting';
      document.getElementById(`step-${n}-time`).textContent = '';
    });
    this.get('progressBar').style.width = '0%';
    this.get('progressBarWrap').classList.remove('visible');
  },

  updateStep(n, status) {
    if (n < 1 || n > 4) return;
    const el = document.getElementById(`step-${n}`);
    const statusEl = document.getElementById(`step-${n}-status`);
    
    el.classList.remove('active', 'done', 'error');
    
    if (status === 'active') {
      el.classList.add('active');
      statusEl.innerHTML = '<span class="spinner"></span> Running…';
    } else if (status === 'done') {
      el.classList.add('done');
      statusEl.textContent = '✔ Complete';
    } else if (status === 'error') {
      el.classList.add('error');
      statusEl.textContent = '✕ Failed';
    }
  },

  showError(msg) {
    this.get('errorBox').classList.add('visible');
    this.get('errorMsg').textContent = msg;
  },

  hideError() {
    this.get('errorBox').classList.remove('visible');
  },

  showReview(data) {
    this.get('resultSection').classList.add('visible');
    this.get('editTitle').value = data.title || '';
    this.get('editDesc').value = data.description || '';
    this.get('editTags').value = (data.tags || []).join(', ');
    this.get('metaTranscript').textContent = data.transcript_preview || '—';
    this.get('metaDuration').textContent = data.duration_seconds + 's';
    this.get('resultSection').scrollIntoView({ behavior: 'smooth' });
  },

  showSuccess(data) {
    this.get('resultTitle').textContent = '✅ Upload Successful';
    this.get('resultUrlBox').style.display = 'flex';
    this.get('publishBtn').style.display = 'none';
    this.get('ytLink').href = data.youtube_url;
    this.get('ytLink').textContent = data.youtube_url;
    
    ['editTitle', 'editDesc', 'editTags'].forEach(id => this.get(id).disabled = true);
  },

  renderLogs(lines) {
    const container = this.get('logContainer');
    if (!lines.length) {
      container.innerHTML = '<div class="log-empty">No logs yet…</div>';
      return;
    }
    container.innerHTML = lines.map(l => {
      let cls = 'log-INFO';
      if (l.includes('ERROR'))   cls = 'log-ERROR';
      else if (l.includes('WARNING')) cls = 'log-WARNING';
      else if (l.includes('DEBUG'))   cls = 'log-DEBUG';
      return `<div class="log-line ${cls}">${Utils.escHtml(l)}</div>`;
    }).join('');
    container.scrollTop = container.scrollHeight;
  },

  animateProgressBar(pb, isUploading) {
    let pct = 0;
    const step = () => {
      if (!isUploading()) return;
      pct = Math.min(pct + Math.random() * 0.8, 98);
      pb.style.width = pct + '%';
      setTimeout(step, 600);
    };
    step();
  }
};
