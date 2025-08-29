"use client";

import {
  SignInButton,
  SignUpButton,
  SignedIn,
  SignedOut,
  UserButton,
} from "@clerk/nextjs";
import { Button } from "@/components/ui/button";

export function Header() {
  return (
    <header className="flex justify-end items-center p-4 gap-4 h-16 border-b border-gray-200">
      <SignedOut>
        <SignInButton />
        <SignUpButton>
          <Button.Root className="h-10 px-4">
            <Button.Text>Sign Up</Button.Text>
          </Button.Root>
        </SignUpButton>
      </SignedOut>
      <SignedIn>
        <UserButton />
      </SignedIn>
    </header>
  );
}
