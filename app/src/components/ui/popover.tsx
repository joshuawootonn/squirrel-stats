"use client";

import * as React from "react";
import { Popover as HeadlessPopover } from "@base-ui-components/react/popover";
import { Button } from "./button";

const cx = (...classes: Array<string | undefined | false>) =>
  classes.filter(Boolean).join(" ");

type PopoverContextValue = {
  close: () => void;
  setOpen: (open: boolean) => void;
};

const PopoverCtx = React.createContext<PopoverContextValue | null>(null);

function usePopoverInternal() {
  const ctx = React.useContext(PopoverCtx);
  if (!ctx) {
    throw new Error("Popover.Context must be used within Popover.Root");
  }
  return ctx;
}

// Root with internal open state and close() context
function Root(props: React.ComponentProps<typeof HeadlessPopover.Root>) {
  const {
    children,
    open: controlledOpen,
    onOpenChange,
    ...rest
  } = props as any;
  const [uncontrolledOpen, setUncontrolledOpen] =
    React.useState<boolean>(false);
  const isControlled = controlledOpen !== undefined;
  const open = isControlled ? (controlledOpen as boolean) : uncontrolledOpen;

  const setOpen = (next: boolean) => {
    if (!isControlled) setUncontrolledOpen(next);
    onOpenChange?.(next as any);
  };

  const close = () => setOpen(false);

  return (
    <PopoverCtx.Provider value={{ close, setOpen }}>
      <HeadlessPopover.Root
        open={open as any}
        onOpenChange={setOpen as any}
        {...(rest as any)}
      >
        {children}
      </HeadlessPopover.Root>
    </PopoverCtx.Provider>
  );
}

type ButtonProps = React.ComponentPropsWithoutRef<"button"> & {
  className?: string;
  variant?: "default" | "secondary" | "outline" | "ghost" | "destructive";
  size?: "sm" | "default" | "lg" | "xl";
};
function Trigger(props: ButtonProps) {
  const {
    className,
    variant = "default",
    size = "default",
    children,
    ...rest
  } = props;
  return (
    <HeadlessPopover.Trigger
      render={(triggerProps: any) => (
        <Button.Root
          {...triggerProps}
          {...rest}
          variant={variant}
          size={size}
          className={className}
        >
          <Button.Text>{children}</Button.Text>
        </Button.Root>
      )}
    />
  );
}

function Portal(props: React.ComponentProps<typeof HeadlessPopover.Portal>) {
  return <HeadlessPopover.Portal {...props} />;
}

function Positioner(
  props: React.ComponentProps<typeof HeadlessPopover.Positioner> & {
    className?: string;
  }
) {
  const { className, ...rest } = props;
  return <HeadlessPopover.Positioner className={className} {...rest} />;
}

type DivProps = React.ComponentPropsWithoutRef<"div"> & { className?: string };
function Popup(props: DivProps) {
  const { className, ...rest } = props;
  return (
    <HeadlessPopover.Popup
      className={cx("border bg-white p-4 shadow w-80", className)}
      {...rest}
    />
  );
}

type H3Props = React.ComponentPropsWithoutRef<"h3"> & { className?: string };
function Title(props: H3Props) {
  const { className, ...rest } = props;
  return (
    <HeadlessPopover.Title
      className={cx("font-medium mb-2", className)}
      {...rest}
    />
  );
}

type PProps = React.ComponentPropsWithoutRef<"p"> & { className?: string };
function Description(props: PProps) {
  const { className, ...rest } = props;
  return (
    <HeadlessPopover.Description
      className={cx("text-sm text-gray-600 mb-3", className)}
      {...rest}
    />
  );
}

function Arrow({ className }: { className?: string }) {
  return (
    <HeadlessPopover.Arrow
      render={(arrowProps: any) => (
        <svg
          width="20"
          height="10"
          viewBox="0 0 20 10"
          fill="none"
          {...arrowProps}
          className={cx(className)}
        >
          <path d="M0 10 L10 0 L20 10 Z" fill="currentColor" />
        </svg>
      )}
    />
  );
}

// Render-prop Context for convenience close()
function Context(props: {
  children: (ctx: PopoverContextValue) => React.ReactNode;
}) {
  const ctx = usePopoverInternal();
  return <>{props.children(ctx)}</>;
}

export const Popover = {
  Root,
  Trigger,
  Portal,
  Positioner,
  Popup,
  Title,
  Description,
  Arrow,
  Context,
};
