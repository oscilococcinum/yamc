{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs =
    { nixpkgs, ... }@inputs:
    {
      devShells = builtins.listToAttrs (
        map (system: {
          name = system;
          value =
            with import nixpkgs {
              inherit system;
              config.allowUnfree = true;
            }; rec {
              yamc-devshell = pkgs.mkShell {
                nativeBuildInputs =
                  with pkgs;
                  [
                    python313
                  ]
                  ++ (with python313Packages; [
                    numpy
                    sympy
                    pyside6
                    matplotlib
                    debugpy
                  ]);
              };
              default = yamc-devshell;
            };
        }) [ "x86_64-linux" ]
      );
    };
}
