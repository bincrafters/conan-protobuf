#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import requests
from cpt import ci_manager
from cpt.ci_manager import CIManager
from cpt.printer import Printer


if __name__ == "__main__":
    manager = CIManager(Printer())
    response = None
    if ci_manager.is_travis():
        if manager.get_branch() == "stable/3.6.1" and \
           not manager.is_pull_request() and \
           os.getenv("CONAN_CLANG_VERSIONS") == "6.0" and \
           os.getenv("CONAN_ARCHS") == "x86_64" and \
           os.getenv("TRAVIS_TOKEN"):
            json_data = {"request": {"branch": "release/3.6.1"}}
            headers = {"Authorization": "token %s" % os.getenv("TRAVIS_TOKEN"), "Travis-API-Version": "3"}
            response = requests.post(url="https://api.travis-ci.com/repo/bincrafters%2Fprotobuf-integration-test/requests", json=json_data, headers=headers)
        else:
            print("Travis CI job does not match:")
            print("BRANCH: %s" % manager.get_branch())
            print("PULL REQUEST: %s" % manager.is_pull_request())
            print("CLANG_VERSIONS: %s" % os.getenv("CONAN_CLANG_VERSIONS"))
            print("ARCHS: %s" % os.getenv("CONAN_ARCHS"))
            print("TOKEN: %s" % (True if os.getenv("TRAVIS_TOKEN") else None))
    elif ci_manager.is_appveyor():
        if manager.get_branch() == "stable/3.6.1" and \
           not manager.is_pull_request() and \
           os.getenv("CONAN_VISUAL_VERSIONS") == "15" and \
           os.getenv("CONAN_BUILD_TYPES") == "Debug" and \
           os.getenv("APPVEYOR_TOKEN"):
            json_data = {"accountName":"BinCrafters", "projectSlug": "protobuf-integration-test", "branch": "release/3.6.1"}
            headers = {"Authorization": "Bearer %s" % os.getenv("APPVEYOR_TOKEN")}
            response = requests.post(url="https://ci.appveyor.com/api/builds", json=json_data, headers=headers)
        else:
            print("Appveyor job does not match:")
            print("BRANCH: %s" % manager.get_branch())
            print("PULL REQUEST: %s" % manager.is_pull_request())
            print("VISUAL VERSIONS: %s" % os.getenv("CONAN_VISUAL_VERSIONS"))
            print("BUILD_TYPES: %s" % os.getenv("CONAN_BUILD_TYPES"))
            print("TOKEN: %s" % (True if os.getenv("APPVEYOR_TOKEN") else None))
    else:
        print("WARNING: No CI manager detected")

    if response:
        if not response.ok:
            raise Exception("ERROR: Could not trigger a new build: %s" % response.text)
        print(response.text)
