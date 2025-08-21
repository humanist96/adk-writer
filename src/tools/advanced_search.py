"""
Advanced Web Search with Accuracy Evaluation and Reliability Filtering
"""

import re
import json
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import hashlib
from loguru import logger
import numpy as np
from collections import Counter


@dataclass
class SearchQuality:
    """Search result quality metrics"""
    relevance_score: float = 0.0
    credibility_score: float = 0.0
    freshness_score: float = 0.0
    specificity_score: float = 0.0
    overall_score: float = 0.0
    confidence_level: str = "low"  # low, medium, high
    is_reliable: bool = False
    quality_reasons: List[str] = field(default_factory=list)


class AdvancedSearchEvaluator:
    """Advanced search quality evaluation system"""
    
    def __init__(self):
        # Credible Korean financial sources
        self.credible_domains = {
            # Major news outlets
            'hankyung.com': 0.9,  # 한국경제
            'mk.co.kr': 0.9,      # 매일경제
            'sedaily.com': 0.85,  # 서울경제
            'fnnews.com': 0.85,   # 파이낸셜뉴스
            'edaily.co.kr': 0.85, # 이데일리
            'wowtv.co.kr': 0.8,   # 한국경제TV
            'etnews.com': 0.8,    # 전자신문
            
            # Government & Official
            'fss.or.kr': 1.0,     # 금융감독원
            'bok.or.kr': 1.0,     # 한국은행
            'ksd.or.kr': 0.95,    # 한국예탁결제원
            'krx.co.kr': 0.95,    # 한국거래소
            'kofia.or.kr': 0.9,   # 금융투자협회
            
            # Financial institutions
            'kbstar.com': 0.85,   # KB국민은행
            'shinhan.com': 0.85,  # 신한금융
            'hanafn.com': 0.85,   # 하나금융
            
            # Research & Analytics
            'kisrating.co.kr': 0.9,  # 한국신용평가
            'nicerating.com': 0.9,   # NICE신용평가
            'koreabond.co.kr': 0.85, # 한국채권평가
        }
        
        # Keywords indicating high-quality financial content
        self.quality_keywords = {
            'high': ['공시', '발표', '보고서', '분석', '전망', '실적', '정책', '규제', '금융위원회', '한국은행'],
            'medium': ['투자', '시장', '전략', '동향', '예상', '계획', '성장', '수익'],
            'low': ['루머', '추측', '소문', '카더라', '미확인', '논란']
        }
        
        # Minimum thresholds for reliable sources
        self.min_thresholds = {
            'relevance': 0.4,      # Minimum relevance score
            'credibility': 0.5,    # Minimum credibility score
            'freshness': 0.3,      # Minimum freshness score
            'overall': 0.45,       # Minimum overall score
        }
    
    def evaluate_search_quality(self, 
                               search_result: Dict[str, Any],
                               query_context: Dict[str, Any]) -> SearchQuality:
        """Evaluate the quality and reliability of a search result"""
        quality = SearchQuality()
        
        # 1. Calculate relevance score (improved algorithm)
        quality.relevance_score = self._calculate_advanced_relevance(
            search_result, query_context
        )
        
        # 2. Calculate credibility score
        quality.credibility_score = self._calculate_credibility(
            search_result.get('url', ''),
            search_result.get('source', '')
        )
        
        # 3. Calculate freshness score
        quality.freshness_score = self._calculate_freshness(
            search_result.get('content_date'),
            search_result.get('retrieved_at')
        )
        
        # 4. Calculate specificity score
        quality.specificity_score = self._calculate_specificity(
            search_result.get('snippet', ''),
            search_result.get('key_facts', [])
        )
        
        # 5. Calculate overall score with weighted average
        weights = {
            'relevance': 0.35,
            'credibility': 0.30,
            'freshness': 0.20,
            'specificity': 0.15
        }
        
        quality.overall_score = (
            quality.relevance_score * weights['relevance'] +
            quality.credibility_score * weights['credibility'] +
            quality.freshness_score * weights['freshness'] +
            quality.specificity_score * weights['specificity']
        )
        
        # 6. Determine confidence level
        if quality.overall_score >= 0.7:
            quality.confidence_level = "high"
        elif quality.overall_score >= 0.5:
            quality.confidence_level = "medium"
        else:
            quality.confidence_level = "low"
        
        # 7. Determine if reliable enough to use
        quality.is_reliable = self._is_reliable(quality)
        
        # 8. Add quality reasons
        quality.quality_reasons = self._generate_quality_reasons(quality, search_result)
        
        return quality
    
    def _calculate_advanced_relevance(self, 
                                     result: Dict[str, Any],
                                     context: Dict[str, Any]) -> float:
        """Advanced relevance calculation using multiple factors"""
        score = 0.0
        
        # Extract key terms from context
        query_terms = set(context.get('query', '').lower().split())
        doc_terms = set(context.get('document', '').lower().split())
        required_terms = context.get('required_terms', [])
        
        title = result.get('title', '').lower()
        snippet = result.get('snippet', '').lower()
        
        # 1. Query term matching (30%)
        if query_terms:
            query_match = sum(1 for term in query_terms if term in title or term in snippet)
            score += (query_match / len(query_terms)) * 0.3
        
        # 2. Document term matching (25%)
        if doc_terms:
            doc_match = sum(1 for term in list(doc_terms)[:20] if term in snippet)
            score += (doc_match / min(20, len(doc_terms))) * 0.25
        
        # 3. Required terms matching (25%)
        if required_terms:
            req_match = sum(1 for term in required_terms if term.lower() in snippet)
            score += (req_match / len(required_terms)) * 0.25
        
        # 4. Semantic similarity (20%)
        # Use keyword categories for semantic matching
        finance_keywords = ['투자', '수익', '금융', '시장', '전략', 'ESG', 'AI', '펀드', '자산']
        semantic_match = sum(1 for kw in finance_keywords if kw.lower() in snippet)
        score += min(semantic_match / 5, 1.0) * 0.2
        
        return min(score, 1.0)
    
    def _calculate_credibility(self, url: str, source: str) -> float:
        """Calculate source credibility score"""
        # Check if demo/fallback source
        if source in ['Demo', 'Fallback']:
            return 0.3  # Low credibility for demo data
        
        # Extract domain from URL
        import urllib.parse
        try:
            domain = urllib.parse.urlparse(url).netloc
            domain = domain.replace('www.', '')
            
            # Check against credible domains
            for credible_domain, cred_score in self.credible_domains.items():
                if credible_domain in domain:
                    return cred_score
            
            # Check if it's a subdomain of credible source
            for credible_domain, cred_score in self.credible_domains.items():
                if domain.endswith('.' + credible_domain):
                    return cred_score * 0.9  # Slightly lower for subdomains
            
        except:
            pass
        
        # Default credibility for unknown sources
        return 0.4
    
    def _calculate_freshness(self, content_date: Optional[str], 
                            retrieved_at: Optional[str]) -> float:
        """Calculate content freshness score"""
        try:
            # Parse the date
            current_date = datetime.now()
            
            if content_date:
                # Try to parse Korean date format
                if '년' in content_date and '월' in content_date:
                    # Extract year, month, day
                    import re
                    date_match = re.search(r'(\d{4})년\s*(\d{1,2})월\s*(\d{1,2})일', content_date)
                    if date_match:
                        year, month, day = map(int, date_match.groups())
                        content_datetime = datetime(year, month, day)
                        days_old = (current_date - content_datetime).days
                        
                        # Score based on age
                        if days_old <= 1:
                            return 1.0  # Today or yesterday
                        elif days_old <= 7:
                            return 0.9  # Within a week
                        elif days_old <= 30:
                            return 0.7  # Within a month
                        elif days_old <= 90:
                            return 0.5  # Within 3 months
                        elif days_old <= 365:
                            return 0.3  # Within a year
                        else:
                            return 0.1  # Older than a year
            
            # If no content date, use retrieved date
            if retrieved_at:
                return 0.5  # Default score for unknown date
            
        except Exception as e:
            logger.debug(f"Error calculating freshness: {e}")
        
        return 0.3  # Default low freshness score
    
    def _calculate_specificity(self, snippet: str, key_facts: List[str]) -> float:
        """Calculate how specific and detailed the content is"""
        score = 0.0
        
        if not snippet:
            return score
        
        # Check for specific data points
        patterns = {
            'numbers': r'\d+(?:\.\d+)?(?:%|억|조|만|천|백만)',  # Numbers with units
            'dates': r'\d{4}년\s*\d{1,2}월',  # Specific dates
            'quotes': r'["\'].*?["\']',  # Quoted statements
            'companies': r'(?:KB|신한|하나|우리|삼성|LG|SK|현대)',  # Major companies
        }
        
        for pattern_name, pattern in patterns.items():
            matches = re.findall(pattern, snippet)
            if matches:
                score += 0.25
        
        # Bonus for key facts
        if key_facts:
            score += min(len(key_facts) * 0.1, 0.3)
        
        # Check snippet length (longer, detailed snippets score higher)
        if len(snippet) > 200:
            score += 0.2
        elif len(snippet) > 100:
            score += 0.1
        
        return min(score, 1.0)
    
    def _is_reliable(self, quality: SearchQuality) -> bool:
        """Determine if the search result is reliable enough to use"""
        # Check against minimum thresholds
        if quality.relevance_score < self.min_thresholds['relevance']:
            return False
        if quality.credibility_score < self.min_thresholds['credibility']:
            return False
        if quality.freshness_score < self.min_thresholds['freshness']:
            return False
        if quality.overall_score < self.min_thresholds['overall']:
            return False
        
        return True
    
    def _generate_quality_reasons(self, quality: SearchQuality, 
                                 result: Dict[str, Any]) -> List[str]:
        """Generate human-readable quality assessment reasons"""
        reasons = []
        
        # Relevance feedback
        if quality.relevance_score >= 0.7:
            reasons.append("높은 관련성")
        elif quality.relevance_score >= 0.4:
            reasons.append("적절한 관련성")
        else:
            reasons.append("낮은 관련성")
        
        # Credibility feedback
        if quality.credibility_score >= 0.8:
            reasons.append("신뢰할 수 있는 출처")
        elif quality.credibility_score >= 0.5:
            reasons.append("일반적인 출처")
        else:
            reasons.append("신뢰도 낮은 출처")
        
        # Freshness feedback
        if quality.freshness_score >= 0.9:
            reasons.append("최신 정보")
        elif quality.freshness_score >= 0.5:
            reasons.append("비교적 최근 정보")
        else:
            reasons.append("오래된 정보")
        
        # Specificity feedback
        if quality.specificity_score >= 0.7:
            reasons.append("구체적인 데이터 포함")
        elif quality.specificity_score >= 0.4:
            reasons.append("일반적인 정보")
        else:
            reasons.append("모호한 내용")
        
        return reasons


