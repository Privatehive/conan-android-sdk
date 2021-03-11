#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, tools
from conans.errors import ConanException, ConanInvalidConfiguration
from shutil import copytree
from subprocess import Popen, PIPE, STDOUT
import os


class AndroidSDKConan(ConanFile):
    min_api_level = 7
    max_api_level = 30
    name = "android-sdk"
    version = "latest"
    description = "Android commandline tools to obtain the Android SDK. It includes the complete set of development and debugging tools for Android"
    url = "https://github.com/Tereius/conan-android-sdk"
    homepage = "https://developer.android.com/studio#cmdline-tools"
    license = "Apache 2.0"
    short_paths = True
    no_copy_source = True
    build_requires = "java_installer/8.0.144@tereius/stable"
    options = {"buildToolsRevision": "ANY", "platformVersion": list(range(min_api_level, max_api_level + 1))}
    default_options = {"buildToolsRevision": "28.0.3", "platformVersion": 24}
    settings = "os", "arch", "os_build", "arch_build"

    def __getattr_recursive(self, obj, name, default):
        if obj is None:
            return default
        split_names = name.split('.')
        depth = len(split_names)
        if depth == 1:
            return getattr(obj, name, default)
        return self.__getattr_recursive(getattr(obj, split_names[0], default), ".".join(split_names[1:]), default)

    def isSingleProfile(self):
        settings_target = getattr(self, 'settings_target', None)
        if settings_target is None:
            return True
        return False

    def get_setting(self, name: str):
        is_build_setting = name.endswith('_build')
        depth = len(name.split('.'))
        settings_target = getattr(self, 'settings_target', None)
        if settings_target is None:
            # It is running in 'host' context
            setting_val = self.__getattr_recursive(self.settings, name, None)
            if setting_val is None:
                raise ConanInvalidConfiguration("Setting in host context with name %s is missing. Make sure to provide it in your conan host profile." % name)
            return setting_val
        else:
            # It is running in 'build' context and it is being used as a build requirement
            setting_name = name.replace('_build', '')
            if is_build_setting:
                setting_val = self.__getattr_recursive(self.settings, setting_name, None)
            else:
                setting_val = self.__getattr_recursive(settings_target, setting_name, None)
            if setting_val is None:
                raise ConanInvalidConfiguration("Setting in build context with name %s is missing. Make sure to provide it in your conan %s profile." % (setting_name, "build" if is_build_setting else "host"))
            return setting_val

    @property
    def sdkmanager_bin(self):
        #return os.path.join(self.source_folder, "cmdline-tools", "bin", "sdkmanager")
        return os.path.join(self.source_folder, "tools", "bin", "sdkmanager")

    def configure(self):
        if int(str(self.options.platformVersion)) < self.min_api_level or int(str(self.options.platformVersion)) > self.max_api_level:
            raise ConanException("Unsupported Android platform version: " + str(self.options.platformVersion) + " (supported [%i ... %i])" % (self.min_api_level, self.max_api_level))
        if self.get_setting("os_build") not in ["Windows", "Macos", "Linux"]:
            raise ConanException("Unsupported build os: %s. Supported are: Windows, Macos, Linux" % self.get_setting("os_build"))
        if self.get_setting("arch_build") != "x86_64":
            raise ConanException("Unsupported build arch: %s. Supported is: x86_64" % self.get_setting("arch_build"))

    def source(self):
        # TODO: Switch url if http 403 error is gone
        if self.get_setting("os_build") == 'Windows':
            source_url = "https://dl.google.com/android/repository/sdk-tools-windows-4333796.zip"
            #source_url = "https://dl.google.com/android/repository/commandlinetools-win-6858069_latest.zip"
            tools.get(source_url)
        elif self.get_setting("os_build") == 'Linux':
            source_url = "https://dl.google.com/android/repository/sdk-tools-linux-4333796.zip"
            #source_url = "https://dl.google.com/android/repository/commandlinetools-linux-6858069_latest.zip"
            tools.get(source_url, keep_permissions=True)
        elif self.get_setting("os_build") == 'Macos':
            source_url = "https://dl.google.com/android/repository/sdk-tools-mac-4333796.zip"
            #source_url = "https://dl.google.com/android/repository/commandlinetools-mac-6858069_latest.zip"
            tools.get(source_url, keep_permissions=True)
        else:
            raise ConanException("Unsupported build os: " + self.get_setting("os_build"))

    def build(self):
        p = Popen([self.sdkmanager_bin, '--sdk_root=%s' % self.build_folder, '--licenses'], universal_newlines=True, shell=True if tools.os_info.is_windows else False, stdout=PIPE, stdin=PIPE, stderr=STDOUT)
        p.communicate(input='y\ny\ny\ny\ny\ny\ny\ny\ny\ny\ny\ny\ny\ny\n')
        self.run('%s --sdk_root=%s --install "platforms;android-%s"' % (self.sdkmanager_bin, self.build_folder, str(self.options.platformVersion)))
        self.run('%s --sdk_root=%s --install "build-tools;%s"' % (self.sdkmanager_bin, self.build_folder, str(self.options.buildToolsRevision)))
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
        if self.isSingleProfile():
            self.info.include_build_settings()

    def package_info(self):
        sdk_root = self.package_folder

        self.output.info('Creating SDK_ROOT, ANDROID_SDK_ROOT environment variable: %s' % sdk_root)
        self.env_info.SDK_ROOT = sdk_root
        self.env_info.ANDROID_SDK_ROOT = sdk_root

        self.output.info('Creating ANDROID_BUILD_TOOLS_REVISION environment variable: %s' % str(self.options.buildToolsRevision))
        self.env_info.ANDROID_BUILD_TOOLS_REVISION = str(self.options.buildToolsRevision)
