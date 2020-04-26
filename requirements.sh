#!/bin/bash
set -x

echo "Installing Pip Packages"
for pkg in imutils==0.5.3 numpy==1.16.2; do
  python3 -m pip install $pkg
done

echo "Installing Apt Packages"
for pkg in python3-opencv; do
  sudo apt install $pkg
done
