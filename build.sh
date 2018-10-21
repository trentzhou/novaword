#!/usr/bin/env bash
if [ -n "$http_proxy" ]; then
    BUILD_ARG="--build-arg http_proxy=$http_proxy --build-arg https_proxy=$https_proxy"
fi
docker build $BUILD_ARG -t registry.cn-hangzhou.aliyuncs.com/trentzhou/novaword .
