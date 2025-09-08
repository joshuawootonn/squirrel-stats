"use client";

import { useState, useEffect, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";
import { resetPassword } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

function ResetPasswordForm() {
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const router = useRouter();
  const searchParams = useSearchParams();

  const uid = searchParams.get("uid");
  const token = searchParams.get("token");

  useEffect(() => {
    if (!uid || !token) {
      setError("Invalid reset link. Please request a new password reset.");
    }
  }, [uid, token]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setMessage("");

    if (!uid || !token) {
      setError("Invalid reset link. Please request a new password reset.");
      return;
    }

    if (newPassword !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    if (newPassword.length < 8) {
      setError("Password must be at least 8 characters long.");
      return;
    }

    setIsLoading(true);

    try {
      await resetPassword(uid, token, newPassword);
      setMessage(
        "Password reset successful! You can now sign in with your new password."
      );
      setTimeout(() => {
        router.push("/login");
      }, 2000);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to reset password");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex items-center justify-center ">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Set new password
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            Enter your new password below.
          </p>
        </div>
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          <div className="space-y-4">
            <Input.Group>
              <Input.Label htmlFor="new-password">New Password</Input.Label>
              <Input.Root
                id="new-password"
                name="new-password"
                type="password"
                required
                placeholder="New password"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                disabled={isLoading}
              />
            </Input.Group>
            <Input.Group>
              <Input.Label htmlFor="confirm-password">
                Confirm Password
              </Input.Label>
              <Input.Root
                id="confirm-password"
                name="confirm-password"
                type="password"
                required
                placeholder="Confirm new password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                disabled={isLoading}
              />
            </Input.Group>
          </div>

          {error && <Input.Error>{error}</Input.Error>}

          {message && (
            <div className="text-green-600 text-sm text-center">{message}</div>
          )}

          <div>
            <Button.Root type="submit" disabled={isLoading || !uid || !token}>
              {isLoading ? "Resetting..." : "Reset password"}
            </Button.Root>
          </div>

          <div className="text-center">
            <Link href="/login">Back to sign in</Link>
          </div>
        </form>
      </div>
    </div>
  );
}

export default function ResetPasswordPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen flex items-center justify-center bg-gray-50">
          <div className="text-center">
            <div className="text-lg text-gray-600">Loading...</div>
          </div>
        </div>
      }
    >
      <ResetPasswordForm />
    </Suspense>
  );
}
