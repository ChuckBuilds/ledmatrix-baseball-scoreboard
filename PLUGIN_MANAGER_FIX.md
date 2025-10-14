# Plugin Manager Tab Fix

## Issue
The Plugin Manager tab was not loading installed plugins or the plugin store when clicked.

## Root Cause
The issue had two parts:

1. **Incorrect HTMX Trigger**: The plugins tab was using `hx-trigger="intersect once"` which meant HTMX would only load the content when the element intersected with the viewport. However, since the tab was hidden by Alpine.js (`x-show="activeTab === 'plugins'"`), it never intersected with the viewport, so the content never loaded.

2. **Incorrect Event Handler**: The initialization code in `plugins.html` was listening for `htmx:afterSettle` and only checking for `DOMContentLoaded`, but since the content is loaded dynamically via HTMX after the page has already loaded, the `DOMContentLoaded` event had already fired and would never trigger again.

## Solution

### 1. Fixed HTMX Trigger (base.html)
Changed the trigger from `hx-trigger="intersect once"` to `hx-trigger="load"` to match all other tabs:

```html
<!-- Before -->
<div id="plugins-content" hx-get="/v3/partials/plugins" hx-trigger="intersect once" hx-swap="innerHTML">

<!-- After -->
<div id="plugins-content" hx-get="/v3/partials/plugins" hx-trigger="load" hx-swap="innerHTML">
```

This ensures the content loads when the page loads, regardless of whether the tab is visible.

### 2. Fixed Initialization Code (partials/plugins.html)
- Changed event listener from `htmx:afterSettle` to `htmx:afterSwap` for faster initialization
- Added check for document ready state to initialize immediately if DOM is already loaded

```javascript
// Before
document.addEventListener('DOMContentLoaded', initPluginsPage);
document.addEventListener('htmx:afterSettle', function(event) {
    if (event.target.id === 'plugins-content') {
        initPluginsPage();
    }
});

// After
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initPluginsPage);
} else {
    // DOM is already ready, initialize now
    initPluginsPage();
}

document.addEventListener('htmx:afterSwap', function(event) {
    if (event.target.id === 'plugins-content') {
        console.log('HTMX afterSwap event detected for plugins-content, initializing...');
        initPluginsPage();
    }
});
```

## Testing
To test the fix:
1. Navigate to the web interface
2. Click on the "Plugin Manager" tab
3. The tab should now load and display:
   - Installed plugins section with all installed plugins
   - Plugin store section with available plugins from the registry

## Files Modified
- `web_interface/templates/v3/base.html` - Fixed HTMX trigger
- `web_interface/templates/v3/partials/plugins.html` - Fixed initialization code

## Additional Notes
This issue was specific to the plugins tab because it was the only tab using `intersect once` as the trigger. All other tabs were correctly using `hx-trigger="load"`.

