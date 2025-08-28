{
  description = "Python Shell";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs?ref=nixos-unstable";
  };

  outputs = { self, nixpkgs }: 
  let
    pkgs = nixpkgs.legacyPackages."x86_64-linux";
  in
  {
    devShells."x86_64-linux".default = pkgs.mkShell {
      packages = with pkgs; [
        uv
        ruff
        python311
        python311Packages.beautifulsoup4
      ];
      shellHook = "
        echo This is a shell with $(python -V)
      ";
    }; 
  };
}
