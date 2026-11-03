# Signals

Every input to the [product loop](../../reference/product-loop.md) lands here as one row of [`signals.csv`](signals.csv): a customer said something, a thread appeared, a ticket came in, a metric missed, a test finished. Hypotheses aggregate signals.

Columns: `signal_id,date,source_type,source_ref,account,summary,detail,tags`. Rules, privacy and the duplicate rule: [`reference/signal-contract.md`](../../reference/signal-contract.md).

## Use the script, never the file

`scripts/signals/signals.py` is the only writer. Every command takes `--repo-root` (default `.`).

| Command | Does |
|---|---|
| `python scripts/signals/signals.py add --json FILE\|-` | Validate, de-duplicate and append one object or a list. Allocates `SIG-###`. |
| `python scripts/signals/signals.py check` | Validate the whole file. Exit 1 with `error:` lines if anything is wrong. |
| `python scripts/signals/signals.py show SIG-###` | One row plus the hypotheses that cite it. |
| `python scripts/signals/signals.py unassigned [--tag T]` | Signals no hypothesis cites yet. |

Add one by hand with `/log-signal`. `/customer-call` adds one per insight and feature request.

## Reading

Cite a signal in a hypothesis as `SIG-###` in its `## Signals` section. The integrity checks (`signals-*` in [`scripts/integrity-checks/`](../../scripts/integrity-checks/README.md)) flag invalid rows, hypotheses citing a missing or no signal, and signals nothing has picked up after 30 days.
