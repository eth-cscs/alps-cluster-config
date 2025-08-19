# Network configurations

This path contains `network.yaml` files for each micro-architecture (zen, gh200, etc).

* `a100`: A100 nodes in Balfrin/Bristen
* `gh200`: Grace-Hopper nodes in the Daint/Clariden/Santis
* `zen`: for the zen2 and zen3 sytems
* `amdgpu`: for `mi200`/`mi300` nodes

See the [CSCS hardware docs](https://docs.cscs.ch/alps/hardware/#alps-nodes) for more.

The files are sym-linked into the cluster configurations for respective clusters, so that we don't have to maintain copies of the same `network.yaml` file for every cluster.
