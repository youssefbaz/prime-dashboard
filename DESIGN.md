---
name: Prime Dashboard
description: Personal operating system for executing a high-stakes self-improvement plan. Prime is built in silence. Discipline = Freedom.
colors:
  focus-indigo: "#6366f1"
  push-violet: "#a855f7"
  surge-pink: "#ec4899"
  indigo-light: "#818cf8"
  lavender: "#a5b4fc"
  void: "#07070a"
  deep-space: "#0a0a0f"
  void-indigo: "#0f0f1c"
  space-haze: "#1a1a3a"
  text-primary: "#f8fafc"
  text-secondary: "#94a3b8"
  text-muted: "#64748b"
  text-ghost: "#475569"
  emerald: "#34d399"
  amber: "#fbbf24"
  crimson: "#ef4444"
typography:
  display:
    fontFamily: "'Outfit', sans-serif"
    fontSize: "clamp(28px, 5vw, 42px)"
    fontWeight: 900
    lineHeight: 1.1
    letterSpacing: "-1px"
  headline:
    fontFamily: "'Outfit', sans-serif"
    fontSize: "20px"
    fontWeight: 800
    lineHeight: 1.3
  title:
    fontFamily: "'Outfit', sans-serif"
    fontSize: "32px"
    fontWeight: 800
    lineHeight: 1
  body:
    fontFamily: "'Inter', sans-serif"
    fontSize: "14px"
    fontWeight: 400
    lineHeight: 1.6
  label:
    fontFamily: "'JetBrains Mono', monospace"
    fontSize: "11px"
    fontWeight: 700
    lineHeight: 1
    letterSpacing: "2px"
rounded:
  pill: "99px"
  card: "20px"
  surface: "18px"
  component: "16px"
  control: "12px"
  badge: "6px"
spacing:
  xs: "4px"
  sm: "8px"
  md: "16px"
  lg: "24px"
  xl: "32px"
  2xl: "48px"
  3xl: "64px"
components:
  button-primary:
    backgroundColor: "{colors.focus-indigo}"
    textColor: "{colors.text-primary}"
    rounded: "{rounded.control}"
    padding: "10px 24px"
  button-primary-hover:
    backgroundColor: "{colors.indigo-light}"
    textColor: "{colors.text-primary}"
    rounded: "{rounded.control}"
    padding: "10px 24px"
  button-secondary:
    backgroundColor: "#ffffff0a"
    textColor: "{colors.text-secondary}"
    rounded: "{rounded.control}"
    padding: "10px 24px"
  button-secondary-hover:
    backgroundColor: "#ffffff12"
    textColor: "{colors.text-primary}"
    rounded: "{rounded.control}"
    padding: "10px 24px"
  input-default:
    backgroundColor: "#ffffff08"
    textColor: "{colors.text-primary}"
    rounded: "{rounded.control}"
    padding: "10px 14px"
  input-focus:
    backgroundColor: "#ffffff08"
    textColor: "{colors.text-primary}"
    rounded: "{rounded.control}"
    padding: "10px 14px"
---

# Design System: Prime Dashboard

## 1. Overview

**Creative North Star: "The Precision Instrument"**

Prime Dashboard is a personal operating system, not a product to be sold. Like a pilot's cockpit or a professional athlete's training computer, every element on screen exists to help the user execute a plan: the dark glass stays out of the way, the data reads at a glance, the controls respond without hesitation. The aesthetic is earned discipline, not designed atmosphere.

The system draws from Linear and Raycast: precise spacing, a restrained palette anchored by one strong accent color, no surface decoration that doesn't carry information. Where those tools serve teams, Prime serves a single person with a singular mission. That specificity is the license for a slightly sharper edge: monospace counters, gamified XP that feels earned rather than cute, a sidebar that communicates structure without ornamentation.

This system explicitly rejects the corporate BI tool aesthetic (Tableau, Power BI: gray-heavy, clinical, zero personality) and the generic SaaS dashboard pattern (hero metrics, gradient cards, identical stat blocks that could belong to anyone). Prime belongs to one person. The interface reflects that.

**Key Characteristics:**
- Dark-first: the scene is a person at a desk or on a phone in focused work mode. The dark theme is not a style choice; it's the right answer for that scene.
- One accent, used sparingly: Focus Indigo carries CTAs, active states, and progress. Its rarity is its power.
- Three-font system with distinct roles: Outfit for display energy, Inter for readable density, JetBrains Mono for data precision.
- Flat at rest, dramatic on interaction: surfaces are tonal planes until touched.
- Gamification that earns its place: XP, streaks, and level progress exist because the user earned them.

## 2. Colors: The Deep Space Palette

