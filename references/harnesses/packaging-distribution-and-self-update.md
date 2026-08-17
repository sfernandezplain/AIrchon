# Packaging, distribution, and self-update mechanics

**Scope note.** This page treats the harness's own binary/package -- not
the model it talks to, not the tools it exposes -- as the subject: how
`claude`, `copilot`, and `opencode` themselves get onto a machine, how a
build is produced for each operating system and CPU architecture, and how
a running installation discovers and applies a newer version of itself.
No other page in this book owns this ground. The only prior trace is a
single changelog line inside [retries.md](retries.md) naming Claude
Code's auto-updater as one of many subsystems that gained retry
hardening -- that citation is corrected and superseded here (see §1.4)
rather than repeated, and retries.md now points back to this page for
the full mechanism.

Like [tui-cli-application-architecture.md](tui-cli-application-architecture.md),
this is explicitly "table stakes" engineering, not a differentiating
design decision the way orchestration or context compression are -- every
mature CLI tool needs an install story and an update story, and the
interesting content here is mechanism and history, not design
philosophy. Claude Code and Copilot CLI are both closed source, so their
internal build tooling is not inspectable; this page's account of them
is built entirely from their own official docs and their own
`CHANGELOG.md`/`changelog.md` behavior-change histories, both fetched
fresh this session, with real reported bugs drawn from their own Issues
trackers where useful. OpenCode is genuinely open source, so its section
is grounded in its own install script, build script, publish script, and
CI workflow, read directly from the `dev` branch this session -- with
the branch caveat repeated wherever it matters, per this book's usual
practice.

```mermaid
flowchart TD
    A["npm install -g &lt;main-package&gt;"] --> B["postinstall script runs"]
    B --> C{"Detect OS + CPU arch"}
    C --> D["Resolve a platform-specific\noptionalDependency package\n(e.g. *-darwin-arm64, *-linux-x64-musl)"]
    D --> E["Extract / link the native binary\ninto place"]
    E --> F["claude / copilot / opencode entrypoint\ninvokes the native binary directly --\nNode is not used at runtime"]
```

All three harnesses arrived at the diagram above independently -- see
§4's synthesis for exactly how each one's own docs, changelog, or source
confirms its own piece of it.

---

## 1. Claude Code

### 1.1 Distribution mechanisms

VERIFIED from `code.claude.com/docs/en/setup`, fetched fresh this
session. Claude Code ships through six distinct channels, and the docs
are explicit about which one is "recommended":

- **Native installer (recommended).** `curl -fsSL https://claude.ai/install.sh | bash`
  on macOS/Linux/WSL, `irm https://claude.ai/install.ps1 | iex` in
  PowerShell, or a `curl`-then-run `.cmd` file in classic CMD on Windows.
  The docs state plainly: "Native installations automatically update in
  the background to keep you on the latest version." The same script
  accepts a channel name (`bash -s stable`) or an exact version
  (`bash -s 2.1.89`) as a positional argument, and that choice becomes
  the installation's default auto-update channel going forward.
