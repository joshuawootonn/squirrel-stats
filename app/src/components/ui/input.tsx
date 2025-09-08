"use client";

import * as React from "react";

const cx = (...classes: Array<string | undefined | false>) =>
  classes.filter(Boolean).join(" ");

// Base input variants and sizes
const inputVariants = {
  variant: {
    default: "border-gray-300 focus:ring-black focus:border-transparent",
    error: "border-red-300 focus:ring-red-500 focus:border-transparent",
    success: "border-green-300 focus:ring-green-500 focus:border-transparent",
  },
  size: {
    sm: "px-2 py-1 text-xs h-8",
    default: "px-3 py-2 text-sm h-10",
    lg: "px-4 py-3 text-base h-12",
  },
} as const;

type InputVariant = keyof typeof inputVariants.variant;
type InputSize = keyof typeof inputVariants.size;

// Base input props
type BaseInputProps = {
  variant?: InputVariant;
  size?: InputSize;
  className?: string;
  error?: boolean;
  disabled?: boolean;
};

// Root input component
type RootProps = React.ComponentPropsWithoutRef<"input"> & BaseInputProps;

function Root(props: RootProps) {
  const {
    variant = "default",
    size = "default",
    className,
    error,
    disabled,
    ...rest
  } = props;

  // Override variant if error prop is true
  const effectiveVariant = error ? "error" : variant;

  return (
    <input
      disabled={disabled}
      className={cx(
        // Base styles
        "w-full border-[1.5px] transition-colors",
        "focus:outline-none focus:ring-2 focus:ring-offset-0",
        "disabled:opacity-50 disabled:cursor-not-allowed disabled:bg-gray-50",
        "placeholder:text-gray-400",
        // Variant styles
        inputVariants.variant[effectiveVariant],
        // Size styles
        inputVariants.size[size],
        className
      )}
      {...rest}
    />
  );
}

// Label component for consistent typography
type LabelProps = React.ComponentPropsWithoutRef<"label"> & {
  className?: string;
  required?: boolean;
};

function Label(props: LabelProps) {
  const { children, className, required, ...rest } = props;

  return (
    <label
      className={cx("block text-sm font-medium text-gray-700 mb-1", className)}
      {...rest}
    >
      {children}
      {required && <span className="text-red-500 ml-1">*</span>}
    </label>
  );
}

// Error message component
type ErrorProps = {
  children: React.ReactNode;
  className?: string;
};

function Error(props: ErrorProps) {
  const { children, className } = props;

  return (
    <p className={cx("text-sm text-red-600 mt-1", className)}>{children}</p>
  );
}

// Helper text component
type HelperProps = {
  children: React.ReactNode;
  className?: string;
};

function Helper(props: HelperProps) {
  const { children, className } = props;

  return (
    <p className={cx("text-sm text-gray-500 mt-1", className)}>{children}</p>
  );
}

// Group wrapper for input with label and error
type GroupProps = {
  children: React.ReactNode;
  className?: string;
};

function Group(props: GroupProps) {
  const { children, className } = props;

  return <div className={cx("space-y-1", className)}>{children}</div>;
}

// Textarea variant
type TextareaProps = React.ComponentPropsWithoutRef<"textarea"> &
  BaseInputProps;

function Textarea(props: TextareaProps) {
  const {
    variant = "default",
    size = "default",
    className,
    error,
    disabled,
    ...rest
  } = props;

  // Override variant if error prop is true
  const effectiveVariant = error ? "error" : variant;

  return (
    <textarea
      disabled={disabled}
      className={cx(
        // Base styles
        "w-full border-[1.5px] transition-colors resize-vertical",
        "focus:outline-none focus:ring-2 focus:ring-offset-0",
        "disabled:opacity-50 disabled:cursor-not-allowed disabled:bg-gray-50",
        "placeholder:text-gray-400",
        // Variant styles
        inputVariants.variant[effectiveVariant],
        // Size styles (using default padding for textarea)
        "px-3 py-2 text-sm min-h-[80px]",
        className
      )}
      {...rest}
    />
  );
}

export const Input = {
  Root,
  Label,
  Error,
  Helper,
  Group,
  Textarea,
};

// Export individual components for convenience
export { Root as InputRoot };
export { Label as InputLabel };
export { Error as InputError };
export { Helper as InputHelper };
export { Group as InputGroup };
export { Textarea as InputTextarea };
