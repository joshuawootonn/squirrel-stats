"use client";

import { SignedIn, SignedOut } from "@clerk/nextjs";
import { useState } from "react";
import { useSites } from "@/hooks/useSites";
import type { Site } from "@/lib/api";

export default function Home() {
  const [newSiteName, setNewSiteName] = useState("");
  const {
    sites,
    isLoading,
    error,
    refetch,
    createSite,
    isCreating,
    createError,
  } = useSites();

  const handleCreateSite = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newSiteName.trim()) return;
    createSite(newSiteName.trim());
    setNewSiteName("");
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <SignedOut>
        <div className="text-center py-12">
          <h1 className="text-4xl font-bold mb-4">Squirrel Stats</h1>
          <p className="text-gray-600">Please sign in to manage your sites.</p>
        </div>
      </SignedOut>

      <SignedIn>
        <div className="space-y-8">
          {/* Header */}
          <div>
            <h1 className="text-3xl font-bold">My Sites</h1>
            <p className="text-gray-600 mt-2">
              Manage your website analytics and tracking
            </p>
          </div>

          {/* Create Site Form */}
          <div className="bg-gray-50 p-6 rounded-lg border">
            <h2 className="text-xl font-semibold mb-4">Create New Site</h2>
            <form onSubmit={handleCreateSite} className="flex gap-3">
              <input
                type="text"
                value={newSiteName}
                onChange={(e) => setNewSiteName(e.target.value)}
                placeholder="Enter site name"
                className="flex-1 px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-black focus:border-transparent"
                disabled={isCreating}
              />
              <button
                type="submit"
                disabled={isCreating || !newSiteName.trim()}
                className="px-4 py-2 bg-black text-white rounded hover:bg-gray-800 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
              >
                {isCreating ? "Creating..." : "Create Site"}
              </button>
            </form>
          </div>

          {/* Error Display */}
          {(error || createError) && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
              <strong>Error:</strong> {error?.message || createError?.message}
            </div>
          )}

          {/* Sites List */}
          <div>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold">
                Your Sites ({sites.length})
              </h2>
              <button
                onClick={() => refetch()}
                disabled={isLoading}
                className="px-3 py-1 text-sm bg-gray-100 hover:bg-gray-200 rounded transition-colors disabled:opacity-50"
              >
                {isLoading ? "Loading..." : "Refresh"}
              </button>
            </div>

            {isLoading ? (
              <div className="text-center py-8">
                <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-black"></div>
                <p className="mt-2 text-gray-600">Loading sites...</p>
              </div>
            ) : sites.length === 0 ? (
              <div className="text-center py-12 bg-gray-50 rounded-lg border-2 border-dashed border-gray-300">
                <p className="text-gray-600">
                  No sites yet. Create your first site above!
                </p>
              </div>
            ) : (
              <div className="grid gap-4">
                {sites.map((site: Site) => (
                  <div
                    key={site.id}
                    className="bg-white border border-black p-4"
                  >
                    <div className="flex flex-row gap-1 justify-between items-center">
                      <h3 className="font-semibold text-lg ">
                        {site.name} ({site.identifier})
                      </h3>
                      <div>
                        <span className="font-medium">Created:</span>{" "}
                        {new Date(site.created_at).toLocaleDateString()}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </SignedIn>
    </div>
  );
}
