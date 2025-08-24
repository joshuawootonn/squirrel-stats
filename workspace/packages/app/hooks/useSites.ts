import { useAuth } from "@clerk/nextjs";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect } from "react";
import { createSite, fetchSites } from "../lib/api";

export function useSites() {
  const { getToken, isSignedIn } = useAuth();
  const queryClient = useQueryClient();

  // Fetch sites using React Query
  const sitesQuery = useQuery({
    queryKey: ["sites"],
    queryFn: async () => {
      const token = await getToken();
      if (!token) {
        throw new Error("No authentication token");
      }
      return fetchSites(token);
    },
    enabled: false, // We'll enable it manually when signed in
  });

  // Auto-fetch when signed in
  useEffect(() => {
    if (isSignedIn) {
      sitesQuery.refetch();
    }
  }, [isSignedIn, sitesQuery]);

  // Create site mutation
  const createSiteMutation = useMutation({
    mutationFn: async (name: string) => {
      const token = await getToken();
      if (!token) {
        throw new Error("No authentication token");
      }
      return createSite(token, name);
    },
    onSuccess: () => {
      // Invalidate and refetch sites
      queryClient.invalidateQueries({ queryKey: ["sites"] });
    },
  });

  return {
    sites: sitesQuery.data || [],
    isLoading: sitesQuery.isLoading,
    error: sitesQuery.error,
    refetch: sitesQuery.refetch,
    createSite: createSiteMutation.mutate,
    isCreating: createSiteMutation.isPending,
    createError: createSiteMutation.error,
  };
}
