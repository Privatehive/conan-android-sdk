#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain
from conan.tools.files import patch, load, get, replace_in_file, copy
from conan.tools.build import cross_building, build_jobs
from conan.tools.env import VirtualBuildEnv, Environment
from conan.tools.scm import Git
from subprocess import check_call, Popen, PIPE, STDOUT, DEVNULL
import json, os
import shutil
import configparser
import tempfile
import requests

required_conan_version = ">=2.0"

class AndroidSDKConan(ConanFile):

    min_api_level = 7
    max_api_level = 33

    jsonInfo = json.load(open("info.json", 'r'))
    # ---Package reference---
    name = jsonInfo["projectName"]
    version = jsonInfo["version"]
    user = jsonInfo["domain"]
    channel = "stable"
    # ---Metadata---
    description = jsonInfo["projectDescription"]
    license = jsonInfo["license"]
    author = jsonInfo["vendor"]
    topics = jsonInfo["topics"]
    homepage = jsonInfo["homepage"]
    url = jsonInfo["repository"]
    # ---Requirements---
    requires = []
    tool_requires = ["openjdk/19.0.2@%s/%s" % (user, channel)]
    # ---Sources---
    exports = ["info.json"]
    exports_sources = []
    # ---Binary model---
    settings = "os", "arch"
    options = {"ndkVersion": ["ANY"], "buildToolsRevision": ["ANY"], "platformVersion": list(range(min_api_level, max_api_level + 1))}
    default_options = {"ndkVersion": "25.1.8937393", "buildToolsRevision": "33.0.2", "platformVersion": 33}
    # ---Build---
    generators = []
    # ---Folders---
    no_copy_source = True

    @property
    def toolchain_path(self):
        return os.path.join(self.package_folder, "android_sdk_path.cmake")

    def validate(self):
        if self.settings.arch != "x86_64":
            raise ConanInvalidConfiguration("Unsupported Architecture. This package currently only supports x86_64.")
        if self.settings.os not in ["Windows", "Macos", "Linux"]:
            raise ConanInvalidConfiguration("Unsupported os. This package currently only support Linux/Macos/Windows")
        if int(str(self.options.platformVersion)) < self.min_api_level or int(str(self.options.platformVersion)) > self.max_api_level:
            raise ConanException("Unsupported Android platform version: " + str(self.options.platformVersion) + " (supported [%i ... %i])" % (self.min_api_level, self.max_api_level))

    def build(self):
        key = self.settings.os
        get(self, **self.conan_data["sources"][self.version][str(key)], destination=self.source_folder)

        sdkmanager_bin = os.path.join(self.source_folder, "cmdline-tools", "bin", "sdkmanager")

        env = VirtualBuildEnv(self)
        buildEnv = env.vars()

        # Accept all the licenses
        p = Popen([sdkmanager_bin, '--sdk_root=%s' % self.source_folder, '--licenses'], env=buildEnv, universal_newlines=True, shell=True if self.settings.os == 'Windows' else False, stdout=PIPE, stdin=PIPE, stderr=STDOUT)
        p.communicate(input='y\ny\ny\ny\ny\ny\ny\ny\ny\ny\ny\ny\ny\ny\n')

        check_call('%s --sdk_root=%s --install "platforms;android-%s"' % (sdkmanager_bin, self.source_folder, str(self.options.platformVersion)), env=buildEnv, stdout=DEVNULL, stderr=STDOUT, shell=True)
        check_call('%s --sdk_root=%s --install "build-tools;%s"' % (sdkmanager_bin, self.source_folder, str(self.options.buildToolsRevision)), env=buildEnv, stdout=DEVNULL, stderr=STDOUT, shell=True)
        check_call('%s --sdk_root=%s --install "platform-tools"' % (sdkmanager_bin, self.source_folder), env=buildEnv, stdout=DEVNULL, stderr=STDOUT, shell=True)
        check_call('%s --sdk_root=%s --install "ndk;%s"' % (sdkmanager_bin, self.source_folder, self.options.ndkVersion), env=buildEnv, stdout=DEVNULL, stderr=STDOUT, shell=True)

    def package(self):
        copy(self, pattern="*", src=os.path.join(self.source_folder, "build-tools"), dst=os.path.join(self.package_folder, "build-tools"))
        copy(self, pattern="*", src=os.path.join(self.source_folder, "licenses"), dst=os.path.join(self.package_folder, "licenses"))
        copy(self, pattern="*", src=os.path.join(self.source_folder, "platforms"), dst=os.path.join(self.package_folder, "platforms"))
        copy(self, pattern="*", src=os.path.join(self.source_folder, "platform-tools"), dst=os.path.join(self.package_folder, "platform-tools"))
        copy(self, pattern="*", src=os.path.join(self.source_folder, "platforms"), dst=os.path.join(self.package_folder, "platforms"))
        copy(self, pattern="*", src=os.path.join(self.source_folder, "ndk"), dst=os.path.join(self.package_folder, "ndk"))
        with open(os.path.join(self.package_folder, self.toolchain_path), "w") as f:
            f.write("set(ANDROID_SDK_ROOT \"%s\" CACHE PATH \"Set ANDROID_SDK_ROOT\")" % self.package_folder)

    def package_info(self):
        self.output.info('Creating SDK_ROOT, ANDROID_SDK_ROOT environment variable: %s' % self.package_folder)
        self.buildenv_info.define_path("SDK_ROOT", self.package_folder)
        self.buildenv_info.define_path("ANDROID_SDK_ROOT", self.package_folder)
        self.output.info('Injecting cmaketoolchain:user_toolchain: %s' % self.toolchain_path)
        self.conf_info.append("tools.cmake.cmaketoolchain:user_toolchain", self.toolchain_path)
