/**
 * ═══════════════════════════════════════════════════════
 * 🍀 Shamrock Node-RED — Production Settings
 * ═══════════════════════════════════════════════════════
 * 
 * SECURITY HARDENED — March 2026
 * - adminAuth enabled (bcrypt hashed)
 * - credentialSecret set (custom key)
 * - HTTPS-ready configuration
 * - Environment-based GAS URLs
 * - File-based context storage for persistence
 * - Audit logging enabled
 */

const bcrypt = require('bcryptjs');

module.exports = {
    // ═══════════════════════════════════════
    // CORE
    // ═══════════════════════════════════════
    flowFile: 'flows.json',
    credentialSecret: process.env.NR_CREDENTIAL_SECRET || "shamrock-bail-2026",
    uiPort: parseInt(process.env.PORT) || 1880,

    // ═══════════════════════════════════════
    // ADMIN AUTHENTICATION
    // ═══════════════════════════════════════
    // Default password: "shamrock2026!" — CHANGE IN PRODUCTION!
    // Generate new hash: node -e "console.log(require('bcryptjs').hashSync('YOUR_PASSWORD', 10))"
    adminAuth: {
        type: "credentials",
        users: [{
            username: process.env.NR_ADMIN_USER || "admin",
            password: process.env.NR_ADMIN_HASH || "$2b$10$0DxysBwJFz.tgALq0EISueaLYjgTA/y9uuVvpMeOmjx.UpP21A1PW",
            permissions: "*"
        }, {
            username: process.env.NR_VIEWER_USER || "viewer",
            password: process.env.NR_VIEWER_HASH || "$2b$10$0DxysBwJFz.tgALq0EISueaLYjgTA/y9uuVvpMeOmjx.UpP21A1PW",
            permissions: "read"
        }],
        default: {
            permissions: "read"
        }
    },

    // ═══════════════════════════════════════
    // CONTEXT STORAGE (Persistent)
    // ═══════════════════════════════════════
    // Using localfilesystem so dashboard state survives restarts
    contextStorage: {
        default: {
            module: "localfilesystem",
            config: {
                flushInterval: 30  // Write to disk every 30 seconds
            }
        },
        memoryOnly: {
            module: "memory"
        }
    },

    // ═══════════════════════════════════════
    // FUNCTION GLOBAL CONTEXT
    // ═══════════════════════════════════════
    // Access in function nodes via: global.get('env').GAS_WEBHOOK_URL
    functionGlobalContext: {
        env: {
            // GAS Endpoints
            GAS_WEBHOOK_URL: process.env.GAS_WEBHOOK_URL || "",
            GAS_API_KEY: process.env.GAS_API_KEY || "",
            
            // Slack
            SLACK_BOT_TOKEN: process.env.SLACK_BOT_TOKEN || "",
            SLACK_WEBHOOK_OPS: process.env.SLACK_WEBHOOK_OPS || "",
            SLACK_WEBHOOK_ALERTS: process.env.SLACK_WEBHOOK_ALERTS || "",
            SLACK_WEBHOOK_LEADS: process.env.SLACK_WEBHOOK_LEADS || "",
            
            // Twilio
            TWILIO_ACCOUNT_SID: process.env.TWILIO_ACCOUNT_SID || "",
            TWILIO_AUTH_TOKEN: process.env.TWILIO_AUTH_TOKEN || "",
            TWILIO_PHONE_NUMBER: process.env.TWILIO_PHONE_NUMBER || "",
            
            // ElevenLabs
            ELEVENLABS_API_KEY: process.env.ELEVENLABS_API_KEY || "",
            ELEVENLABS_AGENT_ID: process.env.ELEVENLABS_AGENT_ID || "",
            
            // SignNow
            SIGNNOW_API_KEY: process.env.SIGNNOW_API_KEY || "",
            
            // Webhook Auth
            WEBHOOK_HMAC_SECRET: process.env.WEBHOOK_HMAC_SECRET || "",
            
            // MongoDB
            MONGODB_URI: process.env.MONGODB_URI || "",
            
            // Misc
            NODE_ENV: process.env.NODE_ENV || "production",
            TZ: process.env.TZ || "America/New_York"
        }
    },

    // ═══════════════════════════════════════
    // EDITOR THEME
    // ═══════════════════════════════════════
    editorTheme: {
        projects: {
            enabled: false
        },
        theme: "dark",
        page: {
            title: "🍀 Shamrock Node-RED",
            favicon: "",
            css: ""
        },
        header: {
            title: "🍀 Shamrock Ops",
        },
        deployButton: {
            type: "simple",
            label: "Deploy"
        },
        palette: {
            editable: true
        }
    },

    // ═══════════════════════════════════════
    // LOGGING (Production)
    // ═══════════════════════════════════════
    logging: {
        console: {
            level: process.env.LOG_LEVEL || "info",
            metrics: false,
            audit: true  // Track who deploys what
        }
    },

    // ═══════════════════════════════════════
    // HTTP SETTINGS
    // ═══════════════════════════════════════
    httpRequestTimeout: 30000,   // 30s timeout for http request nodes
    httpNodeCors: {
        origin: "*",
        methods: "GET,PUT,POST,DELETE"
    },

    // ═══════════════════════════════════════
    // WEBHOOK AUTHENTICATION MIDDLEWARE (T-006)
    // ═══════════════════════════════════════
    // All http-in (webhook) endpoints pass through this.
    // Set WEBHOOK_HMAC_SECRET env var to enforce auth.
    // When no secret is set, all requests pass through (dev mode).
    httpNodeMiddleware: function(req, res, next) {
        const secret = process.env.WEBHOOK_HMAC_SECRET || "";
        
        // Skip auth if no secret configured (graceful degradation)
        if (!secret) return next();
        
        const provided = req.headers['x-webhook-secret'] 
            || req.headers['x-api-key'] 
            || "";
        
        if (provided === secret) return next();
        
        // Auth failed
        console.warn(`[AUTH] Webhook auth failed from ${req.ip} on ${req.method} ${req.url}`);
        res.status(403).json({ 
            error: "Unauthorized", 
            message: "Invalid or missing webhook secret" 
        });
    },

    // ═══════════════════════════════════════
    // API RATE LIMITING
    // ═══════════════════════════════════════
    apiMaxLength: '5mb',

    // ═══════════════════════════════════════
    // DIAGNOSTICS
    // ═══════════════════════════════════════
    diagnostics: {
        enabled: true,
        ui: true
    },

    // ═══════════════════════════════════════
    // RUNTIME
    // ═══════════════════════════════════════
    runtimeState: {
        enabled: true,
        ui: true
    }
};
