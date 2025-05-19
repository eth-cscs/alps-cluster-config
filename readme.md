# Alps Cluster Configuration

The cluster-specific configuration and site-wide package repository for building uenv using [stackinator](https://github.com/eth-cscs/stackinator) on Alps.

## versioning

The `releases/v5` branch provides support for building uenv images using Spack up to and including version 0.23.
It should be used with the branch of the same name, `releases/v5` of Stackinator for building existing uenv images.

The `master` branch used to be the main development branch, before `main` became the main branch at the same time `releases/v5` was created.
The `master` branch is fixed at that point in time, and will be deleted in the future, once pipelines and workflows that depend on that specific version have been updated.

The `main` branch contains in-development support for the upcoming Spack v1.0 release.
