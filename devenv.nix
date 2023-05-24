{ pkgs, ... }:

{
  packages = with pkgs; [

  ];
  languages.python =
    {
      enable = true;
      poetry = {
        enable = true;
        activate.enable = true;
        install.enable = true;
      };
    };
}
