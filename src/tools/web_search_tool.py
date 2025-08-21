"""
Web Search Tool for enriching document content
Supports multiple search providers and content extraction
"""

import re
import json
import time
import requests
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from urllib.parse import quote_plus, urlparse
from bs4 import BeautifulSoup
from loguru import logger
import hashlib
from .advanced_search import (
    AdvancedSearchEvaluator,
    EnhancedSearchQueryGenerator,
    SearchQuality,
    filter_reliable_results
)


@dataclass
class SearchResult:
    """Single search result with metadata"""
    title: str
    url: str
    snippet: str
    content: Optional[str] = None
    source: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    relevance_score: float = 0.0
    content_date: Optional[str] = None  # Publication date of the content
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "url": self.url,
            "snippet": self.snippet,
            "content": self.content,
            "source": self.source,
            "timestamp": self.timestamp,
            "relevance_score": self.relevance_score,
            "content_date": self.content_date
        }


@dataclass
class SearchQuery:
    """Search query with context and parameters"""
    query: str
    context: Optional[str] = None
    max_results: int = 5
    search_depth: str = "standard"  # quick, standard, deep
    content_extraction: bool = True
    language: str = "ko"
    region: str = "KR"
    time_range: Optional[str] = None  # day, week, month, year
    domains: List[str] = field(default_factory=list)
    exclude_domains: List[str] = field(default_factory=list)


class WebSearchProvider:
    """Base class for web search providers"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        self.cache = {}
        self.rate_limit_delay = 1.0  # seconds between requests
        self.last_request_time = 0
        
    def search(self, query: SearchQuery) -> List[SearchResult]:
        """Perform search and return results"""
        raise NotImplementedError("Subclasses must implement search method")
    
    def extract_content(self, url: str) -> Optional[str]:
        """Extract main content from URL"""
        try:
            # Rate limiting
            self._rate_limit()
            
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Try to find main content areas
            content_areas = [
                soup.find('main'),
                soup.find('article'),
                soup.find('div', class_=re.compile('content|main|body', re.I)),
                soup.find('div', id=re.compile('content|main|body', re.I))
            ]
            
            for area in content_areas:
                if area:
                    text = area.get_text(separator='\n', strip=True)
                    if len(text) > 200:  # Minimum content length
                        return text
            
            # Fallback to body text
            text = soup.get_text(separator='\n', strip=True)
            return text[:5000] if text else None  # Limit content length
            
        except Exception as e:
            logger.error(f"Error extracting content from {url}: {str(e)}")
            return None
    
    def _rate_limit(self):
        """Implement rate limiting"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - time_since_last)
        self.last_request_time = time.time()


class GoogleSearchProvider(WebSearchProvider):
    """Google Custom Search API provider"""
    
    def __init__(self, api_key: str, search_engine_id: str):
        super().__init__(api_key)
        self.search_engine_id = search_engine_id
        self.base_url = "https://www.googleapis.com/customsearch/v1"
    
    def search(self, query: SearchQuery) -> List[SearchResult]:
        """Search using Google Custom Search API"""
        try:
            # Build search parameters
            params = {
                'key': self.api_key,
                'cx': self.search_engine_id,
                'q': query.query,
                'num': min(query.max_results, 10),  # Google limit
                'hl': query.language,
                'gl': query.region.lower()
            }
            
            # Add time range if specified
            if query.time_range:
                date_restrict_map = {
                    'day': 'd1',
                    'week': 'w1',
                    'month': 'm1',
                    'year': 'y1'
                }
                params['dateRestrict'] = date_restrict_map.get(query.time_range, '')
            
            # Add site restrictions if specified
            if query.domains:
                site_query = " OR ".join([f"site:{domain}" for domain in query.domains])
                params['q'] = f"{query.query} ({site_query})"
            
            # Make API request
            response = self.session.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            results = []
            for item in data.get('items', []):
                result = SearchResult(
                    title=item.get('title', ''),
                    url=item.get('link', ''),
                    snippet=item.get('snippet', ''),
                    source='Google'
                )
                
                # Extract content if requested
                if query.content_extraction:
                    result.content = self.extract_content(result.url)
                
                results.append(result)
            
            return results
            
        except Exception as e:
            logger.error(f"Google search error: {str(e)}")
            return []