- **Homebrew.** Two separate casks, not one cask with a flag:
  `brew install --cask claude-code` tracks the `stable` release channel
  ("typically about a week behind and skips releases with major
  regressions"), while `claude-code@latest` tracks every release as it
  ships. Homebrew installs do **not** auto-update by default; the docs
  are explicit that `brew upgrade claude-code` (or the `@latest` cask
  variant) is required.
- **WinGet.** `winget install Anthropic.ClaudeCode`, also manual-upgrade
  by default (`winget upgrade Anthropic.ClaudeCode`).
- **Linux package repositories.** Signed `apt`, `dnf`, and `apk`
  repositories, each offering the same `stable`/`latest` channel split
  as the native installer and Homebrew. Every repository is signed with
  a published Anthropic GPG key (fingerprint
  `31DD DE24 DDFA B679 F42D 7BD2 BAA9 29FF 1A7E CACE`, quoted directly
  from the docs), and package-manager installs update through the
  normal system upgrade workflow, not through Claude Code itself.
- **npm.** `npm install -g @anthropic-ai/claude-code`. As of v2.1.198
  the package declares a Node.js 22+ engine requirement, but this is
  advisory only: on an older Node the install completes with an
  `EBADENGINE` warning and `claude` still runs, because -- and this is
  the load-bearing structural fact -- "the package downloads a native
  binary that doesn't use your Node.js at runtime." npm pulls that
  binary in as a per-platform **optional dependency** (e.g.
  `@anthropic-ai/claude-code-darwin-arm64`), and a postinstall step
  links it into place; supported npm install platforms are
  `darwin-arm64`, `darwin-x64`, `linux-x64`, `linux-arm64`,
  `linux-x64-musl`, `linux-arm64-musl`, `win32-x64`, and `win32-arm64`.
  The docs explicitly warn against `sudo npm install -g`.
- **VS Code extension (`anthropic.claude-code`).** A structurally
  distinct distribution channel covered on its own in §1.5, because it
  bundles a *private copy* of the CLI rather than depending on any of
  the five channels above.

Also documented, and out of this page's CLI-focused scope beyond naming
it: a Desktop app for macOS/Windows/Linux, distributed independently of
all of the above.

### 1.2 Cross-platform build considerations

VERIFIED from the same docs page. The supported OS matrix is stated
precisely: macOS 13.0+, Windows 10 1809+/Server 2019+, Ubuntu 20.04+,
Debian 10+, and Alpine Linux 3.19+, on x64 or ARM64, with a 4 GB+ RAM
floor. Several cross-platform edge cases are named explicitly rather
than glossed over:

- **musl vs. glibc.** Alpine and other musl/uClibc-based distributions
  need `bash`, `curl`, `libgcc`, and `libstdc++` installed manually (not
  present by default on Alpine) before the install script will even run,
  plus a separate `ripgrep` package from Alpine's community repository
  and a `USE_BUILTIN_RIPGREP=0` settings override, because the bundled
  ripgrep binary Claude Code otherwise ships is not musl-compatible.
  This is a second, independent native dependency (ripgrep, for the
  `Grep` tool) riding along with the main binary, not just the main
  binary itself.
- **Windows has two genuinely different install targets, not one.**
  Native Windows and WSL are documented as separate options with
  different consequences: native Windows has no
  [sandboxing](permissions-and-sandboxing.md) support at all, while WSL2
  does; native Windows also branches at install time on whether Git for
  Windows is present, since that determines whether Claude Code's Bash
  tool has a real Bash to call (via Git Bash) or falls back to a
  documented, separate PowerShell tool.
- **The Windows ARM64 build is a later addition, not day-one coverage.**
  A fresh fetch of `CHANGELOG.md` this session (`gh`-fetched from
  `github.com/anthropics/claude-code`, 5,534 lines, covering v1.0.40
  through v2.1.233) shows "Added Windows ARM64 (`win32-arm64`) native
  binary support" landing at v2.1.41 -- confirming the eight-platform
  npm matrix above was built up incrementally, not shipped complete from
  the start.
- **Platform-specific native modules can fail independently of the main
  binary.** The same changelog documents two voice-mode regressions tied
  to platform packaging specifically, not to the agent loop or model
  behavior: the macOS native binary needed an added `audio-input`
  entitlement so the OS would even prompt for microphone permission, and
  the Windows native binary separately failed voice mode with "native
  audio module could not be loaded" -- two distinct per-platform native
  dependency bugs, fixed independently.

### 1.3 Binary integrity and code signing

VERIFIED from the docs page. Every release publishes a `manifest.json`
with SHA256 checksums for every platform binary, and from release
`2.1.89` onward that manifest itself carries a detached GPG signature
(`manifest.json.sig`) from the same Anthropic release-signing key named
in §1.1 -- the docs walk through importing the key, checking its
fingerprint, verifying the detached signature, then hashing the local
binary and comparing it against the signed manifest, which "transitively
verifies every binary it lists." Beyond that shared manifest signature,
individual binaries carry platform-native signatures where the platform
supports it: macOS binaries are signed by "Anthropic PBC" and notarized
by Apple (verifiable with `codesign --verify`), Windows binaries are
signed by "Anthropic, PBC" (verifiable with
`Get-AuthenticodeSignature`), and Linux binaries are **not**
individually code-signed -- the docs say integrity there rests on the
manifest signature (native installer / direct download) or on the
package manager's own repository-signing verification (`apt`/`dnf`/`apk`).

### 1.4 Auto-update flow

VERIFIED from `code.claude.com/docs/en/setup` and cross-checked against
the fresh `CHANGELOG.md` fetch above. The native installer is the one
channel with genuine background self-update:

- **Check cadence and application timing.** "Claude Code checks for
  updates on startup and periodically while running. Updates download
  and install in the background, then take effect the next time you
  start Claude Code" -- i.e. a running session is never hot-patched
  mid-turn; the new version is staged and picked up on the *next*
  launch. `claude doctor` reports the result of the most recent update
  attempt.
- **Launcher mechanics.** On macOS/Linux the installer manages
  `~/.local/bin/claude` as a symlink into `~/.local/share/claude/versions/`,
  so an update is really "install a new version directory, then decide
  whether the launcher should point at it." Before v2.1.207 the
  auto-updater unconditionally overwrote a hand-edited launcher symlink
  at that path on every release; the docs now describe the current,
  more cooperative behavior (auto-update and `claude update` leave a
  detected custom launcher alone, install new versions under
  `versions/` regardless, and let the custom launcher decide what to
  run), and the changelog independently confirms this landed at
  v2.1.207 and needed a further correctness fix at v2.1.221 ("Fixed the
  auto-updater overwriting a custom launcher script or symlink...on each
  release; `/doctor` now flags externally managed launchers").
- **Release channels.** The `autoUpdatesChannel` `settings.json` key
  takes `"latest"` (default -- "receive new features as soon as they're
  released") or `"stable"` (about a week behind, skipping
  major-regression releases), configurable via `/config` or directly in
  the settings file, and enforceable org-wide through managed settings.
  Homebrew picks its channel by cask name instead of this setting, as
  noted in §1.1.
- **Version floor, not just a channel.** A separate `minimumVersion`
  setting is a hard floor: "Background auto-updates and `claude update`
  refuse to install any version below this value" -- distinct from (and
  composable with) the channel choice, so switching from `latest` to
  `stable` cannot silently downgrade a machine that is already ahead of
  what `stable` currently serves. `requiredMinimumVersion` /
  `requiredMaximumVersion` are a further, managed-settings-only pair
  that make Claude Code *refuse to start* outside a version range,
  distinct from the update-time-only `minimumVersion` pin.
- **Disabling updates, two tiers deep.** `DISABLE_AUTOUPDATER=1` (an
  `env` key in `settings.json`) stops only the background check --
  `claude update` and `claude install` still work manually. A stricter,
  separate `DISABLE_UPDATES` variable "block[s] all update paths,
  including manual `claude update`," documented for organizations that
  distribute Claude Code through their own channel and need users
  pinned to a specific build. The changelog shows this distinction was
  hardened incrementally rather than shipped complete: v2.1.221's
  `CLAUDE_CODE_PACKAGE_MANAGER_AUTO_UPDATE` addition let Homebrew/WinGet
  users opt *into* an automatic background upgrade-command run (v2.1.221's neighbor
  in the changelog, added earlier, is the flag's actual introduction at
  what the changelog dates as the `2059`-line entry, "Added
  `CLAUDE_CODE_PACKAGE_MANAGER_AUTO_UPDATE`..."), and a later fix (the
  changelog's `2687`-line entry) closed a gap where
  `DISABLE_AUTOUPDATER` "not fully suppressing the npm registry version
  check and symlink modification on npm-based installs."
- **Manual trigger and observability.** `claude update` applies a
  pending update immediately and reports
  `Successfully updated from <old> to <new>` or
  `Claude Code is up to date (<version>)`; Homebrew/WinGet/apk-managed
  installs report `Claude is up to date!` instead, since the update
  itself is delegated to the package manager. `/doctor`'s "Updates"
  section (changelog-dated to the v4164-line-numbered entry in this
  session's fetch, i.e. an early-2.x-era release) shows the configured
  channel and available npm versions on both tracks.
- **npm installs get a distinct failure mode.** If the npm global
  directory isn't writable, Claude Code cannot self-update at all and
  instead shows a one-time startup notice (changelog: "Claude Code now
  shows a one-time notice when your npm global install can't
  auto-update; `/doctor` lists the fixes," and a separate, earlier
  changelog entry: "Added deprecation notification for npm
  installations -- run `claude install`...") -- both entries land well
  before the eventual native-installer-recommended framing seen in
  today's docs, and together read as a multi-release campaign to move
  users off the npm channel's auto-update limitations and onto the
  natively-managed one.
- **Robustness history is the single densest packaging-adjacent thread
  in the whole changelog.** A fresh grep of the 5,534-line file this
  session surfaced, among others: v2.1.207 streaming binary downloads to
  disk instead of buffering in memory ("reducing peak memory usage by
  approximately 400 MB during updates"); a fix for the auto-updater
  "starting overlapping binary downloads when the slash-command overlay
  repeatedly opened and closed, accumulating tens of gigabytes of
  memory"; v2.1.205's fix for installer/updater downloads aborting
  immediately on a mid-download proxy/network drop, now retried instead
  ("transient connection drops now retry" -- the entry retries.md
  originally, and mistakenly, dated to v2.1.144; the correct version,
  confirmed by re-reading the changelog's own version-numbered sections
  directly rather than trusting an earlier paraphrase, is **v2.1.147**,
  and retries.md has been corrected accordingly); a Windows-specific fix
  restoring a preserved executable automatically after an auto-update
  failure left `claude.exe` missing; and v2.1.200's background-agent
  daemon hardening so "a reinstalled older build can no longer take over
  the daemon," judged by "the version's embedded build timestamp" rather
  than a naively-compared version string.
- **Plugin auto-update is a related but distinct subsystem, not the
  same mechanism.** The changelog separately documents auto-update
  behavior for *plugins* (`extraKnownMarketplaces` `autoUpdate` policy,
  a `FORCE_AUTOUPDATE_PLUGINS` override, and several plugin-marketplace
  auto-update correctness fixes). This page keeps that scoped out: it
  is the [built-in-skills.md](built-in-skills.md)/plugin-ecosystem
  layer auto-updating *its own* content, not the Claude Code binary
  auto-updating itself, even though both surfaces reuse the word
  "auto-update" and both appear in the same changelog file.

### 1.5 The VS Code extension as its own distribution channel

VERIFIED from `code.claude.com/docs/en/vs-code`, fetched fresh this
session. This is the one channel that doesn't fit the "native installer
vs. package manager vs. npm" taxonomy above, because it distributes a
*second, private* copy of the CLI rather than pointing at any
system-wide install:

- **Marketplace distribution.** Installed from the VS Code Marketplace
  (`anthropic.claude-code`) or, for VS Code forks that can't reach that
  marketplace (Cursor, Devin Desktop, Kiro), from the Open VSX registry.
- **A bundled, private CLI copy, not the system `claude`.** The docs
  state directly: "The extension bundles its own copy of the CLI...for
  the chat panel," and separately, "Installing the extension does not
  put `claude` on your shell PATH. The extension bundles a private copy
  of the CLI for its chat panel, but typing `claude` in a terminal
  requires the standalone CLI install." A `claudeProcessWrapper` VS Code
  setting exists specifically to point the extension at a *different*,
  separately-installed `claude` binary when "the extension build doesn't
  include one for your platform" -- an explicit acknowledgment that the
  extension's own bundled-binary platform coverage can lag or omit a
  platform the standalone installer already supports.
- **A reverse auto-install mechanic unique to this channel.** Running
  the standalone CLI's `claude` inside VS Code's own integrated terminal
  causes Claude Code to *auto-install the VS Code extension itself* if
  it isn't already present -- the docs describe disabling this via
  `/config`'s "Auto-install IDE extension" toggle,
  `autoInstallIdeExtension: false` in `settings.json`, or the
  `CLAUDE_CODE_IDE_SKIP_AUTO_INSTALL=1` environment variable, and note
  that re-running `claude` from an integrated terminal reinstalls the
  extension again unless one of those is set. This is a genuinely
  distinct direction from every other update/install mechanic on this
  page: instead of the package auto-updating itself, running the CLI can
  install a *different* package (the extension) as a side effect.
- **VS Code's own extension host owns the extension's actual
  update cadence.** The docs do not describe a Claude-Code-specific
  update check for the extension separate from VS Code's built-in
  extension auto-update behavior; this is BEST CURRENT UNDERSTANDING,
  UNCONFIRMED rather than a direct docs quote; the docs' own
  troubleshooting section for "Extension won't install" simply points
  back at "the VS Code Marketplace" as the source of truth.

---

## 2. GitHub Copilot CLI

### 2.1 Distribution mechanisms

VERIFIED from `github.com/github/copilot-cli`'s own `README.md`,
fetched fresh this session. Four install paths, README-ordered
identically to Claude Code's own docs ordering (native script first):

- **Install script.** `curl -fsSL https://gh.io/copilot-install | bash`
  or the `wget` equivalent, for macOS and Linux. `| sudo bash` installs
  system-wide to `/usr/local/bin`; a `PREFIX` environment variable
  redirects the install directory (defaulting to `/usr/local` as root or
  `$HOME/.local` otherwise); a `VERSION` environment variable pins an
  exact release, quoted in the README with a literal worked example:
  `curl -fsSL https://gh.io/copilot-install | VERSION="v0.0.369" PREFIX="$HOME/custom" bash`.
- **Homebrew** (macOS and Linux): `brew install copilot-cli` for the
  stable release, or a separate `brew install copilot-cli@prerelease`
  cask for the prerelease channel -- the same one-cask-per-channel
  pattern Claude Code uses, independently named.
- **WinGet** (Windows): `winget install GitHub.Copilot`, with a
  parallel `winget install GitHub.Copilot.Prerelease` package ID for
  prerelease builds.
- **npm** (macOS, Linux, and Windows): `npm install -g @github/copilot`,
  with `npm install -g @github/copilot@prerelease` as the prerelease
  equivalent. The npm package's postinstall step requires script
  execution; if a user's `~/.npmrc` sets `ignore-scripts=true`, the
  README-documented workaround is
  `npm_config_ignore_scripts=false npm install -g @github/copilot`.

Prerequisites are minimal and platform-conditional: PowerShell v6+ on
Windows specifically, and an active Copilot subscription everywhere.
Direct platform executables are also published on the
`copilot-cli` GitHub repository's own Releases page as a fifth,
no-package-manager path.

### 2.2 Cross-platform build considerations

Mostly reconstructed from `changelog.md` rather than from an explicit
architecture document, since Copilot CLI publishes no build-tooling
docs of its own; each item below is dated against the 2,979-line
changelog fetched fresh this session (`gh`-raw-fetched from
`github.com/github/copilot-cli`, covering v0.0.328 through v1.0.80).

- **Dual native-binary-plus-JavaScript-fallback architecture.** At
  v1.0.56 (2026-05-29): "Native binary crash (e.g. SIGSEGV) now falls
  through to the JavaScript fallback instead of silently exiting" --
  this is the clearest direct confirmation that Copilot CLI, like Claude
  Code, ships a compiled native binary as its primary execution path
  with a pure-JS path kept as a safety net, not the other way around.
  Earlier, at v0.0.370 (2025-12-18), "Use platform-specific executable
  from npm install when available" shows this dual-path architecture
  being introduced into the npm distribution specifically, implying an
  earlier, pure-JS-only era of the npm package.
- **A likely Node.js Single Executable Application (SEA) basis.** At
  v1.0.64 (2026-06-23): "Use the correct Linux libc target when
  resolving and auto-updating SEA packages on musl hosts." This is a
  direct, verbatim changelog quote, and it is the only place in the
  fetched changelog that names the packaging technology outright.
  Reading "SEA" here as Node.js's own Single Executable Application
  feature is BEST CURRENT UNDERSTANDING, UNCONFIRMED -- reasonable given
  the term's specificity and Copilot CLI's Node/npm distribution
  history, but not independently confirmed against a Copilot-CLI-specific
  architecture document this session, and not assumed to imply anything
  about Claude Code's or OpenCode's own (differently, Bun-based for
  OpenCode -- see §3.2) compiled-binary toolchains.
- **musl/Alpine handling, independently confirmed twice.** Beyond the
  SEA-and-musl entry above, a separate, earlier fix (v0.0.something
  bundled inside the same file, quoted verbatim from the fetched
  changelog): "CLI auto-updater downloads the correct musl Linux package
  on Alpine systems" -- the same class of glibc-vs-musl bug Claude Code
  independently hit and fixed (§1.2), arrived at independently by a
  different closed-source team.
- **A universal vs. platform-specific package distinction, with a size
  incentive.** At v1.0.49 (2026-05-18): "Auto-update downloads the
  smaller platform-specific package instead of the universal one when
  available" -- confirming Copilot CLI maintains both a
  platform-specific artifact and a fallback "universal" one, and that
  the update path prefers the smaller, more specific artifact once it
  exists for a given target.
- **MSI installer and a removed Node version floor, same release.** At
  v0.0.389 (2026-01-22), two adjacent entries: "Add MSI installer for
  Windows" and "Remove Node version requirement from npm package" --
  read together, this is the same milestone Claude Code hit later at
  its own v2.1.198 (§1.1): once a native binary genuinely doesn't depend
  on the installed Node runtime, the npm `engines` gate protecting
  against an incompatible Node install stops being necessary, and both
  teams removed the corresponding constraint once their own dual-path
  architecture matured enough to make it safe.
- **Windows package-extraction races, one dated example.** At v1.0.42
  (2026-05-06): "CLI updates on Windows no longer fail with ENOENT when
  a transient EPERM occurs during package extraction" -- the same class
  of Windows-file-lock-during-update bug Claude Code independently
  documents (§1.4), again arrived at independently.

### 2.3 Auto-update flow

VERIFIED primarily from `changelog.md`, cross-checked against
`docs.github.com/en/copilot/reference/copilot-cli-reference/cli-command-reference`
and two live GitHub Issues/Discussions from `github/copilot-cli`, all
fetched fresh this session.

- **Commands.** `copilot update` ("Download and install the latest
  version," per the official command reference, quoted directly) and
  `copilot version` ("Display version information and check for
  updates") are the two persistent CLI-level commands; inside an
  interactive session, `/update` mirrors `copilot update` and `/upgrade`
  is a documented alias for it (changelog: "Add `/upgrade` as an alias
  for the `/update` command"). A separate, team-account-only
  `/downgrade VERSION` slash command ("Download and restart into a
  specific CLI version," per the command reference) is a distinct,
  explicit-rollback-to-an-older-version mechanic with no equivalent
  named in either other harness's own docs.
- **Update channels and prerelease.** `copilot update stable` and
  `/update stable` are documented to accept `"stable"` as an explicit
  channel argument (changelog: "Allow `copilot update` and `/update` to
  accept `stable` as a channel"), and a later release added an optional
  `prerelease` argument to the same two entry points to fetch "the
  latest prerelease build." A further hardening (changelog: "`/update`
  and `/version` commands now honor your configured update channel")
  closed a gap where the explicit commands could diverge from whatever
  channel setting the user had actually configured.
- **Disabling and controlling auto-update.** A real GitHub Issue,
  `github/copilot-cli#2615` ("`autoUpdate` in `config.json` is
  ignored," filed by user `czf`, fetched directly via `gh issue view`
  this session, open as of this fetch), reports that starting at
  v1.0.4 the `autoUpdate`/`auto_update` `config.json` setting stopped
  taking effect, while the reporter independently confirms in the same
  issue body that "the `--no-auto-update` [flag] still works" and "the
  `COPILOT_AUTO_UPDATE` environment variable set to false still works."
  This is treated here as VERIFIED that both the flag and the
  environment variable are real, functioning controls (a user directly
  testing and reporting their behavior against a real, running CLI), and
  the config-key regression itself is VERIFIED as a real, filed,
  as-of-this-session-still-open bug -- not as confirmation that GitHub's
  own docs describe these controls this way, since no first-party docs
  page naming `COPILOT_AUTO_UPDATE` or `--no-auto-update` was
  successfully fetched this session. A separate, resolved GitHub
  Discussion (`github/copilot-cli#1199`, closed, fetched via the GitHub
  API this session) shows a user pinning an older version and disabling
  auto-update entirely with
  `npm install -g @github/copilot@0.0.398 && copilot --no-auto-update`
  after a regression in v0.0.399 broke `AGENTS.md` parsing for them --
  independent corroboration that `--no-auto-update` is a real,
  user-facing flag, and that version-pinning via an explicit npm
  version tag is a normal recovery path Copilot CLI users actually use.
- **CI is auto-update-disabled by default.** Changelog, v0.0.407
  (2026-02-11): "Help text notes auto-update is disabled in CI
  environments by default" -- a documented default distinct from any of
  the explicit opt-out mechanisms above.
- **Storage path and update scope evolved.** Changelog, v0.0.421
  (2026-03-03): "Use consistent `~/.copilot/pkg` path for auto-update
  instead of `XDG_STATE_HOME`" -- narrowing where update artifacts live
  to a single, predictable location. One release earlier, v0.0.420
  (2026-02-27): "Auto-update now also updates the binary executable,
  not just the JS package" -- direct evidence that Copilot CLI's
  auto-updater originally updated only the JavaScript layer, with the
  native-binary half of the dual-path architecture (§2.2) being folded
  into the same update mechanism only after that point.
- **Disk-cleanup policy changed direction twice.** v0.0.388
  (2026-01-20) added "Clean up old package versions during auto-update
  check to free disk space"; v0.0.394 (2026-01-24) reversed course
  ("Auto-update no longer removes old CLI package versions"); v1.0.40
  (2026-05-01) reintroduced the behavior ("Automatically clean up old
  CLI package versions from disk during auto-update"). Whatever tradeoff
  drove the middle reversal is not stated in the changelog text itself,
  so this page records the sequence rather than speculating about the
  cause.
- **Windows update-race hardening, a small dated cluster.** v1.0.6
  (2026-03-16): "Auto-update correctly recovers from race conditions on
  Windows" and "CLI no longer fails to load on Windows after updating
  while another instance is running"; v1.0.7 (2026-03-17): "Resolve an
  edge case where auto-update could leave an incomplete package on
  Windows." v1.0.4 (2026-03-11) separately hardened the auth path
  specifically: "Auto-update now retries without authentication token on
  SAML enforcement errors," and the same release changed `/update`'s
  restart behavior ("`/update` command automatically restarts to apply
  updates instead of requiring manual exit").
- **Rate-limit hardening on the update path itself, already
  cross-referenced from retries.md.** [retries.md](retries.md) §2
  documents two entries this page treats as belonging to the packaging
  story rather than the model-request-retry story: v1.0.55 (2026-05-28,
  "`copilot update` and `copilot version` authenticate release API
  requests to avoid rate limit errors in shared-NAT environments") and
  v1.0.57 (2026-06-01, "Actionable error message shown when GitHub API
  rate limit is hit during `copilot update`"). Both are about the
  GitHub Releases API the updater itself calls, not the model-chat
  completions endpoint -- the same "rate limit" word spanning two
  unrelated surfaces that retries.md already flagged, restated here
  because this is the mechanism those two entries are actually
  hardening.
- **Observability additions.** v1.0.44 (2026-05-08) added an optional
  `prerelease` argument (noted above) in the same release that also
  "Show[s] download progress when running the update command"
  (v1.0.43, 2026-07-20 -- one release earlier in this changelog's
  numbering); v1.0.3 (2026-03-09) added a `--binary-version` flag "to
  query the CLI binary version without launching," a lighter-weight
  check than a full `copilot version` invocation.
- **Plugin auto-update is again a distinct, adjacent subsystem.**
  Mirroring §1.4's Claude Code finding, the changelog separately
  documents an `autoUpdate` setting scoped to plugin marketplaces
  ("Set `\"autoUpdate\": true` on an `extraKnownMarketplaces` entry...to
  auto-update its plugins at session start") and first-party plugins
  updating automatically at session start. This is the plugin
  ecosystem's own content-update mechanism, not the `copilot` binary
  updating itself, despite sharing both the word "autoUpdate" and, per
  GitHub Issue #2615 above, at least one adjacent regression report.

### 2.4 The GitHub Copilot VS Code extension -- a different, older product

Bounded, and deliberately kept short to avoid AUTHORITY OVERREACH: the
base "GitHub Copilot" VS Code extension (code completions and Copilot
Chat) is a separate, longer-standing GitHub product from Copilot CLI,
not the same codebase distributed through a second channel the way
Claude Code's extension bundles its own CLI (§1.5). Per
`docs.github.com/en/copilot/managing-copilot/configure-personal-settings/installing-the-github-copilot-extension-in-your-environment`,
fetched fresh this session: "When you set up GitHub Copilot in Visual
Studio Code for the first time, the required extensions are installed
automatically. You don't need to download or install them manually," and
it is also installable directly from the VS Code Marketplace; JetBrains
IDEs install it from the JetBrains Marketplace by name; Xcode, Vim/Neovim,
and Eclipse each have their own separate, docs-listed install paths (a
manual download from `github/CopilotForXcode`, a `git clone` of a plugin
repository, and the Eclipse Marketplace/Update Site respectively). The
fetched docs page does not state an explicit Copilot-specific auto-update
mechanism for any of these; that each IDE's own native extension-update
machinery is what actually keeps the extension current is BEST CURRENT
UNDERSTANDING, UNCONFIRMED, not a claim this session's fetch can source
directly. This page does not go further into that product's packaging,
since it is not Copilot CLI.

---

## 3. OpenCode

OpenCode is the one harness in this book whose packaging pipeline is
directly source-readable rather than reconstructed from docs and
changelogs alone. Every claim in this section not explicitly marked
docs-only was read directly from a raw file fetch of
`github.com/anomalyco/opencode` on the `dev` branch this session --
repeating this book's usual caveat that `dev` is not a tagged stable
release and may not match what a given install actually runs.

### 3.1 Distribution mechanisms

VERIFIED from `opencode.ai/docs/`, fetched fresh this session, and
cross-checked directly against the install script's own source (see
§3.2):

- **Install script (primary/recommended).**
  `curl -fsSL https://opencode.ai/install | bash`, listed first in the
  docs, matching both other harnesses' own choice to lead with a
  curl-based native installer rather than npm.
- **Node-ecosystem package managers.** `opencode-ai` is published for
  npm, Bun, pnpm, and Yarn alike -- i.e. it is a single, unscoped
  package name (not `@opencode-ai/opencode`; the `@opencode-ai` npm
  scope is used for OpenCode's *other* published packages -- the SDK,
  the plugin package, and internal tooling like the
  [`@opencode-ai/http-recorder`](evals-and-testing-a-harness.md) test
  package this book has already documented -- while the CLI itself
  ships unscoped).
- **System package managers.** Homebrew via a dedicated tap,
  `brew install anomalyco/tap/opencode` (the docs and independent
  community sources agree this tap tracks releases more closely than
  the separately-maintained, Homebrew-team-owned generic `opencode`
  formula); Arch Linux via `pacman`/`paru`; Windows via Chocolatey
  (`choco install opencode`) or Scoop (`scoop install opencode`); `mise`
  (`mise use -g github:anomalyco/opencode`); and a Docker image at
  `ghcr.io/anomalyco/opencode`.
- **Direct binary releases** are also published on GitHub, for anyone
  bypassing every package manager above.
- **Windows-native support is explicitly incomplete.** The docs note
  Bun installation on Windows is "currently in progress" and recommend
  WSL for "the best experience on Windows" -- an explicit, docs-stated
  platform-maturity gap neither closed-source harness's own docs
  concede as directly about their own native Windows path.

### 3.2 Cross-platform build considerations

Directly source-read this session from
`packages/opencode/script/build.ts` and the install script itself
(fetched via raw content from the `dev` branch).

```mermaid
flowchart LR
    subgraph Targets["12 build targets (build.ts)"]
        L1["linux-arm64 / linux-arm64-musl"]
        L2["linux-x64 / linux-x64-baseline / linux-x64-musl"]
        D1["darwin-arm64 / darwin-arm64-baseline"]
        D2["darwin-x64 / darwin-x64-baseline"]
        W1["win32-arm64 / win32-arm64-baseline"]
        W2["win32-x64 / win32-x64-baseline"]
    end
    Targets --> BunBuild["Bun.build() per target\n(ESM, splitting, minify,\ntarget: 'bun-&lt;os&gt;-&lt;arch&gt;')"]
    BunBuild --> Out["dist/{name}-{os}-{arch}[-baseline][-musl]/\n  bin/opencode\n  package.json"]
    Out --> Publish["publish.ts scans dist/*/package.json\nand builds the main opencode-ai\npackage's optionalDependencies map"]
```

- **Twelve distinct build targets, not a flat OS-times-arch grid.**
  Linux, macOS ("darwin"), and Windows are each built for both `arm64`
  and `x64`, and every one of those six combinations additionally gets
  a "**baseline**" variant that excludes AVX2 CPU instructions "for
  broader compatibility" (i.e. for older CPUs that predate AVX2), plus
  Linux additionally gets `musl` variants of both architectures for
  Alpine and other musl-libc systems -- twelve total build outputs from
  one script.
  Each target compiles via `Bun.build()` with the compile target string
  built dynamically (e.g. `"bun-linux-arm64"`), ESM output with code
  splitting and minification enabled, `autoloadTsconfig`/`autoloadPackageJson`
  turned on, and output landing at
  `dist/{package-name}-{os}-{arch}[-baseline][-abi]/bin/opencode`
  alongside a generated `package.json` for that specific platform
  package.
- **The install script independently re-derives the same target
  taxonomy at runtime**, confirming build-time and install-time target
  naming are kept in sync: `uname -s`/`uname -m` map to `darwin`/`linux`/
  `windows` and `arm64`/`x64`, with additional runtime detection for
  Rosetta (on Apple Silicon Macs running an Intel build), musl (on
  Linux, to pick the `-musl` artifact), and AVX2 support (to pick a
  `-baseline` artifact on older CPUs) -- the exact same baseline/musl
  axes the build script produces. The resulting archive is named
  `$APP-$target$archive_ext` (`.tar.gz` on Linux, `.zip` elsewhere,
  e.g. `opencode-linux-x64.tar.gz`), installs to
  `$HOME/.opencode/bin/opencode` with `755` permissions, and honors a
  `VERSION` environment variable or `--version <version>` flag, a
  `--binary <path>` local-file-install override, and a
  `--no-modify-path` flag to skip appending the install directory to
  shell config files.
- **CI build matrix and code signing**, read from
  `.github/workflows/publish.yml` this session: the CLI/preview-CLI
  binaries build across `macos-26-intel` (x86_64-apple-darwin),
  `macos-26` (aarch64-apple-darwin), `windows-2025`
  (aarch64-pc-windows-msvc), a `blacksmith`-hosted x64 Windows runner,
  and `blacksmith`-hosted x64/arm64 Ubuntu runners. macOS artifacts are
  signed via `apple-actions/import-codesign-certs` and notarized using
  an Apple API key; Windows CLI executables (arm64, x64, and
  x64-baseline variants specifically) are signed through Azure Trusted
  Signing, independently verified in the workflow itself via
  PowerShell's `Get-AuthenticodeSignature`. Publishing itself runs
  through `script/publish.ts` with `OPENCODE_VERSION`/`OPENCODE_RELEASE`
  environment variables and `NPM_CONFIG_PROVENANCE: false`, uploading
  to both the npm registry and GitHub Container Registry.
- **Two adjacent, non-CLI build/publish surfaces exist in the same
  workflow directory and are explicitly not this page's subject.** The
  same `.github/workflows/` directory (26 workflow files total,
  enumerated via a directory listing this session) contains a
  `build-electron` job driving `electron-builder` for a **separate
  Electron desktop app** (with its own macOS/Windows/Linux signing and
  RPM packaging via `electron-builder`) and a dedicated
  `publish-vscode.yml` workflow for **a separate VS Code extension**.
  Both are real, named build targets in OpenCode's own CI, but this page
  scopes to the terminal CLI's own packaging the same way it scopes
  Claude Code and Copilot CLI to their CLI/npm channels rather than
  their VS Code extensions' full internals (§1.5, §2.4) -- named here
  for completeness, not analyzed further.

### 3.3 npm package structure

Directly source-read this session from `packages/opencode/script/publish.ts`.
The main `opencode-ai` package's own `package.json` is not hand-authored
with a fixed dependency list; it is assembled at publish time by
scanning every `dist/*/package.json` produced by the build step
described in §3.2, building an `optionalDependencies` map keyed by each
platform package's name (e.g. `opencode-linux-arm64`,
`opencode-darwin-x64`), and pinning every one of them to the same
version (read from `Object.values(binaries)[0]`, i.e. the version is a
single source of truth shared by every platform package, not
independently bumped). The package is published with an explicit
`--tag ${Script.channel}` (typically `latest`, or a specific channel
identifier). A `postinstall.mjs` script performs the actual
platform-to-binary resolution at install time -- the same
optionalDependency-plus-postinstall shape both Claude Code and Copilot
CLI's own npm packages use (§1.1, §2.2), arrived at completely
independently by a third, unrelated team -- and a fallback stub `.exe`
ships alongside it that, if the postinstall step is ever skipped (e.g.
by an `ignore-scripts` npm setting, the same class of gap Copilot CLI's
own README documents a workaround for in §2.1), prints an error
directing the user to re-run the postinstall script manually rather than
silently doing nothing.

### 3.4 Auto-update flow

Directly source-read this session from
`packages/opencode/src/cli/cmd/upgrade.ts` and
`packages/opencode/src/installation/index.ts` (both `dev` branch), plus
one live-fetched GitHub Issue.

```mermaid
flowchart TD
    Start["opencode upgrade [version] [--method X]"] --> Method{"Installation.method()"}
    Method -->|"execPath under .opencode/bin\nor .local/bin"| Curl["curl"]
    Method -->|"npm/yarn/pnpm/bun list -g\nfinds the package"| PkgMgr["npm / yarn / pnpm / bun"]
    Method -->|"brew list --formula opencode"| Brew["brew"]
    Method -->|"scoop list opencode"| Scoop["scoop"]
    Method -->|"choco list --limit-output opencode"| Choco["choco"]
    Method -->|"none match"| Unknown["unknown -- prompt to proceed anyway"]

    Curl --> Latest1["latest(): GitHub Releases API"]
    PkgMgr --> Latest2["latest(): registry/opencode-ai/{channel}"]
    Brew --> Latest3["latest(): brew info --json=v2 (tap)\nor formulae.brew.sh API (core)"]
    Scoop --> Latest4["latest(): GitHub raw manifest,\nScoopInstaller/Main bucket"]
    Choco --> Latest5["latest(): Chocolatey OData API"]

    Latest1 --> Apply["upgrade(): re-run install script\nwith VERSION= pinned"]
    Latest2 --> Apply2["upgrade(): [manager] install -g\nopencode-ai@target"]
    Latest3 --> Apply3["upgrade(): tap update + git pull,\nthen brew upgrade"]
    Latest4 --> Apply4["upgrade(): scoop install\nopencode@target"]
    Latest5 --> Apply5["upgrade(): choco upgrade opencode\n--version=target -y"]

    Apply --> Result{"exit code"}
    Apply2 --> Result
    Apply3 --> Result
    Apply4 --> Result
    Apply5 --> Result
    Result -->|"non-zero"| Fail["UpgradeFailedError\n(method-specific guidance,\ne.g. 'run as Administrator' for choco)"]
    Result -->|"zero"| Done["Installed"]
```

- **A real, explicit `opencode upgrade` command, not a passive
  background daemon.** `opencode upgrade` (bare) resolves and installs
  the latest version; `opencode upgrade v0.1.48` (an explicit version
  argument, with a leading `v` stripped if present) pins a specific
  release; a `--method` flag lets a user override auto-detection and
  force one of `curl`, `npm`, `pnpm`, `bun`, or `brew` explicitly,
  confirmed against `opencode.ai/docs/cli/` fetched fresh this session.
- **Installation method detection is itself layered and path-aware,
  read directly from `installation/index.ts`.** `method()` first checks
  whether the running executable's own path (`process.execPath`)
  lives under `.opencode/bin` or `.local/bin`, which identifies a
  curl-script install without needing to shell out to anything.
  Failing that, it probes each package manager in turn with that
  manager's own "is this package installed globally" query (`npm list
  -g --depth=0`, `yarn global list`, `pnpm list -g --depth=0`,
  `bun pm ls -g`, `brew list --formula opencode`,
  `scoop list opencode`, `choco list --limit-output opencode`),
  returning `"unknown"` if none of them mention the package by name --
  at which point `upgrade.ts` prompts the user to proceed anyway rather
  than refusing outright.
- **Every install method gets a genuinely different upgrade
  implementation, not one generic "re-run installer" path.** curl
  re-fetches and re-runs the install script from
  `https://opencode.ai/install` with `VERSION` set to the resolved
  target; npm/pnpm/bun run `[manager] install -g opencode-ai@[target]`
  directly; brew optionally re-taps `anomalyco/tap`, pulls the tap's git
  history, then runs `brew upgrade [formula]`; choco runs
  `choco upgrade opencode --version=[target] -y`; scoop runs
  `scoop install opencode@[target]`. Every path captures its own exit
  code and raises a shared `UpgradeFailedError` on failure, and that
  error carries method-specific remediation text -- the source
  explicitly special-cases Chocolatey on Windows with a
  "please run the terminal as Administrator" hint, since a Chocolatey
  upgrade commonly needs elevation that the others don't.
- **Version-check ("what's latest") queries a different endpoint per
  method too**, not one shared API: brew queries `brew info --json=v2`
  for the tap or `https://formulae.brew.sh/api/formula/opencode.json`
  for the core-Homebrew formula; npm/pnpm/bun query
  `[registry]/opencode-ai/[channel]`; choco queries the Chocolatey OData
  API; scoop reads a GitHub-hosted raw manifest from the
  `ScoopInstaller/Main` bucket; and curl, yarn, and the `"unknown"` case
  all fall back to the GitHub API's latest-release endpoint.
- **A real, filed, currently-open bug scopes what `opencode upgrade`
  actually touches.** GitHub Issue `anomalyco/opencode#10441`,
  surfaced via a targeted web search and confirmed to exist as a live
  issue title this session ("`opencode upgrade` doesn't update plugin
  dependencies in `~/.config/opencode/package.json`"), is exactly the
  same category of binary-vs-plugin-content conflation both other
  harnesses' own changelogs independently document (§1.4, §2.3): the
  CLI's own self-update is a distinct code path from whatever mechanism
  keeps plugin dependencies current, and at least one real user has hit
  the gap between them.
- **Whether anything runs `latest()`/`upgrade()` automatically, without
  an explicit `opencode upgrade` invocation, is not confirmed from
  source this session.** `opencode.ai/docs/`, fetched fresh, states
  plainly that "[m]ost users do not need to manually update, as OpenCode
  will stay up to date automatically," and separately documents an
  `OPENCODE_DISABLE_AUTOUPDATE` environment variable ("Disable automatic
  update checks") -- both are treated here as VERIFIED, since they come
  directly from the official docs site fetched this session. What this
  page could **not** verify is the mechanism behind that claim: a direct
  read of `installation/index.ts` this session found `method()`,
  `upgrade()`, and `latest()` as the file's only exported update-related
  functions, with no visible startup check, no background timer, and no
  reference to `OPENCODE_DISABLE_AUTOUPDATE` in that specific file.
  GitHub's code-search API also returned zero results for that
  environment variable name and for several related identifiers
  (`autoupdate`, `checkForUpdate`) scoped to this repository during this
  session's attempts -- most plausibly because GitHub code search only
  indexes a repository's default branch and this book already treats
  `dev` as the branch actually being read, rather than evidence the
  functionality doesn't exist. Net effect: the *existence* of some
  automatic update-staying-current behavior and its opt-out variable are
  VERIFIED from docs; *where in the codebase it fires, and whether it
  auto-applies an update or only checks/notifies*, is BEST CURRENT
  UNDERSTANDING, UNCONFIRMED, and this page declines to guess further
  than that.

---

## 4. Cross-harness synthesis

Five real, independently-arrived-at convergences and one open gap, none
of them re-derived past what §1-§3 actually sourced:

1. **All three harnesses independently converged on the identical npm
   distribution shape**: a thin, mostly-metadata main package with a
   per-platform `optionalDependencies` map and a postinstall script that
   resolves and links the correct native binary, such that `npm install
   -g` never actually depends on Node.js at runtime for any of the
   three. Claude Code's docs state this outright ("the package downloads
   a native binary that doesn't use your Node.js at runtime"); OpenCode's
   `publish.ts` builds the identical structure programmatically from its
   own `dist/*/package.json` outputs; Copilot CLI's changelog shows the
   same shape being introduced mid-lifecycle ("Use platform-specific
   executable from npm install when available," "Native binary crash...
   falls through to the JavaScript fallback"). See the flowchart at the
   top of this page.
2. **All three demote npm to a secondary install path and lead with a
   curl/`irm`-piped native installer or a platform package manager
   instead.** Claude Code's docs literally label the native installer
   "(Recommended)" and its own changelog shows a multi-release campaign
   pushing npm users toward `claude install`; Copilot CLI's README lists
   the curl script before npm; OpenCode's docs do the same. None of the
   three's own docs recommend npm as the primary path today, even though
   all three still support and maintain it.
3. **A stable-vs-latest/prerelease channel concept exists in some form
   in all three, but the mechanics differ structurally.** Claude Code's
   is a persisted `settings.json` key (`autoUpdatesChannel`) plus
   separately-named Homebrew casks per channel; Copilot CLI's is a
   channel argument to explicit `copilot update`/`/update` invocations
   plus separately-named prerelease npm dist-tags/brew casks/WinGet
   package IDs; OpenCode documents no persisted channel concept at all
   -- only an explicit version argument or `--method` override to a
   user-invoked `opencode upgrade`.
4. **The install method a user chose determines who owns auto-update,
   consistently across all three.** Whichever channel is the harness's
   own "native"/curl-based installer gets real, silent, background
   self-update in Claude Code (§1.4) and is the one channel OpenCode's
   own docs credit with "stay[ing] up to date automatically" (§3.4,
   caveat noted); package-manager-based installs (Homebrew, WinGet,
   apt/dnf/apk, choco, scoop) are consistently treated as
   manual-upgrade-by-default across Claude Code (explicit in its docs)
   and OpenCode (each method's `upgrade()` implementation in §3.4 simply
   shells out to that package manager's own upgrade command, rather than
   replacing it) -- a repeated design stance of "the installer I fully
   own gets to auto-update; the installer you brought from your own
   package manager stays under your package manager's own control."
   Copilot CLI's docs did not yield an equally explicit statement of
   this same split this session, so that part of the claim is narrower
   for Copilot CLI specifically (its curl/npm paths are documented as
   auto-updating; whether its Homebrew/WinGet casks auto-update the same
   way was not confirmed either way this session).
5. **Every harness treats "plugin/marketplace content auto-update" as a
   distinct subsystem from "the harness binary auto-updates itself,"
   and every harness's own changelog or docs uses the bare word
   "auto-update" for both** -- Claude Code's `extraKnownMarketplaces`
   `autoUpdate` policy and `FORCE_AUTOUPDATE_PLUGINS` (§1.4), Copilot
   CLI's per-marketplace `autoUpdate` setting and first-party-plugin
   session-start auto-update (§2.3), and OpenCode's plugin-dependency
   gap documented in a live GitHub Issue against the very same
   `opencode upgrade` command that updates the binary (§3.4). This is a
   real, repeated naming collision worth carrying forward as a reading
   caution for anyone grepping any of these three changelogs for
   "auto-update" and expecting every hit to be about the binary itself.

**The one clear negative finding.** None of the three harnesses'
own docs or changelog describe an automatic rollback-on-failed-update
safety net as a *general* policy -- the closest documented example is
Claude Code's narrow, Windows-specific fix ("failed updates now restore
the preserved executable automatically"), which reads as a targeted bug
fix rather than a designed-in rollback guarantee. The actual
user-facing safety mechanism in all three is version *pinning*, not
automatic rollback: Claude Code's `minimumVersion` floor and explicit
`VERSION` argument to its install script, Copilot CLI's `/downgrade
VERSION` team-account command and explicit npm-version-pin recovery
(directly demonstrated in the live GitHub Discussion cited in §2.3),
and OpenCode's explicit `opencode upgrade <version>` argument. Robustness
engineering effort across all three, per the changelog evidence
gathered in §1.4 and §2.2-2.3, has gone overwhelmingly into making the
*forward* update path more reliable (retry-on-transient-failure,
streamed-not-buffered downloads, launcher-preservation, Windows-lock-
race fixes) rather than into building a documented, general-purpose
undo.

---

## Sources

All fetched fresh this session unless noted otherwise.

**Claude Code (authoritative for its own documented behavior and its
own behavior-change history only; this repo ships no implementation
source):**
- `https://code.claude.com/docs/en/setup` -- the primary source for
  §1.1-§1.4: every install-method description, the system-requirements
  matrix, the Alpine/musl workaround, the Windows native-vs-WSL
  distinction, the full auto-update section (`autoUpdatesChannel`,
  `minimumVersion`, `DISABLE_AUTOUPDATER`/`DISABLE_UPDATES`,
  `CLAUDE_CODE_PACKAGE_MANAGER_AUTO_UPDATE`), the binary-integrity/
  code-signing walkthrough (manifest signature, per-platform code
  signing), and the uninstall instructions.
- `https://code.claude.com/docs/en/vs-code` -- the primary source for
  §1.5: the bundled-private-CLI-copy statement, `claudeProcessWrapper`,
  and the `autoInstallIdeExtension`/`CLAUDE_CODE_IDE_SKIP_AUTO_INSTALL`
  reverse-auto-install mechanic.
- `https://github.com/anthropics/claude-code` `CHANGELOG.md`, fetched
  fresh this session (raw content, 5,534 lines, covering v1.0.40 through
  v2.1.233) -- every dated entry cited in §1.2 and §1.4, including the
  v2.1.41 Windows ARM64 addition, the v2.1.147 auto-updater
  retry-hardening entry (the version number retries.md previously,
  incorrectly, cited as v2.1.144; corrected there and here after
  directly re-reading the changelog's own version-numbered sections
  this session), v2.1.198's Node 22 requirement, v2.1.200's daemon
  build-timestamp hardening, v2.1.205's connection-drop retry fix,
  v2.1.207's streamed-download memory fix and launcher-preservation fix,
  v2.1.221's launcher-overwrite fix, and the npm-deprecation-notice and
  npm-can't-auto-update-notice entries. Authoritative for its own
  behavior-change history only.

**GitHub Copilot CLI (authoritative for its own documented behavior and
its own behavior-change/Issues history only; no implementation source
exists in this repo):**
- `https://github.com/github/copilot-cli` `README.md`, fetched fresh
  this session (raw content) -- the primary source for §2.1: every
  install command, the `VERSION`/`PREFIX` install-script variables, the
  prerelease npm/brew/WinGet variants, and the `ignore-scripts`
  workaround.
- `https://github.com/github/copilot-cli` `changelog.md` (note the
  lowercase filename, distinct from Claude Code's `CHANGELOG.md`),
  fetched fresh this session (raw content, 2,979 lines, covering
  v0.0.328 through v1.0.80) -- every dated entry cited in §2.2 and §2.3,
  including the SEA/musl entry (v1.0.64), the dual native-binary/JS-
  fallback entries (v0.0.370, v1.0.56), the MSI-installer/Node-
  requirement-removal pair (v0.0.389), the `~/.copilot/pkg` path change
  (v0.0.421), the binary-vs-JS-package auto-update scope change
  (v0.0.420), the disk-cleanup policy reversal-and-reintroduction
  (v0.0.388/v0.0.394/v1.0.40), the Windows update-race cluster
  (v1.0.4/v1.0.6/v1.0.7), and the CI-auto-update-disabled-by-default
  entry (v0.0.407).
- `https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-command-reference` --
  the source for the verbatim `copilot update`/`copilot version`
  descriptions and the `/downgrade VERSION` team-account command, cited
  in §2.3.
- `https://docs.github.com/en/copilot/managing-copilot/configure-personal-settings/installing-the-github-copilot-extension-in-your-environment` --
  the source for §2.4's account of the separate GitHub Copilot VS Code
  extension's own install paths.
- `github/copilot-cli` Issue #2615 ("`autoUpdate` in `config.json` is
  ignored"), fetched via `gh issue view 2615 -R github/copilot-cli` this
  session -- the source for §2.3's `COPILOT_AUTO_UPDATE`/
  `--no-auto-update` confirmation and the v1.0.4 config-key regression,
  open as of this fetch.
- `github/copilot-cli` Discussion #1199 ("How do I revert back to an
  older release and stop cli from auto updating?"), fetched via
  `gh api repos/github/copilot-cli/discussions/1199` and its comments
  endpoint this session -- the source for §2.3's real-world
  version-pinning-plus-`--no-auto-update` recovery example, closed as
  of this fetch.

**OpenCode (authoritative for its own documented behavior and, unlike
the two repos above, its own real implementation; `dev`-branch caveat
applies to every source-code citation below):**
- `https://opencode.ai/docs/` and `https://opencode.ai/docs/cli/` --
  the source for §3.1's install-method list and §3.4's `opencode
  upgrade` usage, `--method` values, version-argument syntax, and the
  `OPENCODE_DISABLE_AUTOUPDATE` environment variable and
  "stay up to date automatically" claim.
- `https://raw.githubusercontent.com/anomalyco/opencode/dev/install`
  (the curl-installer script) -- the source for §3.1/§3.2's OS/arch
  detection, Rosetta/musl/AVX2-baseline handling, archive-naming
  convention, install location, and `VERSION`/`--version`/`--binary`/
  `--no-modify-path` handling.
- `https://raw.githubusercontent.com/anomalyco/opencode/dev/packages/opencode/script/build.ts` --
  the source for §3.2's twelve-target build matrix and `Bun.build()`
  invocation details.
- `https://raw.githubusercontent.com/anomalyco/opencode/dev/packages/opencode/script/publish.ts` --
  the source for §3.3's `optionalDependencies`-map-assembly and
  shared-version-pinning logic.
- `https://raw.githubusercontent.com/anomalyco/opencode/dev/.github/workflows/publish.yml`
  and a directory listing of
  `https://github.com/anomalyco/opencode/tree/dev/.github/workflows` --
  the source for §3.2's CI build-matrix, code-signing/notarization
  detail, and the adjacent Electron-desktop/VS Code-extension workflow
  names.
- `https://github.com/anomalyco/opencode/blob/dev/packages/opencode/src/cli/cmd/upgrade.ts`
  and
  `https://raw.githubusercontent.com/anomalyco/opencode/dev/packages/opencode/src/installation/index.ts` --
  the source for §3.4's `method()`/`upgrade()`/`latest()` mechanics, the
  per-method command list, and the explicit finding that this file
  contains no visible background/startup auto-update-check logic.
- `anomalyco/opencode` Issue #10441 ("`opencode upgrade` doesn't update
  plugin dependencies in `~/.config/opencode/package.json`"), confirmed
  to exist as a live issue title via a targeted web search this session
  -- the source for §3.4's plugin-vs-binary-update-scope finding.

**Cross-references within this book, not re-derived:**
[retries.md](retries.md) (corrected, this session, to cite v2.1.147
rather than v2.1.144 for Claude Code's auto-updater retry hardening, and
to point back to this page for the full mechanism; also the source of
the Copilot CLI 1.0.55/1.0.57 release-API rate-limit entries reused in
§2.3), [tui-cli-application-architecture.md](tui-cli-application-architecture.md)
(the sibling "table stakes" page this one follows in framing),
[built-in-skills.md](built-in-skills.md) (the plugin/skill-content layer
whose own auto-update mechanism §1.4/§2.3/§3.4 each explicitly
distinguish from binary self-update), and
[permissions-and-sandboxing.md](permissions-and-sandboxing.md) (cited in
passing in §1.2 for the native-Windows-vs-WSL sandboxing distinction).
