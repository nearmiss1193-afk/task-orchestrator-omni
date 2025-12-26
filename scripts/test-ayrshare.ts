
import { SocialConnector } from '../modules/orchestrator/lib/connectors/social';

async function main() {
    console.log("🧪 Testing Ayrshare Integration...");

    // Inject key directly for testing purposes (User provided)
    process.env.AYRSHARE_API_KEY = "57FCF9E6-1B534A66-9F05E51C-9ADE2CA5";

    const social = new SocialConnector();

    console.log("1. Fetching recent comments/history...");
    const comments = await social.fetchRecentComments();
    console.log(`   Found ${comments.length} comments.`);
    if (comments.length > 0) {
        console.log("   Latest:", comments[0]);
    }

    // Uncomment to test posting (Safety: Don't auto-post unless requested)
    // console.log("2. Posting test status...");
    // const postResult = await social.postStatus("Test message from Antigravity Agent - System Verification", ["twitter"]);
    // console.log("   Post Result:", postResult);
}

main().catch(console.error);
