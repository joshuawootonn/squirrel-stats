interface Site {
  id: string;
  name: string;
  identifier: string;
  created_at: string;
  updated_at: string;
  pageview_count: number;
}

interface HourlyData {
  hour: string;
  hour_display: string;
  pageviews: number;
  unique_sessions: number;
}

interface DailyData {
  day: string;
  day_display: string;
  pageviews: number;
  unique_sessions: number;
}

interface HourlyChartsResponse {
  hours: HourlyData[];
  total_pageviews: number;
  total_unique_sessions: number;
  range: string;
  data_type: "hourly";
  timezone_offset?: number;
}

interface DailyChartsResponse {
  days: DailyData[];
  total_pageviews: number;
  total_unique_sessions: number;
  range: string;
  data_type: "daily";
  timezone_offset?: number;
}

type ChartsResponse = HourlyChartsResponse | DailyChartsResponse;

interface SitesResponse {
  count: number;
  results: Site[];
}

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

interface AuthCredentials {
  email: string;
  password: string;
}

interface User {
  id: number;
  username: string;
  email: string;
}

interface AuthResponse {
  message: string;
  user: User;
}

const fetchWithCredentials = (url: string, options: RequestInit = {}) => {
  return fetch(url, {
    ...options,
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
  });
};

// Authentication API functions
export async function signup(credentials: AuthCredentials): Promise<User> {
  const response = await fetchWithCredentials(`${API_BASE_URL}/auth/signup`, {
    method: "POST",
    body: JSON.stringify(credentials),
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(
      errorData.error || `HTTP ${response.status}: ${response.statusText}`
    );
  }

  const data: AuthResponse = await response.json();
  return data.user;
}

export async function login(credentials: AuthCredentials): Promise<User> {
  const response = await fetchWithCredentials(`${API_BASE_URL}/auth/login`, {
    method: "POST",
    body: JSON.stringify(credentials),
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(
      errorData.error || `HTTP ${response.status}: ${response.statusText}`
    );
  }

  const data: AuthResponse = await response.json();
  return data.user;
}

export async function logout(): Promise<void> {
  const response = await fetchWithCredentials(`${API_BASE_URL}/auth/logout`, {
    method: "POST",
  });

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
  }
}

export async function forgotPassword(email: string): Promise<void> {
  const response = await fetchWithCredentials(
    `${API_BASE_URL}/auth/forgot-password`,
    {
      method: "POST",
      body: JSON.stringify({ email }),
    }
  );

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(
      errorData.error || `HTTP ${response.status}: ${response.statusText}`
    );
  }
}

export async function resetPassword(
  uid: string,
  token: string,
  newPassword: string
): Promise<void> {
  const response = await fetchWithCredentials(
    `${API_BASE_URL}/auth/reset-password`,
    {
      method: "POST",
      body: JSON.stringify({ uid, token, new_password: newPassword }),
    }
  );

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(
      errorData.error || `HTTP ${response.status}: ${response.statusText}`
    );
  }
}

export async function getCurrentUser(): Promise<User | null> {
  try {
    const response = await fetchWithCredentials(`${API_BASE_URL}/auth/user`);

    if (response.status === 401) {
      return null; // Not authenticated
    }

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    const data = await response.json();
    return data.user;
  } catch (error) {
    console.error("Error getting current user:", error);
    return null;
  }
}

export async function fetchSites(): Promise<Site[]> {
  const response = await fetchWithCredentials(`${API_BASE_URL}/sites/`);

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
  }

  const data: SitesResponse = await response.json();
  return data.results || [];
}

export async function createSite(name: string): Promise<Site> {
  const response = await fetchWithCredentials(`${API_BASE_URL}/sites/`, {
    method: "POST",
    body: JSON.stringify({ name: name.trim() }),
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(
      errorData.error || `HTTP ${response.status}: ${response.statusText}`
    );
  }

  return response.json();
}

/**
 * Fetch hourly pageview data for charts
 */
export async function fetchChartsData(
  siteId: string,
  range:
    | "today"
    | "yesterday"
    | "last_7_days"
    | "last_30_days"
    | "this_month"
    | "last_month" = "today",
  timezoneOffset?: number
): Promise<ChartsResponse> {
  const params = new URLSearchParams({
    site_id: siteId,
    range,
  });

  if (timezoneOffset !== undefined) {
    params.append("timezone_offset", timezoneOffset.toString());
  }

  const response = await fetchWithCredentials(
    `${API_BASE_URL}/chart?${params}`
  );

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(
      errorData.error || `HTTP ${response.status}: ${response.statusText}`
    );
  }

  return response.json();
}

export type {
  Site,
  HourlyData,
  DailyData,
  ChartsResponse,
  HourlyChartsResponse,
  DailyChartsResponse,
  AuthCredentials,
  User,
};