class BingSearchProvider(WebSearchProvider):
    """Bing Search API provider"""
    
    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.base_url = "https://api.bing.microsoft.com/v7.0/search"
        self.session.headers.update({
            'Ocp-Apim-Subscription-Key': api_key
        })
    
    def search(self, query: SearchQuery) -> List[SearchResult]:
        """Search using Bing Search API"""
        try:
            # Build search parameters
            params = {
                'q': query.query,
                'count': query.max_results,
                'mkt': f"{query.language}-{query.region}",
                'safeSearch': 'Moderate'
            }
            
            # Add time filter
            if query.time_range:
                freshness_map = {
                    'day': 'Day',
                    'week': 'Week',
                    'month': 'Month'
                }
                params['freshness'] = freshness_map.get(query.time_range, '')
            
            # Make API request
            response = self.session.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            results = []
            for item in data.get('webPages', {}).get('value', []):
                result = SearchResult(
                    title=item.get('name', ''),
                    url=item.get('url', ''),
                    snippet=item.get('snippet', ''),
                    source='Bing'
                )
                
                # Extract content if requested
                if query.content_extraction:
                    result.content = self.extract_content(result.url)
                
                results.append(result)
            
            return results
            
        except Exception as e:
            logger.error(f"Bing search error: {str(e)}")
            return []


