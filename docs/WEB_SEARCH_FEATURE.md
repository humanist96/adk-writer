# Web Search Feature Documentation

## Overview
The Web Search Feature enhances document generation by automatically searching and incorporating relevant web content based on document titles. This feature enriches the generated documents with current market trends, statistics, and relevant information.

## Features

### 1. Multiple Search Providers
- **Fallback Provider** (Default): No API key required, uses DuckDuckGo
- **Google Search**: Requires Google Custom Search API key and Search Engine ID
- **Bing Search**: Requires Bing Search API key

### 2. Content Enrichment
- Automatic keyword extraction from document title and content
- Generation of relevant search queries based on document type
- Extraction of key facts and statistics from search results
- Intelligent content integration into document drafts

### 3. Configurable Search Options
- **Search Depth**: Quick (1-2 results), Standard (3-5 results), Deep (5-10 results)
- **Content Extraction**: Option to extract full page content for deeper analysis
- **Language & Region**: Optimized for Korean financial content

## How to Use

### 1. Enable Web Search in UI
1. Open the application sidebar
2. Expand "🔍 웹 검색 설정"
3. Check "웹 검색 활성화"
4. Configure search options as needed

### 2. Search Provider Configuration

#### Using Fallback Provider (No API Key)
- Select "기본 검색 (API 키 불필요)"
- No additional configuration needed

#### Using Google Search
1. Select "Google 검색 (API 키 필요)"
2. Enter your Google Custom Search API key
3. Enter your Search Engine ID
4. [Get API Key](https://developers.google.com/custom-search/v1/introduction)

#### Using Bing Search
1. Select "Bing 검색 (API 키 필요)"
2. Enter your Bing Search API key
3. [Get API Key](https://www.microsoft.com/en-us/bing/apis/bing-web-search-api)

### 3. Document Generation with Web Search
1. Enter your document requirements
2. Provide a clear document title/subject (used for search queries)
3. Click "🚀 문서 생성"
4. The system will:
   - Generate an initial draft
   - Search for relevant web content
   - Enrich the draft with found information
   - Provide references and sources

## Technical Architecture

### Components

1. **WebSearchProvider**: Base class for search providers
   - `GoogleSearchProvider`: Google Custom Search implementation
   - `BingSearchProvider`: Bing Search implementation
   - `FallbackSearchProvider`: DuckDuckGo scraping fallback

2. **WebSearchEnricher**: Main enrichment engine
   - Keyword extraction
   - Query generation
   - Result processing and ranking
   - Content integration

3. **EnhancedDraftWriterAgent**: Enhanced agent with web search
   - Integrates with LoopAgent pipeline
   - Generates enriched drafts
   - Manages search configuration

### Data Flow
```
User Input → Document Title → Keyword Extraction → Search Query Generation
    ↓
Web Search → Result Processing → Content Extraction → Relevance Scoring
    ↓
Draft Generation → Content Integration → Enhanced Document → Output
```

## API Configuration

### Google Custom Search
```python
config = {
    "search_provider": "google",
    "search_api_key": "YOUR_GOOGLE_API_KEY",
    "google_search_engine_id": "YOUR_SEARCH_ENGINE_ID"
}
```

### Bing Search
```python
config = {
    "search_provider": "bing",
    "search_api_key": "YOUR_BING_API_KEY"
}
```

## Search Quality Optimization

### Best Practices
1. **Clear Titles**: Provide specific, descriptive document titles
2. **Relevant Keywords**: Include industry-specific terms in requirements
3. **Document Type**: Select appropriate document type for better search targeting
4. **Search Depth**: Use "deep" search for comprehensive research documents

### Search Query Examples
- Investment proposals: "[keyword] 투자 제안 사례"
- Market analysis: "[keyword] 시장 전망 2024"
- Financial reports: "[keyword] 분석 보고서"

## Performance Considerations

### Rate Limiting
- Fallback provider: 1 second between requests
- Google/Bing: Based on API tier limits

### Caching
- Search results cached for session duration
- Content extraction cached to avoid redundant fetches

### Token Usage
- Web search adds ~25-30% more tokens per document
- Use "quick" search depth for token optimization

## Troubleshooting

### Common Issues

1. **No search results found**
   - Check internet connection
   - Verify API keys (if using Google/Bing)
   - Try different search terms or fallback provider

2. **Content extraction fails**
   - Some websites block automated access
   - Try disabling content extraction
   - Use different search provider

3. **API errors**
   - Verify API key validity
   - Check API quota/limits
   - Switch to fallback provider

## Security & Privacy

- API keys are not stored permanently
- Search queries are not logged
- Web content is processed locally
- No user data is sent to third parties (except search queries to providers)

## Future Enhancements

- [ ] Support for more search providers (Serper, SerpAPI)
- [ ] Advanced MCP integration (Firecrawl, Playwright)
- [ ] Real-time news integration
- [ ] Financial data API integration
- [ ] Multi-language search support
- [ ] Search result caching database
- [ ] Custom domain filtering
- [ ] Sentiment analysis of search results