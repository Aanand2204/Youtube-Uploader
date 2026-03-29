// JS Constants & Config
export const CONFIG = {
  selectors: {
    dropZone: 'drop-zone',
    fileInput: 'file-input',
    fileInfo: 'file-info',
    fileName: 'file-name',
    fileSize: 'file-size',
    uploadBtn: 'upload-btn',
    btnText: 'btn-text',
    progressBar: 'progress-bar',
    progressBarWrap: 'progress-bar-wrap',
    errorBox: 'error-box',
    errorMsg: 'error-msg',
    resultSection: 'result-section',
    resultTitle: 'result-card-title',
    resultUrlBox: 'result-url-box',
    publishBtn: 'publish-btn',
    ytLink: 'yt-link',
    editTitle: 'edit-title',
    editDesc: 'edit-desc',
    editTags: 'edit-tags',
    metaTranscript: 'meta-transcript',
    metaDuration: 'meta-duration',
    logContainer: 'log-container',
    logCount: 'log-count',
    autoRefreshBtn: 'auto-refresh-btn'
  },
  endpoints: {
    process: '/api/v1/process-video',
    publish: '/api/v1/publish-video',
    logs: '/api/v1/logs'
  },
  timers: {
    logRefresh: 2000,
    fakeStepIntervals: [4000, 20000, 15000]
  }
};
