# agents.md

## versions

`versions` is a self-contained Python script that uses `uv` as its runner (shebang: `#!/usr/bin/env -S uv run --script`). Dependencies (`packaging`, `rich`, `tabulate`) are declared inline via PEP 723 script metadata, so `uv` installs them automatically on first run — no separate install step needed.

Run it with:
```
./versions
```

## Data collected

### Properties (`collect_properties`)

A list of `{key, value}` string pairs describing the system environment, collected in order:

- `os`: parsed from `/etc/os-release` (`NAME` + `VERSION_ID`), e.g. `"SLES 15.6"`.
- `cluster`: from the `CLUSTER_NAME` environment variable.
- `nvidia-driver` / `cuda`: from `nvidia-smi --version` (only added if `nvidia-smi` is available).

### Packages (`collect_data`)

A fixed list of packages is defined in `PACKAGES` (a dict of logical name → RPM name). For each, `query_rpm` is called, which runs `rpm -q --queryformat '%{VERSION} %{RELEASE}'` and returns:

- `version`: the package version (`%{VERSION}` field), stripped to the leading numeric `major.minor.patch[.N]` part to drop non-PEP 440 build suffixes like `_cray_21_g120f975`.
- `shs`: a `Version` extracted from the `%{RELEASE}` field if it contains a `SHS<X.Y.Z>` substring — present only for Slingshot Host Software packages.
- `prefix`: install prefix inferred by scanning the RPM file list (`rpm -ql`) for standard subdirectory names (`bin`, `lib`, `include`, etc.).

### GCC (`collect_gcc_data`)

All installed `gccN` base packages are discovered by scanning `rpm -qa` for names matching `gcc<digits>`. For each major version found:

- `version`, `prefix`: obtained via the same `query_rpm` as above.
- `c` / `cxx` / `fortran`: path to the versioned compiler binary (e.g. `/usr/bin/gcc-13`), or `None` if the corresponding RPM (`gccN`, `gccN-c++`, `gccN-fortran`) is not installed.
