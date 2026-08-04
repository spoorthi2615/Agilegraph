import { supabase } from '../lib/supabase';

export class ApiError extends Error {
  status: number;
  code: string;
  details?: any;

  constructor(status: number, message: string, code: string = 'UNKNOWN_ERROR', details?: any) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.code = code;
    this.details = details;
  }
}

export interface RequestOptions extends Omit<RequestInit, 'body'> {
  body?: any;
  queryParams?: Record<string, string | number | boolean | undefined>;
  timeout?: number;
}

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1";

const DEFAULT_TIMEOUT = 30000; // 30 seconds

async function handleResponse<T>(response: Response): Promise<T> {
  const isJson = response.headers.get("content-type")?.includes("application/json");
  let data: any = null;

  if (response.status !== 204 && isJson) {
    try {
      data = await response.json();
    } catch (err) {
      data = null;
    }
  }

  if (response.ok) {
    return data as T;
  }

  // Parse error
  const message = data?.message || data?.detail || response.statusText || `HTTP Error ${response.status}`;
  const code = data?.code || `HTTP_${response.status}`;
  const details = data?.details || data;

  throw new ApiError(response.status, message, code, details);
}

export async function request<T>(endpoint: string, options: RequestOptions = {}): Promise<T> {
  const {
    body,
    queryParams,
    timeout = DEFAULT_TIMEOUT,
    headers: customHeaders,
    ...customConfig
  } = options;

  // Build URL with query params
  // If endpoint is a full URL, use it directly, else prepend API_BASE_URL
  const baseUrl = endpoint.startsWith('http') ? endpoint : `${API_BASE_URL}${endpoint.startsWith('/') ? '' : '/'}${endpoint}`;
  const url = new URL(baseUrl);
  
  if (queryParams) {
    Object.entries(queryParams).forEach(([key, value]) => {
      if (value !== undefined) {
        url.searchParams.append(key, String(value));
      }
    });
  }

  const controller = new AbortController();
  const id = setTimeout(() => controller.abort(), timeout);

  // Link user-provided signal if present
  if (customConfig.signal) {
    customConfig.signal.addEventListener('abort', () => {
      controller.abort();
    });
  }

  const headers = new Headers(customHeaders as HeadersInit);
  
  // Attach Supabase Auth Token
  const { data: { session } } = await supabase.auth.getSession();
  if (session?.access_token) {
    headers.set('Authorization', `Bearer ${session.access_token}`);
  }
  
  let fetchBody: BodyInit | null = null;
  
  if (body) {
    if (body instanceof FormData) {
      fetchBody = body;
      // Do not set Content-Type for FormData, browser sets it automatically with the correct boundary
    } else {
      fetchBody = JSON.stringify(body);
      if (!headers.has('Content-Type')) {
        headers.set('Content-Type', 'application/json');
      }
    }
  }

  try {
    const response = await fetch(url.toString(), {
      ...customConfig,
      headers,
      body: fetchBody,
      signal: controller.signal,
    });
    clearTimeout(id);
    return await handleResponse<T>(response);
  } catch (error: any) {
    clearTimeout(id);
    if (error.name === 'AbortError') {
      throw new ApiError(408, "Request Timeout", "TIMEOUT_ERROR");
    }
    if (error instanceof ApiError) {
      throw error;
    }
    throw new ApiError(500, error.message || "Network Error", "NETWORK_ERROR");
  }
}

export const apiClient = {
  get: <T>(endpoint: string, options?: Omit<RequestOptions, 'body'>) => 
    request<T>(endpoint, { ...options, method: 'GET' }),
  post: <T>(endpoint: string, options?: RequestOptions) => 
    request<T>(endpoint, { ...options, method: 'POST' }),
  put: <T>(endpoint: string, options?: RequestOptions) => 
    request<T>(endpoint, { ...options, method: 'PUT' }),
  patch: <T>(endpoint: string, options?: RequestOptions) => 
    request<T>(endpoint, { ...options, method: 'PATCH' }),
  delete: <T>(endpoint: string, options?: Omit<RequestOptions, 'body'>) => 
    request<T>(endpoint, { ...options, method: 'DELETE' }),
};
