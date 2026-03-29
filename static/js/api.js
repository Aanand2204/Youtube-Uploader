// JS API Service
import { CONFIG } from './constants.js';

export const API = {
  async processVideo(file) {
    const form = new FormData();
    form.append('file', file);
    const res = await fetch(CONFIG.endpoints.process, { method: 'POST', body: form });
    return { ok: res.ok, status: res.status, data: await res.json() };
  },

  async publishVideo(payload) {
    const res = await fetch(CONFIG.endpoints.publish, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    return { ok: res.ok, status: res.status, data: await res.json() };
  },

  async fetchLogs(lines = 150) {
    const res = await fetch(`${CONFIG.endpoints.logs}?lines=${lines}`);
    return await res.json();
  }
};
