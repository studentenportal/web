{
  description = "python devshell";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
    pre-commit-hooks = {
      url = "github:cachix/git-hooks.nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
    pyproject-nix = {
      url = "github:pyproject-nix/pyproject.nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
    treefmt-nix = {
      url = "github:numtide/treefmt-nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs =
    {
      self,
      nixpkgs,
      treefmt-nix,
      pre-commit-hooks,
      pyproject-nix,
      ...
    }:
    let
      systems = nixpkgs.lib.platforms.unix;
      eachSystem =
        f:
        nixpkgs.lib.genAttrs systems (
          system:
          f (
            import nixpkgs {
              inherit system;
              config = { };
              overlays = [ ];
            }
          )
        );
      treefmtPkg =
        pkgs:
        (treefmt-nix.lib.evalModule pkgs (_: {
          projectRootFile = "flake.nix";
          programs = {
            # python
            black.enable = true;
            # FIXME:
            # isort.enable = true;
            # docker
            dockerfmt.enable = true;
            # yaml
            yamlfmt.enable = true;
            # toml
            taplo.enable = true;
            # markdown
            mdformat.enable = true;
            # nix
            nixfmt.enable = true;
            statix.enable = true;
          };
        })).config.build.wrapper;
    in
    {
      devShells = eachSystem (
        pkgs:
        let
          # TODO: clean this up / make this work properly
          python = pkgs.python3;
          project = pyproject-nix.lib.project.loadRequirementsTxt {
            projectRoot = ./.;
            requirements =
              (builtins.readFile ./requirements/base/requirements.txt)
              + (builtins.readFile ./requirements/testing/requirements.txt);
          };

          pythonEnv =
            assert project.validators.validateVersionConstraints { inherit python; } == { };
            (python.withPackages (project.renderers.withPackages { inherit python; }));

          inherit (self.checks.${pkgs.stdenv.hostPlatform.system}) pre-commit-check;
        in
        {
          default = pkgs.mkShell {
            inherit (pre-commit-check) shellHook;
            buildInputs = pre-commit-check.enabledPackages;
            packages = [
              pkgs.black
              # pythonEnv
              (python.withPackages (
                p: with p; [
                  django
                  psycopg2
                  python-dateutil
                  # django-messagegroups
                  (buildPythonPackage rec {
                    pname = "django-messagegroups";
                    version = "0.4.5";
                    pyproject = true;
                    build-system = [ setuptools ];
                    src = fetchPypi {
                      inherit pname version;
                      sha256 = "sha256-HlchcB/udg6nMHMy7GktQvFBwW3YUL2L3diOboIPGbc=";
                    };
                  })
                  # django-registration-redux
                  (buildPythonPackage rec {
                    pname = "django-registration-redux";
                    version = "2.12";
                    pyproject = true;
                    build-system = [ setuptools ];
                    src = fetchPypi {
                      inherit pname version;
                      sha256 = "sha256-IhO76HMr5yckA09BRvAlWnvWZutaXhstjYqmM/6K+JQ=";
                    };
                  })
                  # django-downloadview
                  (buildPythonPackage rec {
                    pname = "django-downloadview";
                    version = "2.3.0";
                    pyproject = true;
                    build-system = [ setuptools-scm ];
                    propagatedBuildInputs = [
                      django
                      requests
                    ];
                    src = fetchPypi {
                      inherit pname version;
                      sha256 = "sha256-mrqgVKNJFD+gcQd4i9i1nfzuBF4WgF4F0vswUUL6xIE=";
                    };
                  })
                  django-model-utils
                  django-compressor
                  # django-mathfilters
                  (buildPythonPackage rec {
                    pname = "django-mathfilters";
                    version = "1.0.0";
                    pyproject = true;
                    build-system = [ setuptools ];
                    src = fetchPypi {
                      inherit pname version;
                      sha256 = "sha256-ybiS7238iTaD51z9AnnBh6YBymj0aEw4+dpEZX+2Swc=";
                    };
                  })
                  easy-thumbnails
                  pyscss
                  beautifulsoup4
                  vobject
                  djangorestframework
                ]
              ))
            ];
          };
        }
      );

      formatter = eachSystem treefmtPkg;

      checks = eachSystem (pkgs: {
        pre-commit-check = pre-commit-hooks.lib.${pkgs.stdenv.hostPlatform.system}.run {
          src = ./.;
          hooks.treefmt = {
            enable = true;
            packageOverrides.treefmt = treefmtPkg pkgs;
          };
        };
      });
    };
}
