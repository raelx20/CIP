const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface RequestOptions {
  method?: string;
  body?: unknown;
  headers?: Record<string, string>;
  token?: string;
}

export async function apiClient<T>(
  endpoint: string,
  options: RequestOptions = {}
): Promise<T> {
  const { method = 'GET', body, headers = {}, token } = options;

  const requestHeaders: Record<string, string> = {
    'Content-Type': 'application/json',
    ...headers,
  };

  if (token) {
    requestHeaders['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE}${endpoint}`, {
    method,
    headers: requestHeaders,
    body: body ? JSON.stringify(body) : undefined,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Request failed' }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }

  if (response.status === 204) {
    return null as T;
  }

  return response.json();
}

export const auth = {
  login: (email: string, password: string) =>
    apiClient<{ access_token: string; token_type: string; user: User }>('/api/v1/auth/login', {
      method: 'POST',
      body: { email, password },
    }),
  register: (data: RegisterRequest) =>
    apiClient<User>('/api/v1/auth/register', { method: 'POST', body: data }),
};

export const citizen = {
  submit: (data: SubmissionCreate, token: string) =>
    apiClient<Submission>('/api/v1/citizen/submissions', { method: 'POST', body: data, token }),
  getSubmission: (id: string, token: string) =>
    apiClient<Submission>(`/api/v1/citizen/submissions/${id}`, { token }),
  getStatus: (id: string, token: string) =>
    apiClient<SubmissionStatus>(`/api/v1/citizen/submissions/${id}/status`, { token }),
  chat: (data: ChatMessage, token: string) =>
    apiClient<ChatResponse>('/api/v1/citizen/chat', { method: 'POST', body: data, token }),
  getMyIssues: (token: string) =>
    apiClient<{ issues: IssueCluster[]; total: number; message: string }>('/api/v1/citizen/my-issues', { token }),
};

export const mp = {
  getDashboard: (token: string) =>
    apiClient<Dashboard>('/api/v1/mp/dashboard', { token }),
  getIssues: (params: string, token: string) =>
    apiClient<IssueListResponse>(`/api/v1/mp/issues?${params}`, { token }),
  getIssueDetail: (id: string, token: string) =>
    apiClient<IssueDetail>(`/api/v1/mp/issues/${id}`, { token }),
  getPriorities: (params: string, token: string) =>
    apiClient<PriorityResponse>(`/api/v1/mp/priorities?${params}`, { token }),
  getHotspots: (params: string, token: string) =>
    apiClient<{ hotspots: Hotspot[] }>(`/api/v1/mp/hotspots?${params}`, { token }),
  copilot: (data: CopilotQuery, token: string) =>
    apiClient<CopilotResponse>('/api/v1/mp/copilot', { method: 'POST', body: data, token }),
};

export const admin = {
  getDashboard: (token: string) =>
    apiClient<Dashboard>('/api/v1/admin/dashboard', { token }),
  getIssues: (params: string, token: string) =>
    apiClient<IssueListResponse>(`/api/v1/admin/issues?${params}`, { token }),
  getIssueDetail: (id: string, token: string) =>
    apiClient<IssueDetail>(`/api/v1/admin/issues/${id}`, { token }),
  getPriorities: (params: string, token: string) =>
    apiClient<PriorityResponse>(`/api/v1/admin/priorities?${params}`, { token }),
  copilot: (data: CopilotQuery, token: string) =>
    apiClient<CopilotResponse>('/api/v1/admin/copilot', { method: 'POST', body: data, token }),
};

export const system = {
  health: () => apiClient<{ status: string }>('/api/v1/system/health'),
  ready: () => apiClient<{ status: string; database: string }>('/api/v1/system/ready'),
};

export interface User {
  id: string;
  email: string;
  full_name: string;
  role: 'citizen' | 'mp' | 'officer' | 'admin';
  is_active: boolean;
  phone?: string;
  constituency?: string;
  district?: string;
  state?: string;
  created_at: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  full_name: string;
  role?: string;
  phone?: string;
  constituency?: string;
  district?: string;
  state?: string;
}

export interface Submission {
  id: string;
  status: string;
  source_modality: string;
  original_content: string;
  normalized_content?: string;
  detected_language?: string;
  category?: string;
  subcategory?: string;
  severity?: number;
  urgency?: number;
  created_at: string;
  updated_at: string;
}

export interface SubmissionCreate {
  citizen_id: string;
  content: string;
  source_modality?: string;
  source_channel?: string;
  language?: string;
  gps_permission_granted?: boolean;
  sender_latitude?: number;
  sender_longitude?: number;
  sender_gps_accuracy?: number;
}

export interface SubmissionStatus {
  submission_id: string;
  status: string;
  progress: number;
  status_message: string;
  created_at: string;
  updated_at: string;
}

export interface ChatMessage {
  role: 'citizen' | 'assistant';
  content: string;
  detected_language?: string;
  timestamp?: string;
}

export interface ChatResponse {
  message: ChatMessage;
  submission_id?: string;
  status?: string;
  requires_clarification: boolean;
  clarification_questions: string[];
}

export interface IssueCluster {
  id: string;
  title: string;
  summary?: string;
  category: string;
  subcategory?: string;
  latitude?: number;
  longitude?: number;
  formatted_address?: string;
  raw_submission_count: number;
  trusted_demand: number;
  suspicious_demand: number;
  affected_population?: number;
  severity?: number;
  urgency?: number;
  lifecycle_state: string;
  confidence: number;
  first_reported: string;
  latest_report: string;
  created_at: string;
}

export interface IssueDetail extends IssueCluster {
  administrative_areas?: string[];
  supporting_evidence?: Record<string, unknown>[];
  contradictory_evidence?: Record<string, unknown>[];
  demand_velocity?: number;
  persistence?: string;
}

export interface IssueListResponse {
  issues: IssueCluster[];
  total: number;
  skip: number;
  limit: number;
}

export interface Dashboard {
  total_submissions: number;
  pending_review: number;
  active_clusters: number;
  high_priority: number;
  issues_by_category: { category: string; count: number }[];
  recent_submissions: number;
  avg_priority_score?: number;
}

export interface PriorityResponse {
  rankings: PriorityRanking[];
  total: number;
  skip: number;
  limit: number;
  scoring_version: string;
}

export interface PriorityRanking {
  id: string;
  cluster_id: string;
  final_score: number;
  priority_level: string;
  rank?: number;
  scoring_version: string;
  components?: ScoreComponent[];
  reasoning?: string;
  calculation_timestamp: string;
  created_at: string;
}

export interface ScoreComponent {
  dimension: string;
  raw_value: number;
  normalized_value: number;
  weight: number;
  weighted_score: number;
  description?: string;
}

export interface Hotspot {
  latitude: number;
  longitude: number;
  cluster_id: string;
  title: string;
  category: string;
  submission_count: number;
  severity?: number;
  urgency?: number;
}

export interface CopilotQuery {
  query: string;
  constituency?: string;
  category_filter?: string;
  time_window_days?: number;
}

export interface CopilotResponse {
  answer: string;
  citations?: CopilotCitation[];
  uncertainty?: string;
  sources_used?: string[];
}

export interface CopilotCitation {
  evidence_id: string;
  source_type: string;
  source_name: string;
  excerpt: string;
  confidence: number;
}
