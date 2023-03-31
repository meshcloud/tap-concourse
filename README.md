# tap-concourse

`tap-concourse` is a Singer tap for Concourse CI.

Warning: this tap uses the private Concourse ATC API like the `fly` cli tool. This is not an official integration.

Built with the [Meltano Tap SDK](https://sdk.meltano.com) for Singer Taps.

## Installation

At this moment, the tap is only available via GitHub.
To install via `meltano.yml`, specify this repository via pip_url

```yaml
plugins:
  extractors:
  - name: tap-concourse
    namespace: tap-concourse
    pip_url: git+https://github.com/meshcloud/tap-concourse
    executable: tap-concourse
```

## Configuration

### Accepted Config Options

- `base_url`: meshStack federation config
- `team`: name of the concours team to fetch data from
- `build_start_id`: id to start collecting data from - use 0 to start from beginning of time
- `build_lookback_count`: size of lookback window to catch running builds on incremental replication
- `auth`: authentication options
  - `basic`: basic auth configuration
    - `username`: username
    - `password`: password

Note: The last few pages of builds in concourse typically have running builds that have no final status.
This means the tap cannot assume that it has fetched all builds in their final state.
The `build_lookback_count` configure the size of a lookback window (counted in build ids) to collect
updates for these builds on the next incremental run of the tap.

A full list of supported settings and capabilities for this tap is available by running:

```bash
tap-concourse --about
```

## Usage

You can easily run `tap-concourse` by itself or in a pipeline using [Meltano](https://meltano.com/).

### Executing the Tap Directly

```bash
tap-concourse --version
tap-concourse --help
tap-concourse --config CONFIG --discover > ./catalog.json
```

## Developer Resources

### Initialize your Development Environment

```bash
pipx install poetry
poetry install
```

### Create and Run Tests

Create tests within the `tap-concourse/tests` subfolder and
  then run:

```bash
poetry run pytest
```

You can also test the `tap-concourse` CLI interface directly using `poetry run`:

```bash
poetry run tap-concourse --help
```

### Testing with [Meltano](https://www.meltano.com)

For local development on the tap, specify an executable directly in `meltano.yml`

```yaml
executable: /path/to/tap-concourse/.venv/bin/tap-concourse
```

### SDK Dev Guide

See the [dev guide](https://sdk.meltano.com/en/latest/dev_guide.html) for more instructions on how to use the SDK to 
develop your own taps and targets.
