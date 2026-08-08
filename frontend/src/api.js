const API_BASE = '/api';

export async function checkHealth() {
  try {
    const res = await fetch(`${API_BASE}/health`);
    if (!res.ok) throw new Error('Backend unavailable');
    return await res.json();
  } catch (err) {
    return { status: 'offline', error: err.message };
  }
}

export async function predictScore(studentData) {
  const res = await fetch(`${API_BASE}/predict`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(studentData),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || 'Prediction request failed');
  }
  return await res.json();
}

export async function predictBatch(file) {
  const formData = new FormData();
  formData.append('file', file);

  const res = await fetch(`${API_BASE}/predict-batch`, {
    method: 'POST',
    body: formData,
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || 'Batch processing failed');
  }
  return await res.json();
}

export async function getStats() {
  const res = await fetch(`${API_BASE}/stats`);
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || 'Failed to fetch dataset stats');
  }
  return await res.json();
}

export async function getModelInfo() {
  const res = await fetch(`${API_BASE}/model-info`);
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || 'Failed to fetch model info');
  }
  return await res.json();
}

export async function trainModel() {
  const res = await fetch(`${API_BASE}/train`, {
    method: 'POST',
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || 'Model retraining failed');
  }
  return await res.json();
}
