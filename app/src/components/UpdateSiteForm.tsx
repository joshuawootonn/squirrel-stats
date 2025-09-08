"use client";

import React, { useState, useRef } from "react";
import { useSiteUpdate } from "@/hooks/useSites";
import { Popover } from "@/components/ui/popover";
import { Button } from "@/components/ui/button";
import type { Site } from "@/lib/api";

interface UpdateSiteFormProps {
  site: Site;
}

export function UpdateSiteForm({ site }: UpdateSiteFormProps) {
  const [siteName, setSiteName] = useState(site.name);
  const { updateSite, error, isUpdating } = useSiteUpdate({
    onError: (error) => {
      console.error(error);
    },
    onSuccess: (site: Site) => {
      setSiteName(site.name);
      if (closeRef.current) {
        closeRef.current();
      }
    },
  });
  const closeRef = useRef<(() => void) | null>(null);

  const handleUpdateSite = (e: React.FormEvent) => {
    e.preventDefault();
    if (!siteName.trim() || siteName.trim() === site.name) return;

    updateSite({ id: site.id, name: siteName.trim() });
  };

  return (
    <Popover.Root>
      <Popover.Trigger variant="secondary" size="sm">
        Edit
      </Popover.Trigger>
      <Popover.Portal>
        <Popover.Positioner sideOffset={8}>
          <Popover.Popup className="border-[1.5px] border-gray-300 bg-white p-4 shadow">
            <Popover.Title className="font-medium mb-2">
              Update Site Name
            </Popover.Title>
            <Popover.Description className="text-sm text-gray-600 mb-3">
              Change the name for "{site.name}".
            </Popover.Description>
            {error && (
              <div className="bg-red-50 border-[1.5px] border-red-200 text-red-700 px-3 py-2 mb-3 text-sm">
                <strong>Error:</strong> {error.message}
              </div>
            )}
            <Popover.Context>
              {(context: any) => {
                // Store the close function in the ref
                closeRef.current = context.close;

                return (
                  <form
                    onSubmit={handleUpdateSite}
                    className="flex flex-col gap-2"
                  >
                    <input
                      type="text"
                      value={siteName}
                      onChange={(e) => setSiteName(e.target.value)}
                      placeholder="Enter site name"
                      className="flex-1 px-3 py-2 border-[1.5px] border-gray-300 focus:outline-none focus:ring-2 focus:border-transparent h-10"
                      disabled={isUpdating}
                    />
                    <Button.Root
                      type="submit"
                      disabled={
                        !siteName.trim() ||
                        siteName.trim() === site.name ||
                        isUpdating
                      }
                      loading={isUpdating}
                    >
                      {isUpdating ? "Updating..." : "Update"}
                    </Button.Root>
                  </form>
                );
              }}
            </Popover.Context>
          </Popover.Popup>
        </Popover.Positioner>
      </Popover.Portal>
    </Popover.Root>
  );
}
