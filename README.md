# tap-concourse

`tap-concourse` is a Singer tap for Concourse CI

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
- `auth`: authentication options
  - `bearer_token`: bearer token

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