class EnhancedSearchQueryGenerator:
    """Generate high-quality search queries with advanced techniques"""
    
    def __init__(self):
        self.query_templates = {
            'financial': [
                '{topic} {year}년 전망 분석',
                '{topic} 시장 동향 {year}',
                '{company} {topic} 투자 전략',
                '{topic} 규제 정책 금융위원회',
                '{topic} 실적 발표 {quarter}',
            ],
            'technical': [
                '{technology} {industry} 적용 사례',
                '{technology} 기술 동향 {year}',
                '{company} {technology} 도입 효과',
                '{technology} ROI 분석 보고서',
            ],
            'market': [
                '{market} 시장 규모 {year}',
                '{market} 성장률 전망',
                '{market} 주요 기업 점유율',
                '{market} 투자 기회 분석',
            ]
        }
    
    def generate_advanced_queries(self, 
                                 document: str,
                                 title: str,
                                 document_type: str,
                                 context: Dict[str, Any]) -> List[Tuple[str, float]]:
        """Generate advanced search queries with priority scores"""
        queries = []
        
        # Extract key entities and terms
        entities = self._extract_entities(document, title)
        key_terms = self._extract_key_terms(document, title)
        
        # Generate different types of queries
        # 1. Exact match queries (highest priority)
        for entity in entities[:3]:
            for term in key_terms[:2]:
                query = f'"{entity}" "{term}" {datetime.now().year}년'
                queries.append((query, 1.0))
        
        # 2. Broad queries (medium priority)
        for term in key_terms[:5]:
            query = f'{term} 최신 동향 {datetime.now().year}'
            queries.append((query, 0.8))
        
        # 3. Related queries (lower priority)
        related_terms = self._get_related_terms(key_terms)
        for term in related_terms[:3]:
            query = f'{term} 분석 보고서'
            queries.append((query, 0.6))
        
        # Remove duplicates and sort by priority
        unique_queries = {}
        for query, priority in queries:
            if query not in unique_queries or unique_queries[query] < priority:
                unique_queries[query] = priority
        
        sorted_queries = sorted(unique_queries.items(), key=lambda x: x[1], reverse=True)
        
        return sorted_queries[:15]  # Return top 15 queries
    
    def _extract_entities(self, document: str, title: str) -> List[str]:
        """Extract important entities from document"""
        entities = []
        
        # Company names
        company_pattern = r'(?:KB|신한|하나|우리|삼성|LG|SK|현대|코스콤)(?:금융|그룹|전자|증권)?'
        companies = re.findall(company_pattern, document + ' ' + title)
        entities.extend(companies)
        
        # Financial terms
        finance_pattern = r'(?:ESG|AI|블록체인|핀테크|디지털금융|자산운용|투자)'
        finance_terms = re.findall(finance_pattern, document + ' ' + title)
        entities.extend(finance_terms)
        
        return list(set(entities))[:10]
    
    def _extract_key_terms(self, document: str, title: str) -> List[str]:
        """Extract key terms using TF-IDF-like approach"""
        text = (title + ' ' + document).lower()
        
        # Remove common words
        stop_words = {'은', '는', '이', '가', '을', '를', '의', '에', '와', '과', '로', '으로', '에서', '까지'}
        words = [w for w in text.split() if w not in stop_words and len(w) > 1]
        
        # Count word frequency
        word_freq = Counter(words)
        
        # Get top terms
        top_terms = [word for word, count in word_freq.most_common(20)]
        
        # Filter for meaningful terms
        meaningful_terms = []
        for term in top_terms:
            if any(c in term for c in ['투자', '금융', '시장', '전략', '분석', '보고', '전망']):
                meaningful_terms.append(term)
        
        return meaningful_terms[:10]
    
    def _get_related_terms(self, key_terms: List[str]) -> List[str]:
        """Get related terms for query expansion"""
        related_map = {
            'ESG': ['지속가능', '친환경', '사회책임투자'],
            'AI': ['인공지능', '머신러닝', '딥러닝'],
            '투자': ['자산운용', '포트폴리오', '수익률'],
            '금융': ['핀테크', '디지털금융', '금융혁신'],
        }
        
        related = []
        for term in key_terms:
            for key, values in related_map.items():
                if key in term:
                    related.extend(values)
        
        return list(set(related))[:5]


