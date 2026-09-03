# Memory-mapped model loading

Loading a multi-gigabyte model file the naive way -- `read()` the
whole file into a heap buffer, then parse tensors out of that buffer --
pays two costs an inference engine would rather avoid: the *time* to
copy every byte of the file through the kernel's I/O path into process
memory before any inference can start, and the *physical RAM* to hold
a full copy of the file in addition to whatever the OS's own page
cache is already holding for it. **Memory-mapped (`mmap`) loading**
avoids both by asking the operating system to map the file's pages
directly into the process's virtual address space instead of copying
them: the process gets a pointer it can read tensor bytes through as
if they were an in-memory array, but the backing physical pages are
populated lazily, on first touch, straight from the page cache (or
disk, on a cold cache) -- and because they are the *same* physical
pages the kernel's page cache already manages, they can be shared,
read-only, across every process that maps the same file.

## 1. Why GGUF was designed to make this possible

As covered on [model-file-formats.md](model-file-formats.md) §3, this
is not an incidental optimisation bolted onto an existing format --
GGUF's own specification (`ggml-org/ggml`'s `docs/gguf.md`, fetched
2026-09-03) states its alignment requirement exists specifically "so
that models can be loaded using `mmap` for fast loading and saving,"
and mandates every tensor's byte offset be aligned to a configurable
boundary (default 32 bytes, stored in the `general.alignment`
metadata key) precisely so a tensor's start address always lands on a
boundary the host CPU's virtual-memory hardware can map without a
realigning copy. A tensor format that packed tensors at arbitrary,
unaligned byte offsets could still technically be `mmap`'d, but the
engine would then have to copy every misaligned tensor into a
freshly-aligned buffer before use -- which is exactly the copy `mmap`
loading exists to avoid. GGUF's alignment guarantee is what lets
llama.cpp (and anything built on it) map a `.gguf` file and hand out
pointers straight into the mapped region as live tensors, with zero
intermediate copy.

## 2. llama.cpp's own load-mode surface

VERIFIED (`ggml-org/llama.cpp`'s `tools/cli/README.md`, fetched
2026-09-03): the current, consolidated flag is `--load-mode MODE`
(superseding the older, separately-toggled `--mmap`/`--no-mmap`
flags), with five documented modes:

- **`auto`** -- memory-map the file unless the platform or filesystem
  does not support it, in which case fall back to a plain read.
- **`mmap`** -- always memory-map.
- **`mlock`** -- keep the model's pages permanently resident in
  physical RAM (via the POSIX `mlock`/Windows `VirtualLock` family of
  calls), preventing the OS from paging them back out under memory
  pressure -- at the cost of pinning that much physical RAM for the
  lifetime of the process even if the OS would otherwise want to
  reclaim it for something else.
- **`mmap+mlock`** -- combine both: map the file (so unused pages need
  never be faulted in at all if a given tensor's region is never
  touched), and additionally lock whichever pages *are* touched into
  physical RAM once loaded, so they are never evicted back out under
  memory pressure.
- **`dio`** -- use DirectIO where the platform supports it, bypassing
  the OS page cache entirely for the read.

The documentation's own tradeoff note, quoted directly: "if mmap
disabled, slower load but may reduce pageouts if not using mlock" --
i.e. disabling `mmap` trades away the fast, lazy, shared-page-cache
loading path in exchange for a loading strategy that cannot be
silently paged back out to disk mid-inference the way an `mmap`'d,
not-`mlock`'d region can be under severe memory pressure.

## 3. What memory-mapping actually changes at runtime

Three concrete, engine-observable consequences follow directly from
mapping rather than copying a model file:

- **Load latency drops from "proportional to file size" to
  "proportional to first-touch working set."** A cold process opening
  a 40 GB GGUF file with `mmap` returns from the "load" call almost
  immediately -- the address space is reserved, but no page has
  actually been read from disk yet. Pages are faulted in lazily as the
  first forward pass actually touches each tensor's bytes, so the
  *perceived* load time for a first inference call is closer to "read
  the working set this one forward pass needs" than "read the whole
  file."
