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

export async function fetchSites(token: string): Promise<Site[]> {
  const response = await fetch(`${API_BASE_URL}/sites/`, {
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
  });

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
  }

  const data: SitesResponse = await response.json();
  return data.results || [];
}

export async function createSite(token: string, name: string): Promise<Site> {
  const response = await fetch(`${API_BASE_URL}/sites/`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
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
  token: string,
  siteId: string,
  range: "today" | "yesterday" | "last_7_days" | "last_30_days" | "this_month" | "last_month" = "today",
  timezoneOffset?: number
): Promise<ChartsResponse> {
  const params = new URLSearchParams({
    site_id: siteId,
    range,
  });

  if (timezoneOffset !== undefined) {
    params.append("timezone_offset", timezoneOffset.toString());
  }

  const response = await fetch(`${API_BASE_URL}/chart?${params}`, {
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(
      errorData.error || `HTTP ${response.status}: ${response.statusText}`
    );
  }

  return response.json();
}

export type { Site, HourlyData, DailyData, ChartsResponse, HourlyChartsResponse, DailyChartsResponse };