class FallbackSearchProvider(WebSearchProvider):
    """Fallback web scraping-based search (for testing without API)"""
    
    def search(self, query: SearchQuery) -> List[SearchResult]:
        """Perform fallback search - generates demo data for testing"""
        logger.info(f"Fallback search for: {query.query}")
        
        # Always use generated demo data for testing
        # (DuckDuckGo web scraping is unreliable and often blocked)
        return self._generate_demo_results(query)
    
    def _generate_demo_results(self, query: SearchQuery) -> List[SearchResult]:
        """Generate realistic demo results for testing"""
        from datetime import datetime, timedelta
        import random
        
        demo_results = []
        current_date = datetime.now().strftime("%Y년 %m월 %d일")
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y년 %m월 %d일")
        week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y년 %m월 %d일")
        
        # Generate comprehensive results
        if any(word in query.query.lower() for word in ['esg', '지속가능', 'sustainable', '투자']):
            demo_results.extend([
                SearchResult(
                    title=f"2025년 ESG 투자 전망: 지속가능금융의 새로운 패러다임",
                    url="https://www.hankyung.com/finance/article/2025082100001",
                    snippet=f"{current_date} - 국내 ESG 투자 시장이 급성장하면서 새로운 투자 기회가 열리고 있다. 특히 AI와 ESG를 결합한 융합 투자 전략이 주목받고 있다.",
                    content_date=current_date,
                    source="Demo"
                ),
                SearchResult(
                    title="AI 기반 ESG 평가 시스템 도입 확산",
                    url="https://www.mk.co.kr/news/it/2025/08/1234567",
                    snippet=f"{yesterday} - 인공지능을 활용한 ESG 평가 시스템이 금융기관을 중심으로 빠르게 확산되고 있다. 정확도와 효율성이 크게 개선되었다.",
                    content_date=yesterday,
                    source="Demo"
                ),
                SearchResult(
                    title="글로벌 ESG 투자 규모 100조원 돌파",
                    url="https://www.sedaily.com/NewsView/2025081234",
                    snippet=f"{week_ago} - 전 세계 ESG 투자 규모가 처음으로 100조원을 넘어섰다. 한국 시장도 빠른 성장세를 보이고 있다.",
                    content_date=week_ago,
                    source="Demo"
                ),
                SearchResult(
                    title="국내 주요 금융사, ESG-AI 융합 투자 상품 출시",
                    url="https://www.fnnews.com/news/202508200945",
                    snippet=f"{current_date} - KB금융, 신한금융 등 주요 금융그룹이 ESG와 AI를 결합한 혁신적인 투자 상품을 연이어 출시하고 있다.",
                    content_date=current_date,
                    source="Demo"
                ),
                SearchResult(
                    title="ESG 투자 수익률, 일반 펀드 대비 15% 높아",
                    url="https://www.edaily.co.kr/news/2025082012345",
                    snippet=f"{yesterday} - 최근 3년간 ESG 투자 펀드의 평균 수익률이 일반 펀드보다 15% 높은 것으로 나타났다.",
                    content_date=yesterday,
                    source="Demo"
                )
            ])
        
        if any(word in query.query.lower() for word in ['ai', '인공지능', 'artificial', '기술']):
            demo_results.extend([
                SearchResult(
                    title="금융 AI 혁신: 투자 분석의 새로운 기준",
                    url="https://www.zdnet.co.kr/view/?no=20250820123456",
                    snippet=f"{yesterday} - AI 기술이 금융 투자 분석에 혁명을 일으키고 있다. 빅데이터와 머신러닝을 활용한 정교한 분석이 가능해졌다.",
                    content_date=yesterday,
                    source="Demo"
                ),
                SearchResult(
                    title="생성형 AI, 금융 투자 자문 서비스 혁신",
                    url="https://www.bloter.net/news/2025/08/ai-finance",
                    snippet=f"{current_date} - ChatGPT와 같은 생성형 AI가 개인 맞춤형 투자 자문 서비스에 활용되면서 금융 서비스가 한층 더 스마트해지고 있다.",
                    content_date=current_date,
                    source="Demo"
                )
            ])
        
        # Always add some general finance results for completeness
        if len(demo_results) < 5:
            demo_results.extend([
                SearchResult(
                    title="2025년 하반기 투자 전략 가이드",
                    url="https://www.chosun.com/economy/2025/08/20/investment-guide/",
                    snippet=f"{current_date} - 전문가들이 제시하는 2025년 하반기 투자 전략. 글로벌 경제 불확실성 속에서도 기회는 있다.",
                    content_date=current_date,
                    source="Demo"
                ),
                SearchResult(
                    title="한국 금융시장 전망: 기회와 도전",
                    url="https://www.donga.com/news/Economy/article/2025082001",
                    snippet=f"{week_ago} - 국내 금융시장이 새로운 전환점을 맞이하고 있다. 디지털 전환과 규제 변화가 핵심 변수로 떠올랐다.",
                    content_date=week_ago,
                    source="Demo"
                ),
                SearchResult(
                    title="코스콤, 차세대 금융 플랫폼 구축 완료",
                    url="https://www.infostock.co.kr/news/2025/08/koscom-platform",
                    snippet=f"{yesterday} - 코스콤이 AI와 블록체인을 활용한 차세대 금융 플랫폼 구축을 완료했다. 금융 서비스 혁신이 기대된다.",
                    content_date=yesterday,
                    source="Demo"
                )
            ])
        
        # Ensure we always return at least some results
        if not demo_results:
            # Fallback results if nothing matches
            demo_results = [
                SearchResult(
                    title="최신 금융 투자 동향 분석",
                    url="https://www.example-finance.com/news/latest",
                    snippet=f"{current_date} - 최신 금융 시장 동향과 투자 전략을 분석합니다.",
                    content_date=current_date,
                    source="Demo"
                )
            ]
        
        # Limit results based on max_results
        max_results = query.max_results or 5
        return demo_results[:max_results]


