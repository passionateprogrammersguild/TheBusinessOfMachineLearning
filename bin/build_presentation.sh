#! /bin/sh

cd presentation

mkdir -p md
mkdir -p js
mkdir -p css
mkdir -p plugin
mkdir -p lib

docker rmi thebusinessofmachinelearning_presentation
docker build -t thebusinessofmachinelearning_presentation .