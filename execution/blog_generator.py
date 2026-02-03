"""
Blog Generator - AI-Powered Blog Creation & Deployment
========================================================

Generates SEO-optimized blog posts with embedded videos and AI content.
Deploys to GHL, WordPress, or other CMS platforms.

Part of the Content Engine & Social Command Center.
"""

import os
import json
import re
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List, Any

# Try to import Gemini
try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False

# Self-annealing integration
try:
    from annealing_engine import self_annealing, log_annealing_event
    ANNEALING_ENABLED = True
except ImportError:
    ANNEALING_ENABLED = False
    def self_annealing(func):
        return func

# Configuration
CONTENT_LIBRARY_DIR = Path(__file__).parent.parent / "content_library"
BLOGS_DIR = CONTENT_LIBRARY_DIR / "blogs"

# Blog templates
BLOG_TEMPLATES = {
    "ai_tips": {
        "tone": "helpful and conversational",
        "sections": ["intro", "main_points", "actionable_tips", "conclusion"],
        "target_words": 800
    },
    "industry_update": {
        "tone": "professional and informative",
        "sections": ["summary", "analysis", "implications", "next_steps"],
        "target_words": 1000
    },
    "case_study": {
        "tone": "storytelling with data",
        "sections": ["challenge", "solution", "results", "takeaways"],
        "target_words": 1200
    },
    "how_to": {
        "tone": "clear and instructional",
        "sections": ["overview", "step_by_step", "tips", "summary"],
        "target_words": 900
    }
}


