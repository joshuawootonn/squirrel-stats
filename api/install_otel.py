#!/usr/bin/env python3
"""
Script to install OpenTelemetry dependencies and test the observability setup.
"""

import os
import subprocess
import sys


def run_command(command, description):
    """Run a command and handle errors."""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        if result.stdout:
            print(f"Output: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed")
        print(f"Error: {e.stderr}")
        return False


def main():
    """Main installation and test function."""
    print("🚀 Installing OpenTelemetry dependencies for squirrel-stats...")

    # Check if we're in the right directory
    if not os.path.exists("requirements.txt"):
        print("❌ requirements.txt not found. Please run this script from the api directory.")
        sys.exit(1)

    # Install dependencies
    if not run_command("pip install -r requirements.txt", "Installing dependencies"):
        print("❌ Failed to install dependencies. Please check your Python environment.")
        sys.exit(1)

    # Test imports
    print("\n🧪 Testing OpenTelemetry imports...")
    try:
        from opentelemetry import trace
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
        from opentelemetry.instrumentation.django import DjangoInstrumentor
        from opentelemetry.instrumentation.redis import RedisInstrumentor
        from opentelemetry.sdk.trace import TracerProvider

        print("✅ All OpenTelemetry imports successful")
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        sys.exit(1)

    # Test configuration
    print("\n🔧 Testing OpenTelemetry configuration...")
    try:
        from otel_config import configure_server_telemetry

        print("✅ OpenTelemetry configuration imports successful")

        # Check if environment variables are set
        axiom_token = os.getenv("AXIOM_API_TOKEN")
        if not axiom_token:
            print("⚠️  AXIOM_API_TOKEN not set - configuration will fail at runtime")
            print("   Please set up your environment variables:")
            print("   1. cp axiom.env.example .env.prod")
            print("   2. Edit .env.prod with your actual token")
            print("   3. export $(xargs < .env.prod)")
        else:
            print(f"✅ AXIOM_API_TOKEN is set ({axiom_token[:20]}...)")

            # Test tracer creation (only if token is available)
            try:
                tracer = configure_server_telemetry()
                print("✅ Tracer configuration successful")
            except Exception as config_error:
                print(f"❌ Tracer configuration failed: {config_error}")
                print("   This may be due to network connectivity or invalid credentials")

    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        sys.exit(1)

    print("\n🎉 OpenTelemetry setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Set up environment variables:")
    print("   - Copy axiom.env.example to .env.prod")
    print("   - Update AXIOM_API_TOKEN with your actual token")
    print("   - Load environment: export $(xargs < .env.prod)")
    print("2. Install dependencies: pip install -r requirements.txt")
    print("3. Start your Django server: python manage.py runserver")
    print("4. Start your queue workers: ./scripts/start_workers.sh")
    print("5. Check your Axiom dashboard for incoming traces:")
    print("   - Server traces in 'server' dataset")
    print("   - Queue worker traces in 'queue-workers' dataset")
    print("\n🔍 Trace data will include:")
    print("   - HTTP requests to Django")
    print("   - Database queries")
    print("   - Redis operations")
    print("   - Queue job processing")
    print("   - Custom spans in pageview tracking")


if __name__ == "__main__":
    main()
