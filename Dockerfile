# syntax = docker/dockerfile:1.2

# Stage 1: Nix builder
FROM nixos/nix:latest AS builder

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
RUN mkdir /tmp/nix-store-closure
RUN cp -R $(nix-store -qR result/) /tmp/nix-store-closure

# Compile static files
ENV POETFOLIO_STATIC=/tmp/static
RUN mkdir /tmp/static
# RUN /tmp/build/result/bin/python /tmp/build/result/lib/python3.12/site-packages/ekiree_dashboard/manage.py collectstatic --no-input

# Stage 2: Production
FROM alpine:latest

WORKDIR /app

# Copy /nix/store
COPY --from=builder /tmp/nix-store-closure /nix/store
COPY --from=builder /tmp/build/result /app

#Copy Static files onto the instance Static
COPY --from=builder /tmp/static /app/static

# Copy Application Direcotry
COPY --from=builder /tmp/build/result/lib/python3.12/site-packages/ekiree_dashboard .

# Expose port for web traffic
EXPOSE 8000
EXPOSE 3306

# Run Django Server
# add in "--log-file=/var/log/djangoApp/gunicorn.log \" when we have logging figured out
ENTRYPOINT ["/app/bin/gunicorn", "--workers=2", "--bind=0.0.0.0:8000", "poetfolio.wsgi:application"]
