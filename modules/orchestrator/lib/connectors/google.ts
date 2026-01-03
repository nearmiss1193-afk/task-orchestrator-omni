
import { BaseConnector } from './base';
import axios from 'axios';

export class GoogleConnector extends BaseConnector {
    name = 'GoogleMaps';

    async execute(action: string, params: any): Promise<any> {
        this.log(`Executing ${action} with params: ${JSON.stringify(params)}`);

        if (action === 'search_leads') {
            const apiKey = process.env.GOOGLE_API_KEY;
            if (!apiKey) {
                this.log("No GOOGLE_API_KEY found. Using Mock Data.");
                return [
                    { name: "Mock Plumber A", phone: "555-0100", email: "mock@plumber.com", source: "Mock" },
                    { name: "Mock Plumber B", phone: "555-0101", email: "mock@plumber.com", source: "Mock" }
                ];
            }

            try {
                // 1. Search for Places (New API)
                const query = params.query || "plumbers in florida";
                this.log(`Searching Google Places (New API) for: ${query}`);

                const searchUrl = `https://places.googleapis.com/v1/places:searchText`;

                const searchRes = await axios.post(searchUrl, {
                    textQuery: query
                }, {
                    headers: {
                        'Content-Type': 'application/json',
                        'X-Goog-Api-Key': apiKey,
                        'X-Goog-FieldMask': 'places.displayName,places.formattedAddress,places.rating,places.websiteUri,places.nationalPhoneNumber'
                    }
                });

                if (!searchRes.data.places) {
                    this.log("No places found.");
                    return [];
                }

                const results = searchRes.data.places.slice(0, 5); // Take top 5

                // 2. Map Results
                const leads = results.map((place: any) => {
                    let lead = {
                        name: place.displayName?.text || "Unknown",
                        address: place.formattedAddress || "",
                        rating: place.rating || 0,
                        source: "Google Places V1",
                        phone: place.nationalPhoneNumber || null,
                        website: place.websiteUri || null,
                        email: null as string | null
                    };

                    // 3. Email Heuristic
                    if (lead.website) {
                        try {
                            const domain = new URL(lead.website).hostname.replace('www.', '');
                            lead.email = `info@${domain}`;
                        } catch (e) { lead.email = `contact@${lead.name.replace(/\s+/g, '').toLowerCase()}.com`; }
                    } else {
                        lead.email = `contact@${lead.name.replace(/\s+/g, '').toLowerCase()}.com`;
                    }

                    return lead;
                });

                this.log(`Found ${leads.length} leads.`);
                return leads;

            } catch (error: any) {
                this.log(`Google Search Failed: ${error.message} - ${JSON.stringify(error.response?.data || {})}`);

                // Fallback for 403/Forbidden (Invalid Key)
                if (error.response?.status === 403) {
                    this.log("Google API returned 403 (Forbidden). Using fallback mock data.");
                    return [
                        { name: "Mock Plumber A (Fallback)", phone: "555-0100", email: "mock1@plumber.com", source: "Mock Fallback" },
                        { name: "Mock Plumber B (Fallback)", phone: "555-0101", email: "mock2@plumber.com", source: "Mock Fallback" }
                    ];
                }
                throw error;
            }
        }
        throw new Error(`Unknown action: ${action}`);
    }
}
