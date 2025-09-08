"use client";

import { useState } from "react";
import Link from "next/link";
import { forgotPassword } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setMessage("");
    setIsLoading(true);

    try {
      await forgotPassword(email);
      setMessage(
        "If an account with that email exists, a password reset link has been sent."
      );
      setEmail("");
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to send reset email"
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex items-center justify-center ">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Reset your password
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            Enter your email address and we'll send you a link to reset your
            password.
          </p>
        </div>
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          <Input.Group>
            <Input.Label htmlFor="email">Email address</Input.Label>
            <Input.Root
              id="email"
              name="email"
              type="email"
              required
              placeholder="Email address"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              disabled={isLoading}
            />
          </Input.Group>

          {error && <Input.Error>{error}</Input.Error>}

          {message && (
            <div className="text-green-600 text-sm text-center">{message}</div>
          )}

          <div>
            <Button.Root type="submit" disabled={isLoading} className="w-full">
              {isLoading ? "Sending..." : "Send reset link"}
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
