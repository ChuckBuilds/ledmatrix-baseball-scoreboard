# Nested Config Schemas

## Overview

The plugin manager now supports **nested config schemas**, allowing you to organize complex plugin configurations into logical, collapsible sections in the web interface. This makes plugins with many configuration options much easier to understand and manage.

## Benefits

### Before (Flat Schema)
With a flat schema, all 32+ configuration options appear in a long, overwhelming list:
- `nfl_enabled`
- `nfl_favorite_teams`
- `nfl_show_live`
- `nfl_show_recent`
- `nfl_show_upcoming`
- `nfl_recent_games_to_show`
- `nfl_upcoming_games_to_show`
- `nfl_show_records`
- `nfl_show_ranking`
- `nfl_show_odds`
- `nfl_show_favorite_teams_only`
- `nfl_show_all_live`
- (... and 20+ more for NCAA Football)

### After (Nested Schema)
With nested schemas, options are organized into collapsible sections:
- **NFL Settings** (collapsible section)
  - enabled
  - favorite_teams
  - **Display Modes** (nested section)
    - show_live
    - show_recent
    - show_upcoming
  - **Game Limits** (nested section)
    - recent_games_to_show
    - upcoming_games_to_show
  - **Display Options** (nested section)
    - show_records
    - show_ranking
    - show_odds
  - **Filtering Options** (nested section)
    - show_favorite_teams_only
    - show_all_live
- **NCAA Football Settings** (collapsible section)
  - (same nested structure as NFL)

## How to Use Nested Schemas

### Schema Structure

To create a nested object in your `config_schema.json`, use `type: "object"` with a `properties` field:

```json
{
  "type": "object",
  "properties": {
    "nfl": {
      "type": "object",
      "title": "NFL Settings",
      "description": "Configuration for NFL games",
      "properties": {
        "enabled": {
          "type": "boolean",
          "default": true,
          "description": "Enable NFL games"
        },
        "favorite_teams": {
          "type": "array",
          "items": { "type": "string" },
          "default": [],
          "description": "List of favorite teams"
        },
        "display_modes": {
          "type": "object",
          "title": "Display Modes",
          "description": "Control which game types to show",
          "properties": {
            "show_live": {
              "type": "boolean",
              "default": true,
              "description": "Show live games"
            }
          }
        }
      }
    }
  }
}
```

### Key Points

1. **Nested objects** use `"type": "object"` and have their own `properties` field
2. **Title and description** are optional but recommended for clarity
3. **Unlimited nesting depth** - you can nest objects within objects as deep as needed
4. **Automatic UI generation** - collapsible sections are created automatically
5. **Config storage** - nested config is stored as nested JSON objects

### Example: Simple to Nested Migration

#### Before (Flat):
```json
{
  "properties": {
    "nfl_enabled": { "type": "boolean", "default": true },
    "nfl_show_live": { "type": "boolean", "default": true },
    "nfl_show_recent": { "type": "boolean", "default": true }
  }
}
```

#### After (Nested):
```json
{
  "properties": {
    "nfl": {
      "type": "object",
      "title": "NFL Settings",
      "properties": {
        "enabled": { "type": "boolean", "default": true },
        "show_live": { "type": "boolean", "default": true },
        "show_recent": { "type": "boolean", "default": true }
      }
    }
  }
}
```

## Accessing Nested Config in Plugin Code

### In Your Plugin Manager

When you use nested schemas, your config will be stored as nested objects:

```python
# With nested schema, config looks like:
{
    "enabled": True,
    "nfl": {
        "enabled": True,
        "favorite_teams": ["TB", "DAL"],
        "display_modes": {
            "show_live": True,
            "show_recent": True
        }
    }
}

# Access nested values:
nfl_enabled = config.get("nfl", {}).get("enabled", True)
show_live = config.get("nfl", {}).get("display_modes", {}).get("show_live", True)
```

### Helper Function for Safe Access

```python
def get_nested_config(config, path, default=None):
    """
    Safely access nested config using dot notation.
    
    Example:
        get_nested_config(config, "nfl.display_modes.show_live", True)
    """
    keys = path.split('.')
    value = config
    
    for key in keys:
        if isinstance(value, dict) and key in value:
            value = value[key]
        else:
            return default
    
    return value
```

