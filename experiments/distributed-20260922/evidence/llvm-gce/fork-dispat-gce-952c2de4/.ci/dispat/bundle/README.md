This package merges the verified LLVM, Clang and LLD install trees without
compiling its providers. See [the setup guide](../README.md). Changes to shared
inputs such as `cmake/`, `third-party/`, and release setup must explicitly name
a package such as `llvm` in their CCME scope; fixed versioning moves the group.
