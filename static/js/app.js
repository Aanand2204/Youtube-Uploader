// YouTube Auto-Uploader — Main Entry Module
import { CONFIG } from './constants.js';
import { Utils } from './utils.js';
import { API } from './api.js';
import { UI } from './ui.js';

// ── State Management ───────────────────────────────────────────────────────
const State = {
  selectedFile: null,
  isUploading: false,
  currentVideoId: null,
  currentStep: 0,
  autoRefreshOn: false,
  autoRefreshTimer: null,
  fakeStepTimer: null,

  reset() {
    this.selectedFile = null;
    this.isUploading = false;
    this.currentVideoId = null;
    this.currentStep = 0;
  }
};

// ── App Controller ─────────────────────────────────────────────────────────
const App = {
  init() {
    this.bindEvents();
  },

  bindEvents() {
    const dz = UI.get('dropZone');
    const fi = UI.get('fileInput');

    dz.addEventListener('dragover', e => { e.preventDefault(); dz.classList.add('drag-over'); });
    dz.addEventListener('dragleave', () => dz.classList.remove('drag-over'));
    dz.addEventListener('drop', e => {
      e.preventDefault();
      dz.classList.remove('drag-over');
      const f = e.dataTransfer.files[0];
      if (f) this.handleFileSelect(f);
    });
    fi.addEventListener('change', () => {
      if (fi.files[0]) this.handleFileSelect(fi.files[0]);
    });

    // Global window exports for inline HTML handlers (legacy compatibility)
    window.setFile = this.handleFileSelect.bind(this);
    window.clearFile = this.handleFileClear.bind(this);
    window.startUpload = this.handleUpload.bind(this);
    window.startPublishing = this.handlePublish.bind(this);
    window.copyUrl = this.handleCopyUrl.bind(this);
    window.fetchLogs = this.handleFetchLogs.bind(this);
    window.toggleAutoRefresh = this.handleToggleAutoRefresh.bind(this);
    window.clearLogView = () => UI.get('logContainer').innerHTML = '<div class="log-empty">Log view cleared. Press Refresh to reload.</div>';
  },

  handleFileSelect(file) {
    State.selectedFile = file;
    UI.setFile(file);
  },

  handleFileClear() {
    State.reset();
    UI.clearFile();
  },

  async handleUpload() {
    if (!State.selectedFile || State.isUploading) return;
    
    State.isUploading = true;
    UI.hideError();
    UI.get('resultSection').classList.remove('visible');
    UI.get('resultTitle').textContent = '📝 Review AI Suggestions';
    UI.get('resultUrlBox').style.display = 'none';
    
    const pBtn = UI.get('publishBtn');
    pBtn.style.display = 'block';
    pBtn.disabled = false;
    pBtn.innerHTML = '🚀 Confirm & Publish to YouTube';

    UI.resetSteps();

    const uBtn = UI.get('uploadBtn');
    uBtn.disabled = true;
    uBtn.classList.add('loading');
    UI.get('btnText').innerHTML = '<span class="spinner"></span> Processing…';

    UI.get('progressBarWrap').classList.add('visible');
    
    this.simulateProcessing();
    UI.animateProgressBar(UI.get('progressBar'), () => State.isUploading);

    try {
      const { ok, data } = await API.processVideo(State.selectedFile);
      this.clearSimulations();

      if (!ok) {
        UI.showError(data.detail || 'Processing failed.');
        UI.updateStep(State.currentStep || 1, 'error');
        UI.get('progressBar').style.width = '0%';
      } else {
        State.currentVideoId = data.video_id;
        [1, 2, 3].forEach(n => UI.updateStep(n, 'done'));
        UI.updateStep(4, 'active');
        
        UI.get('progressBar').style.width = '100%';
        await Utils.sleep(300);
        UI.showReview(data);
        this.handleFetchLogs();
      }
    } catch (err) {
      this.clearSimulations();
      UI.showError('Network error: ' + err.message);
      UI.updateStep(State.currentStep || 1, 'error');
    } finally {
      State.isUploading = false;
      uBtn.disabled = false;
      uBtn.classList.remove('loading');
      UI.get('btnText').textContent = '🎬 Process Another Video';
    }
  },

  async handlePublish() {
    if (!State.currentVideoId || State.isUploading) return;

    const pBtn = UI.get('publishBtn');
    pBtn.disabled = true;
    pBtn.innerHTML = '<span class="spinner"></span> Publishing...';

    const payload = {
      video_id: State.currentVideoId,
      title: UI.get('editTitle').value,
      description: UI.get('editDesc').value,
      tags: UI.get('editTags').value.split(',').map(t => t.trim()).filter(t => t)
    };

    try {
      const { ok, data } = await API.publishVideo(payload);
      if (!ok) {
        UI.showError(data.detail || 'Publishing failed.');
        UI.updateStep(4, 'error');
        pBtn.disabled = false;
        pBtn.textContent = '❌ Try Publishing Again';
      } else {
        UI.updateStep(4, 'done');
        UI.showSuccess(data);
        this.handleFetchLogs();
      }
    } catch (err) {
      UI.showError('Network error during publishing: ' + err.message);
      UI.updateStep(4, 'error');
      pBtn.disabled = false;
    }
  },

  async handleFetchLogs() {
    try {
      const data = await API.fetchLogs();
      UI.renderLogs(data.lines || []);
      UI.get('logCount').textContent = data.total + ' lines';
    } catch {}
  },

  handleToggleAutoRefresh() {
    State.autoRefreshOn = !State.autoRefreshOn;
    const btn = UI.get('autoRefreshBtn');
    
    if (State.autoRefreshOn) {
      btn.classList.add('active-auto');
      btn.textContent = '⟳ Auto ON';
      State.autoRefreshTimer = setInterval(() => this.handleFetchLogs(), CONFIG.timers.logRefresh);
      this.handleFetchLogs();
    } else {
      btn.classList.remove('active-auto');
      btn.textContent = '⟳ Auto';
      clearInterval(State.autoRefreshTimer);
    }
  },

  handleCopyUrl() {
    const url = UI.get('ytLink').href;
    navigator.clipboard.writeText(url).then(() => {
      const btn = document.querySelector('.copy-btn');
      const oldText = btn.textContent;
      btn.textContent = '✅ Copied!';
      setTimeout(() => btn.textContent = oldText, 2000);
    });
  },

  simulateProcessing() {
    UI.updateStep(1, 'active');
    let elapsed = 0;
    CONFIG.timers.fakeStepIntervals.forEach((dur, i) => {
      elapsed += dur;
      State.fakeStepTimer = setTimeout(() => {
        if (State.isUploading && i < 2) {
          UI.updateStep(i + 1, 'done');
          UI.updateStep(i + 2, 'active');
          State.currentStep = i + 2;
        }
      }, elapsed);
    });
  },

  clearSimulations() {
    clearTimeout(State.fakeStepTimer);
  }
};

// Initialize
document.addEventListener('DOMContentLoaded', () => App.init());
