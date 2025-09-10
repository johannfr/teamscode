{ pkgs ? import <nixpkgs> {} }:
pkgs.mkShell {
  packages = [
    pkgs.python3
    pkgs.python3Packages.python-dotenv
    pkgs.python3Packages.notify2
    pkgs.python3Packages.pyclip
  ];

  env.LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath [
    pkgs.stdenv.cc.cc.lib
    pkgs.libz
  ];
}
