{ pkgs, ... }:

{
  packages = with pkgs; [ ];
  languages.python.enable = true;
  languages.python.package = pkgs.python311.withPackages (ps: with ps; [ requests typer colorama rich shellingham typing-extensions ]);
}
