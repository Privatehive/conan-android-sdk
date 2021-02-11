#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, tools
from conans.errors import ConanException
from shutil import copytree
from subprocess import Popen, PIPE, STDOUT
import os


class AndroidSDKConan(ConanFile):
    name = "android-sdk"
    version = "latest"
    description = "Android commandline tools to obtain the Android SDK. It includes the complete set of development and debugging tools for Android"
    url = "https://github.com/Tereius/conan-android-sdk"
    homepage = "https://developer.android.com/studio#cmdline-tools"
    license = "Apache 2.0"
    short_paths = True
    no_copy_source = True
    build_requires = "java_installer/8.0.144@tereius/stable"
    options = {"bildToolsRevision": "ANY"}
    default_options = "bildToolsRevision=28.0.2"
    settings = {"os": ["Android"], "os_build": ["Windows", "Linux", "Macos"], "arch_build": ["x86_64"]}

    min_api_level = 7
    max_api_level = 30

    @property
    def sdkmanager_bin(self):
        return os.path.join(self.source_folder, "cmdline-tools", "bin", "sdkmanager")

    def configure(self):
        if int(str(self.settings.os.api_level)) < self.min_api_level or int(str(self.settings.os.api_level)) > self.max_api_level:
            raise ConanException("Unsupported API level: " + str(self.settings.os.api_level) + " (supported [%i ... %i])" % (self.min_api_level, self.max_api_level))

    def source(self):
        if self.settings.os_build == 'Windows':
            source_url = "https://dl.google.com/android/repository/commandlinetools-win-6858069_latest.zip"
            tools.get(source_url)
        elif self.settings.os_build == 'Linux':
            source_url = "https://dl.google.com/android/repository/commandlinetools-linux-6858069_latest.zip"
            tools.get(source_url, keep_permissions=True)
        elif self.settings.os_build == 'Macos':
            source_url = "https://dl.google.com/android/repository/commandlinetools-mac-6858069_latest.zip"
            tools.get(source_url, keep_permissions=True)
        else:
            raise ConanException("Unsupported build os: " + self.settings.os_build)

    def build(self):
        p = Popen([self.sdkmanager_bin, '--sdk_root=%s' % self.build_folder, '--licenses'], universal_newlines=True, shell=True if self.settings.os_build == "Windows" else False, stdout=PIPE, stdin=PIPE, stderr=STDOUT)
        p.communicate(input='y\ny\ny\ny\ny\ny\ny\ny\ny\ny\ny\ny\ny\ny\n')
        self.run('%s --sdk_root=%s --install "platforms;android-%s"' % (self.sdkmanager_bin, self.build_folder, str(self.settings.os.api_level)))
        self.run('%s --sdk_root=%s --install "build-tools;%s"' % (self.sdkmanager_bin, self.build_folder, str(self.options.bildToolsRevision)))
        self.run('%s --sdk_root=%s --install "platform-tools"' % (self.sdkmanager_bin, self.build_folder))

    sdk_copied = False

    def package(self):
        # Called twice because of 'no_copy_source'. First from source-, then from build-dir
        if not self.sdk_copied:
            copytree(os.path.join(self.build_folder, "build-tools"), os.path.join(self.package_folder, "build-tools"))
            copytree(os.path.join(self.build_folder, "licenses"), os.path.join(self.package_folder, "licenses"))
            copytree(os.path.join(self.build_folder, "platforms"), os.path.join(self.package_folder, "platforms"))
            copytree(os.path.join(self.build_folder, "tools"), os.path.join(self.package_folder, "tools"))
            self.sdk_copied = True

    def package_id(self):
        self.info.include_build_settings()

    def package_info(self):
        sdk_root = self.package_folder

        self.output.info('Creating SDK_ROOT, ANDROID_SDK_ROOT environment variable: %s' % sdk_root)
        self.env_info.SDK_ROOT = sdk_root
        self.env_info.ANDROID_SDK_ROOT = sdk_root

        self.output.info('Creating ANDROID_BUILD_TOOLS_REVISION environment variable: %s' % str(self.options.bildToolsRevision))
        self.env_info.ANDROID_BUILD_TOOLS_REVISION = str(self.options.bildToolsRevision)
