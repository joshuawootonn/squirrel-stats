"use client";

import { useAuth } from "@/components/AuthProvider";
import { logout } from "@/lib/api";
import { Button } from "@/components/ui/button";
import Link from "next/link";

export function Header() {
  const { user, isAuthenticated, setUser } = useAuth();

  const handleLogout = async () => {
    try {
      await logout();
      setUser(null);
    } catch (error) {
      console.error("Logout error:", error);
      // Force logout even if API call fails
      setUser(null);
    }
  };

  return (
    <header className="flex justify-between items-center p-4 gap-4 h-16 border-b border-gray-200">
      <div className="flex items-center">
        <Link href="/">
          <h1 className="text-xl font-bold">Squirrel Stats</h1>
        </Link>
      </div>

      {isAuthenticated && user && (
        <div className="flex items-center gap-4">
          <span className="text-sm text-gray-600">
            Welcome, {user.username}
          </span>
          <Button.Root
            onClick={handleLogout}
            variant="secondary"
            className="h-10 px-4"
          >
            Sign Out
          </Button.Root>
        </div>
      )}
    </header>
  );
}
