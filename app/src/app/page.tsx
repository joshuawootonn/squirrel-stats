"use client";

import { SignedIn, SignedOut } from "@clerk/nextjs";
import { useState } from "react";
import { useSites } from "@/hooks/useSites";
import { Popover } from "@/components/ui/popover";
import { Button } from "@/components/ui/button";
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

  const handleCreateSite = (e: React.FormEvent, close: () => void) => {
    e.preventDefault();
    if (!newSiteName.trim()) return;
    createSite(newSiteName.trim(), {
      onSuccess: () => {
        setNewSiteName("");
        close();
      },
    } as any);
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

          {/* Create Site moved to Popover in header below */}

          {/* Error Display */}
          {(error || createError) && (
            <div className="bg-red-50 border-[1.5px] border-red-200 text-red-700 px-4 py-3">
              <strong>Error:</strong> {error?.message || createError?.message}
            </div>
          )}

          {/* Sites List */}
          <div>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold">
                Your Sites ({sites.length})
              </h2>
              <div className="flex items-center gap-2">
                <Button.Root
                  onClick={() => refetch()}
                  disabled={isLoading}
                  variant="secondary"
                  loading={isLoading}
                >
                  <Button.Text>Refresh</Button.Text>
                </Button.Root>
                <Popover.Root>
                  <Popover.Trigger>Create</Popover.Trigger>
                  <Popover.Portal>
                    <Popover.Positioner sideOffset={8}>
                      <Popover.Popup className="border-[1.5px] border-gray-300 bg-white p-4 shadow w-80">
                        <Popover.Title className="font-medium mb-2">
                          Create New Site
                        </Popover.Title>
                        <Popover.Description className="text-sm text-gray-600 mb-3">
                          Enter a name for your site.
                        </Popover.Description>
                        <Popover.Context>
                          {(context: any) => (
                            <form
                              onSubmit={(e) =>
                                handleCreateSite(e, () => context.close?.())
                              }
                              className="flex gap-2"
                            >
                              <input
                                type="text"
                                value={newSiteName}
                                onChange={(e) => setNewSiteName(e.target.value)}
                                placeholder="Enter site name"
                                className="flex-1 px-3 py-2 border-[1.5px] border-gray-300 focus:outline-none focus:ring-2 focus:ring-black focus:border-transparent h-10"
                                disabled={isCreating}
                              />
                              <Button.Root
                                type="submit"
                                disabled={!newSiteName.trim()}
                                loading={isCreating}
                              >
                                <Button.Text>Create</Button.Text>
                              </Button.Root>
                            </form>
                          )}
                        </Popover.Context>
                      </Popover.Popup>
                    </Popover.Positioner>
                  </Popover.Portal>
                </Popover.Root>
              </div>
            </div>

            {isLoading ? (
              <div className="text-center py-8">
                <div className="inline-block animate-spin h-8 w-8 border-b-2 border-black"></div>
                <p className="mt-2 text-gray-600">Loading sites...</p>
              </div>
            ) : sites.length === 0 ? (
              <div className="text-center py-12 bg-gray-50 border-[1.5px] border-dashed border-gray-300">
                <p className="text-gray-600">
                  No sites yet. Create your first site above!
                </p>
              </div>
            ) : (
              <div className="grid gap-4">
                {sites.map((site: Site) => (
                  <div
                    key={site.id}
                    className="bg-white border-[1.5px] border-black p-4"
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
                    <div className="mt-2 text-sm text-gray-600">
                      <span className="font-medium">Page Views:</span>{" "}
                      {site.pageview_count}
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
