"""
Main entry point for Railway deployment
Starts the webhook handler (always-on service)
"""
import os
from webhook_handler import app

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    print(f"🚂 Railway Prospecting Engine starting on port {port}")
    print(f"📧 Webhook handler: http://0.0.0.0:{port}/ghl/webhook")
    print(f"💊 Health check: http://0.0.0.0:{port}/health")
    app.run(host="0.0.0.0", port=port, debug=False)
