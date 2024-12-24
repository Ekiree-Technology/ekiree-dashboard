# syntax = docker/dockerfile:1.2

# Nix builder
FROM nixos/nix:latest AS builder

# Copy our source and setup our working dir.
COPY . /tmp/build
WORKDIR /tmp/build

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
ENV POETFOLIO_STATIC = /tmp/static
RUN mkdir /tmp/static
RUN /tmp/build/result/bin/python /tmp/build/result/lib/python3.12/site-packages/ekiree_dashboard/manage.py collectstatic --no-input

# Final image is based on scratch. We copy a bunch of Nix dependencies
# but they're fully self-contained so we don't need Nix anymore.
FROM alpine:latest

WORKDIR /app

# Expose port for web traffic
EXPOSE 8000

# Copy /nix/store
COPY --from=builder /tmp/nix-store-closure /nix/store
COPY --from=builder /tmp/build/result /app

#Copy Static files onto the instance Static
COPY --from=builder /tmp/static /app/static

# Copy Application Direcotry
COPY --from=builder /tmp/build/result/lib/python3.12/site-packages/ekiree_dashboard .

# Run Django Server
# add in "--log-file=/var/log/djangoApp/gunicorn.log \" when we have logging figured out
#CMD ["/app/bin/gunicorn", "--workers=2", "--bind=0.0.0.0:8000", "poetfolio.wsgi:application"]
CMD ["/app/bin/python", "manage.py", "runserver"]
