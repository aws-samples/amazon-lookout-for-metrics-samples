#!/bin/bash

mkdir alfm_starter
rm -rf alfm_starter
mkdir alfm_starter
cp *.ipynb alfm_starter/
cp README.md alfm_starter/
cp package_up.sh alfm_starter/
cp awsconfig alfm_starter/
cp *.YAML alfm_starter/
cp *.py alfm_starter/

zip -r alfm_starter.zip alfm_starter