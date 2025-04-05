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
          jq
          pkg-config
          poetry
          poetryDev
        ];
        # Command run upon shell start
        shellHook = ''
          export MYSQLCLIENT_CFLAGS="-I${libmysqlclient}/include"
          export MYSQLCLIENT_LDFLAGS="-L${libmysqlclient}/lib -lmysqlclient"
          export PKG_CONFIG_PATH=${mariadb}/lib/pkgconfig
          
          # Load environment variables from .env file
          if [ -f .env ]; then
            echo "Loading environment from .env file"
            while IFS='=' read -r key value || [ -n "$key" ]; do
              # Skip comments and empty lines
              if [[ $key != \#* ]] && [[ -n $key ]]; then
                # Remove leading/trailing whitespace and quotes from value
                value=$(echo "$value" | sed -e 's/^[[:space:]]*//;s/[[:space:]]*$//;s/^"//;s/"$//')
                export "$key"="$value"
                echo "Loaded: $key"
              fi
            done < .env
          else
            echo "No .env file found. Please create one with required environment variables."
            exit 1
          fi
          
          export PS1="\n(develop)\[\033[1;32m\][\[\e]0;\u@\h: \w\a\]\u@\h:\w]\$\[\033[0m\] "
        '';
      };
      packages.${system}.default = poetryProd.dependencyEnv;
    };
}
