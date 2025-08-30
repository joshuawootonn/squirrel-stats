"use client";

import { useState, useEffect, useCallback } from "react";
import { useAuth } from "@clerk/nextjs";
import { fetchChartsData, type ChartsResponse } from "@/lib/api";

type TimeRange =
  | "today"
  | "yesterday"
  | "last_7_days"
  | "last_30_days"
  | "this_month"
  | "last_month";

interface UseChartsDataOptions {
  siteId: string;
  range?: TimeRange;
  autoRefresh?: boolean;
  refreshInterval?: number; // in milliseconds
}

interface UseChartsDataReturn {
  data: ChartsResponse | null;
  isLoading: boolean;
  error: Error | null;
  refetch: () => Promise<void>;
  setRange: (range: TimeRange) => void;
  currentRange: TimeRange;
}

/**
 * Hook for fetching and managing charts data (both hourly and daily)
 */
export function useChartsData({
  siteId,
  range = "today",
  autoRefresh = false,
  refreshInterval = 60000, // 1 minute default
}: UseChartsDataOptions): UseChartsDataReturn {
  const { getToken } = useAuth();
  const [data, setData] = useState<ChartsResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const [currentRange, setCurrentRange] = useState<TimeRange>(range);

  const fetchData = useCallback(async () => {
    if (!siteId) return;

    try {
      setIsLoading(true);
      setError(null);

      const token = await getToken();
      if (!token) {
        throw new Error("Authentication required");
      }

      // Get client timezone offset
      const timezoneOffset = new Date().getTimezoneOffset();

      const result = await fetchChartsData(
        token,
        siteId,
        currentRange,
        timezoneOffset
      );
      setData(result);
    } catch (err) {
      const error =
        err instanceof Error ? err : new Error("Failed to fetch charts data");
      setError(error);
      console.error("Error fetching charts data:", error);
    } finally {
      setIsLoading(false);
    }
  }, [siteId, currentRange, getToken]);

  // Initial fetch and range changes
  useEffect(() => {
    fetchData();
  }, [fetchData]);

  // Auto-refresh functionality - adjust interval based on data type
  useEffect(() => {
    if (!autoRefresh || !siteId) return;

    // For hourly data (today/yesterday), refresh more frequently
    // For daily data, refresh less frequently since it changes less often
    const isHourlyRange =
      currentRange === "today" || currentRange === "yesterday";
    const actualRefreshInterval = isHourlyRange
      ? refreshInterval
      : refreshInterval * 5; // 5x less frequent for daily

    const interval = setInterval(() => {
      fetchData();
    }, actualRefreshInterval);

    return () => clearInterval(interval);
  }, [autoRefresh, refreshInterval, fetchData, siteId, currentRange]);

  const setRange = useCallback((newRange: TimeRange) => {
    setCurrentRange(newRange);
  }, []);

  const refetch = useCallback(async () => {
    await fetchData();
  }, [fetchData]);

  return {
    data,
    isLoading,
    error,
    refetch,
    setRange,
    currentRange,
  };
}
