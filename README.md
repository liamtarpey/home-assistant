# home-assistant

My Home Assistant setup: a button-card design system, page views (TfL, Utilities, Lounge lights, Studio, Bedroom lights), cards, automations and notes. It runs on a Raspberry Pi 5 with Home Assistant OS.

If you are an AI assistant helping with this repo, read [`handoff/HANDOFF.md`](handoff/HANDOFF.md) first: it explains the setup, conventions, lessons learned and what is still open.

## Layout

| Folder | What it holds |
|---|---|
| `handoff/` | Context for an AI assistant: setup, conventions, status, open items. |
| `dashboard/templates/` | One button-card template per file (44). Edit these. |
| `dashboard/dist/` | `button-card-templates.yaml`, generated: the whole block to paste into the dashboard's raw configuration. |
| `dashboard/pages/` | The card for each page view (view type: Panel). |
| `dashboard/cards/` | Standalone cards (weather, the lights card on the main dashboard). |
| `dashboard/tools/` | `build_templates.py` joins `templates/` into `dist/`. |
| `automations/` | Automations, plus proposals not yet applied. |
| `logic-pro/` | The listener that sends Logic Pro's recording signal to Home Assistant. |
| `plan/` | The smart-home plan checklist (open `smart-home-plan.html` in a browser). |

## Updating the live dashboard

1. Edit a file in `dashboard/templates/`.
2. Run `python3 dashboard/tools/build_templates.py`.
3. Copy `dashboard/dist/button-card-templates.yaml` into the dashboard's raw configuration editor, replacing the `button_card_templates:` section. Run Check configuration before restarting anything.

## Secrets

`secrets.yaml`, API keys and the webhook ID are never stored here. Placeholders look like `REPLACE_...`.
