import { EmailConnector } from '../lib/connectors/email';

try {
    const connector = new EmailConnector();
    console.log("✅ EmailConnector loaded successfully. Syntax is valid.");
} catch (e) {
    console.error("❌ Failed to load EmailConnector:", e);
    process.exit(1);
}
