"use client";

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { useChartsData } from "@/hooks/useChartsData";
import { Button } from "@/components/ui/button";
import type { Site } from "@/lib/api";

type TimeRange =
  | "today"
  | "yesterday"
  | "last_7_days"
  | "last_30_days"
  | "this_month"
  | "last_month";

interface AnalyticsChartProps {
  site: Site;
  className?: string;
}

const TIME_RANGE_OPTIONS: {
  value: TimeRange;
  label: string;
  dataType: "hourly" | "daily";
}[] = [
  { value: "today", label: "Today", dataType: "hourly" },
  { value: "yesterday", label: "Yesterday", dataType: "hourly" },
  { value: "last_7_days", label: "Last 7 Days", dataType: "daily" },
  { value: "last_30_days", label: "Last 30 Days", dataType: "daily" },
  { value: "this_month", label: "This Month", dataType: "daily" },
  { value: "last_month", label: "Last Month", dataType: "daily" },
];

/**
 * Custom tooltip component for the chart
 */
function ChartTooltip({ active, payload, label, dataType }: any) {
  if (active && payload && payload.length) {
    const data = payload[0].payload;
    const displayLabel =
      dataType === "hourly" ? data.hour_display : data.day_display;

    return (
      <div className="bg-white border-[1.5px] border-gray-300 p-3 shadow-lg">
        <p className="font-medium text-gray-900">{displayLabel}</p>
        <p className="text-sm text-gray-600">
          <span className="font-medium text-blue-600">{data.pageviews}</span>{" "}
          pageviews
        </p>
        <p className="text-sm text-gray-600">
          <span className="font-medium text-green-600">
            {data.unique_sessions}
          </span>{" "}
          unique sessions
        </p>
      </div>
    );
  }
  return null;
}

/**
 * Analytics chart component that displays both hourly and daily data
 */
export function AnalyticsChart({ site, className }: AnalyticsChartProps) {
  const { data, isLoading, error, refetch, setRange, currentRange } =
    useChartsData({
      siteId: site.id,
      range: "today",
      autoRefresh: false,
    });

  const handleRangeChange = (range: TimeRange) => {
    setRange(range);
  };

  // Get current data type and chart data
  const currentOption = TIME_RANGE_OPTIONS.find(
    (opt) => opt.value === currentRange
  );
  const isHourlyData = data?.data_type === "hourly";
  const chartData = isHourlyData ? (data as any)?.hours : (data as any)?.days;
  const xAxisKey = isHourlyData ? "hour_display" : "day_display";

  if (error) {
    return (
      <div
        className={`bg-red-50 border-[1.5px] border-red-200 text-red-700 p-4 ${className}`}
      >
        <div className="flex items-center justify-between">
          <div>
            <strong>Error loading chart data:</strong>
            <p className="text-sm mt-1">{error.message}</p>
          </div>
          <Button.Root onClick={refetch} variant="outline" size="sm">
            <Button.Text>Retry</Button.Text>
          </Button.Root>
        </div>
      </div>
    );
  }

  return (
    <div className={`bg-white border-[1.5px] border-gray-300 p-6 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">
            {isHourlyData ? "Hourly" : "Daily"} Pageviews - {site.name}
          </h3>
          {data && (
            <p className="text-sm text-gray-600 mt-1">
              {data.total_pageviews} total pageviews •{" "}
              {data.total_unique_sessions} unique sessions
            </p>
          )}
        </div>

        <div className="flex items-center gap-2">
          <Button.Root
            onClick={refetch}
            disabled={isLoading}
            variant="secondary"
            size="sm"
            loading={isLoading}
          >
            <Button.Text>Refresh</Button.Text>
          </Button.Root>
        </div>
      </div>

      {/* Time Range Selector */}
      <div className="flex items-center gap-2 mb-6">
        <span className="text-sm font-medium text-gray-700">Time Range:</span>
        <Button.Group>
          {TIME_RANGE_OPTIONS.map((option) => (
            <Button.Root
              key={option.value}
              variant={currentRange === option.value ? "default" : "outline"}
              size="sm"
              onClick={() => handleRangeChange(option.value)}
              disabled={isLoading}
            >
              <Button.Text>{option.label}</Button.Text>
            </Button.Root>
          ))}
        </Button.Group>
      </div>

      {/* Chart */}
      <div className="h-80">
        {isLoading ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-center">
              <div className="inline-block animate-spin h-8 w-8 border-b-2 border-black mb-2"></div>
              <p className="text-sm text-gray-600">Loading chart data...</p>
            </div>
          </div>
        ) : data && chartData && chartData.length > 0 ? (
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={chartData}
              margin={{
                top: 20,
                right: 30,
                left: 20,
                bottom: 5,
              }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis
                dataKey={xAxisKey}
                tick={{ fontSize: 12, fill: "#6b7280" }}
                axisLine={{ stroke: "#d1d5db" }}
                tickLine={{ stroke: "#d1d5db" }}
              />
              <YAxis
                tick={{ fontSize: 12, fill: "#6b7280" }}
                axisLine={{ stroke: "#d1d5db" }}
                tickLine={{ stroke: "#d1d5db" }}
              />
              <Tooltip content={<ChartTooltip dataType={data.data_type} />} />
              <Bar
                dataKey="pageviews"
                fill="#3b82f6"
                name="Pageviews"
                radius={[0, 0, 0, 0]}
              />
            </BarChart>
          </ResponsiveContainer>
        ) : (
          <div className="flex items-center justify-center h-full">
            <div className="text-center">
              <p className="text-gray-600 mb-2">No data available</p>
              <p className="text-sm text-gray-500">
                {currentRange === "today"
                  ? "No pageviews recorded today yet"
                  : `No pageviews recorded for ${TIME_RANGE_OPTIONS.find(
                      (opt) => opt.value === currentRange
                    )?.label.toLowerCase()}`}
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Chart Legend/Info */}
      {data && chartData && chartData.length > 0 && (
        <div className="mt-4 pt-4 border-t border-gray-200">
          <div className="flex items-center justify-between text-sm text-gray-600">
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 bg-blue-500"></div>
                <span>Pageviews</span>
              </div>
            </div>
            <div>
              Showing {isHourlyData ? "hourly" : "daily"} data for{" "}
              {TIME_RANGE_OPTIONS.find(
                (opt) => opt.value === currentRange
              )?.label.toLowerCase()}
              {data.timezone_offset !== undefined && (
                <span className="ml-2 text-gray-500">(Local timezone)</span>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// Export with both names for backward compatibility
export { AnalyticsChart as HourlyChart };
