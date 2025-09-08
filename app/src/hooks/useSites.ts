import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect } from "react";
import {
  createSite,
  deleteSite,
  fetchSites,
  Site,
  updateSite,
} from "@/lib/api";
import { useAuth } from "@/components/AuthProvider";

const queryKey = ["sites"];

/**
 * Hook for fetching sites
 */
export function useSites() {
  const sitesQuery = useQuery({
    queryKey: queryKey,
    queryFn: fetchSites,
  });

  return {
    sites: sitesQuery.data || [],
    isLoading: sitesQuery.isLoading,
    error: sitesQuery.error,
    refetch: sitesQuery.refetch,
  };
}

/**
 * Hook for creating a new site
 */
export function useSiteCreate({
  onError,
  onSuccess,
}: {
  onError?: (error: Error) => void;
  onSuccess?: () => void;
}) {
  const queryClient = useQueryClient();

  const createSiteMutation = useMutation({
    mutationFn: createSite,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKey });
      onSuccess?.();
    },
    onError: (error) => {
      onError?.(error);
    },
  });

  return {
    createSite: createSiteMutation.mutate,
    createSiteAsync: createSiteMutation.mutateAsync,
    isCreating: createSiteMutation.isPending,
    error: createSiteMutation.error,
  };
}

/**
 * Hook for updating an existing site
 */
export function useSiteUpdate({
  onError,
  onSuccess,
}: {
  onError?: (error: Error) => void;
  onSuccess?: (data: Site) => void;
}) {
  const queryClient = useQueryClient();

  const updateSiteMutation = useMutation({
    mutationFn: ({ id, name }: { id: string; name: string }) =>
      updateSite(id, name),
    onSuccess: (data: Site) => {
      queryClient.invalidateQueries({ queryKey: queryKey });
      onSuccess?.(data);
    },
    onError: (error) => {
      onError?.(error);
    },
  });

  return {
    updateSite: updateSiteMutation.mutate,
    updateSiteAsync: updateSiteMutation.mutateAsync,
    isUpdating: updateSiteMutation.isPending,
    error: updateSiteMutation.error,
  };
}

/**
 * Hook for deleting a site
 */
export function useSiteDelete({
  onError,
  onSuccess,
}: {
  onError?: (error: Error) => void;
  onSuccess?: () => void;
}) {
  const queryClient = useQueryClient();

  const deleteSiteMutation = useMutation({
    mutationFn: deleteSite,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKey });
      onSuccess?.();
    },
    onError: (error) => {
      onError?.(error);
    },
  });

  return {
    deleteSite: deleteSiteMutation.mutate,
    deleteSiteAsync: deleteSiteMutation.mutateAsync,
    isDeleting: deleteSiteMutation.isPending,
    error: deleteSiteMutation.error,
  };
}
