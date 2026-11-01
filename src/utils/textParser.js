// Text and document utilities for EvalLens

export const MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024; // 10 MB
export const MAX_SUBMISSION_WORDS = 5000;

export const SUPPORTED_EXTENSIONS = [
  'txt', 'md', 'pdf', 'docx', 'py', 'cpp', 'h', 'hpp', 
  'java', 'js', 'ts', 'json', 'html', 'css', 'sql'
];

/**
 * Accurately counts words matching Python split() behavior
 */
export function countWords(text = '') {
  if (!text || typeof text !== 'string') return 0;
  const tokens = text.trim().split(/\s+/);
  return tokens.length === 1 && tokens[0] === '' ? 0 : tokens.length;
}

/**
 * Suggests an evaluation title from the first heading, title tag, or filename
 */
export function suggestEvaluationTitle(filename = '', text = '') {
  if (text) {
    const lines = text.split('\n');
    for (const rawLine of lines) {
      let line = rawLine.trim().replace(/^#+\s*/, '').trim();
      if (line.startsWith('<title>') && line.endsWith('</title>')) {
        line = line.replace(/<\/?title>/g, '').trim();
      }
      if (line && !line.startsWith('---') && !line.startsWith('===') && !line.startsWith('L1:')) {
        return line.slice(0, 100);
      }
    }
  }
  if (filename) {
    const dotIdx = filename.lastIndexOf('.');
    return dotIdx > 0 ? filename.slice(0, dotIdx) : filename;
  }
  return 'Untitled Evaluation';
}

/**
 * Reads a text-based File object directly in the browser
 */
export async function readFileContent(file) {
  if (!file) throw new Error('No file provided');
  if (file.size > MAX_FILE_SIZE_BYTES) {
    throw new Error(`File exceeds the 10 MB limit (${(file.size / (1024 * 1024)).toFixed(1)} MB)`);
  }

  const ext = file.name.split('.').pop()?.toLowerCase() || '';
  
  // Direct text reader for source code, markdown, json, txt, etc.
  if (['txt', 'md', 'py', 'cpp', 'h', 'hpp', 'java', 'js', 'ts', 'json', 'html', 'css', 'sql'].includes(ext)) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = (e) => resolve(e.target.result || '');
      reader.onerror = () => reject(new Error('Failed to read text file'));
      reader.readAsText(file);
    });
  }

  // Binary types (DOCX, PDF) in pure browser:
  // If the user uploads a PDF or DOCX, we attempt to read text or provide an informative note
  return new Promise((resolve) => {
    const reader = new FileReader();
    reader.onload = (e) => {
      const arrayBuffer = e.target.result;
      // Simple text extract attempt for text streams in binary
      try {
        const textDecoder = new TextDecoder('utf-8', { fatal: false });
        const raw = textDecoder.decode(arrayBuffer);
        // Clean out null bytes and non-printable noise
        const cleaned = raw.replace(/[\x00-\x08\x0B\x0C\x0E-\x1F\x7F-\x9F]/g, ' ');
        // Keep recognizable words
        const words = cleaned.match(/[A-Za-z0-9_.,!?'"()\-:;]{2,}/g) || [];
        if (words.length > 50) {
          resolve(words.join(' '));
          return;
        }
      } catch (err) {
        // fallback
      }
      resolve(`[Extracted from binary ${file.name}] - Document contains formatted binary streams.`);
    };
    reader.readAsArrayBuffer(file);
  });
}

