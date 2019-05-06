#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, tools
from conans.errors import ConanException
from shutil import copytree
from subprocess import Popen, PIPE, STDOUT
import time


class AndroidSDKConan(ConanFile):
    name = "android-sdk"
    version = "26.1.1"
    description = "Android SDK Tools is a component for the Android SDK. It includes the complete set of development and debugging tools for Android"
    url = "https://github.com/Tereius/conan-android-sdk"
    homepage = "https://developer.android.com/studio/releases/sdk-tools"
    license = "Apache 2.0"
    short_paths = True
    no_copy_source = True
    build_requires = "java_installer/8.0.144@tereius/stable"
    options = {"bildToolsRevision": "ANY"}
    default_options = "bildToolsRevision=28.0.2"
    settings = {"os_build": ["Windows", "Linux", "Macos"],
                "os": ["Android"]}

    min_api_level = 7
    max_api_level = 28

    def configure(self):
        if int(str(self.settings.os.api_level)) < self.min_api_level or int(str(self.settings.os.api_level)) > self.max_api_level:
            raise ConanException("Unsupported API level: " + str(self.settings.os.api_level) + " (supported [%i ... %i])" % (self.min_api_level, self.max_api_level))

    def source(self):
        if self.settings.os_build == 'Windows':
            source_url = "https://dl.google.com/android/repository/sdk-tools-windows-4333796.zip"
            tools.get(source_url, sha256="7e81d69c303e47a4f0e748a6352d85cd0c8fd90a5a95ae4e076b5e5f960d3c7a")
        elif self.settings.os_build == 'Linux':
            source_url = "https://dl.google.com/android/repository/sdk-tools-linux-4333796.zip"
            tools.get(source_url, sha256="92ffee5a1d98d856634e8b71132e8a95d96c83a63fde1099be3d86df3106def9")
        elif self.settings.os_build == 'Macos':
            source_url = "https://dl.google.com/android/repository/sdk-tools-darwin-4333796.zip"
            tools.get(source_url, sha256="ecb29358bc0f13d7c2fa0f9290135a5b608e38434aad9bf7067d0252c160853e")
        else:
            raise ConanException("Unsupported build os: " + self.settings.os_build)

    def build(self):
        p = Popen(["%s/tools/bin/sdkmanager" % (self.source_folder), '--licenses'], universal_newlines=True ,shell=True, stdout=PIPE, stdin=PIPE, stderr=STDOUT)
        p.communicate(input='y\ny\ny\ny\ny\ny\ny\ny\ny\ny\ny\ny\ny\ny\n')
        self.run('"%s/tools/bin/sdkmanager" --install platforms;android-%s' % (self.source_folder, str(self.settings.os.api_level)))
        self.run('"%s/tools/bin/sdkmanager" --install build-tools;%s' % (self.source_folder, str(self.options.bildToolsRevision)))
        self.run('"%s/tools/bin/sdkmanager" --install platform-tools' % (self.source_folder))

    sdk_copied = False

    def package(self):
        # Called twice because of 'no_copy_source'. First from source-, then from build-dir
        if not self.sdk_copied:
            copytree(self.source_folder + "/build-tools", self.package_folder + "/build-tools")
            copytree(self.source_folder + "/licenses", self.package_folder + "/licenses")
            copytree(self.source_folder + "/platforms", self.package_folder + "/platforms")
            copytree(self.source_folder + "/tools", self.package_folder + "/tools")
            self.sdk_copied = True

    def package_info(self):
        sdk_root = self.package_folder

        self.output.info('Creating SDK_ROOT, ANDROID_SDK_ROOT environment variable: %s' % sdk_root)
        self.env_info.SDK_ROOT = sdk_root
        self.env_info.ANDROID_SDK_ROOT = sdk_root

        self.output.info('Creating ANDROID_BUILD_TOOLS_REVISION environment variable: %s' % str(self.options.bildToolsRevision))
        self.env_info.ANDROID_BUILD_TOOLS_REVISION = str(self.options.bildToolsRevision)
