# chromtech_m1

A SiLA connector for Chromtech / Teledyne SSI M1-Class pumps, built with the UniteLabs CDK.

It implements these features from
[sila_abstract_base_features](https://github.com/RxnRover/sila_abstract_base_features):

- `MeteringPumpController` - start, stop, flow rate, max flow rate, estimated volume dispensed
- `KeypadController` - enable or disable the pump's front panel buttons

The pump is controlled over its serial protocol (Appendix A of the M1-Class Pump Operator Manual).
Its micro-USB port shows up as a virtual COM port; the RS-232 port works the same way.

## Getting Started

### Prerequisites

- Python 3.10 or newer
- [uv][] (`pipx install uv`)
- Access to the UniteLabs package index for `unitelabs-bus` (see the `.netrc` setup in the
  connector-factory instructions)
- The [sila_abstract_base_features](https://github.com/RxnRover/sila_abstract_base_features) repository

### Install

From this directory:

```sh
uv sync --all-extras
```

### Configure

Create a configuration file:

```sh
uv run config create --app unitelabs.chromtech_m1:create_app
```

This writes `config.json` in the current directory (it is git-ignored). Set these values for your pump:

| Field             | Description                                                            |
|-------------------|------------------------------------------------------------------------|
| `port`            | Serial port of the pump, e.g. `COM5` or `/dev/ttyUSB0`                 |
| `baudrate`        | Baud rate from the pump's setup menu, `9600` (default) or `19200`      |
| `simulation_mode` | `true` to use a simulated pump, `false` to control the real hardware   |

To find the port, plug in the pump and run `uv run python -m serial.tools.list_ports -v`. If the pump
does not appear, install the USB driver from the SSI website (Support > Downloads).

Run `uv run config show --app unitelabs.chromtech_m1:create_app` for a description of every value.

### Run

```sh
uv run connector start --app unitelabs.chromtech_m1:create_app -vvv
```

To use a configuration file at another location, add `-cfg <path to config>`.

On start-up the connector asks the pump for its maximum flow rate (`MF`); if the pump does not answer
within 5 seconds, start-up fails with an error. Logs are written to `logs/connector.log`.

## Usage

To interact with the running connector, we recommend using the
[SiLA Browser](https://gitlab.com/unitelabs/sila2/sila-browser).

### Encryption

To secure communication between the connector and its clients, you can enable TLS encryption. Install
the optional `cryptography` package and generate a certificate:

```sh
uv pip install cryptography
uv run certificate generate
```

Without any arguments this uses the default config location to get the connector's UUID and host
name, and prompts to update the config file to enable TLS. Use `-y` to update it without prompting,
`-e` to embed the certificate contents in the config file, `-cfg <path>` for a config file at another
location, or `--target <dir>` to change where `cert.pem` and `key.pem` are written.

If you do not let the command update your config, set these values under `sila_server` yourself:

- `certificate_chain` - the path to the `cert.pem` file
- `private_key` - the path to the `key.pem` file
- `tls` - a boolean that toggles on/off TLS encryption for the SiLA server

> **Important:** Never share the `key.pem` file with anyone. Only the `cert.pem` is required for
> clients to connect to encrypted servers.

## Development

### Dev-Mode

Run the connector against the simulated pump, reloading whenever source code changes:

```sh
uv run connector dev --app unitelabs.chromtech_m1:create_app
```

### Tests and linting

```sh
uv run pytest
uv run ruff format src/ && uv run ruff check src/ --fix
```

### pre-commit hooks

```sh
uv run pre-commit install
```

### Project layout

- `src/unitelabs/chromtech_m1/io/` - talks to the pump: serial framing (`ssi.py`), commands
  (`protocol.py`), and the simulated pump (`simulation.py`). No SiLA code.
- `src/unitelabs/chromtech_m1/features/` - SiLA features, each implementing an abstract base feature
  and calling into `io/`.
- `src/unitelabs/chromtech_m1/__init__.py` - `create_app`, which opens the pump connection and
  registers the features.

## Contact

If you found a bug, please use the [issue tracker][issue-tracker].

[issue-tracker]: https://github.com/RxnRover/sila_hackathon_devices/issues
[uv]: https://docs.astral.sh/uv/