def filter_reliable_results(search_results: List[Dict[str, Any]], 
                           min_quality_score: float = 0.5) -> List[Dict[str, Any]]:
    """Filter search results based on quality evaluation"""
    evaluator = AdvancedSearchEvaluator()
    filtered_results = []
    
    for result in search_results:
        # Create context for evaluation
        context = {
            'query': result.get('query', ''),
            'document': result.get('document_context', ''),
            'required_terms': result.get('required_terms', [])
        }
        
        # Evaluate quality
        quality = evaluator.evaluate_search_quality(result, context)
        
        # Add quality metrics to result
        result['quality_metrics'] = {
            'overall_score': quality.overall_score,
            'relevance': quality.relevance_score,
            'credibility': quality.credibility_score,
            'freshness': quality.freshness_score,
            'specificity': quality.specificity_score,
            'confidence': quality.confidence_level,
            'reasons': quality.quality_reasons
        }
        
        # Only include reliable results
        if quality.is_reliable and quality.overall_score >= min_quality_score:
            filtered_results.append(result)
            logger.info(f"Accepted result: {result.get('title')} (score: {quality.overall_score:.2f})")
        else:
            logger.warning(f"Filtered out: {result.get('title')} (score: {quality.overall_score:.2f})")
    
    # Sort by quality score
    filtered_results.sort(key=lambda x: x['quality_metrics']['overall_score'], reverse=True)
    
    return filtered_results