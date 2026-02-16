import { browser } from '$app/environment';

export const API_BASE_URL = 'http://localhost:8000';

export interface ApiResponse<T = any> {
    Message: string;
    Data: T;
    ErrorCode: number;
}

export interface UserQuery {
    id: number;
    user_id: number;
    query_text: string;
    status: string;
    reply: string | null;
    reply_time: string | null;
}

export interface Feedback {
    user_name: string;
    user_id: number;
    rating: number;
    comment: string | null;
    comment_time: string;
}

async function request<T>(path: string, options: RequestInit = {}): Promise<ApiResponse<T>> {
    const headers = new Headers(options.headers);

    if (browser) {
        const apiKey = localStorage.getItem('api_key');
        if (apiKey) {
            headers.set('X-API-Key', apiKey);
        }
    }

    if (options.body && !(options.body instanceof FormData)) {
        headers.set('Content-Type', 'application/json');
    }

    const response = await fetch(`${API_BASE_URL}${path}`, {
        ...options,
        headers
    });

    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
}

export const api = {
    login: (credentials: any) => request<{ api_key: string }>('/login', {
        method: 'POST',
        body: JSON.stringify(credentials)
    }),

    getQueries: () => request<{ queries: UserQuery[] }>('/support/queries/get', {
        method: 'POST'
    }),

    replyToQuery: (queryId: number, reply: string) => request('/support/queries/reply', {
        method: 'POST',
        body: JSON.stringify({ query_id: queryId, reply })
    }),

    getFeedbacks: () => request<{ feedbacks: Feedback[] }>('/support/feedback/get_all', {
        method: 'POST'
    })
};
