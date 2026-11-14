# Home Assistant project handoff

Written 14 Nov 2026 from a long working session with Claude. Attach this file at the start of a new chat so Claude knows the setup, the conventions, what has been built and what is still open.

## 0. How to use this pack

- Attach `HANDOFF.md` to the first message and say what you want to do. Attach only the code file you are changing (for example `dashboard/templates/lounge_scene.yaml`). Each template is its own small file in `dashboard/templates/`, and `dashboard/dist/button-card-templates.yaml` (about 155KB) is the combined block, so avoid attaching that one unless you really need it.
- **The live Home Assistant config is the source of truth.** The files here are a reconstruction of the latest versions and may differ slightly from what is live. To export the live dashboard: Settings > Dashboards > open the dashboard > pencil (Edit) > three dots > Raw configuration editor > select all > copy.
- Not in this pack: the main dashboard's TV, Spotify and PS5/Switch cards, and the sections of `configuration.yaml` that hold the Switch, PS5, Octopus, TfL, weather-forecast and RAWG sensors. Export those from the live config (dashboard raw editor and VS Code).
- Deliberately not included: `secrets.yaml`, the RAWG API key, the Octopus key, Backblaze keys, the webhook ID, the 1Password items. Placeholders are marked `REPLACE_...`.

## 1. The user and how to work with him

- Liam, England. Home Assistant is a hobby project for his flat.
- Wants direct answers and results, not setup questions first.
- For Home Assistant code he wants the **complete replacement** (whole card, whole template, whole config block) so he can paste over the old one, and everything in **one paste** where possible. Anything over about 28KB should be delivered as a file, and the file must actually be attached or he cannot see it.
- All dashboard cards are **250px high**. Pages must fit the iPad without scrolling.
- For visual work he likes a mockup first (a design canvas or artifact), then code.
- He tests on a wall iPad (Companion app, Kiosk mode) and on a work laptop in Safari, and reports back by pasting. Claude cannot render the dashboard, so JavaScript logic was tested with node and YAML with PyYAML, but layout is only confirmed when he sees it. Say so when that applies.
- He pushes back when something is wrong. He was right more than once: check before defending an answer.

## 2. The setup

**Platform.** Raspberry Pi 5 running Home Assistant OS on Ethernet, SD card. IP `192.168.1.124`, served on port 80 (not 8123). Automatic daily backups to Backblaze B2 (database excluded, encryption key in 1Password). Home Assistant core was **not** updated to 2026.11.0: that update left it in recovery mode and he restored from a backup. Suspected causes: HACS being absorbed into core as "Marketplace" on first start, and the entity naming change. Wait for 2026.11.1 or later, update HACS integrations first, and keep "backup before updating" on.

**Frontend.** HACS: button-card (the whole design system is button-card templates in the dashboard raw config), Mushroom (badges). Dashboard shown on an iPad mounted on the wall.

