# conan-android-sdk

[![Conan Remote Recipe](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fapi.github.com%2Frepos%2FPrivatehive%2Fconan-android-sdk%2Fproperties%2Fvalues&query=%24%5B%3F(%40.property_name%20%3D%3D%20'conan-package')%5D.value&style=flat&logo=conan&label=conan&color=%232980b9)](https://conan.privatehive.de/ui/repos/tree/General/public-conan/de.privatehive) 

#### A conan package that provides the android sdk

---

| os        | arch     | CI Status                                                                                                                                                                                                                                                                 |
| --------- | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `Linux`   | `x86_64` | [![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/Privatehive/conan-android-sdk/main.yml?branch=master&style=flat&logo=github&label=Docker+build)](https://github.com/Privatehive/conan-android-sdk/actions?query=branch%3Amaster) |
| `Windows` | `x86_64` | [![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/Privatehive/conan-android-sdk/main.yml?branch=master&style=flat&logo=github&label=Docker+build)](https://github.com/Privatehive/conan-android-sdk/actions?query=branch%3Amaster) |

### Usage

The following packages will be installed:

- ndk;${ndkVersion}
- platforms;android-${platformVersion}
- build-tools;${buildToolsRevision}
- platform-tools

The NDK is also installed because the Gradle task "stripDebugDebugSymbols" searches for the NDK with the Version (specified in gradle.properties `androidNdkVersion`) in the SDK dir.

| option             | values | default        |
| ------------------ | ------ | -------------- |
| ndkVersion         | "ANY"  | "25.1.8937393" |
| buildToolsRevision | "ANY"  | "33.0.2"       |
| platformVersion    | 7..34  | 33             |