class BlogGenerator:
    """
    AI-powered blog content generator with video embedding.
    """
    
    def __init__(self, gemini_key: Optional[str] = None):
        """
        Initialize Blog Generator.
        
        Args:
            gemini_key: Google Gemini API key
        """
        self.gemini_key = gemini_key or os.getenv("GOOGLE_API_KEY")
        
        if self.gemini_key and GENAI_AVAILABLE:
            genai.configure(api_key=self.gemini_key)
            self.llm = genai.GenerativeModel("gemini-1.5-flash")
        else:
            self.llm = None
            print("[BLOG] Warning: Gemini not configured - limited functionality")
        
        BLOGS_DIR.mkdir(parents=True, exist_ok=True)
        self.generated_blogs = []
    
    @self_annealing
    def generate_blog(
        self,
        topic: str,
        template: str = "ai_tips",
        keywords: Optional[List[str]] = None,
        video_url: Optional[str] = None,
        target_audience: str = "small business owners",
        cta_link: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a complete blog post.
        
        Args:
            topic: Blog topic/title
            template: Blog template type
            keywords: SEO keywords to include
            video_url: Video to embed in blog
            target_audience: Who the blog is for
            cta_link: Call-to-action link
        
        Returns:
            Generated blog with metadata
        """
        if not self.llm:
            return {"success": False, "error": "Gemini not configured"}
        
        template_config = BLOG_TEMPLATES.get(template, BLOG_TEMPLATES["ai_tips"])
        keywords_str = ", ".join(keywords) if keywords else "AI, automation, business"
        
        prompt = f"""Write a blog post about: {topic}

Target audience: {target_audience}
Tone: {template_config['tone']}
Target length: {template_config['target_words']} words
Keywords to include naturally: {keywords_str}

Structure the post with these sections: {', '.join(template_config['sections'])}

Requirements:
- Write in a conversational, engaging style
- Include practical, actionable advice
- Use subheadings for each section
- Include 2-3 bullet point lists where appropriate
- End with a clear call-to-action
- Do NOT use phrases like "delve", "tapestry", "landscape", or other AI-isms

Output format:
---
title: [Catchy SEO-optimized title]
meta_description: [155 character meta description]
slug: [url-friendly-slug]
---

[Blog content in Markdown format]
"""
        
        try:
            response = self.llm.generate_content(prompt)
            content = response.text.strip()
            
            # Parse frontmatter
            metadata = self._parse_frontmatter(content)
            body = self._extract_body(content)
            
            # Embed video if provided
            if video_url:
                body = self._embed_video(body, video_url)
            
            # Add CTA if provided
            if cta_link:
                body = self._add_cta(body, cta_link)
            
            # Generate slug if not in response
            slug = metadata.get("slug") or self._generate_slug(topic)
            
            blog = {
                "id": f"blog_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "title": metadata.get("title", topic),
                "meta_description": metadata.get("meta_description", ""),
                "slug": slug,
                "body": body,
                "template": template,
                "keywords": keywords or [],
                "video_url": video_url,
                "cta_link": cta_link,
                "target_audience": target_audience,
                "word_count": len(body.split()),
                "created_at": datetime.now().isoformat(),
                "status": "draft"
            }
            
            # Save to file
            blog_path = BLOGS_DIR / f"{slug}.json"
            with open(blog_path, "w") as f:
                json.dump(blog, f, indent=2)
            
            # Save markdown version
            md_path = BLOGS_DIR / f"{slug}.md"
            with open(md_path, "w") as f:
                f.write(f"# {blog['title']}\n\n{body}")
            
            self.generated_blogs.append(blog)
            
            print(f"[BLOG] ✅ Generated: {blog['title']}")
            print(f"[BLOG] Word count: {blog['word_count']}")
            
            return {
                "success": True,
                "blog": blog,
                "markdown_path": str(md_path),
                "json_path": str(blog_path)
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _parse_frontmatter(self, content: str) -> Dict[str, str]:
        """Extract YAML frontmatter from content."""
        metadata = {}
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                fm = parts[1].strip()
                for line in fm.split("\n"):
                    if ":" in line:
                        key, value = line.split(":", 1)
                        metadata[key.strip()] = value.strip().strip('"\'')
        return metadata
    
    def _extract_body(self, content: str) -> str:
        """Extract body content after frontmatter."""
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                return parts[2].strip()
        return content
    
    def _generate_slug(self, title: str) -> str:
        """Generate URL-friendly slug from title."""
        slug = title.lower()
        slug = re.sub(r'[^a-z0-9\s-]', '', slug)
        slug = re.sub(r'[\s_]+', '-', slug)
        slug = re.sub(r'-+', '-', slug)
        return slug[:60].strip('-')
    
    def _embed_video(self, body: str, video_url: str) -> str:
        """Embed video in appropriate location in blog."""
        # Find first heading after intro
        lines = body.split('\n')
        insert_idx = 0
        heading_count = 0
        
        for i, line in enumerate(lines):
            if line.startswith('#'):
                heading_count += 1
                if heading_count == 2:  # After first section heading
                    insert_idx = i
                    break
        
        video_embed = f"\n\n<video src=\"{video_url}\" controls width=\"100%\"></video>\n\n"
        
        if insert_idx > 0:
            lines.insert(insert_idx, video_embed)
        else:
            lines.append(video_embed)
        
        return '\n'.join(lines)
    
    def _add_cta(self, body: str, cta_link: str) -> str:
        """Add call-to-action at the end."""
        cta = f"""

---

## Ready to Get Started?

[**Schedule a Free Strategy Session →**]({cta_link})

Let us show you how AI can transform your business operations.
"""
        return body + cta
    
    @self_annealing
    def generate_series(
        self,
        theme: str,
        num_posts: int = 4,
        keywords: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Generate a series of related blog posts.
        
        Args:
            theme: Overall theme for the series
            num_posts: Number of posts to generate
            keywords: Shared keywords
        
        Returns:
            Series metadata and all posts
        """
        if not self.llm:
            return {"success": False, "error": "Gemini not configured"}
        
        # First, generate topic ideas
        topic_prompt = f"""Generate {num_posts} blog post topics for a series about: {theme}

Target audience: Small business owners interested in AI and automation
Each topic should be specific and actionable.

Return as a numbered list with just the titles, no explanations."""
        
        try:
            response = self.llm.generate_content(topic_prompt)
            topics = [line.strip().lstrip("0123456789.)-") for line in response.text.strip().split("\n") if line.strip()]
            topics = topics[:num_posts]
            
            series = {
                "id": f"series_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "theme": theme,
                "posts": []
            }
            
            templates = list(BLOG_TEMPLATES.keys())
            
            for i, topic in enumerate(topics):
                template = templates[i % len(templates)]
                result = self.generate_blog(
                    topic=topic,
                    template=template,
                    keywords=keywords
                )
                if result.get("success"):
                    series["posts"].append(result["blog"])
            
            return {
                "success": True,
                "series": series,
                "post_count": len(series["posts"])
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def deploy_to_ghl(
        self,
        blog_id: str,
        location_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Deploy blog to GHL (placeholder for GHL blog API).
        
        Args:
            blog_id: Blog ID to deploy
            location_id: GHL location ID
        
        Returns:
            Deployment status
        """
        # Load blog
        blog = self._load_blog(blog_id)
        if not blog:
            return {"success": False, "error": "Blog not found"}
        
        # GHL blog deployment would go here
        # For now, mark as ready for deployment
        blog["status"] = "ready_for_deployment"
        blog["deployment_platform"] = "ghl"
        
        # Save updated status
        blog_path = BLOGS_DIR / f"{blog['slug']}.json"
        with open(blog_path, "w") as f:
            json.dump(blog, f, indent=2)
        
        return {
            "success": True,
            "message": "Blog marked ready for GHL deployment",
            "blog_id": blog_id,
            "title": blog["title"]
        }
    
    def _load_blog(self, blog_id: str) -> Optional[Dict]:
        """Load blog by ID."""
        for blog_file in BLOGS_DIR.glob("*.json"):
            with open(blog_file, "r") as f:
                blog = json.load(f)
                if blog.get("id") == blog_id:
                    return blog
        return None
    
    def list_blogs(self, status: Optional[str] = None) -> List[Dict]:
        """List all generated blogs."""
        blogs = []
        for blog_file in BLOGS_DIR.glob("*.json"):
            with open(blog_file, "r") as f:
                blog = json.load(f)
                if status is None or blog.get("status") == status:
                    blogs.append(blog)
        return blogs


# Convenience functions
def quick_blog(topic: str, video_url: Optional[str] = None) -> Dict[str, Any]:
    """Generate a quick AI tips blog."""
    generator = BlogGenerator()
    return generator.generate_blog(
        topic=topic,
        template="ai_tips",
        video_url=video_url,
        keywords=["AI", "automation", "business growth"]
    )


if __name__ == "__main__":
    print("[BLOG] Blog Generator - AI Content Creation")
    print("=" * 50)
    
    api_key = os.getenv("GOOGLE_API_KEY")
    if api_key:
        print(f"[BLOG] Gemini: Configured")
    else:
        print("[BLOG] ⚠️ GOOGLE_API_KEY not set")
    
    print(f"[BLOG] Blogs directory: {BLOGS_DIR}")
    print()
    print("[BLOG] Available templates:")
    for name, config in BLOG_TEMPLATES.items():
        print(f"  - {name}: {config['target_words']} words, {config['tone']}")
    
    # List existing blogs
    generator = BlogGenerator()
    blogs = generator.list_blogs()
    print(f"\n[BLOG] Existing blogs: {len(blogs)}")
