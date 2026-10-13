# Project charter

## Purpose

Build a durable reference for understanding how Sony structured the ILCE-6000 firmware and for locating the smallest safe extension point when porting a new feature.

For each feature, the research should answer:

1. Which firmware image, process, library, or configuration owns it?
2. What call, IPC, file, or protocol path connects the trigger to the implementation?
3. Which addresses, structures, constants, and firmware-version differences matter?
4. How can another researcher reproduce and test the result safely?

## Scope

The target is the Sony ILCE-6000 / α6000. Firmware 3.21 is the baseline. Earlier versions will be added when their update packages can be acquired and hashed.

The work covers acquisition, offline extraction, region mapping, boot and updater structure, kernel and Android components, native userspace, camera services, settings, media, lens, USB, Wi-Fi, application interfaces, static analysis, read-only runtime observations, version comparisons, and feature-porting case studies.

## Safety and publication rules

- Begin with offline and read-only analysis.
- Do not write to camera flash while building the platform map.
- Keep proprietary firmware images, decrypted trees, raw NAND dumps, recovered APKs, and personal camera data private unless distribution is clearly authorized.
- Keep raw decompiler pseudocode, assembly, strings, reference graphs, and native value-flow output from proprietary firmware in the private research archive unless distribution is separately reviewed.
- Publish hashes, offsets, derived metadata, scripts, and explanations so another researcher can reproduce the work from the official source.
- Apply project licenses only to original scripts, documentation, and annotations; do not grant a project license to Sony or other third-party material.
- Record the exact camera, firmware version, tool version, command, and input hash for every result.

## Evidence standard

Each claim receives one status:

- **Confirmed**: reproduced from bytes, metadata, or a controlled runtime observation.
- **Strong inference**: supported by multiple independent observations but not fully reproduced.
- **Working hypothesis**: plausible interpretation awaiting a confirming experiment.
- **Unknown**: currently lacks enough evidence.

Decompiler output is a lead. A confirmed claim should connect it to assembly, references, data bytes, runtime behavior, or an independent comparison.

## Workflow

```text
source package or authorized dump
    -> hash and manifest
    -> extract and verify regions
    -> import native images into REA/Ghidra
    -> record functions, strings, calls, data, and addresses
    -> test a hypothesis with a controlled observation
    -> publish the map, evidence, limitation, and next question
```

REA is the investigation interface. Extracted native images remain the durable source material, and exported evidence remains readable without an active REA session.

## Milestones

| ID | Outcome | Exit condition |
| --- | --- | --- |
| M0 | Charter and research ledger | Scope, safety, evidence rules, and baseline are recorded |
| M1 | Reproducible acquisition | One firmware package is hashed and provenance is recorded |
| M2 | Verified extraction | The package is unpacked and the region map is reproducible |
| M3 | REA/native-analysis baseline | One extracted native image is analyzed and archived |
| M4 | Platform map | Boot, kernel, Android, services, and native components are connected |
| M5 | Subsystem maps | At least three feature-oriented paths are documented |
| M6 | Version comparison | The same anchors are compared across at least two versions |
| M7 | Feature case study | One small feature is traced, reproduced, and tested end to end |
| M8 | Reference release | A clean researcher can reproduce the documented workflow |
