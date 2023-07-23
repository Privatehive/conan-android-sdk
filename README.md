# conan-android-sdk

### A conan package that provides the android sdk

The following packages will be installed:

- platforms;android-${platformVersion}
- build-tools;${buildToolsRevision}
- platform-tools

| option             | values | default  |
| ------------------ | ------ | -------- |
| buildToolsRevision | "ANY"  | "33.0.2" |
| platformVersion    | 7..34  | 33       |
