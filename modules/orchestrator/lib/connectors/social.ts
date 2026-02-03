import axios from 'axios';

export interface SocialComment {
    id: string;
    platform: 'linkedin' | 'twitter' | 'instagram' | 'facebook';
    user: string;
    text: string;
    timestamp: string;
    replied: boolean;
    postUrl?: string;
}

export class SocialConnector {
    private apiKey: string;
    private baseUrl = 'https://app.ayrshare.com/api';

    constructor() {
        this.apiKey = process.env.AYRSHARE_API_KEY || '';
        if (!this.apiKey) {
            console.warn("⚠️ [Social] AYRSHARE_API_KEY is missing. Connector will fail.");
        }
    }

    private get headers() {
        return {
            'Authorization': `Bearer ${this.apiKey}`,
            'Content-Type': 'application/json'
        };
    }

    /**
     * Fetches recent comments via Ayrshare API.
     */
    async fetchRecentComments(): Promise<SocialComment[]> {
        console.log("📡 [Social] Scanning engagement via Ayrshare...");

        if (!this.apiKey) return [];

        try {
            // Hitting the /comments endpoint to get latest interactions
            const response = await axios.get(`${this.baseUrl}/comments`, {
                headers: this.headers
            });

            const comments: SocialComment[] = [];

            // Ayrshare returns generic comment objects, we normalize them
            // Note: Structure depends on Ayrshare's exact response which can vary by platform
            if (response.data && Array.isArray(response.data)) {
                for (const c of response.data) {
                    comments.push({
                        id: c.id || c.commentId,
                        platform: c.platform,
                        user: c.senderName || c.username || 'Unknown',
                        text: c.comment || c.text,
                        timestamp: c.created || new Date().toISOString(),
                        replied: false, // We'd need to track this state locally or check sub-replies
                        postUrl: c.postUrl
                    });
                }
            }

            return comments;

        } catch (error: any) {
            console.error("❌ [Social] Failed to fetch comments:", error.response?.data || error.message);
            return [];
        }
    }

    /**
     * Posts a generic update across platforms.
     */
    async postStatus(text: string, platforms: string[] = ['linkedin', 'twitter']): Promise<any> {
        console.log(`📣 [Social] Broadcasting to ${platforms.join(',')}: "${text}"`);

        try {
            const response = await axios.post(`${this.baseUrl}/post`, {
                post: text,
                platforms: platforms
            }, { headers: this.headers });

            return response.data;
        } catch (error: any) {
            console.error("❌ [Social] Post failed:", error.response?.data || error.message);
            throw error;
        }
    }

    /**
     * Posts a reply to a specific comment.
     * Note: Ayrshare /comments/reply requires a commentId.
     */
    async postReply(commentId: string, text: string, platform: string): Promise<boolean> {
        console.log(`💬 [Social] Replying to ${commentId} on ${platform}: "${text}"`);

        try {
            await axios.post(`${this.baseUrl}/comments/reply`, {
                commentId: commentId,
                platform: platform,
                comment: text
            }, { headers: this.headers });

            return true;
        } catch (error: any) {
            console.error("❌ [Social] Reply failed:", error.response?.data || error.message);
            return false;
        }
    }
}
