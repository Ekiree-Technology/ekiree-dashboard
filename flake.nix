{
  description = "Dashboard Nix Package";
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";

    pyproject-nix = {
      url = "github:pyproject-nix/pyproject.nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };

    uv2nix = {
      url = "github:pyproject-nix/uv2nix";
      inputs.pyproject-nix.follows = "pyproject-nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };

    pyproject-build-systems = {
      url = "github:pyproject-nix/build-system-pkgs";
      inputs.pyproject-nix.follows = "pyproject-nix";
      inputs.uv2nix.follows = "uv2nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = {
    nixpkgs,
    pyproject-nix,
    uv2nix,
    pyproject-build-systems,
    ...
  }: let
    supportedSystems = ["x86_64-linux" "aarch64-linux" "x86_64-darwin" "aarch64-darwin"];
    forAllSystems = f: nixpkgs.lib.genAttrs supportedSystems (system: f system);

    # Load the uv workspace (system-independent)
    workspace = uv2nix.lib.workspace.loadWorkspace {workspaceRoot = ./.;};
    workspaceOverlay = workspace.mkPyprojectOverlay {sourcePreference = "wheel";};
    editableOverlay = workspace.mkEditablePyprojectOverlay {root = "$REPO_ROOT";};

    mkPkgs = system: let
      pkgs = import nixpkgs {inherit system;};

      # Custom overrides for packages that need native dependencies
      customOverrides = final: prev: {
        # mysqlclient has no wheel for Linux — built from sdist.
        # Needs setuptools as a build system, plus native MySQL libs.
        mysqlclient = prev.mysqlclient.overrideAttrs (old: {
          nativeBuildInputs =
            (old.nativeBuildInputs or [])
            ++ [
              pkgs.pkg-config
              final.setuptools
            ];
          buildInputs =
            (old.buildInputs or [])
            ++ [
              pkgs.libmysqlclient
            ];
        });
      };

      # Build the base Python package set
      pythonSet =
        (pkgs.callPackage pyproject-nix.build.packages {
          python = pkgs.python312;
        })
        .overrideScope
        (
          pkgs.lib.composeManyExtensions [
            pyproject-build-systems.overlays.default
            workspaceOverlay
            customOverrides
          ]
        );

      prodEnv = pythonSet.mkVirtualEnv "ekiree-dashboard-env" workspace.deps.default;

      # Editable overlay needs editables package for hatchling's editable mode
      editablePythonSet = pythonSet.overrideScope (
        pkgs.lib.composeManyExtensions [
          editableOverlay
          (final: prev: {
            ekiree-dashboard = prev.ekiree-dashboard.overrideAttrs (old: {
              nativeBuildInputs = (old.nativeBuildInputs or []) ++ [final.editables];
            });
          })
        ]
      );
      devEnv = editablePythonSet.mkVirtualEnv "ekiree-dashboard-dev-env" workspace.deps.all;
    in {
      inherit pkgs prodEnv devEnv;
    };
  in {
    packages = forAllSystems (system: let
      env = mkPkgs system;
    in {
      default = env.prodEnv;
      dev = env.devEnv;
    });

    devShells = forAllSystems (system: let
      env = mkPkgs system;
      pkgs = env.pkgs;
    in {
      default = pkgs.mkShell {
        nativeBuildInputs = [
          pkgs.jq
          pkgs.pkg-config
          pkgs.uv
          env.devEnv
        ];
        shellHook = ''
          # Set the repo root for editable installs
          export REPO_ROOT=$(pwd)

          # Prevent uv from managing environments and downloading Python
          export UV_NO_SYNC=1
          export UV_PYTHON_DOWNLOADS=never

          export MYSQLCLIENT_CFLAGS="-I${pkgs.libmysqlclient}/include"
          export MYSQLCLIENT_LDFLAGS="-L${pkgs.libmysqlclient}/lib -lmysqlclient"
          export PKG_CONFIG_PATH=${pkgs.mariadb}/lib/pkgconfig

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
            echo "Warning: No .env file found. Create one with required environment variables for full functionality."
          fi

          export PS1="\n(develop)\[\033[1;32m\][\[\e]0;\u@\h: \w\a\]\u@\h:\w]\$\[\033[0m\] "
        '';
      };
    });

    formatter = forAllSystems (system: (import nixpkgs {inherit system;}).alejandra);
  };
}
