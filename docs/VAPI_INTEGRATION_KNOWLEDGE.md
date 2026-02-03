# Empire Knowledge Base: Vapi Voice Integration

## Working Pattern for Voice Call Widget

The Vapi HTML Script Tag SDK creates a floating pill-shaped call button. Here's the authoritative working pattern:

### Script Loading

```html
<script src="https://cdn.jsdelivr.net/gh/VapiAI/html-script-tag@latest/dist/assets/index.js"></script>
```

### Auto-Init Pattern (Verified Working)

```javascript
(function () {
    var script = document.createElement('script');
    script.src = "https://cdn.jsdelivr.net/gh/VapiAI/html-script-tag@latest/dist/assets/index.js";
    script.defer = true;
    script.async = true;
    script.onload = function () {
        if (window.vapiSDK && !window.vapiWidgetInitialized) {
            window.vapiWidgetInitialized = true;
            vapiInstance = window.vapiSDK.run({
                apiKey: VAPI_PUBLIC_KEY,
                assistant: ASSISTANT_ID,
                config: {
                    position: "bottom-right",
                    idle: { color: "#2563eb", type: "pill", title: "Voice Uplink" },
                    loading: { color: "#94a3b8", type: "pill", title: "Connecting..." },
                    active: { color: "#22c55e", type: "pill", title: "Live Call" }
                }
            });
        }
    };
    document.head.appendChild(script);
})();
```

### Key Configuration

| Key | Value | Use For |
|-----|-------|---------|
| VAPI_PUBLIC_KEY | `3b065ff0-a721-4b66-8255-30b6b8d6daab` | All Vapi calls |
| ORCHESTRATOR_ASSISTANT_ID | `a3e439a2-4560-4625-99c8-222678bf130d` | Voice Board / Executive Bridge |
| SARAH_ASSISTANT_ID | `1a797f12-e2dd-4f7f-b2c5-08c38c74859a` | Customer campaigns / Sales |
| EMPIRE_SALES_ID | `d19cae13-d11b-499b-a9e7-2e113efe1112` | Landing pages |

## Voice Assistant Roles

| Assistant | ID | Role |
|-----------|-----|------|
| **Antigravity (Orchestrator)** | `a3e439a2...` | Executive Terminal - talking to YOU on Voice Board |
| **Sarah 3.0 (Grok)** | `1a797f12...` | Sales AI - answers calls, campaigns, prospects |
| **Empire Sales Specialist** | `d19cae13...` | Generic sales calls from landing pages |

## Common Issues & Fixes

| Issue | Solution |
|-------|----------|
| Widget not appearing | Use auto-init pattern, not manual button |
| "Vapi is not defined" | Wait for script to load with `onload` callback |
| SDK not loaded error | Check for `window.vapiSDK` before calling |

## Files Using This Pattern

- `public/hvac.html` - Auto-init ✅
- `public/dashboard.html` - Auto-init ✅ (fixed 2026-01-06)
- Other landing pages use same pattern
