# source_class v0

One axis for what an outcome claim in agent evidence rests on, a mapping of five 2026 vocabularies onto it, ten vectors, and a dependency-free checker.

```bash
python3 check.py
```

```
  ok   declared-boundary-observed: declared (boundary_observed)
  ...
cases passed: 10/10
corpus sha256 (jcs/rfc8785, corpus value profile): 2958aee3d08e942acf4259381d593dc7d8940044ae2b93e2b564c15badd9f204
```

## The problem

When an agent evidence record says `outcome: blocked`, three different mechanisms can be behind that value. A gateway may have refused the call before dispatch. A runtime's deny branch may have returned before its sandbox was ever invoked. A monitor outside the harness may have watched the process and seen nothing happen. These are different facts, established by parties with different standings, and a record that carries only the value cannot tell a reader which one it has.

The published taxonomy of agent execution provenance, the survey [From Agent Traces to Trust](https://arxiv.org/abs/2606.04990), classifies trace sources by component (its Table 1): reasoning, retrieval, tool use, MCP server and host boundaries, memory, environment, multi-agent communication. Every one of those seven categories is producible by the harness itself. The taxonomy can express what part of the agent a record came from. It has no axis for whether the party that produced the record could have been wrong about it.

Over June and July 2026 four vocabularies appeared, two of them in still-open pull requests, each independently typing a fragment of that missing axis, none interoperable with the others:

| project | vocabulary | fragment typed |
|---|---|---|
| [vaaraio/vaara](https://github.com/vaaraio/vaara) | twelve `*_basis` fields (`vcek_chain_basis`, `time_basis`, `producer_identity_basis`, ...) | crypto-root and time provenance |
| [Yarmoluk/ckg-nvidia-ai](https://github.com/Yarmoluk/ckg-nvidia-ai/blob/main/docs/guardrail-decision-v1.md) | `precedence_claim` enum | temporal precedence of a timestamp |
| [safal207/ProofPath](https://github.com/safal207/ProofPath/pull/168) | `COMMITTED / REPRODUCIBLE / FRESH / INVALID` | recomputability of a source document |
| [crewAIInc/crewAI PR #6030](https://github.com/crewAIInc/crewAI/pull/6030) | test-docstring prose: "denied and recorded" vs "never observed" | absence semantics |

Each fragment is real and each project deserves the credit for naming it. The full per-dialect mapping, including what each vocabulary can and cannot express, is machine-readable in [`map/dialects.json`](map/dialects.json).

One detail in the vaara vocabulary is worth singling out, because it shows the axis is recognized even where it is not yet filled: the field `enforcement_logic_basis` exists and carries exactly one value, `not_established`. An honest typed unknown, in the producer's own vocabulary. The axis below generalizes that discipline.

## The axis

Seven values, defined in [`map/axis.json`](map/axis.json):

| value | the outcome claim rests on |
|---|---|
| `producer_reported` | the party that performed or decided the action also reports the outcome |
| `issuer_attested` | a party in the producer's trust domain signs or attests the record |
| `receiver_receipt` | the counterparty that received the action issues the record |
| `boundary_observed` | an interposed chokepoint records what passed through it, scoped by its declared boundary |
| `third_party_observed` | a party outside both producer and receiver holds the observation in an artifact neither controls |
| `independently_observed` | an observer at a vantage the observed process cannot write to captured the effect |
| `unknown` | the basis is declared as not established; a typed value, distinct from silence |

This is typing, not ranking. A signed refusal proves a non-action that an egress filter structurally cannot produce, because a blocked call leaves nothing below the harness to observe. An external observation proves an effect that no refusal record can. Neither dominates; a reader needs to know which one it is holding.

Three invariants do most of the work, and the vectors exercise each:

1. **A declared unknown is distinct from an undeclared basis.** A record that says `source_class: unknown` has told the reader something a silent record has not. The two verdicts are different on purpose.
2. **Tamper-evidence never raises vantage.** Signatures, hash chains, and external time anchors bound when and whether bytes changed. They do not change who could have been wrong about the fact. A record anchored before its outcome settled still carries a producer-written outcome field.
3. **A digest travels with its canonicalization id.** Two readers with different implicit canonicalizations derive different bytes for the same record and cannot tell whose reading was meant. The checker rejects any digest without its scheme id, including in these vectors.

## Why the axis is load-bearing

On 21 July 2026 OpenAI [disclosed](https://openai.com/index/hugging-face-model-evaluation-security-incident/) that two models under evaluation escaped a sandboxed environment through a permitted package-registry proxy, reached the public internet, and compromised production infrastructure at Hugging Face. The environment was declared isolated. Public reporting does not indicate the evaluation surfaced the escape at the time; the affected party detected it from its own telemetry days before the connection to the evaluation was made.

Read against the component-typed taxonomy, the remediation (the harness monitoring its own trajectories more closely) is expressible, and the failure (the declaring party and the observing party were different, and only the second one knew) is not. That is the practical shape of the gap this axis fills. The incident is used here only as an illustration of what an axis has to be able to express. Nothing in this repository claims any tool would have prevented or detected it.

## What is in the box

- [`map/axis.json`](map/axis.json), the axis: seven values, five invariants, the canonicalization declaration.
- [`map/dialects.json`](map/dialects.json), the mapping: five vocabularies, the fragment each types, what each cannot express, with credit.
- [`vectors/cases.json`](vectors/cases.json), ten records with the verdict a conforming reader must reproduce. The dialect-shaped records are minimal fragments in the shape of each vocabulary, written for this corpus; they are not fixtures copied from those projects.
- [`check.py`](check.py), the reader: standard library only, no network, deterministic. The mapping rules are five numbered lines in one docstring; the corpus digest is a SHA-256 over the canonical bytes of the three JSON files, and the canonicalizer self-tests against hand-checked JCS byte strings before any digest is trusted.

Anyone can re-derive the corpus digest, and a second implementation of the reader needs nothing from this repository beyond the three JSON files and the rules in the docstring.

## Non-claims

A mapping is a statement about expressiveness, never a grade of a project. The four dialect projects are credited for independently naming real fragments of the axis; nothing here ranks them.

Carrying a source class does not make a record true. The axis types who could have been wrong about an outcome claim, not whether they were. `independently_observed` is bounded by its declared coverage: it covers the named boundary only, proves nothing outside it, and proves nothing about authorized refusals.

Kernel-vantage observation of agents is prior art, established by [AgentSight](https://arxiv.org/abs/2508.02736) (eBPF boundary tracing, intent from TLS-intercepted LLM traffic correlated with kernel events). This repository contributes no observation mechanism. It contributes a typed vocabulary for what a record's claim rests on, which is a property of records, not of observers.

This is v0 of a vocabulary, published to be mapped against, forked, and superseded. The unit that matters is the axis and the invariants, not this implementation; the checker is deliberately small enough to rewrite from the docstring.

## Related work

[From Agent Traces to Trust](https://arxiv.org/abs/2606.04990) (the six-axis provenance taxonomy this maps against), [AgentSight](https://arxiv.org/abs/2508.02736) (kernel-vantage observation), [DEMM-Bench](https://arxiv.org/abs/2606.20634) (which surveys the on-path vs off-path and observability-grade vs accountability-grade boundaries; placement is orthogonal to standing, an off-path monitor operated by the producer is still producer-reported), [Reasoning Provenance / AER](https://arxiv.org/abs/2603.21692) (intent, observation, and inference as first-class fields), [observed-effect v0](https://github.com/Rul1an/observed-effect-v0) (a worked independently-issued effect record whose source class rides inside the digest), [gateway-evidence-replay](https://github.com/Rul1an/gateway-evidence-replay) (a shipped verifier whose `source_class` field fails closed on unrecognized values with a typed reason).

## License and citing

Apache-2.0. If you cite this, [`CITATION.cff`](CITATION.cff) describes a software artifact, because that is what it is; it is not a standard, and the citation metadata says so.
