import os

# Set JWT_SECRET_KEY for tests before any app imports
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-not-for-production")