**Network.** Moving from Vodafone to BT next month. Plan: same Wi-Fi name and password, keep 2.4GHz on, DHCP reservations for the Pi (`192.168.1.124`), the Fire TV (`192.168.1.110`) and the new Tapo strip, check the Pi has no manual gateway (BT's hub is `192.168.1.254`), disable Tapo auto-update.

**Devices and integrations.**
- Lounge lights: WiZ bulbs (`light.wiz_rgbw_tunable_181e98` Big lamp, `light.wiz_rgbw_tunable_19f62e` TV uplight, `light.wiz_rgbw_tunable_1a3d76` Couch uplight), `light.lounge_lounge_candle`, Tapo L900-5 light strips `light.lounge_lightstrip_left` and `_right`, group `light.all_lounge_lights`. Bedroom: `light.bed_light_strip` (a Tapo L900 that needed the Tapo app's third-party compatibility toggled off and on before Home Assistant could add it).
- Lounge scenes: `scene.movie_mode`, `party_mode`, `sleep_mode`, `off_mode`, `pink_bright`, `pink_dim`, `green_bright` (renamed **Zelda lights**), `green_dim`, `blue_bright`, `blue_dim`, `red_bright`, `red_dim`. Helper `input_boolean.movie_mode_active`.
- Studio: Tapo P304M 4-socket strip (TP-Link Smart Home integration, not Matter). Switches `switch.office_studio_power_speakers_and_amps_yahama_msp5_left` (the left one really is spelled "yahama"), `..._yamaha_msp5_right`, `..._evh_5150iii`, `..._little_walter_22w`. Sensors per socket: `sensor.office_power_<device>_current_consumption`, `_today_s_consumption`, `_voltage`, `_current`; `binary_sensor.office_power_<device>_overheated` and `_overloaded`. Devices: Yamaha MSP5 monitors (left and right), EVH 5150III and Little Walter 22W valve amp heads. Auto-off switches are left off on purpose.
- TV: Fire TV `media_player.fire_tv_192_168_1_110`. Its `hdmi_input` attribute is always null.
- PS5: `sensor.panhalen37_now_playing`, `image.panhalen37_now_playing`, `sensor.ps5_last_played`, `input_text.ps5_cover_version`.
- Switch 2: Nintendo Parental Controls integration (`sensor.nintendo_switch_2_used_screen_time`) plus template sensors in `configuration.yaml`: `sensor.switch_2_last_game`, `binary_sensor.switch_2_active`, `sensor.switch_2_last_active`, `sensor.switch_2_artwork` (artwork from RAWG through `rest_command.rawg_search`, URL in `secrets.yaml` as `rawg_search_url`).
- Spotify: `media_player.lounge_spotify`, `sensor.spotify_last_track`, `input_text.spotify_cover_version`.
- Weather: `weather.forecast_home`; a template sensor `sensor.weather_daily_forecast` keeps the daily forecast as JSON in `forecast_json`.
- TfL: `sensor.london_underground_<line>` for 14 lines, DLR departures for Stratford High Street, roundel SVGs in `/config/www/svg/tfl/roundel-<line>-no-text.svg`.
- Utilities: Octopus sensors for electricity and gas; no water integration found.
- Not bought yet, deliberately: the ZBT-2 Zigbee radio (no device needs it yet). The blinds plan is in `plan/smart-home-plan.html`.

## 3. Dashboards and code architecture

- Main dashboard: the original 3x2 grid (weather, TV, PS5/Switch stack, lights, Spotify, PS5/Switch stack). A tried-and-rejected redesign was reverted, so there are no `home_*` templates in the latest block.
- Separate "page" views, each of type **Panel (1 card)** with one card: `template: [page_shell, <page template>]` plus `grid_options: columns: full`. `page_shell` provides the full-height grid (hero, side, and scrolling areas a, b, c). Pages: TfL, Utilities, Lounge lights, Studio, Bedroom lights. See `dashboard/pages/`.
- All shared styling and logic lives in `dashboard/templates/` (one file per template, 44 in total). `python3 dashboard/tools/build_templates.py` joins them into `dashboard/dist/button-card-templates.yaml`, which is what gets pasted into the dashboard's raw configuration (or use `!include_dir_merge_named templates/` in a YAML-mode dashboard). Families: `glass_*` (card base, title, power button, big icon, Ken Burns art), `scene_btn`, `tfl_*`, `ut_*`, `lt_*` (lounge lights, with swatch templates), `lounge_scene` (scene card with effects, including Zelda mode), `page_shell`, `studio_*`, `lt_hero_room` and `bedroom_page`.
- In the live raw configuration a template is replaced by name: search for `  name:` at two-space indent and replace down to just before the next template. In this repo, edit the template's file and rebuild `dashboard/dist/`.
- Weather card with the temperature curve: `dashboard/cards/weather-card.yaml` (a standalone card).

## 4. Design language

Dark glass cards, 250px high, rounded 18px, a big headline figure with a coloured glow and a subtle animation, accent colours per section, scene and power buttons as 46px round glass buttons. Zelda mode is a forest scene with downlight shafts, fairies with comet trails, fireflies and a gold Triforce.

## 5. Hard-won lessons

1. A bare `#` in an unquoted YAML value starts a comment: quote hex colours and gradients. This once cut off the scenes-row mask lines.
2. In button-card, a nested card inside another card's config has its `[[[ ]]]` templates evaluated by the **parent** card. Any nested card with its own logic has to be a template.
3. A missing semicolon in a CSS rule inside a template string made the browser drop the whole rule. Check punctuation first when styling "does nothing".
4. A button-card element can pick up `max-width: fit-content` from outside; `page_shell` forces `:host { display: block !important; width: 100% !important; ... }`.
5. Run **Check configuration** before every restart. One wrong indent once made `configuration.yaml` invalid.
6. On the work laptop, Safari reaches Home Assistant but Chrome and scripts fail on `homeassistant.local` (the always-on VPN's DNS). Use the IP address in scripts.
7. Tapo devices on newer firmware use TPAP encryption that Home Assistant's TP-Link integration may not support. Toggling third-party compatibility off and on in the Tapo app fixed it. Turn off auto-update on Tapo devices.
8. Nintendo's usage data lags many minutes, and forcing an update changes nothing. The Fire TV's `hdmi_input` is null, but the ADB command `dumpsys tv_input` shows each HDMI port's state.
9. RAWG can be down or missing a new game. The Switch card's `kb_img` has an `OVERRIDES` map (game name fragment to `/local/switch/<file>`) that is used before Nintendo's small icon.
10. Home Assistant no longer hands cards the forecast, which is why `sensor.weather_daily_forecast` exists.
11. Do not guess. Several wrong turns happened because an answer assumed something unverified (an entity ID, which IP belonged to which device, a firmware theory). Ask for a quick check first.

## 6. What has been built

Lights page with a scene card that matches the real lights (detects custom lights); Zelda mode and its automation; TfL page with overnight "closed" handling and a lines-open card; Utilities page; Studio page (hero with power button and amp warm-up bar, power strip card, three gear cards, overheat and overload warnings); Bedroom lights page; weather temperature-curve card; Spotify card spacing; Lounge lights card on the main dashboard with a button that opens the Lounge lights view; automations (see `automations/`); Backblaze B2 backups; the plan page.

## 7. Open items

1. **Switch 2 card is slow** (Nintendo data). Proposed fix in `automations/proposed-not-yet-applied.yaml`: read the Fire TV's HDMI port states every 20 seconds. First confirm that port 1 (HW4) flips from state 1 to 0 when the Switch wakes, then check the PS5 on port 2, then update the TV card mapping.
2. **Logic recording signal.** Working so far: Logic's Recording Light sends MIDI (notes 24 and 25, channel 0) through the IAC Driver, the script on the work laptop reads it, and the webhook returns HTTP 200. Still to do: confirm `studio_logic_midi` events appear in Developer tools > Events, find which note means armed, recording and stopped, then add the `input_select.logic_status` helper (idle, armed, recording) and show it on the studio page. Fallback: ESP32 route in the plan.
3. Move to BT next month (see section 2).
4. Bedroom scenes card (the right-hand slot on the bedroom page is empty on purpose).
5. West Ham matchday badge was made safe against a missing date (`as_datetime(raw, none)`).
6. Running per-game play totals on the Switch card (idea only, not built).
7. Maintainability: the templates are about 2,000 lines. Options discussed: split into one file per template with `!include_dir_merge_named` in YAML mode and keep it in a GitHub repo, or a real custom card repo installed through HACS.

## 8. Connecting Claude to Home Assistant (notes for the new account)

- Home Assistant's built-in **Anthropic** integration needs an API key from the Anthropic console with billing enabled. It is separate from a claude.ai plan.
- A claude.ai **custom connector** over MCP connects from Anthropic's servers, so Home Assistant would have to be reachable from the public internet. Home Assistant sits on a home network, so that would need Home Assistant Cloud or a reverse proxy, with the security care that implies.
- Pasting YAML into Home Assistant by hand, as in this project, needs neither.

## 9. This repository

- `README.md` is a short human-facing summary; this file is the context for Claude. Read this file first.
- Layout: `handoff/` (this file), `dashboard/` (`templates/` one file per template, `dist/` generated combined block, `pages/` view cards, `cards/`, `tools/`), `automations/`, `logic-pro/`, `plan/`. A `plugins/` folder is planned for later (custom cards) and does not exist yet.
- Never commit `secrets.yaml` or API keys. `.gitignore` already excludes them. Placeholders in this repo are marked `REPLACE_...`.
- In Claude, add this repo with the GitHub integration (the + menu in a chat, or in a project's knowledge) and pick only the files needed for the task, starting with `handoff/HANDOFF.md`. Click **Sync now** after pushing changes.