## Backward Compatibility

### Fully Compatible
- **Flat schemas still work** exactly as before
- **Existing plugins don't need changes** - all current flat schemas continue to work
- **Mixed mode supported** - you can have both flat and nested properties in the same schema

### Migration Strategy

You don't have to migrate all at once. You can:

1. **Keep using flat schemas** - they work perfectly
2. **Gradually nest** - start with a few nested sections, keep others flat
3. **Full migration** - restructure entire schema when ready

## UI Behavior

### Collapsible Sections
- Click section headers to expand/collapse
- Chevron icon (▼) indicates expand/collapse state
- Sections are **expanded by default** when first opened
- Visual hierarchy with indentation for nested sections

### Visual Design
- **Gray background** for nested sections (differentiates from main form)
- **Borders** around each nested section
- **Hover effects** on section headers
- **Smooth animations** when expanding/collapsing
- **Indentation** for deeply nested sections (up to 3-4 levels recommended)

## Best Practices

### When to Use Nested Schemas

**Good candidates for nesting:**
- Multiple related settings (e.g., all NFL settings)
- Groups of options that control one feature
- Settings that naturally form categories
- Plugins with 15+ configuration options

**Keep flat for:**
- Simple plugins with <10 options
- Options that don't naturally group together
- Top-level settings like `enabled` and `display_duration`

### Organizing Your Schema

```json
{
  "properties": {
    // Top-level essentials (flat)
    "enabled": { ... },
    "display_duration": { ... },
    "update_interval": { ... },
    
    // Grouped features (nested)
    "sport_name": {
      "type": "object",
      "title": "Sport Name Settings",
      "properties": {
        "enabled": { ... },
        "teams": { ... },
        
        // Sub-groups within groups
        "display_options": {
          "type": "object",
          "title": "Display Options",
          "properties": { ... }
        }
      }
    }
  }
}
```

### Naming Conventions

1. **Use clear, descriptive titles** - shown in the UI header
2. **Add helpful descriptions** - shown as help text
3. **Keep property names concise** - they become form field names
4. **Use consistent patterns** - similar sections should have similar structures

## Example: Football Scoreboard

See `config_schema_nested_example.json` in the football-scoreboard plugin for a complete example of:
- Two top-level sections (NFL and NCAA Football)
- Four nested sub-sections per sport (Display Modes, Game Limits, Display Options, Filtering)
- Clear organization of 30+ configuration options
- Consistent structure between similar sections

## Technical Details

### Form Field Naming
Nested fields use **dot notation** for form field names:
- `nfl.enabled` → checkbox for NFL enabled
- `nfl.display_modes.show_live` → checkbox for showing live NFL games
- `ncaa_fb.game_limits.recent_games_to_show` → number input

### Config Serialization
- **Form submission** converts dot notation back to nested objects
- **Config loading** handles both flat and nested structures
- **Type conversion** works for all nested fields (boolean, integer, array, etc.)
- **Default values** are applied recursively through nested structures

### API Compatibility
The existing `/api/v3/plugins/config` endpoint handles both:
- Flat config: `{"nfl_enabled": true}`
- Nested config: `{"nfl": {"enabled": true}}`

No backend changes needed!

## Troubleshooting

### My nested sections aren't collapsing
- Check that you have `type: "object"` in your schema
- Ensure `properties` is defined within the nested object
- Verify JavaScript console for errors

### Values aren't saving correctly
- Check that field names match your schema structure
- Verify dot notation is correct in generated form fields
- Check browser console for serialization errors

### Sections look wrong
- Ensure the styles are loaded (check `<style>` block in plugins.html)
- Verify nested-section CSS classes are applied
- Check for conflicting styles

## Summary

Nested config schemas provide:
✅ **Better organization** for complex plugins
✅ **Improved UX** with collapsible sections
✅ **Full backward compatibility** with existing flat schemas
✅ **No backend changes required**
✅ **Unlimited nesting depth**
✅ **Automatic UI generation**

Start using nested schemas today to make your plugins easier to configure!

