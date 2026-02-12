# syntax=docker/dockerfile:1

# Stage 1: Nix builder
FROM ghcr.io/nixos/nix AS builder

ARG PYTHON_VERSION=3.12

# Copy our source and setup our working dir.
COPY . /tmp/build
WORKDIR /tmp/build

# Set environment variables to optimize Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Build our Nix environment
RUN nix \
    --extra-experimental-features "nix-command flakes" \
    --option filter-syscalls false \
    build

# Copy the Nix store closure into a directory. The Nix store closure is the
# entire set of Nix store values that we need for our build.
RUN mkdir /tmp/nix-store-closure \
    && cp -R $(nix-store -qR result/) /tmp/nix-store-closure

# Compile static files
ENV POETFOLIO_STATIC=/tmp/static
RUN mkdir /tmp/static \
    && /tmp/build/result/bin/python /tmp/build/result/lib/python${PYTHON_VERSION}/site-packages/ekiree_dashboard/manage.py collectstatic --no-input

# Prepare files needed by the scratch stage:
# - /etc/passwd and /etc/group: Python's getpass.getuser() needs these to resolve
#   UID 1000 to a username. Without them, Django's settings.py crashes on import.
# - /tmp: gunicorn workers need a writable temp directory for heartbeat files.
#   Python's tempfile module also requires it.
RUN mkdir -p /tmp/etc /tmp/scratch-tmp /tmp/scratch-var-tmp \
    && chmod 1777 /tmp/scratch-tmp /tmp/scratch-var-tmp \
    && echo 'root:x:0:0:root:/root:/bin/sh' > /tmp/etc/passwd \
    && echo 'appuser:x:1000:1000:appuser:/app:/bin/sh' >> /tmp/etc/passwd \
    && echo 'root:x:0:' > /tmp/etc/group \
    && echo 'appuser:x:1000:' >> /tmp/etc/group

# Stage 2: Production
FROM scratch

ARG PYTHON_VERSION=3.12

# Ensure Python output is not buffered in production
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Provide /etc/passwd and /etc/group so Python can resolve UID 1000
COPY --from=builder /tmp/etc/passwd /etc/passwd
COPY --from=builder /tmp/etc/group /etc/group

# Provide writable temp directories for gunicorn worker heartbeat files and Python tempfile
COPY --from=builder --chown=1000:1000 /tmp/scratch-tmp /tmp
COPY --from=builder --chown=1000:1000 /tmp/scratch-var-tmp /var/tmp

# Copy /nix/store
COPY --from=builder /tmp/nix-store-closure /nix/store
COPY --from=builder /tmp/build/result /app

# Copy Static files onto the instance Static
COPY --from=builder /tmp/static /app/static

# Copy Application Directory
COPY --from=builder /tmp/build/result/lib/python${PYTHON_VERSION}/site-packages/ekiree_dashboard .

# Run as non-root user
USER 1000

# Expose port for web traffic
EXPOSE 8000

# Run Django Server
# add in "--log-file=/var/log/djangoApp/gunicorn.log \" when we have logging figured out
ENTRYPOINT ["/app/bin/python", "/app/entrypoint.prod.py"]
