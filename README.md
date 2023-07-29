# conan-android-sdk

### A conan package that provides the android sdk

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
