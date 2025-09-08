"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/components/AuthProvider";
import { login } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const { setUser } = useAuth();
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setIsLoading(true);

    try {
      const user = await login({ email, password });
      setUser(user);
      router.push("/");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex items-center justify-center ">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Sign in to Squirrel Stats
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            Or{" "}
            <Link href="/signup" className="font-medium">
              create a new account
            </Link>
          </p>
        </div>
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          <div className="space-y-4">
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
            <Input.Group>
              <Input.Label htmlFor="password">Password</Input.Label>
              <Input.Root
                id="password"
                name="password"
                type="password"
                required
                placeholder="Password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                disabled={isLoading}
              />
            </Input.Group>
          </div>

          <div className="flex items-center justify-center">
            <Link href="/forgot-password" className="text-sm ">
              Forgot your password?
            </Link>
          </div>

          {error && <Input.Error>{error}</Input.Error>}

          <div>
            <Button.Root type="submit" disabled={isLoading} className="w-full">
              {isLoading ? "Signing in..." : "Sign in"}
            </Button.Root>
          </div>
        </form>
      </div>
    </div>
  );
}
