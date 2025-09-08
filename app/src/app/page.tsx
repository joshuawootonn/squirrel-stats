"use client";

import { useState } from "react";
import { useSites } from "@/hooks/useSites";
import { useAuth } from "@/components/AuthProvider";
import { LandingPage } from "@/components/LandingPage";
import { Button } from "@/components/ui/button";
import { HourlyChart } from "@/components/HourlyChart";
import { CreateSiteForm } from "@/components/CreateSiteForm";
import { DeleteSiteButton } from "@/components/DeleteSiteButton";
import { UpdateSiteForm } from "@/components/UpdateSiteForm";
import type { Site } from "@/lib/api";

export default function Home() {
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  const [selectedSite, setSelectedSite] = useState<Site | null>(null);
  const { sites, isLoading, error, refetch } = useSites();

  // Show loading while checking
  if (authLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="inline-block animate-spin">Loading...</div>
      </div>
    );
  }

  // Show landing page when not authenticated
  if (!isAuthenticated) {
    return <LandingPage />;
  }

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="space-y-8">
        {error && (
          <div className="bg-red-50 border-[1.5px] border-red-200 text-red-700 px-4 py-3">
            <strong>Error:</strong> {error.message}
          </div>
        )}

        <div>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold">Your Sites</h2>
            <div className="flex items-center gap-2">
              <Button.Root
                onClick={() => refetch()}
                disabled={isLoading}
                variant="secondary"
                loading={isLoading}
              >
                Refresh
              </Button.Root>
              <CreateSiteForm />
            </div>
          </div>

          {isLoading ? (
            <div className="text-center py-8">
              <div className="inline-block animate-spin">Loading...</div>
            </div>
          ) : sites.length === 0 ? (
            <div className="text-center py-12 bg-gray-50 border-[1.5px] border-dashed border-gray-300">
              <p className="text-gray-600">
                No sites yet. Create your first site above!
              </p>
            </div>
          ) : (
            <div className="space-y-6">
              {/* Sites Grid */}
              <div className="grid gap-4">
                {sites.map((site: Site) => (
                  <div
                    key={site.id}
                    className={`bg-white border-[1.5px] p-4 cursor-pointer transition-colors ${
                      selectedSite?.id === site.id
                        ? "border-black bg-gray-50"
                        : "border-gray-300 hover:border-gray-400"
                    }`}
                    onClick={(e) => {
                      if (e.isDefaultPrevented()) {
                        return;
                      }
                      setSelectedSite(
                        selectedSite?.id === site.id ? null : site
                      );
                    }}
                  >
                    <div className="flex flex-row gap-1 justify-between items-center">
                      <h3 className="font-semibold text-lg">
                        {site.name} ({site.identifier})
                      </h3>
                      <div className="flex items-center gap-4">
                        <div
                          className="flex items-center gap-2"
                          onClick={(e) => e.stopPropagation()}
                        >
                          <UpdateSiteForm site={site} />
                          <DeleteSiteButton
                            site={site}
                            onDeleteComplete={() => {
                              // Clear selected site if it was the one being deleted
                              if (selectedSite?.id === site.id) {
                                setSelectedSite(null);
                              }
                            }}
                          />
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              {/* Analytics Chart */}
              {selectedSite && (
                <div className="mt-6">
                  <HourlyChart site={selectedSite} />
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