A near-black foundation with a single dominant indigo accent, a purple-to-pink gradient reserved for progress and celebration, and a slate-gray text hierarchy that reads cleanly at every level.

### Primary
- **Focus Indigo** (`#6366f1`): The single active-state voice. Used on primary CTAs (as gradient base), active nav item, progress bar fills, focus rings, XP bar, and hover border emphasis. Its rarity on any given screen is intentional.
- **Indigo Light** (`#818cf8`): The readable variant of Focus Indigo. Used for supertitles (day counter, plan metadata), sidebar section headers, and the "NOW" live indicator text. Never as a fill color.
- **Lavender** (`#a5b4fc`): Active tab text only. Softer than Indigo Light, communicates selection without asserting.

### Secondary
- **Push Violet** (`#a855f7`): Gradient endpoint for primary buttons and the XP progress bar (indigo → violet). Not used independently as a flat color.

### Tertiary
- **Surge Pink** (`#ec4899`): Third point in the celebration gradient (XP bar: indigo → violet → pink) and the ambient glow orb. Appears only in gradient or background-glow contexts. Never as a UI surface color or text.

### Semantic
- **Emerald** (`#34d399`): Success, completion, positive weight delta, habit-done states.
- **Amber** (`#fbbf24`): Warning, paused states, category colors (Career, neutral events).
- **Crimson** (`#ef4444`): Error, destructive actions, overdue goal states.

### Neutral
- **Void** (`#07070a`): The deepest background. Radial gradient endpoint. Near-black with the faintest cool tint.
- **Deep Space** (`#0a0a0f`): Base page background. Never pure black.
- **Void Indigo** (`#0f0f1c`): Sidebar surface. Slightly lighter and more blue-tinted than the page background, creating structural separation without a strong border.
- **Space Haze** (`#1a1a3a`): The top-left radial gradient highlight. Gives the background a sense of depth and keeps it from reading as flat.
- **Text Primary** (`#f8fafc`): Headings, values, critical data.
- **Text Secondary** (`#94a3b8`): Body text, descriptions, secondary labels.
- **Text Muted** (`#64748b`): Metadata, timestamps, section labels in data-dense areas.
- **Text Ghost** (`#475569`): Disabled states, completed/struck-through items, faint hints.

### Named Rules

**The One Voice Rule.** Focus Indigo (`#6366f1`) is used on 10% or fewer of any given screen's interactive elements. It marks the single most important action or the current state. When everything is accented, nothing is.

**The No Pure Black Rule.** `#000` and `#fff` are forbidden. Every background uses Void or Deep Space; every text color uses the slate-text hierarchy. The gap between the lightest and darkest surfaces is deliberate: they live in the same visual world.

## 3. Typography

**Display Font:** Outfit (fallback: system-ui, sans-serif)
**Body Font:** Inter (fallback: system-ui, sans-serif)
**Label/Data Font:** JetBrains Mono (fallback: 'Courier New', monospace)

**Character:** Outfit brings ambition and weight to titles without feeling editorial or precious. Inter is invisible in the right way: dense, readable, neutral. JetBrains Mono grounds data and labels in technical precision, signaling that numbers here are real.

### Hierarchy

- **Display** (Outfit 900, `clamp(28px, 5vw, 42px)`, line-height 1.1, letter-spacing -1px): Page titles only. One per page. The single largest type on screen.
- **Title** (Outfit 800, `32px`, line-height 1): Large data values in stat cards (.s-val). Communicates a single critical number.
- **Headline** (Outfit 800, `20px`, line-height 1.3): Section headers (.sec-title). Divides the page into named zones.
- **Body** (Inter 400-600, `14px`, line-height 1.6): All paragraph text, descriptions, notes. Max line length: 65ch.
- **Label** (JetBrains Mono 700, `11px`, letter-spacing 2px, ALL CAPS): Stat card labels (.s-label), badge text, plan metadata supertitles. Data classification, not prose.
- **Caption** (Inter 400, `13px`, `#94a3b8`): Sub-labels, secondary copy, milestone rows, timestamps.

### Named Rules

**The Three-Font Boundary Rule.** Outfit is for display and section headers only. Inter is for body and UI copy. JetBrains Mono is for labels, badges, and numerical metadata. Do not use Mono for body copy or Outfit for UI labels. The three fonts signal three different types of information.

**The No Gradient Text Rule.** Current code uses gradient text (`background-clip: text`) on `.page-title`. This is the one existing violation of the absolute bans. New screens should use `{colors.text-primary}` (`#f8fafc`) for display titles with weight and scale providing the hierarchy. The gradient adds complexity without meaning.

## 4. Elevation

