# Slint Kit

**125+ native UI components for Rust and Slint**: typed forms and validation, virtualized tables and lists, date and time pickers, exact decimal fields, dialogs, navigation and layout, with complete light and dark themes.

Rust owns validated values and stable identity; Slint owns presentation and native interaction (caret, selection, undo, IME).

<p>
  <img alt="Virtualized data table" src="https://slint-kit.dev/assets/components/data-table@2x.png" width="32%">
  <img alt="Calendar in dark theme" src="https://slint-kit.dev/assets/components/calendar-dark@2x.png" width="32%">
  <img alt="Dialog" src="https://slint-kit.dev/assets/components/dialog-surface@2x.png" width="32%">
</p>

**[Browse all components, in light and dark →](https://slint-kit.dev/components/)** · [Getting started](https://slint-kit.dev/guides/getting-started/) · [Forms guide](https://slint-kit.dev/guides/forms/) · [Documentation en français](https://slint-kit.dev/fr/)

## Install

```toml
[dependencies]
slint-kit = "0.7"
slint = { version = "~1.18.1", default-features = false, features = ["std", "compat-1-18", "backend-winit", "renderer-skia", "accessibility"] }

[build-dependencies]
slint-kit-build = "0.7"
```

Compile your UI in `build.rs`:

```rust
fn main() {
    slint_kit_build::compile("ui/app.slint").expect("compile application UI");
}
```

Import public components in Slint:

```slint
import { KitButton, KitTextField } from "@kit";
```

Call `slint_kit::install(&window)` once per window before showing it. It installs validation and the pure calculation services; component state stays local to each instance.

Use `slint_kit` in Rust for strict domain values, `Choices<K>`, `FieldSpec<T,E>` and `KeyedModel<K,Row>`. Enable `native` for asynchronous file/directory bindings, or `native-winit` for the explicit winit file-drop bridge. The manifest above is a desktop example; choose the Slint backend and renderer for your target as described in [Project setup](https://slint-kit.dev/guides/project-setup/). Keep `slint-kit` and `slint-kit-build` on the same release.

## Why Slint Kit

- **Typed forms:** input is parsed once into typed values, with HTML-style constraints and draft/commit/cancel handling.
- **Stable identity:** selection, sorting and editing follow your business keys, never row indexes.
- **Large collections:** virtualized tables and lists render only what is visible.
- **Exact values:** money and decimals use exact arithmetic.
- **Complete themes:** every state is designed in light and dark, and checked at 200% text size.

## Quality

No `unsafe` in the kit's hand-written Rust. CI runs `cargo fmt`, `clippy` with warnings denied, about 400 behavior tests (keyboard, pointer, focus, identity, geometry), generated-file verification and a lint that rejects hard-coded design values.

## Requirements

Rust 1.92 or later and Slint 1.18 (patch releases from 1.18.1). Desktop platforms: macOS, Windows and Linux. [Source, showcase and bilingual documentation](https://github.com/damione1/slint-kit).

## License

Open source under the [GNU GPL v3.0 or later](LICENSE); dependencies retain their own licenses. From 1.0, a commercial license will be available for proprietary applications, along with **Slint Kit Pro** advanced components. [Get in touch](https://github.com/damione1/slint-kit/discussions).
