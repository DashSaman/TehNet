# Natural educational cable visuals

**Goal:** Respond to the owner's request for real photographs and more natural 3D presentation in the existing localhost preview.

**Architecture:** Keep the production media review policy and renderer unchanged. Replace the local demo presentation with a real-photo-first gallery, and improve our original normalized educational GLB using geometry and PBR materials. Public 3D references inform appearance only; their geometry, textures and brand claims are not copied.

**Scope:** `ops/build-exploded-demo.py`, demo-only templates in `ops/visuals/`, licensed educational photographs in `content/media/educational-cable-reference/`, focused browser checks and documentation. Existing branch continues; production runtime is outside this change.

**Constraints:** Photograph bytes remain unchanged and checksummed. Source, author and public-domain dedication stay visible. These Cat7 educational photographs are not pictures of any TehNet SKU. No inferred micron values, exact materials, CAD provenance, real360 sequence or product identity. No payment, indexing or external publication changes.

- [x] Inspect real photographic references and public 3D examples; verify reuse status separately from visual inspiration.
- [x] Add real-photo default, source/credit, local original download and explicit photo/3D switch; preserve lazy model loading.
- [x] Improve the original GLB: capped curved tubes, woven shield geometry, foil surface variation, distinct twisted-pair colours and matte/metal PBR response.
- [x] Build and verify desktop/mobile, reduced/normal motion, switches, image checksums, native animation and absence of external asset requests; inspect screenshots.
- [x] Record results and remaining exact-SKU evidence requirements in HANDOFF/PROGRESS/TASKS. Commit the bounded change after final diff review.

Review focus: switching away during model load; returning to an exploded model; narrow-screen framing; source-image/hash drift; truthful alt/caption text in both modes.
