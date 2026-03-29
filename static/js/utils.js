// JS Utils
export const Utils = {
  formatBytes(b) {
    if (b < 1024) return b + ' B';
    if (b < 1024**2) return (b/1024).toFixed(1) + ' KB';
    return (b/1024**2).toFixed(1) + ' MB';
  },
  
  escHtml(s) {
    return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
  },
  
  sleep(ms) {
    return new Promise(r => setTimeout(r, ms));
  }
};