- **Repeated process launches against the same file are cheap after
  the first.** Because the mapped pages live in the OS page cache
  (shared, read-only, keyed by the underlying file), a second process
  -- or the same engine reloading the same model after a restart --
  reuses whatever pages are still resident from the first load instead
  of hitting disk again, as long as the OS has not evicted them under
  memory pressure. This is directly relevant to a harness that spawns
  a fresh inference-engine process per request or per session against
  the same model file: the *disk* cost of loading is paid once, not
  once per process.
- **Under memory pressure, a merely-mapped (not `mlock`'d) region can
  be silently paged back out and re-faulted in later**, which shows up
  to the caller as an unexplained latency spike mid-generation rather
  than a load-time cost -- the tradeoff `mlock`/`mmap+mlock` exists to
  eliminate, at the cost of pinning that RAM unconditionally for the
  process's lifetime.

## 4. Interaction with quantization and offloading

Memory-mapped loading composes directly with the other engine-level
concerns on this book's other pages. A `Q4_K_M`-quantized GGUF file
(see [quantization-at-inference-time.md](quantization-at-inference-time.md))
is smaller on disk and therefore has a smaller total working set to
ever fault in, compounding the latency benefit of mapping over
copying. Memory-mapping also interacts with
[cpu-gpu-heterogeneous-offloading.md](cpu-gpu-heterogeneous-offloading.md):
tensors an engine has decided to keep resident on CPU can stay mapped
directly from the file and read on demand, while tensors slated for
GPU execution still need an explicit copy across the PCIe bus into
device memory -- `mmap` only removes the *host-side* copy, not the
host-to-device transfer for whichever portion of the model is being
offloaded to an accelerator.

## 5. Why an agent-harness builder cares

A harness that treats "swap the local model" as a cheap, frequent
operation -- e.g. an agent that routes different sub-tasks to
differently-sized or differently-specialized local models, or a
development loop that restarts the inference server on every code
change -- benefits directly from `mmap`'s lazy-fault-in and
shared-page-cache behaviour: repeated loads of the same file, even
across process restarts, are far cheaper than the naive read-the-whole-
file path would suggest, as long as the host has enough free RAM to
let the OS keep those pages cached rather than evicting them. Where a
harness instead needs *predictable, jitter-free* per-token latency
(e.g. a long-running, resource-constrained production deployment where
an unexpected page-in stall mid-generation is unacceptable),
`mlock`/`mmap+mlock` is the mechanism that trades a fixed RAM
reservation for eliminating that source of runtime latency variance --
a decision to surface as a deployment-time configuration choice rather
than something a harness should leave at each engine's own default.

## Sources

- `ggml-org/llama.cpp`, `tools/cli/README.md` -- fetched 2026-09-03.
  Authoritative for the `--load-mode` flag, its five modes
  (`auto`/`mmap`/`mlock`/`mmap+mlock`/`dio`), and the quoted
  load-speed-vs-pageout tradeoff.
- `ggml-org/ggml`, GGUF file format specification --
  `github.com/ggml-org/ggml/blob/master/docs/gguf.md`. Fetched
  2026-09-03. Source of the alignment-for-mmap design rationale
  referenced in §1 and detailed on
  [model-file-formats.md](model-file-formats.md) §3.
- §1, §3, and §4's characterisation of general `mmap`/page-cache/
  `mlock` operating-system behaviour (lazy fault-in, shared read-only
  page cache across processes, eviction under memory pressure) is
  BEST CURRENT UNDERSTANDING, UNCONFIRMED against these three
  specific sources -- it is standard POSIX/Windows virtual-memory
  behaviour rather than a claim any of the three fetched documents
  states in those terms directly, and is held apart here from the
  VERIFIED llama.cpp-flag and GGUF-spec claims above.
