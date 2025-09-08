"use client";

import React, { useState } from "react";
import { useSiteDelete } from "@/hooks/useSites";
import { Button } from "@/components/ui/button";
import type { Site } from "@/lib/api";

interface DeleteSiteButtonProps {
  site: Site;
  onDeleteStart?: () => void;
  onDeleteComplete?: () => void;
}

export function DeleteSiteButton({
  site,
  onDeleteComplete,
}: DeleteSiteButtonProps) {
  const [showConfirmModal, setShowConfirmModal] = useState(false);
  const { deleteSite, isDeleting, error } = useSiteDelete({
    onError: (error) => {
      console.error(error);
    },
    onSuccess: () => {
      onDeleteComplete?.();
    },
  });

  const handleDeleteClick = (e: React.MouseEvent) => {
    e.stopPropagation(); // Prevent triggering parent click events
    setShowConfirmModal(true);
  };

  const handleConfirmDelete = () => {
    deleteSite(site.id);
    setShowConfirmModal(false);
  };

  const handleCancelDelete = () => {
    setShowConfirmModal(false);
  };

  return (
    <>
      <Button.Root
        onClick={handleDeleteClick}
        disabled={isDeleting}
        variant="secondary"
        size="sm"
        className="text-red-600 hover:text-red-700 hover:bg-red-50"
      >
        <Button.Text>{isDeleting ? "Deleting..." : "Delete"}</Button.Text>
      </Button.Root>

      {/* Confirmation Modal */}
      {showConfirmModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white p-6 border-[1.5px] border-gray-300 shadow-lg max-w-md w-full mx-4">
            <h3 className="text-lg font-semibold mb-2">Delete Site</h3>
            <p className="text-gray-600 mb-4">
              Are you sure you want to delete <strong>"{site.name}"</strong>?
              This action cannot be undone and will permanently remove all
              associated data.
            </p>

            {error && (
              <div className="bg-red-50 border-[1.5px] border-red-200 text-red-700 px-3 py-2 mb-4 text-sm">
                <strong>Error:</strong> {error.message}
              </div>
            )}

            <div className="flex gap-3 justify-end">
              <Button.Root
                onClick={handleCancelDelete}
                variant="secondary"
                disabled={isDeleting}
              >
                <Button.Text>Cancel</Button.Text>
              </Button.Root>
              <Button.Root
                onClick={handleConfirmDelete}
                disabled={isDeleting}
                loading={isDeleting}
                className="bg-red-600 hover:bg-red-700 text-white"
              >
                <Button.Text>
                  {isDeleting ? "Deleting..." : "Delete Site"}
                </Button.Text>
              </Button.Root>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
