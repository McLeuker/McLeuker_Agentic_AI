"""
McLeuker AI V8 - Expanded Data Tools
=====================================
Integration with Pinterest, YouTube, X/Twitter (via Grok-4), and other data sources.
Provides parallel research capabilities for comprehensive data insights.
"""

import os
import json
import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger(__name__)


# API Keys from environment
PINTEREST_API_KEY = os.getenv("PINTEREST_API_KEY", "")
PINTEREST_SECRET_KEY = os.getenv("PINTEREST_SECRET_KEY", "")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_DATA_API_V3", "")
GROK_API_KEY = os.getenv("GROK_API_KEY", "") or os.getenv("XAI_API_KEY", "")
EXA_API_KEY = os.getenv("EXA_API_KEY", "")


class DataSource(Enum):
    """Available data sources"""
    PINTEREST = "pinterest"
    YOUTUBE = "youtube"
    X_TWITTER = "x_twitter"
    WEB_SEARCH = "web_search"
    NEWS = "news"


@dataclass
class DataResult:
    """Result from a data source"""
    source: DataSource
    query: str
    results: List[Dict]
    metadata: Dict = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    success: bool = True
    error: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            "source": self.source.value,
            "query": self.query,
            "results": self.results,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat(),
            "success": self.success,
            "error": self.error
        }


