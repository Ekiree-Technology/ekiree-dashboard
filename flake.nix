{
  description = "Dashboard Nix Package";

  inputs = {
    # Nix Packages
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
  };

  outputs = {
    nixpkgs,
    poetry2nix,
    ...
  }: let
    system = "x86_64-linux";
    pkgs = import nixpkgs {inherit system;};

    # Setting up nix2poetry
    inherit
      (poetry2nix.lib.mkPoetry2Nix {inherit pkgs;})
      mkPoetryApplication
      mkPoetryEnv
      overrides
      ;

    # Configure production python application with poetry2nix
    poetryProd = mkPoetryApplication {
      projectDir = ./.;
      preferWheels = true;
      overrides = overrides.withDefaults (final: prev: {
        reportlab = prev.reportlab.override {
          preferWheel = false;
        };
      });
    };

    # Configure development python environment with poetry2nix
    poetryDev = mkPoetryEnv {
      projectDir = ./.;
      preferWheels = true;
      extraPackages = ps: [ps.pip ps.django-stubs];
      overrides = overrides.withDefaults (final: prev: {
        reportlab = prev.reportlab.override {
          preferWheel = false;
        };
      });
    };
  in
    with pkgs; {
      # Development shell
      devShell.${system} = mkShell {
        nativeBuildInputs = [
          poetry
          jq
          sops
          pkg-config
          poetryDev
        ];

        # Command run upon shell start
        shellHook = ''
          export POETFOLIO_SECRET_KEY=$(sops  --decrypt ./secrets/secrets.json | jq -r .poetfolio_secret_key)
          export POETFOLIO_PRODUCTION=$(sops  --decrypt ./secrets/secrets.json | jq -r .poetfolio_production)
          export POETFOLIO_DB_NAME=$(sops  --decrypt ./secrets/secrets.json | jq -r .poetfolio_db_name)
          export POETFOLIO_DB_USER=$(sops  --decrypt ./secrets/secrets.json | jq -r .poetfolio_db_user)
          export POETFOLIO_DB_PASSWORD=$(sops  --decrypt ./secrets/secrets.json | jq -r .poetfolio_db_password)

          export POETFOLIO_DB_HOST=$(sops  --decrypt ./secrets/secrets.json | jq -r .poetfolio_db_host)
          export POETFOLIO_STATIC=$(sops  --decrypt ./secrets/secrets.json | jq -r .poetfolio_static)
          export POETFOLIO_MEDIA=$(sops  --decrypt ./secrets/secrets.json | jq -r .poetfolio_media)
          export POETFOLIO_EMAIL_HOST=$(sops  --decrypt ./secrets/secrets.json | jq -r .poetfolio_email_host)
          export POETFOLIO_EMAIL_USER=$(sops  --decrypt ./secrets/secrets.json | jq -r .poetfolio_email_user)
          export POETFOLIO_EMAIL_PASSWORD=$(sops  --decrypt ./secrets/secrets.json | jq -r .poetfolio_email_password)

          export PS1="\n(develop)\[\033[1;32m\][\[\e]0;\u@\h: \w\a\]\u@\h:\w]\$\[\033[0m\] "
        '';
      };
      packages.${system}.default = poetryProd.dependencyEnv;
    };
}
