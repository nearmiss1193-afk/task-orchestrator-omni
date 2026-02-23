/**
 * TypeScript type definitions for Sovereign Empire Dashboard API
 * Matches the actual API response structure from /api/dashboard-stats
 */

export type ScraperHealthStatus = 'healthy' | 'degraded' | 'critical';

export interface Overview {
    total_businesses: number;
    total_leads_in_pipeline: {
        with_owner: number;
        without_owner: number;
        enrichment_coverage_pct: number;
    };
    total_vibe_summaries_generated: number;
    vibe_coverage_pct: number;
}

export interface DataQuality {
    businesses_with_email: number;
    businesses_with_website: number;
    businesses_with_owner_name: number;
}

export interface RecentError {
    id: number;
    source: string;
    error_type: string;
    error_message: string | null;
    severity: string;
    resolved: boolean;
    created_at: string;
}

export interface ScraperHealth {
    health_score: number;
    status: ScraperHealthStatus;
    unresolved_errors: number;
    recent_errors: RecentError[];
}

export interface DashboardData {
    overview: Overview;
    data_quality: DataQuality;
    scraper_health: ScraperHealth;
    timestamp: string;
}

export interface RevenueForecast {
    pipeline_size: number;
    velocity_7d: {
        opens: number;
        replies: number;
    };
    forecast: {
        predicted_weekly_bookings: number;
        pipeline_health_score: number;
        sustainability: string;
    };
}