Prime uses a flat-at-rest, dramatic-on-interaction model. At rest, surfaces are distinguished by tonal lightness alone: Deep Space (base) → Void Indigo (sidebar) → card surfaces (rgba overlays). No shadows on idle components.

Interaction triggers a full elevation response: cards lift 8px, rotate 2deg on the X axis, and cast a deep ambient shadow (`0 25px 50px -12px rgba(0,0,0,0.5)`). The lift is emphatic because the rest state is flat. You always know what's interactive.

The glassmorphism layer (`backdrop-filter: blur(20px)` on `.s-card`) is reserved for the primary stat card component only. It is not applied globally. Section containers use opaque tonal backgrounds without blur. Glass blur on every surface collapses the hierarchy between primary and secondary content.

### Shadow Vocabulary

- **Card hover shadow** (`0 25px 50px -12px rgba(0,0,0,0.5)`): Applied to `.s-card` on hover, alongside translateY(-8px) rotateX(2deg). The dramatic lift earns this shadow depth.
- **Button glow** (`0 4px 15px rgba(99,102,241,0.25)`, hover: `0 8px 25px rgba(99,102,241,0.4)`): The primary button's indigo ambient glow. Communicates energy, not elevation.
- **Focus ring** (`0 0 0 3px rgba(129,140,248,0.1)`): Applied to focused inputs. Thin, indigo-tinted, non-distracting.

### Named Rules

**The Flat-at-Rest Rule.** No component carries a resting shadow. Elevation is a response to state (hover, focus, active), not an ambient style. A card that always looks elevated has no room to react.

**The Selective Glass Rule.** `backdrop-filter: blur()` is used on `.s-card` stat cards and the sidebar only. Section containers, forms, and secondary content use opaque tonal surfaces (`rgba(255,255,255,0.02)`). Blur everywhere is noise; blur on the primary layer is signal.

## 5. Components

### Buttons

Tactile and confident. The primary button is the single most prominent interactive element on any given screen.

- **Shape:** Gently rounded (12px, described as "control radius"). Not pill-shaped — this is a tool, not a consumer app.
- **Primary:** Gradient fill `linear-gradient(135deg, #6366f1, #a855f7)` with `box-shadow: 0 4px 15px rgba(99,102,241,0.25)`. Outfit 600, white text.
- **Primary Hover:** `translateY(-2px) scale(1.01)`, shadow intensifies to `0 8px 25px rgba(99,102,241,0.4)`, `filter: brightness(1.1)`. The button visibly responds.
- **Primary Active:** `translateY(0)` — snaps back to rest position.
- **Secondary:** `rgba(255,255,255,0.04)` background, `1px solid rgba(255,255,255,0.10)` border, `#cbd5e1` text. Subdued by design; it should not compete with Primary.
- **Secondary Hover:** `rgba(255,255,255,0.07)`, border shifts to `rgba(129,140,248,0.35)`, text brightens to `#e2e8f0`, `translateY(-1px)`.

### Cards / Containers

Two tiers, clearly distinct:

- **Stat Card (`.s-card`):** The primary data container. `rgba(255,255,255,0.03)` background, `backdrop-filter: blur(20px)`, `1px solid rgba(255,255,255,0.08)` border, 20px radius, 24px padding. Hover triggers full lift (8px up, 2deg X-rotation, deep shadow). A shimmer sweep (`::before` pseudo-element) animates on hover. Text-center aligned.
- **Section Container (`.section-card`):** Secondary grouping. `rgba(255,255,255,0.02)`, `1px solid rgba(255,255,255,0.06)`, 18px radius, 24px padding. No blur, no hover transform. Structural, not interactive.
- **Specialty Cards:** Goal cards (16px radius, pinned variant with indigo tint, completed with emerald tint, overdue with crimson tint), job rows (12px radius, hover: `translateX(4px)`). State is communicated through the border and background, not icons alone.

**Never nest a stat card inside a section card.** The hierarchy collapses and both levels lose meaning.

### Inputs / Fields

- **Style:** `rgba(255,255,255,0.03)` background, `1px solid rgba(255,255,255,0.06)` border, 12px radius, `10px 14px` padding, `#f1f5f9` text.
- **Focus:** Border shifts to `rgba(129,140,248,0.40)`, adds `box-shadow: 0 0 0 3px rgba(129,140,248,0.10)`. Visible but not aggressive.
- **Disabled/Error:** Not explicitly styled beyond Streamlit defaults. Semantic alert boxes use 14px radius and standard Streamlit semantic colors.

### Navigation

