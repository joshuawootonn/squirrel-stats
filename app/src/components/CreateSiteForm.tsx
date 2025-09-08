"use client";

import React, { useState, useRef } from "react";
import { useSiteCreate } from "@/hooks/useSites";
import { Popover } from "@/components/ui/popover";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

export function CreateSiteForm() {
  const [newSiteName, setNewSiteName] = useState("");
  const { createSite, error, isCreating } = useSiteCreate({
    onError: (error) => {
      console.error(error);
    },
    onSuccess: () => {
      setNewSiteName("");
      if (closeRef.current) {
        closeRef.current();
      }
    },
  });
  const closeRef = useRef<(() => void) | null>(null);

  const handleCreateSite = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newSiteName.trim()) return;

    createSite(newSiteName.trim());
  };

  return (
    <Popover.Root>
      <Popover.Trigger>Create</Popover.Trigger>
      <Popover.Portal>
        <Popover.Positioner sideOffset={8}>
          <Popover.Popup className="border-[1.5px] border-gray-300 bg-white p-4 shadow">
            <Popover.Title className="font-medium mb-2">
              Create New Site
            </Popover.Title>
            <Popover.Description className="text-sm text-gray-600 mb-3">
              Enter a name for your site.
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
                    onSubmit={handleCreateSite}
                    className="flex flex-col gap-2"
                  >
                    <Input.Root
                      type="text"
                      value={newSiteName}
                      onChange={(e) => setNewSiteName(e.target.value)}
                      placeholder="Enter site name"
                      disabled={isCreating}
                    />
                    <Button.Root
                      type="submit"
                      disabled={!newSiteName.trim() || isCreating}
                      loading={isCreating}
                    >
                      Create
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
