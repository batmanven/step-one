import { Output, ProcessResponse } from "@/types";

const API_BASE = '/api/v1';

export async function processDataset(datasetName: string): Promise<ProcessResponse> {
  const res = await fetch(`${API_BASE}/process/${datasetName}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
  });
  if (!res.ok) throw new Error('Failed to start processing');
  return res.json();
}

export async function getSessionStatus(sessionId: string): Promise<Output> {
  const res = await fetch(`${API_BASE}/process/${sessionId}/status`);
  if (!res.ok) throw new Error('Failed to get status');
  return res.json();
}

export async function getHealth(): Promise<{ status: string }> {
  const res = await fetch('/health');
  if (!res.ok) throw new Error('API is not reachable');
  return res.json();
}
