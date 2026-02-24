import { MetadataRoute } from "next";
import * as fs from "fs";
import * as path from "path";

const baseUrl = "https://aiserviceco.com";

// Recursively find all page.tsx files
function getPages(dir: string, pages: string[] = []) {
    const files = fs.readdirSync(dir);

    for (const file of files) {
        const fullPath = path.join(dir, file);
        if (fs.statSync(fullPath).isDirectory()) {
            getPages(fullPath, pages);
        } else if (file === "page.tsx") {
            pages.push(fullPath);
        }
    }
    return pages;
}

export default function sitemap(): MetadataRoute.Sitemap {
    const appDir = path.join(process.cwd(), "src", "app");

    try {
        const pagePaths = getPages(appDir);

        // Filter and format the routes
        const routes = pagePaths
            .map((p) => {
                // Convert OS path to URL path
                let relPath = path.relative(appDir, p).replace(/\\/g, "/");
                // Remove page.tsx
                relPath = relPath.replace(/\/page\.tsx$/, "").replace(/^page\.tsx$/, "");

                // Skip API routes, components, layout files, and specific non-public sections
                if (
                    relPath.startsWith("api/") ||
                    relPath.startsWith("components/") ||
                    relPath.includes("[") || // Skip raw dynamic routes if any
                    ["bids", "intents", "monitor", "campaigns", "dashboard", "inbox", "social", "voice", "lakeland"].some(prefix => relPath === prefix || relPath.startsWith(prefix + "/"))
                ) {
                    return null;
                }

                return relPath ? `/${relPath}` : "";
            })
            .filter((route): route is string => route !== null);

        // Create sitemap entries
        const sitemapEntries = routes.map((route) => ({
            url: `${baseUrl}${route}`,
            lastModified: new Date().toISOString(),
            changeFrequency: "weekly" as const,
            priority: route === "" ? 1.0 : 0.8,
        }));

        // Add any manual edge cases
        return sitemapEntries;

    } catch (error) {
        console.error("Error generating sitemap:", error);
        // Fallback safe minimum
        return [
            {
                url: baseUrl,
                lastModified: new Date().toISOString(),
                changeFrequency: "weekly",
                priority: 1,
            }
        ];
    }
}