class PinterestTool:
    """
    Pinterest API integration for visual trend research.
    Provides access to pins, boards, and visual search.
    """
    
    def __init__(self):
        self.api_key = PINTEREST_API_KEY
        self.secret_key = PINTEREST_SECRET_KEY
        self.base_url = "https://api.pinterest.com/v5"
        self.access_token = None
    
    async def search_pins(self, query: str, limit: int = 25) -> DataResult:
        """Search for pins related to a query"""
        try:
            if not self.api_key:
                return DataResult(
                    source=DataSource.PINTEREST,
                    query=query,
                    results=[],
                    success=False,
                    error="Pinterest API key not configured"
                )
            
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                
                params = {
                    "query": query,
                    "page_size": limit
                }
                
                async with session.get(
                    f"{self.base_url}/search/pins",
                    headers=headers,
                    params=params
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        pins = data.get("items", [])
                        
                        results = []
                        for pin in pins:
                            results.append({
                                "id": pin.get("id"),
                                "title": pin.get("title", ""),
                                "description": pin.get("description", ""),
                                "image_url": pin.get("media", {}).get("images", {}).get("600x", {}).get("url"),
                                "link": pin.get("link"),
                                "board_name": pin.get("board_id"),
                                "created_at": pin.get("created_at"),
                                "save_count": pin.get("pin_metrics", {}).get("save", 0),
                                "type": "pin"
                            })
                        
                        return DataResult(
                            source=DataSource.PINTEREST,
                            query=query,
                            results=results,
                            metadata={"total": len(results), "bookmark": data.get("bookmark")}
                        )
                    else:
                        error_text = await response.text()
                        return DataResult(
                            source=DataSource.PINTEREST,
                            query=query,
                            results=[],
                            success=False,
                            error=f"API error: {response.status} - {error_text}"
                        )
        except Exception as e:
            logger.error(f"Pinterest search error: {e}")
            return DataResult(
                source=DataSource.PINTEREST,
                query=query,
                results=[],
                success=False,
                error=str(e)
            )
    
    async def get_trending_pins(self, category: str = "fashion") -> DataResult:
        """Get trending pins in a category"""
        # Pinterest doesn't have a direct trending endpoint, so we search popular terms
        trending_queries = {
            "fashion": "fashion trends 2026",
            "beauty": "beauty trends makeup",
            "home": "home decor ideas",
            "food": "recipe ideas trending"
        }
        
        query = trending_queries.get(category, f"{category} trending")
        return await self.search_pins(query, limit=30)
    
    async def analyze_visual_trends(self, query: str) -> Dict:
        """Analyze visual trends from Pinterest data"""
        result = await self.search_pins(query, limit=50)
        
        if not result.success:
            return {"error": result.error}
        
        # Analyze the results
        analysis = {
            "query": query,
            "total_pins": len(result.results),
            "top_pins": result.results[:5],
            "engagement_metrics": {
                "avg_saves": sum(p.get("save_count", 0) for p in result.results) / max(len(result.results), 1)
            },
            "insights": []
        }
        
        # Extract common themes from descriptions
        all_descriptions = " ".join(p.get("description", "") for p in result.results)
        words = all_descriptions.lower().split()
        word_freq = {}
        for word in words:
            if len(word) > 4:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        top_themes = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
        analysis["top_themes"] = [{"theme": t[0], "frequency": t[1]} for t in top_themes]
        
        return analysis


class YouTubeTool:
    """
    YouTube Data API integration for video research.
    Provides access to videos, channels, and trending content.
    """
    
    def __init__(self):
        self.api_key = YOUTUBE_API_KEY
        self.base_url = "https://www.googleapis.com/youtube/v3"
    
    async def search_videos(self, query: str, limit: int = 25, order: str = "relevance") -> DataResult:
        """Search for videos related to a query"""
        try:
            if not self.api_key:
                return DataResult(
                    source=DataSource.YOUTUBE,
                    query=query,
                    results=[],
                    success=False,
                    error="YouTube API key not configured"
                )
            
            async with aiohttp.ClientSession() as session:
                params = {
                    "part": "snippet",
                    "q": query,
                    "type": "video",
                    "maxResults": limit,
                    "order": order,
                    "key": self.api_key
                }
                
                async with session.get(
                    f"{self.base_url}/search",
                    params=params
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        items = data.get("items", [])
                        
                        # Get video statistics
                        video_ids = [item["id"]["videoId"] for item in items if "videoId" in item.get("id", {})]
                        stats = await self._get_video_stats(video_ids) if video_ids else {}
                        
                        results = []
                        for item in items:
                            video_id = item.get("id", {}).get("videoId")
                            snippet = item.get("snippet", {})
                            video_stats = stats.get(video_id, {})
                            
                            results.append({
                                "id": video_id,
                                "title": snippet.get("title", ""),
                                "description": snippet.get("description", ""),
                                "channel_title": snippet.get("channelTitle", ""),
                                "channel_id": snippet.get("channelId"),
                                "thumbnail_url": snippet.get("thumbnails", {}).get("high", {}).get("url"),
                                "published_at": snippet.get("publishedAt"),
                                "view_count": video_stats.get("viewCount", 0),
                                "like_count": video_stats.get("likeCount", 0),
                                "comment_count": video_stats.get("commentCount", 0),
                                "url": f"https://www.youtube.com/watch?v={video_id}",
                                "type": "video"
                            })
                        
                        return DataResult(
                            source=DataSource.YOUTUBE,
                            query=query,
                            results=results,
                            metadata={
                                "total": len(results),
                                "next_page_token": data.get("nextPageToken")
                            }
                        )
                    else:
                        error_text = await response.text()
                        return DataResult(
                            source=DataSource.YOUTUBE,
                            query=query,
                            results=[],
                            success=False,
                            error=f"API error: {response.status} - {error_text}"
                        )
        except Exception as e:
            logger.error(f"YouTube search error: {e}")
            return DataResult(
                source=DataSource.YOUTUBE,
                query=query,
                results=[],
                success=False,
                error=str(e)
            )
    
    async def _get_video_stats(self, video_ids: List[str]) -> Dict[str, Dict]:
        """Get statistics for multiple videos"""
        if not video_ids or not self.api_key:
            return {}
        
        try:
            async with aiohttp.ClientSession() as session:
                params = {
                    "part": "statistics",
                    "id": ",".join(video_ids),
                    "key": self.api_key
                }
                
                async with session.get(
                    f"{self.base_url}/videos",
                    params=params
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        stats = {}
                        for item in data.get("items", []):
                            stats[item["id"]] = item.get("statistics", {})
                        return stats
        except Exception as e:
            logger.error(f"Error getting video stats: {e}")
        
        return {}
    
    async def get_trending_videos(self, category_id: str = "0", region: str = "US") -> DataResult:
        """Get trending videos"""
        try:
            if not self.api_key:
                return DataResult(
                    source=DataSource.YOUTUBE,
                    query="trending",
                    results=[],
                    success=False,
                    error="YouTube API key not configured"
                )
            
            async with aiohttp.ClientSession() as session:
                params = {
                    "part": "snippet,statistics",
                    "chart": "mostPopular",
                    "regionCode": region,
                    "maxResults": 25,
                    "key": self.api_key
                }
                
                if category_id != "0":
                    params["videoCategoryId"] = category_id
                
                async with session.get(
                    f"{self.base_url}/videos",
                    params=params
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        items = data.get("items", [])
                        
                        results = []
                        for item in items:
                            snippet = item.get("snippet", {})
                            stats = item.get("statistics", {})
                            
                            results.append({
                                "id": item.get("id"),
                                "title": snippet.get("title", ""),
                                "description": snippet.get("description", "")[:500],
                                "channel_title": snippet.get("channelTitle", ""),
                                "thumbnail_url": snippet.get("thumbnails", {}).get("high", {}).get("url"),
                                "published_at": snippet.get("publishedAt"),
                                "view_count": int(stats.get("viewCount", 0)),
                                "like_count": int(stats.get("likeCount", 0)),
                                "url": f"https://www.youtube.com/watch?v={item.get('id')}",
                                "type": "trending_video"
                            })
                        
                        return DataResult(
                            source=DataSource.YOUTUBE,
                            query="trending",
                            results=results,
                            metadata={"region": region, "category": category_id}
                        )
                    else:
                        error_text = await response.text()
                        return DataResult(
                            source=DataSource.YOUTUBE,
                            query="trending",
                            results=[],
                            success=False,
                            error=f"API error: {response.status}"
                        )
        except Exception as e:
            logger.error(f"YouTube trending error: {e}")
            return DataResult(
                source=DataSource.YOUTUBE,
                query="trending",
                results=[],
                success=False,
                error=str(e)
            )
    
    async def analyze_video_trends(self, query: str) -> Dict:
        """Analyze video trends for a topic"""
        result = await self.search_videos(query, limit=50, order="viewCount")
        
        if not result.success:
            return {"error": result.error}
        
        videos = result.results
        
        analysis = {
            "query": query,
            "total_videos": len(videos),
            "top_videos": videos[:5],
            "engagement_metrics": {
                "total_views": sum(int(v.get("view_count", 0)) for v in videos),
                "avg_views": sum(int(v.get("view_count", 0)) for v in videos) / max(len(videos), 1),
                "total_likes": sum(int(v.get("like_count", 0)) for v in videos),
                "avg_likes": sum(int(v.get("like_count", 0)) for v in videos) / max(len(videos), 1)
            },
            "top_channels": [],
            "insights": []
        }
        
        # Find top channels
        channel_views = {}
        for video in videos:
            channel = video.get("channel_title", "Unknown")
            channel_views[channel] = channel_views.get(channel, 0) + int(video.get("view_count", 0))
        
        top_channels = sorted(channel_views.items(), key=lambda x: x[1], reverse=True)[:5]
        analysis["top_channels"] = [{"channel": c[0], "total_views": c[1]} for c in top_channels]
        
        return analysis


class XTwitterTool:
    """
    X/Twitter data access via Grok-4 model.
    Grok has real-time access to X platform data.
    """
    
    def __init__(self):
        self.api_key = GROK_API_KEY
        self.base_url = "https://api.x.ai/v1"
        self.model = "grok-4"
    
    async def search_x_data(self, query: str, context: str = "general") -> DataResult:
        """Search X/Twitter data using Grok-4's real-time access"""
        try:
            if not self.api_key:
                return DataResult(
                    source=DataSource.X_TWITTER,
                    query=query,
                    results=[],
                    success=False,
                    error="Grok API key not configured"
                )
            
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                
                # Use Grok to search X data
                prompt = f"""Search X (Twitter) for the most recent and relevant posts about: {query}

Context: {context}

Please provide:
1. Recent trending discussions and posts
2. Key influencers and accounts discussing this topic
3. Popular hashtags being used
4. Sentiment analysis of the conversation
5. Notable quotes or insights from posts

Format your response as structured data with specific posts, usernames, engagement metrics where available, and key insights."""

                payload = {
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": "You are a research assistant with real-time access to X (Twitter) data. Provide accurate, current information from the platform."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.3,
                    "max_tokens": 2000
                }
                
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                        
                        # Parse the response into structured results
                        results = self._parse_x_response(content, query)
                        
                        return DataResult(
                            source=DataSource.X_TWITTER,
                            query=query,
                            results=results,
                            metadata={
                                "model": self.model,
                                "context": context,
                                "raw_response": content[:500]
                            }
                        )
                    else:
                        error_text = await response.text()
                        return DataResult(
                            source=DataSource.X_TWITTER,
                            query=query,
                            results=[],
                            success=False,
                            error=f"API error: {response.status} - {error_text}"
                        )
        except Exception as e:
            logger.error(f"X/Twitter search error: {e}")
            return DataResult(
                source=DataSource.X_TWITTER,
                query=query,
                results=[],
                success=False,
                error=str(e)
            )
    
    def _parse_x_response(self, content: str, query: str) -> List[Dict]:
        """Parse Grok's response into structured results"""
        results = [{
            "type": "x_analysis",
            "query": query,
            "content": content,
            "source": "grok-4",
            "timestamp": datetime.utcnow().isoformat()
        }]
        
        # Extract any mentioned usernames
        import re
        usernames = re.findall(r'@(\w+)', content)
        if usernames:
            results.append({
                "type": "mentioned_accounts",
                "accounts": list(set(usernames))[:20]
            })
        
        # Extract hashtags
        hashtags = re.findall(r'#(\w+)', content)
        if hashtags:
            results.append({
                "type": "hashtags",
                "tags": list(set(hashtags))[:20]
            })
        
        return results
    
    async def get_trending_topics(self, category: str = "all") -> DataResult:
        """Get trending topics on X using Grok-4"""
        query = f"What are the current trending topics on X (Twitter) related to {category}? Include hashtags, key discussions, and viral content."
        return await self.search_x_data(query, context=f"trending_{category}")
    
    async def analyze_sentiment(self, topic: str) -> Dict:
        """Analyze sentiment around a topic on X"""
        result = await self.search_x_data(
            f"Analyze the sentiment and public opinion on X about: {topic}",
            context="sentiment_analysis"
        )
        
        if not result.success:
            return {"error": result.error}
        
        return {
            "topic": topic,
            "analysis": result.results,
            "source": "x_twitter_via_grok4"
        }


class ParallelResearchEngine:
    """
    Parallel research engine that queries multiple data sources simultaneously.
    Aggregates and synthesizes results from Pinterest, YouTube, X, and web search.
    """
    
    def __init__(self):
        self.pinterest = PinterestTool()
        self.youtube = YouTubeTool()
        self.x_twitter = XTwitterTool()
    
    async def research(
        self,
        query: str,
        sources: List[DataSource] = None,
        context: str = "general"
    ) -> Dict[str, DataResult]:
        """
        Conduct parallel research across multiple data sources.
        """
        if sources is None:
            sources = [DataSource.PINTEREST, DataSource.YOUTUBE, DataSource.X_TWITTER]
        
        tasks = []
        source_names = []
        
        for source in sources:
            if source == DataSource.PINTEREST:
                tasks.append(self.pinterest.search_pins(query))
                source_names.append("pinterest")
            elif source == DataSource.YOUTUBE:
                tasks.append(self.youtube.search_videos(query))
                source_names.append("youtube")
            elif source == DataSource.X_TWITTER:
                tasks.append(self.x_twitter.search_x_data(query, context))
                source_names.append("x_twitter")
        
        # Execute all searches in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Organize results
        research_results = {}
        for name, result in zip(source_names, results):
            if isinstance(result, Exception):
                research_results[name] = DataResult(
                    source=DataSource(name),
                    query=query,
                    results=[],
                    success=False,
                    error=str(result)
                )
            else:
                research_results[name] = result
        
        return research_results
    
    async def comprehensive_analysis(self, topic: str) -> Dict:
        """
        Conduct comprehensive analysis of a topic across all platforms.
        """
        # Parallel research
        research_results = await self.research(topic)
        
        # Parallel trend analysis
        analysis_tasks = [
            self.pinterest.analyze_visual_trends(topic),
            self.youtube.analyze_video_trends(topic),
            self.x_twitter.analyze_sentiment(topic)
        ]
        
        analyses = await asyncio.gather(*analysis_tasks, return_exceptions=True)
        
        # Compile comprehensive report
        report = {
            "topic": topic,
            "timestamp": datetime.utcnow().isoformat(),
            "sources_queried": list(research_results.keys()),
            "raw_results": {k: v.to_dict() for k, v in research_results.items()},
            "analyses": {
                "pinterest_visual": analyses[0] if not isinstance(analyses[0], Exception) else {"error": str(analyses[0])},
                "youtube_video": analyses[1] if not isinstance(analyses[1], Exception) else {"error": str(analyses[1])},
                "x_sentiment": analyses[2] if not isinstance(analyses[2], Exception) else {"error": str(analyses[2])}
            },
            "summary": self._generate_summary(research_results, analyses)
        }
        
        return report
    
    def _generate_summary(self, results: Dict[str, DataResult], analyses: List) -> Dict:
        """Generate a summary of all research findings"""
        summary = {
            "total_results": sum(len(r.results) for r in results.values() if r.success),
            "successful_sources": [k for k, v in results.items() if v.success],
            "failed_sources": [k for k, v in results.items() if not v.success],
            "key_findings": []
        }
        
        # Extract key findings from each source
        for source, result in results.items():
            if result.success and result.results:
                if source == "pinterest":
                    top_pins = result.results[:3]
                    summary["key_findings"].append({
                        "source": "Pinterest",
                        "insight": f"Found {len(result.results)} visual results",
                        "top_content": [p.get("title", "Untitled") for p in top_pins]
                    })
                elif source == "youtube":
                    top_videos = result.results[:3]
                    summary["key_findings"].append({
                        "source": "YouTube",
                        "insight": f"Found {len(result.results)} video results",
                        "top_content": [v.get("title", "Untitled") for v in top_videos]
                    })
                elif source == "x_twitter":
                    summary["key_findings"].append({
                        "source": "X/Twitter",
                        "insight": "Real-time social analysis via Grok-4",
                        "content_preview": result.results[0].get("content", "")[:200] if result.results else ""
                    })
        
        return summary


# Global instances
pinterest_tool = PinterestTool()
youtube_tool = YouTubeTool()
x_twitter_tool = XTwitterTool()
research_engine = ParallelResearchEngine()


def get_research_engine() -> ParallelResearchEngine:
    """Get the global research engine"""
    return research_engine
