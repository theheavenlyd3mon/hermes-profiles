# Onyx Aerial Mesh — Master Packet R4-DRAFT (familiarization digest)

Source: `~/Downloads/ONYX-AERIAL-MESH-MASTER-PACKET-R4-DRAFT.html`
(5.8 MB single-file HTML snapshot; text dump pattern: strip script/style, strip tags → `/tmp/onyx-packet.txt`, 590K words.)

Familiarized 2026-08-12 (Senna). Snapshot 2026-08-12T13:45:48Z, digest `f332e52cfd80…`, source root `D:\BlueStone\onyx-aerial-mesh`, 251 artifacts (117 MD, 57 CSV, 50 PY, 17 JSON). Submitting entity: Onyx Intelligence Systems LLC (exact legal name flagged unverified).

## What it is
Single-file controlled source packet for **Onyx Aerial Mesh** — a software-in-the-loop (SIL) reference prototype for AI-controlled squad/platoon UAS connected to TOCs (tactical operations centers). **R4-DRAFT is NOT an authorization**: no physical flight, RF, TOC connection, CUI, targeting/effects, contract, or external release. Banner is explicit.

## The system (OAM-SIL-V1)
- Proves command/policy/audit/sync architecture before hardware selection: signed mission-intent capsules, geofence/altitude/battery/lost-link enforcement, platoon deconfliction, store-and-forward TOC gateway, hash-chained dev-signed audit ledger, **Operator Agent** increment (one identity-bound edge support agent per operator; role/currency-filtered local knowledge; cited suggestions; paired-human release required before sync).
- Architecture: logical ontology (14 entity classes, 15 relations, 6 planes, 8 invariants) cleanly separated from physical topologies (4 profiles: OAM-SIL-V1 → squad edge cell → platoon federated mesh → TOC-connected). Compute placement OPN-L/OPN-H/SN-G/PN-G (incl. 3090-class vehicle/shelter concept) deliberately unselected.
- Tech status: Python 3.14.6 stdlib-only, zero third-party deps; 146/146 tests passing 2026-08-11; interactive 3D "Hermes Flight Lab" simulator (120 Hz deterministic physics, 4 aircraft).

## Compliance status (the bulk of the packet)
- **NOT READY** for: proposal release, contract start, federal award, CUI, live flight, TOC connection, classified work. 34 controls: 0 `complete_verified`, 28 `not_started`. 63-item clause screen, 17 portal paths (0 active), 34-item forms catalog, 76 signature routes with 0 signed. Objective audit: `NOT_ACHIEVED`.
- Approval chain A–H (entity → export → cyber → product qualification → air/spectrum → AI assurance → RMF → acquisition), mandatory 10-step sequence, Days 0–180 execution schedule.
- Cyber: NIST 800-171 R2 (110 reqs) and R3 (97 reqs) kept as separate non-interchangeable baselines; 0 implemented/assessed. No CUI authorization.
- **Do-not-claim register**: no "SOCOM approved", "ATO'd", "CMMC certified", "airworthy", "Blue UAS approved", "FAA approved" etc. without issuer-linked evidence. Templates ≠ approvals.

## Governance story (critical)
- **2026-08-12 scope remediation (OAM-SCOPE-CR-001)**: "non-weaponized" was **agent-inherited, unauthorized language** — program owner corrected it. Packet now strictly separates USER_AUTHORIZED / CURRENT_IMPLEMENTATION / PROPOSED_CONTROL / DECISION_PENDING / EXTERNAL_CONDITIONAL. Payload/effects, targeting, autonomy level, mission set, biometrics all DECISION_PENDING by design.
- Third-party: `sieuwe1/Autonomous-Ai-drone-scripts` reviewed at pinned commit `01765567…`; no license → `REFERENCE_CONCEPTS_ONLY_DO_NOT_COPY_OR_EXECUTE`, nothing copied.
- Open tech blockers: gateway restart durability, production identity (HMAC dev signer ≠ hardware-backed), operational corpus authority, privacy/HSI approval, independent review.

## Key references inside the packet
- README (run: `python -m onyx_mesh.demo`, `python -m unittest discover -s tests -v`)
- CONOPS.md (echelons, autonomy envelope, hero demos A–D, work packages 1–6)
- SYSTEM-ONTOLOGY-AND-TOPOLOGY.md, OPERATOR-AGENT-ARCHITECTURE.md
- compliance/READINESS-REPORT.md (generated from registers — the single highest-signal section)
- compliance/MASTER-COMPLIANCE-AND-REGISTRATION-PLAN.md (approval chain, execution schedule)
- compliance/SCOPE-PROVENANCE-AND-DECISION-REGISTER.md, prepared-paperwork/07-ESOF-SCOUT-CARD-DRAFT.md (TRL 3 self-assessment), 10-TEST-EVIDENCE-CROSSWALK.md

## Session follow-up
User asked to "get familiar" — digest delivered 2026-08-12; next step awaits user direction (review/critique, next-doc drafting, evidence work, etc.). Validators: `python compliance\validate_*.py` + `readiness.py --write` on the Windows source root.