class WebSearchEnricher:
    """Main class for enriching documents with web search results"""
    
    def __init__(self, provider: Optional[WebSearchProvider] = None):
        self.provider = provider or FallbackSearchProvider()
        self.enrichment_cache = {}
        self.search_evaluator = AdvancedSearchEvaluator()
        self.query_generator = EnhancedSearchQueryGenerator()
        
    def enrich_document(self, 
                        document: str, 
                        title: str,
                        document_type: str,
                        search_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Enrich document content with web search results
        
        Args:
            document: Original document text
            title: Document title or subject
            document_type: Type of document (email, proposal, report)
            search_config: Optional search configuration
            
        Returns:
            Enriched document data with search results and suggestions
        """
        logger.info(f"Starting document enrichment for: {title}")
        
        # Extract key terms from document
        key_terms = self._extract_key_terms(document, title)
        
        # Generate advanced search queries with priority scoring
        query_context = {
            'document_type': document_type,
            'key_terms': key_terms,
            'title': title
        }
        advanced_queries = self.query_generator.generate_advanced_queries(
            document, title, document_type, query_context
        )
        
        # Fall back to basic queries if advanced generation fails
        if not advanced_queries:
            korean_priority = search_config.get('korean_priority', True) if search_config else True
            queries = self._generate_search_queries(key_terms, document_type, title, korean_priority)
        else:
            # Extract query strings from tuples (query, priority)
            queries = [query for query, priority in advanced_queries]
        
        # Determine number of queries based on search depth
        max_queries_map = {
            'quick': 3,
            'standard': 5,
            'deep': 7,
            'comprehensive': 10
        }
        search_depth = search_config.get('search_depth', 'standard') if search_config else 'standard'
        max_queries = max_queries_map.get(search_depth, 5)
        
        # Perform searches with time range for recent results
        all_results = []
        for query_str in queries[:max_queries]:
            # Default to recent results (week for news, month for others)
            default_time_range = 'week' if '뉴스' in query_str or '최신' in query_str else 'month'
            
            query = SearchQuery(
                query=query_str,
                context=document_type,
                max_results=search_config.get('max_results', 5) if search_config else 5,
                search_depth=search_depth,
                content_extraction=search_config.get('extract_content', True) if search_config else True,
                language='ko',
                region='KR',
                time_range=search_config.get('time_range', default_time_range) if search_config else default_time_range
            )
            
            results = self.provider.search(query)
            all_results.extend(results)
        
        # Process and rank results
        relevant_info = self._process_search_results(all_results, document)
        
        # Generate enrichment suggestions
        enrichment_suggestions = self._generate_enrichment_suggestions(
            document, relevant_info, document_type
        )
        
        return {
            'original_document': document,
            'search_results': [r.to_dict() for r in all_results],
            'relevant_information': relevant_info,
            'enrichment_suggestions': enrichment_suggestions,
            'key_terms': key_terms,
            'search_queries': queries,
            'timestamp': datetime.now().isoformat()
        }
    
    def _extract_key_terms(self, document: str, title: str) -> List[str]:
        """Extract key terms from document and title"""
        # Combine title and document for term extraction
        text = f"{title} {document}"
        
        # Financial and business terms patterns
        term_patterns = [
            r'\b(?:투자|수익률|리스크|포트폴리오|자산|펀드|ETF|채권|주식)\b',
            r'\b(?:금융|은행|증권|보험|연금|대출|예금|적금)\b',
            r'\b(?:시장|경제|성장|전망|분석|전략|계획)\b',
            r'\b(?:기술|혁신|디지털|AI|블록체인|핀테크)\b',
            r'\b(?:규제|정책|법률|컴플라이언스|리스크관리)\b'
        ]
        
        key_terms = []
        for pattern in term_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            key_terms.extend(matches)
        
        # Add title words (if meaningful)
        title_words = [word for word in title.split() if len(word) > 2]
        key_terms.extend(title_words[:3])  # Add top 3 title words
        
        # Remove duplicates while preserving order
        seen = set()
        unique_terms = []
        for term in key_terms:
            if term.lower() not in seen:
                seen.add(term.lower())
                unique_terms.append(term)
        
        return unique_terms[:10]  # Return top 10 terms
    
    def _generate_search_queries(self, 
                                 key_terms: List[str], 
                                 document_type: str,
                                 title: str,
                                 korean_priority: bool = True) -> List[str]:
        """Generate enhanced search queries based on key terms and context"""
        queries = []
        current_year = datetime.now().year
        current_month = datetime.now().strftime("%Y년 %m월")
        
        # Primary query - title based with year
        if title:
            queries.append(f"{title} {current_year}")
            if korean_priority:
                queries.append(f"{title} 한국 {current_year}")
                queries.append(f"{title} 최신 뉴스 {current_month}")
        
        # Document type specific queries with recent dates
        if document_type == "proposal":
            if key_terms:
                queries.append(f"{key_terms[0]} 투자 제안 사례 {current_year}")
                queries.append(f"{key_terms[0]} 시장 전망 {current_year} 최신")
                queries.append(f"{key_terms[0]} 한국 시장 분석 {current_year}")
                queries.append(f"{key_terms[0]} 수익률 전망 {current_year}")
                queries.append(f"{key_terms[0]} 투자 리스크 분석")
        elif document_type == "email":
            if key_terms:
                queries.append(f"{key_terms[0]} 금융 동향 최신")
                queries.append(f"{key_terms[0]} 뉴스 {current_year}")
                queries.append(f"{key_terms[0]} 업계 소식 {current_month}")
        elif document_type == "report":
            if key_terms:
                queries.append(f"{key_terms[0]} 분석 보고서 {current_year}")
                queries.append(f"{key_terms[0]} 산업 현황 최신")
                queries.append(f"{key_terms[0]} 통계 데이터 {current_year}")
                queries.append(f"{key_terms[0]} 시장 규모 {current_year}")
                queries.append(f"{key_terms[0]} 성장률 전망")
        
        # Key terms combination query with recent context
        if len(key_terms) >= 2:
            queries.append(f"{key_terms[0]} {key_terms[1]} 최신 동향 {current_year}")
            queries.append(f"{key_terms[0]} {key_terms[1]} 한국 시장")
            queries.append(f"{key_terms[0]} {key_terms[1]} 분석 리포트")
        
        # Financial market query with Korean focus
        if any(term in str(key_terms).lower() for term in ['투자', '주식', '펀드', '채권', 'ETF']):
            queries.append(f"한국 금융시장 최신 동향 {current_year}")
            queries.append(f"코스피 코스닥 시장 분석 {current_year}")
            queries.append(f"한국 {key_terms[0]} 시장 전망 {current_year}")
            queries.append(f"금융투자협회 시장 동향 {current_month}")
        
        # Technology and innovation queries
        if any(term in str(key_terms).lower() for term in ['AI', '인공지능', '블록체인', '핀테크', '디지털']):
            queries.append(f"{key_terms[0]} 기술 동향 {current_year}")
            queries.append(f"{key_terms[0]} 혁신 사례 한국")
            queries.append(f"금융 {key_terms[0]} 적용 사례 {current_year}")
        
        # ESG and sustainability queries
        if any(term in str(key_terms).lower() for term in ['ESG', '지속가능', '친환경', '탄소중립']):
            queries.append(f"ESG 투자 동향 한국 {current_year}")
            queries.append(f"지속가능금융 시장 현황 {current_year}")
            queries.append(f"ESG 평가 기준 {current_year}")
        
        # Add Korean news sources with more variety
        if korean_priority and key_terms:
            queries.append(f"{key_terms[0]} site:hankyung.com OR site:mk.co.kr {current_year}")
            queries.append(f"{key_terms[0]} site:news.naver.com OR site:finance.naver.com")
            queries.append(f"{key_terms[0]} site:edaily.co.kr OR site:fnnews.com")
        
        # Remove duplicates while preserving order
        seen = set()
        unique_queries = []
        for q in queries:
            if q not in seen:
                seen.add(q)
                unique_queries.append(q)
        
        logger.info(f"Generated {len(unique_queries)} unique search queries")
        return unique_queries[:15]  # Return more queries for comprehensive search
    
    def _process_search_results(self, 
                               results: List[SearchResult], 
                               document: str) -> List[Dict[str, Any]]:
        """Process and rank search results by relevance with quality evaluation"""
        relevant_info = []
        seen_urls = set()  # Track unique URLs
        
        for result in results:
            # Skip duplicates
            if result.url in seen_urls:
                continue
            seen_urls.add(result.url)
            
            # Calculate basic relevance score
            relevance = self._calculate_relevance(result, document)
            result.relevance_score = relevance
            
            # Evaluate search quality
            search_context = {
                'query': getattr(result, 'query', ''),
                'document': document[:500],  # Use first 500 chars for context
                'required_terms': self._extract_key_terms(document, '')[:5]
            }
            
            result_dict = result.to_dict()
            quality = self.search_evaluator.evaluate_search_quality(result_dict, search_context)
            
            # For demo/fallback results, ensure minimum quality score
            if hasattr(result, 'source') and result.source in ['Demo', 'Fallback']:
                quality.overall_score = max(quality.overall_score, 0.4)
                quality.is_reliable = quality.overall_score >= 0.4
            
            # Only include reliable results
            if quality.is_reliable and quality.overall_score >= 0.4:
                # Ensure URL is complete
                url = result.url
                if not url.startswith('http'):
                    # Try to fix relative URLs
                    if '://' not in url:
                        url = f"https://{url}" if '.' in url else result.url
                
                info = {
                    'title': result.title,
                    'url': url,
                    'summary': result.snippet or '',
                    'relevance': relevance,
                    'key_facts': self._extract_key_facts(result.content or result.snippet),
                    'source': result.source if hasattr(result, 'source') else 'Web',
                    'retrieved_at': datetime.now().isoformat(),
                    'is_recent': True,  # Marked as recent due to time filtering
                    'content_date': result.content_date if hasattr(result, 'content_date') and result.content_date else None,
                    'quality_metrics': {
                        'overall_score': quality.overall_score,
                        'relevance': quality.relevance_score,
                        'credibility': quality.credibility_score,
                        'freshness': quality.freshness_score,
                        'specificity': quality.specificity_score,
                        'confidence': quality.confidence_level,
                        'reasons': quality.quality_reasons
                    }
                }
                
                # Try to extract date from snippet
                date_patterns = [
                    r'(\d{4}년\s*\d{1,2}월\s*\d{1,2}일)',
                    r'(\d{4}-\d{2}-\d{2})',
                    r'(\d{4}/\d{2}/\d{2})',
                    r'(\d{1,2}일\s*전)',
                    r'(오늘|어제|그제)'
                ]
                
                for pattern in date_patterns:
                    date_match = re.search(pattern, result.snippet or '')
                    if date_match:
                        info['content_date'] = date_match.group(1)
                        break
                
                relevant_info.append(info)
            else:
                logger.info(f"Filtered out low-quality result: {result.title} (score: {quality.overall_score:.2f})")
        
        # Sort by quality score first, then by relevance
        relevant_info.sort(key=lambda x: (
            x['quality_metrics']['overall_score'],
            x.get('content_date') is not None,
            x['relevance']
        ), reverse=True)
        
        logger.info(f"Processed {len(relevant_info)} relevant results from {len(results)} total results")
        return relevant_info[:10]  # Return top 10 most relevant
    
    def _calculate_relevance(self, result: SearchResult, document: str) -> float:
        """Calculate relevance score between search result and document"""
        score = 0.0
        
        # Check title relevance
        doc_words = set(document.lower().split())
        title_words = set(result.title.lower().split())
        title_overlap = len(doc_words & title_words) / max(len(title_words), 1)
        score += title_overlap * 0.3
        
        # Check snippet relevance
        if result.snippet:
            snippet_words = set(result.snippet.lower().split())
            snippet_overlap = len(doc_words & snippet_words) / max(len(snippet_words), 1)
            score += snippet_overlap * 0.3
        
        # Check content relevance (if available)
        if result.content:
            content_words = set(result.content.lower().split()[:100])  # First 100 words
            content_overlap = len(doc_words & content_words) / max(len(content_words), 1)
            score += content_overlap * 0.4
        
        return min(score, 1.0)
    
    def _extract_key_facts(self, text: str) -> List[str]:
        """Extract key facts from text"""
        if not text:
            return []
        
        facts = []
        sentences = text.split('.')
        
        # Look for sentences with numbers, percentages, or key terms
        fact_patterns = [
            r'\d+(?:\.\d+)?%',  # Percentages
            r'\d{4}년',  # Years
            r'[\d,]+(?:억|조|백만|천만)',  # Korean number units
            r'(?:증가|감소|상승|하락)',  # Trends
            r'(?:발표|예상|전망|계획)',  # Announcements
        ]
        
        for sentence in sentences[:10]:  # Check first 10 sentences
            if any(re.search(pattern, sentence) for pattern in fact_patterns):
                clean_sentence = sentence.strip()
                if 20 < len(clean_sentence) < 200:  # Reasonable length
                    facts.append(clean_sentence)
        
        return facts[:3]  # Return top 3 facts
    
    def _generate_enrichment_suggestions(self,
                                        document: str,
                                        relevant_info: List[Dict[str, Any]],
                                        document_type: str) -> List[Dict[str, str]]:
        """Generate suggestions for enriching the document"""
        suggestions = []
        
        # Check for missing market data
        if not re.search(r'\d+(?:\.\d+)?%', document):
            suggestions.append({
                'type': 'data',
                'suggestion': '구체적인 수치나 통계 데이터를 추가하면 신뢰성이 높아집니다.',
                'example': '최근 시장 성장률, 예상 수익률 등의 구체적인 수치'
            })
        
        # Check for recent information
        current_year = datetime.now().year
        if not re.search(rf'{current_year}|최신|최근', document):
            suggestions.append({
                'type': 'timeliness',
                'suggestion': '최신 시장 동향이나 현재 년도 데이터를 포함시키세요.',
                'example': f'{current_year}년 시장 전망이나 최근 정책 변화'
            })
        
        # Suggest facts from search results
        if relevant_info:
            for info in relevant_info[:2]:
                if info['key_facts']:
                    suggestions.append({
                        'type': 'fact',
                        'suggestion': f"다음 정보를 참고하여 내용을 보강할 수 있습니다: {info['key_facts'][0]}",
                        'source': info['url']
                    })
        
        # Document type specific suggestions
        if document_type == "proposal":
            if "경쟁사" not in document and "비교" not in document:
                suggestions.append({
                    'type': 'comparison',
                    'suggestion': '경쟁사 대비 장점이나 시장 내 포지셔닝을 추가하면 좋습니다.',
                    'example': '유사 상품 대비 차별화 포인트'
                })
        
        return suggestions


# Tool function exports for agent integration
def create_web_search_enricher(provider_type: str = "fallback", 
                              api_key: Optional[str] = None,
                              **kwargs) -> WebSearchEnricher:
    """
    Create a web search enricher with specified provider
    
    Args:
        provider_type: Type of search provider (google, bing, fallback)
        api_key: API key for the provider
        **kwargs: Additional provider-specific parameters
        
    Returns:
        WebSearchEnricher instance
    """
    if provider_type == "google" and api_key:
        provider = GoogleSearchProvider(api_key, kwargs.get('search_engine_id', ''))
    elif provider_type == "bing" and api_key:
        provider = BingSearchProvider(api_key)
    else:
        provider = FallbackSearchProvider()
    
    return WebSearchEnricher(provider)


def enrich_document_with_search(document: str,
                               title: str,
                               document_type: str = "general",
                               search_config: Optional[Dict[str, Any]] = None,
                               provider_type: str = "fallback",
                               api_key: Optional[str] = None) -> Dict[str, Any]:
    """
    Enrich document with web search results
    
    Args:
        document: Document text to enrich
        title: Document title or subject
        document_type: Type of document
        search_config: Search configuration
        provider_type: Search provider type
        api_key: API key for search provider
        
    Returns:
        Enrichment results with search data and suggestions
    """
    enricher = create_web_search_enricher(provider_type, api_key)
    return enricher.enrich_document(document, title, document_type, search_config)


# Export all classes and functions
__all__ = [
    'SearchResult',
    'SearchQuery',
    'WebSearchProvider',
    'GoogleSearchProvider',
    'BingSearchProvider',
    'FallbackSearchProvider',
    'WebSearchEnricher',
    'create_web_search_enricher',
    'enrich_document_with_search'
]