- **Structure:** Sidebar navigation with grouped sections (Overview, Study, Career, Health, Analytics, Planning, Assistant). Groups separated by `.stSidebarNavSeparator`.
- **Default item:** Transparent background, `#94a3b8` text, 10px radius, `10px 14px` padding.
- **Hover:** `rgba(255,255,255,0.04)` background, `translateX(4px)` — a micro-shift that signals direction without drama.
- **Active:** `linear-gradient(90deg, rgba(99,102,241,0.15), rgba(99,102,241,0.02))` background, `inset 3px 0 0 #818cf8` box-shadow. The inset shadow creates a left-rail indicator; note this is technically a 3px left-stripe — this is the one context where a left border is semantically correct (active nav indicator). It is not decorative.
- **Section headers:** JetBrains Mono 700, 13px, `#818cf8`, uppercase, 1.5px letter-spacing. Structural, not navigational.

### XP Bar / Gamification

The level progress bar is the only element in the system that uses the full three-color gradient (indigo → violet → pink). It earns this license: the gradient communicates energy and forward motion in a context where it has semantic meaning (progress toward the next level).

- **LVL badge:** JetBrains Mono 800, 12px, `#818cf8`, uppercase, 1px letter-spacing.
- **XP counter:** JetBrains Mono, 11px, `#64748b`. Secondary to the level indicator.
- **Bar:** 8px height, `rgba(255,255,255,0.1)` track, `linear-gradient(90deg, #6366f1, #ec4899)` fill, 10px radius, shimmer animation.

### Badges / Pills

- **Badge (`.badge`):** JetBrains Mono 600, 11px, 1px letter-spacing, uppercase, `3px 10px` padding, 6px radius. Color varies by semantic context.
- **Pill (`.pill`):** Same typography as badge, 99px radius. Used for category tags and status indicators.
- **NOW tag:** JetBrains Mono 800, 10px, 2px letter-spacing, `#818cf8` text, `rgba(99,102,241,0.18)` background, 6px radius, animated dot prefix.

### Tabs

- **Container:** `rgba(255,255,255,0.02)` background, `1px solid rgba(255,255,255,0.06)` border, 12px radius, 4px internal padding.
- **Default tab:** `#64748b` text, Outfit 600.
- **Active tab:** `rgba(99,102,241,0.20)` background, `#a5b4fc` text, 8px radius.
- **Tab border:** Hidden. The background fill communicates selection.

## 6. Do's and Don'ts

### Do:
- **Do** use Focus Indigo (`#6366f1`) exclusively for the primary action and active state on any screen. One voice.
- **Do** keep card backgrounds in the `rgba(255,255,255,0.02–0.06)` range. Surfaces are dark; content provides the contrast.
- **Do** use JetBrains Mono for all numerical labels, badges, and data classifiers. Numbers are data; they deserve the data font.
- **Do** vary card types by content importance: `.s-card` (glass, stat) for primary KPIs; `.section-card` (opaque, no blur) for secondary content groupings.
- **Do** use the three-step text hierarchy: `#f8fafc` for critical data, `#94a3b8` for secondary copy, `#64748b` for metadata.
- **Do** reserve the indigo-violet-pink gradient for progress bars and the XP system only. These are the celebration contexts.
- **Do** write copy in the voice of the brand: direct, terse, no filler. "Day 47 of 90" not "You're on day 47 of your 90-day journey!"
- **Do** use Emerald (`#34d399`) for completion and success states, Amber (`#fbbf24`) for warnings, Crimson (`#ef4444`) for errors. These are not decoration; they are system state.

### Don't:
- **Don't** use the Corporate BI tool aesthetic: no gray-heavy clinical layouts, no generic stat blocks that could belong to any company's dashboard, no dataviz without personality. Prime has a specific user on a specific mission.
- **Don't** add `backdrop-filter: blur()` to every surface. Glass blur is reserved for `.s-card` stat cards and the sidebar. Blur everywhere collapses the hierarchy.
- **Don't** use gradient text (`background-clip: text` with a gradient fill) on new screens. The existing `.page-title` is a legacy exception. New display titles use `#f8fafc` with weight and scale.
- **Don't** use identical card grids: same size, same structure, icon + heading + text, repeated. If content is that similar, consider a list or table instead.
- **Don't** add a left or right border stripe (`border-left: 4px solid accent`) to cards or list items as a decorative accent. The one exception is the active sidebar nav indicator (3px inset, semantically correct). Everywhere else: use background tints or no accent.
- **Don't** use Outfit for body copy or JetBrains Mono for paragraph text. The three-font boundary is structural, not aesthetic.
- **Don't** animate layout properties (height, width, top, left, margin). Animate transform and opacity only.
- **Don't** use `#000` or `#fff` anywhere. The system lives in the Void-to-Space-Haze range; pure black and pure white look like errors.
- **Don't** write hollow motivational copy ("You're doing great!", "Keep it up!"). Feedback is direct and honest: the data speaks.
