"use client";

import * as React from "react";

const cx = (...classes: Array<string | undefined | false>) =>
  classes.filter(Boolean).join(" ");

// Base button variants and sizes
const buttonVariants = {
  variant: {
    default: "bg-black text-white hover:bg-gray-800 border-black",
    secondary: "bg-gray-100 text-gray-900 hover:bg-gray-200 border-gray-300",
    outline: "border-gray-300 bg-white text-gray-900 hover:bg-gray-50",
    ghost:
      "text-gray-900 hover:bg-gray-100 border-transparent hover:border-gray-200",
    destructive: "bg-red-600 text-white hover:bg-red-700 border-red-600",
  },
  size: {
    sm: "px-3 py-2 text-xs h-8",
    default: "px-4 py-2 text-sm h-10",
    lg: "px-6 py-2 text-base h-12",
    xl: "px-8 py-2 text-lg h-14",
  },
} as const;

type ButtonVariant = keyof typeof buttonVariants.variant;
type ButtonSize = keyof typeof buttonVariants.size;

// Base button props
type BaseButtonProps = {
  variant?: ButtonVariant;
  size?: ButtonSize;
  className?: string;
  disabled?: boolean;
  loading?: boolean;
  children?: React.ReactNode;
};

// Root button component
type RootProps = React.ComponentPropsWithoutRef<"button"> & BaseButtonProps;

function Root(props: RootProps) {
  const {
    variant = "default",
    size = "default",
    className,
    disabled,
    loading,
    children,
    ...rest
  } = props;

  return (
    <button
      disabled={disabled || loading}
      className={cx(
        // Base styles
        "inline-flex items-center justify-center font-medium transition-colors border-[1.5px]",
        "focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-400",
        "disabled:opacity-50 disabled:cursor-not-allowed",
        // Variant styles
        buttonVariants.variant[variant],
        // Size styles
        buttonVariants.size[size],
        className
      )}
      {...rest}
    >
      {loading && <Spinner className="mr-2" />}
      {children}
    </button>
  );
}

// Icon wrapper for consistent spacing
type IconProps = {
  children: React.ReactNode;
  position?: "left" | "right";
  className?: string;
};

function Icon(props: IconProps) {
  const { children, position = "left", className } = props;

  return (
    <span
      className={cx(
        "inline-flex items-center justify-center",
        position === "left" ? "mr-2" : "ml-2",
        className
      )}
    >
      {children}
    </span>
  );
}

// Loading spinner component
type SpinnerProps = {
  className?: string;
  size?: "sm" | "default" | "lg";
};

function Spinner(props: SpinnerProps) {
  const { className, size = "default" } = props;

  const sizeClasses = {
    sm: "w-3 h-3",
    default: "w-4 h-4",
    lg: "w-5 h-5",
  };

  return (
    <svg
      className={cx("animate-spin", sizeClasses[size], className)}
      xmlns="http://www.w3.org/2000/svg"
      fill="none"
      viewBox="0 0 24 24"
    >
      <circle
        className="opacity-25"
        cx="12"
        cy="12"
        r="10"
        stroke="currentColor"
        strokeWidth="4"
      />
      <path
        className="opacity-75"
        fill="currentColor"
        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
      />
    </svg>
  );
}

// Text wrapper for consistent typography
type TextProps = {
  children: React.ReactNode;
  className?: string;
};

function Text(props: TextProps) {
  const { children, className } = props;

  return <span className={cx("truncate", className)}>{children}</span>;
}

// Group wrapper for button groups
type GroupProps = {
  children: React.ReactNode;
  className?: string;
  orientation?: "horizontal" | "vertical";
};

function Group(props: GroupProps) {
  const { children, className, orientation = "horizontal" } = props;

  return (
    <div
      className={cx(
        "inline-flex",
        orientation === "horizontal"
          ? "flex-row [&>*:not(:first-child)]:ml-[-1.5px]"
          : "flex-col [&>*:not(:first-child)]:mt-[-1.5px]",
        className
      )}
    >
      {children}
    </div>
  );
}

// Link button variant (for Next.js Link or similar)
type LinkProps = React.ComponentPropsWithoutRef<"a"> & BaseButtonProps;

function Link(props: LinkProps) {
  const {
    variant = "default",
    size = "default",
    className,
    children,
    ...rest
  } = props;

  return (
    <a
      className={cx(
        // Base styles
        "inline-flex items-center justify-center font-medium transition-colors border-[1.5px]",
        "focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-400",
        "no-underline",
        // Variant styles
        buttonVariants.variant[variant],
        // Size styles
        buttonVariants.size[size],
        className
      )}
      {...rest}
    >
      {children}
    </a>
  );
}

export const Button = {
  Root,
  Icon,
  Spinner,
  Text,
  Group,
  Link,
};

// Export individual components for convenience
export { Root as ButtonRoot };
export { Icon as ButtonIcon };
export { Spinner as ButtonSpinner };
export { Text as ButtonText };
export { Group as ButtonGroup };
export { Link as ButtonLink };
