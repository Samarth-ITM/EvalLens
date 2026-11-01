import { INITIAL_EVALUATIONS } from '../data/sampleEvaluations';

const EVALS_KEY = 'evallens_evaluations';
const SETTINGS_KEY = 'evallens_settings';
const AUTH_KEY = 'evallens_authenticated';

export function getSettings() {
  try {
    const raw = localStorage.getItem(SETTINGS_KEY);
    if (!raw) {
      return {
        geminiApiKey: '',
        geminiModel: 'gemini-2.5-flash',
        passkey: 'evallens2026'
      };
    }
    return JSON.parse(raw);
  } catch (e) {
    return { geminiApiKey: '', geminiModel: 'gemini-2.5-flash', passkey: 'evallens2026' };
  }
}

export function saveSettings(settings) {
  localStorage.setItem(SETTINGS_KEY, JSON.stringify(settings));
}

export function isAuthenticated() {
  return sessionStorage.getItem(AUTH_KEY) === 'true';
}

export function setAuthenticated(isAuth) {
  if (isAuth) {
    sessionStorage.setItem(AUTH_KEY, 'true');
  } else {
    sessionStorage.removeItem(AUTH_KEY);
  }
}

export function getEvaluations() {
  try {
    const raw = localStorage.getItem(EVALS_KEY);
    if (!raw) {
      localStorage.setItem(EVALS_KEY, JSON.stringify(INITIAL_EVALUATIONS));
      return INITIAL_EVALUATIONS;
    }
    return JSON.parse(raw);
  } catch (e) {
    return INITIAL_EVALUATIONS;
  }
}

export function getEvaluation(id) {
  const all = getEvaluations();
  return all.find((item) => item.id === id) || null;
}

export function saveEvaluation(evalObj) {
  const all = getEvaluations();
  const existingIdx = all.findIndex((item) => item.id === evalObj.id);
  let updated;
  if (existingIdx >= 0) {
    updated = [...all];
    updated[existingIdx] = evalObj;
  } else {
    updated = [evalObj, ...all];
  }
  localStorage.setItem(EVALS_KEY, JSON.stringify(updated));
  return evalObj;
}

export function deleteEvaluation(id) {
  const all = getEvaluations();
  const filtered = all.filter((item) => item.id !== id);
  localStorage.setItem(EVALS_KEY, JSON.stringify(filtered));
  return filtered;
}

export function resetToDemoData() {
  localStorage.setItem(EVALS_KEY, JSON.stringify(INITIAL_EVALUATIONS));
  return INITIAL_EVALUATIONS;
}

