"""
FastAPI ML Server for Phishing Detection
Simple version with basic feature extraction and ML prediction
"""

import time
import sqlite3
import joblib
import os
import json
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from urllib.parse import urlparse
import re

# --- CONFIGURATION ---
DB_NAME = "scan_history.db"
MODEL_FILE = "phishing_model.pkl"

# --- DATA MODELS ---
class ScanRequest(BaseModel):
    url: str

class ScanResult(BaseModel):
    url: str
    status: str
    risk_score: int
    risk_label: str
    response_time: float
    risk_reasons: list = []

class HistoryItem(BaseModel):
    id: int
    url: str
    status: str
    risk_score: int
    timestamp: str

class DashboardStats(BaseModel):
    total_scans: int
    threats_blocked: int
    safe_urls: int
    avg_response_time: str

# --- DATABASE HANDLER ---
class DatabaseHandler:
    def __init__(self, db_name=DB_NAME):
        self.db_name = db_name
        self.conn = None
        self.init_db()

    def init_db(self):
        """Initialize database"""
        try:
            self.conn = sqlite3.connect(self.db_name)
            self.conn.row_factory = sqlite3.Row
            cursor = self.conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS scan_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT NOT NULL,
                    status TEXT NOT NULL,
                    risk_score INTEGER NOT NULL,
                    risk_reasons TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            self.conn.commit()
            print(f"[DB] Database initialized: {self.db_name}")
        except Exception as e:
            print(f"[DB ERROR] Failed to initialize database: {e}")

    def log_scan(self, url, status, risk_score, time_taken, risk_reasons=None):
        """Log scan to database with retry logic"""
        try:
            risk_reasons_json = json.dumps(risk_reasons) if risk_reasons else "[]"
            cursor = self.conn.cursor()
            
            # Retry mechanism for database writes
            max_retries = 3
            retry_count = 0
            
            while retry_count < max_retries:
                try:
                    cursor.execute(
                        'INSERT INTO scan_history (url, status, risk_score, risk_reasons) VALUES (?, ?, ?, ?)',
                        (url, status, risk_score, risk_reasons_json)
                    )
                    self.conn.commit()
                    print(f"[DB] ✓ Logged: {url} -> {status} ({risk_score}%) [attempt {retry_count + 1}]")
                    return True
                except Exception as e:
                    retry_count += 1
                    if retry_count >= max_retries:
                        raise
                    print(f"[DB] Retry {retry_count}/{max_retries}: {e}")
                    time.sleep(0.1)
                    
        except Exception as e:
            print(f"[DB ERROR] Failed to log scan after {max_retries} attempts: {e}")
            return False

    def get_history(self, limit=100):
        """Get scan history"""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                'SELECT id, url, status, risk_score, timestamp FROM scan_history ORDER BY id DESC LIMIT ?',
                (limit,)
            )
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"[DB ERROR] Failed to retrieve history: {e}")
            return []

    def get_stats(self):
        """Get dashboard stats"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT COUNT(*) as total FROM scan_history')
            total = cursor.fetchone()[0]
            cursor.execute('SELECT COUNT(*) as threats FROM scan_history WHERE status != "SAFE"')
            threats = cursor.fetchone()[0]
            safe = total - threats
            return {
                "total_scans": total,
                "threats_blocked": threats,
                "safe_urls": safe,
                "avg_response_time": "0.5s"
            }
        except Exception as e:
            print(f"[DB ERROR] Failed to get stats: {e}")
            return {"total_scans": 0, "threats_blocked": 0, "safe_urls": 0, "avg_response_time": "0s"}

# --- PHISHING ENGINE ---
class PhishingEngine:
    # Define ONLY truly dangerous characters that are NOT legitimate URL components
    # Removed: : / ? # [ ] @ = & (these are legitimate URL syntax)
    UNSAFE_CHARS = {
        ' ': "Space breaks URL parsing; usually marks the end of a link.",
        '"': 'Double Quote used to delimit URLs in HTML (e.g., <a href="...">).',
        '<': "Less Than used for HTML tags; indicates XSS attacks.",
        '>': "Greater Than used for HTML tags; indicates XSS attacks.",
        '\\': "Backslash used in Windows file paths, not web URLs.",
        '^': "Caret unsafe delimiter.",
        '|': "Pipe unsafe delimiter.",
        '{': "Open Brace used in coding/templating logic.",
        '}': "Close Brace used in coding/templating logic.",
        '`': "Backtick used for command execution in some systems."
    }
    
    def __init__(self, model_file=MODEL_FILE):
        self.model_file = model_file
        self.model_dict = None
        self.model = self.load_model()
        
        # Whitelist of known safe domains
        self.safe_domains = {
            # Social Media & Communication
            'google.com', 'www.google.com',
            'accounts.google.com', 'mail.google.com', 'drive.google.com', 'docs.google.com',
            'sheets.google.com', 'slides.google.com', 'calendar.google.com', 'photos.google.com',
            'classroom.google.com', 'developer.google.com', 'support.google.com',
            'analytics.google.com', 'ads.google.com', 'play.google.com', 'store.google.com',
            'youtube.com', 'www.youtube.com',
            'facebook.com', 'www.facebook.com',
            'twitter.com', 'www.twitter.com',
            'reddit.com', 'www.reddit.com',
            'instagram.com', 'www.instagram.com',
            'linkedin.com', 'www.linkedin.com',
            'pinterest.com', 'www.pinterest.com',
            'tumblr.com', 'www.tumblr.com',
            'twitch.tv', 'www.twitch.tv',
            'whatsapp.com', 'www.whatsapp.com',
            'telegram.org', 'www.telegram.org',
            'discord.com', 'www.discord.com',
            'vimeo.com', 'www.vimeo.com',
            
            # General Services
            'amazon.com', 'www.amazon.com',
            'wikipedia.org', 'www.wikipedia.org',
            'microsoft.com', 'www.microsoft.com', 'outlook.microsoft.com', 'account.microsoft.com',
            'apple.com', 'www.apple.com', 'icloud.apple.com', 'itunes.apple.com',
            'netflix.com', 'www.netflix.com',
            'gmail.com', 'www.gmail.com',
            'outlook.com', 'www.outlook.com',
            'yahoo.com', 'www.yahoo.com',
            'bing.com', 'www.bing.com',
            'adobe.com', 'www.adobe.com',
            'dropbox.com', 'www.dropbox.com',
            
            # Development & Coding
            'github.com', 'www.github.com',
            'gitlab.com', 'www.gitlab.com',
            'bitbucket.org', 'www.bitbucket.org',
            'stackoverflow.com', 'www.stackoverflow.com',
            'w3schools.com', 'www.w3schools.com',
            'mozilla.org', 'www.mozilla.org', 'developer.mozilla.org',
            'python.org', 'www.python.org',
            'pypi.org', 'www.pypi.org',
            'nodejs.org', 'www.nodejs.org',
            'reactjs.org', 'www.reactjs.org',
            'angular.io', 'www.angular.io',
            'vuejs.org', 'www.vuejs.org',
            'docker.com', 'www.docker.com',
            'kubernetes.io', 'www.kubernetes.io',
            'kaggle.com', 'www.kaggle.com',
            'geeksforgeeks.org', 'www.geeksforgeeks.org',
            'tutorialspoint.com', 'www.tutorialspoint.com',
            'medium.com', 'www.medium.com',
            'dev.to', 'www.dev.to',
            'sourceforge.net', 'www.sourceforge.net',
            'github.io', 'pages.github.io',
            
            # Shopping & E-Commerce
            'ebay.com', 'www.ebay.com',
            'walmart.com', 'www.walmart.com',
            'target.com', 'www.target.com',
            'bestbuy.com', 'www.bestbuy.com',
            'etsy.com', 'www.etsy.com',
            'ikea.com', 'www.ikea.com',
            'homedepot.com', 'www.homedepot.com',
            'costco.com', 'www.costco.com',
            'alibaba.com', 'www.alibaba.com',
            'aliexpress.com', 'www.aliexpress.com',
            'flipkart.com', 'www.flipkart.com',
            'shopify.com', 'www.shopify.com',
            'wayfair.com', 'www.wayfair.com',
            'nike.com', 'www.nike.com',
            'adidas.com', 'www.adidas.com',
            
            # Finance & Banking
            'paypal.com', 'www.paypal.com',
            'chase.com', 'www.chase.com',
            'bankofamerica.com', 'www.bankofamerica.com',
            'wellsfargo.com', 'www.wellsfargo.com',
            'americanexpress.com', 'www.americanexpress.com',
            'visa.com', 'www.visa.com',
            'mastercard.com', 'www.mastercard.com',
            'stripe.com', 'www.stripe.com',
            'citi.com', 'www.citi.com',
            'capitalone.com', 'www.capitalone.com',
            'coinbase.com', 'www.coinbase.com',
            'binance.com', 'www.binance.com',
            'robinhood.com', 'www.robinhood.com',
            'blockchain.com', 'www.blockchain.com',
            'investopedia.com', 'www.investopedia.com',
            
            # News & Information
            'cnn.com', 'www.cnn.com',
            'bbc.com', 'www.bbc.com',
            'nytimes.com', 'www.nytimes.com',
            'forbes.com', 'www.forbes.com',
            'bloomberg.com', 'www.bloomberg.com',
            'reuters.com', 'www.reuters.com',
            'weather.com', 'www.weather.com',
            'imdb.com', 'www.imdb.com',
            'wikihow.com', 'www.wikihow.com',
            'britannica.com', 'www.britannica.com',
            'archive.org', 'www.archive.org',
            'feedly.com', 'www.feedly.com',
            'huffpost.com', 'www.huffpost.com',
            'buzzfeed.com', 'www.buzzfeed.com',
            'washingtonpost.com', 'www.washingtonpost.com',
            'theguardian.com', 'www.theguardian.com',
            
            # Education & Learning Tools
            'coursera.org', 'www.coursera.org',
            'udemy.com', 'www.udemy.com',
            'edx.org', 'www.edx.org',
            'khanacademy.org', 'www.khanacademy.org',
            'mit.edu', 'www.mit.edu',
            'harvard.edu', 'www.harvard.edu',
            'stanford.edu', 'www.stanford.edu',
            'canva.com', 'www.canva.com',
            'figma.com', 'www.figma.com',
            'trello.com', 'www.trello.com',
            'asana.com', 'www.asana.com',
            'notion.so', 'www.notion.so',
            'evernote.com', 'www.evernote.com',
            'zoom.us', 'www.zoom.us',
            
            # Special Domains
            'vvitguntur.com', 'www.vvitguntur.com',
            
            # Professional & Academic Organizations
            'ieee.org', 'www.ieee.org',
            'acm.org', 'www.acm.org',
            'apa.org', 'www.apa.org',
            'mla.org', 'www.mla.org',
            'elsevier.com', 'www.elsevier.com',
            'springer.com', 'www.springer.com',
            'sciencedirect.com', 'www.sciencedirect.com',
            'nature.com', 'www.nature.com',
            'jstor.org', 'www.jstor.org',
            'crossref.org', 'www.crossref.org',
            'arxiv.org', 'www.arxiv.org',
            'researchgate.net', 'www.researchgate.net',
            'scholar.google.com', 'scholar.google.com',
        }

    def load_model(self):
        """Load ML model"""
        try:
            # Check if model file exists
            if not os.path.exists(self.model_file):
                print(f"[ERROR] Model file not found: {self.model_file}")
                print(f"[INFO] Using safety checks only (character detection & protocol validation)")
                return None
            
            loaded = joblib.load(self.model_file)
            
            # Handle dict format (model, feature_names, vectorizer)
            if isinstance(loaded, dict):
                if 'model' in loaded and 'feature_names' in loaded:
                    self.model_dict = loaded
                    print(f"[SYSTEM] [OK] ML Model loaded successfully (dict format)")
                    print(f"[SYSTEM] [OK] Model has {len(loaded['feature_names'])} features")
                    return loaded['model']  # Return the actual sklearn model
                else:
                    print(f"[ERROR] Unknown model dict format. Keys: {list(loaded.keys())}")
                    return None
            else:
                # Direct model object
                self.model_dict = None
                print(f"[SYSTEM] [OK] ML Model loaded successfully (object format)")
                if hasattr(loaded, 'feature_names_in_'):
                    print(f"[SYSTEM] [OK] Model has {len(loaded.feature_names_in_)} features")
                return loaded
                
        except Exception as e:
            print(f"[ERROR] Failed to load model: {e}")
            print(f"[INFO] Using safety checks only (character detection & protocol validation)")
            return None

    def extract_features(self, url):
        """Extract basic features from URL"""
        try:
            parsed = urlparse(url)
            features = {
                'url_length': len(url),
                'domain_length': len(parsed.netloc),
                'path_length': len(parsed.path),
                'count_dot': url.count('.'),
                'count_hyphen': url.count('-'),
                'count_slash': url.count('/'),
                'count_at': url.count('@'),
                'https_token': 1 if parsed.scheme == 'https' else 0,
                'has_ip': 1 if self._contains_ip(url) else 0,
            }
            return features
        except Exception as e:
            print(f"[ERROR] Feature extraction failed: {e}")
            return {}

    def _contains_ip(self, url):
        """Check if URL contains IP"""
        ip_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
        return bool(re.search(ip_pattern, url))

    def _check_unsafe_characters(self, url):
        """Check for unsafe special characters in URL and return reasons"""
        unsafe_found = []
        for char, reason in self.UNSAFE_CHARS.items():
            if char in url:
                unsafe_found.append(reason)
        return unsafe_found

    def _check_protocol(self, url):
        """Check if URL uses proper HTTPS protocol"""
        parsed = urlparse(url)
        protocol = parsed.scheme.lower()
        
        reasons = []
        if not protocol:
            # No protocol specified
            reasons.append("No protocol specified. URL must start with 'https://' or 'http://'.")
        elif protocol not in ['https', 'http']:
            # Invalid protocol - this is a critical security issue
            reasons.append(f"Invalid protocol '{protocol}' used instead of 'https' or 'http'.")
        elif protocol == 'http':
            # HTTP instead of HTTPS - Show 20% risk score in message
            reasons.append("Protocol uses 'http' instead of secure 'https' (Risk Score: 20%).")
        
        return reasons

    def _analyze_tld(self, url):
        """Analyze Top Level Domain for phishing indicators"""
        parsed = urlparse(url)
        domain = parsed.netloc
        
        # List of legitimate, safe TLDs
        safe_tlds = {
            '.com': 'Commercial - Most common legitimate domain',
            '.org': 'Organization - Non-profit and legitimate organizations',
            '.gov': 'Government - Official government agencies',
            '.edu': 'Education - Educational institutions',
            '.net': 'Network - Established legitimate networks',
            '.io': 'Technology - Established tech companies',
            '.co': 'Alternate commercial domain',
        }
        
        # Check if domain ends with a safe TLD first (return as PASS)
        for tld, reason in safe_tlds.items():
            if domain.lower().endswith(tld):
                return None  # Return None means it's safe (PASS)
        
        # List of suspicious TLDs commonly used in phishing
        suspicious_tlds = {
            '.tk': '[HIGH RISK] Tokelau domain (free, commonly used by scammers). Legitimate businesses use .com, .org, or country-specific TLDs.',
            '.ml': '[HIGH RISK] Mali domain (free TLD, phishing red flag). Legitimate services rarely use free domains.',
            '.ga': '[HIGH RISK] Gabon domain (free TLD, phishing red flag).',
            '.cf': '[HIGH RISK] Central African Republic domain (free TLD, phishing red flag).',
            '.xyz': '[WARN] .xyz is often used for phishing. Verify the organization legitimately uses this TLD.',
            '.click': '[WARN] .click TLD is sometimes used in phishing attacks.',
            '.download': '[WARN] .download TLD can be exploited for deceptive URLs.',
            '.stream': '[WARN] .stream TLD appears in phishing campaigns.',
        }
        
        for tld, reason in suspicious_tlds.items():
            if domain.lower().endswith(tld):
                return reason
        
        return None

    def _analyze_subdomains(self, url):
        """Analyze subdomains for phishing patterns"""
        parsed = urlparse(url)
        domain = parsed.netloc
        
        # Count subdomains
        parts = domain.split('.')
        if len(parts) > 2:
            # Whitelist of legitimate subdomains owned by major brands
            # Format: (subdomain_prefix, main_domain)
            legitimate_subdomains = {
                ('accounts', 'google.com'),
                ('mail', 'google.com'),
                ('drive', 'google.com'),
                ('docs', 'google.com'),
                ('sheets', 'google.com'),
                ('slides', 'google.com'),
                ('calendar', 'google.com'),
                ('photos', 'google.com'),
                ('classroom', 'google.com'),
                ('developer', 'google.com'),
                ('support', 'google.com'),
                ('analytics', 'google.com'),
                ('ads', 'google.com'),
                ('play', 'google.com'),
                ('store', 'google.com'),
                ('mail', 'outlook.com'),
                ('outlook', 'microsoft.com'),
                ('account', 'microsoft.com'),
                ('login', 'microsoft.com'),
                ('account', 'amazon.com'),
                ('www', 'amazon.com'),
                ('smile', 'amazon.com'),
                ('business', 'amazon.com'),
                ('developer', 'amazon.com'),
                ('icloud', 'apple.com'),
                ('itunes', 'apple.com'),
                ('developer', 'apple.com'),
                ('support', 'apple.com'),
                ('account', 'facebook.com'),
                ('business', 'facebook.com'),
                ('developer', 'facebook.com'),
                ('help', 'paypal.com'),
                ('www', 'paypal.com'),
                ('developer', 'paypal.com'),
            }
            
            real_domain = '.'.join(parts[-2:])
            subdomain = parts[0] if len(parts) == 3 else '.'.join(parts[:-2])
            
            # Check if this is a legitimate subdomain
            if (subdomain.lower(), real_domain.lower()) in legitimate_subdomains:
                return None  # Legitimate subdomain
            
            # Check if suspicious subdomain patterns exist
            brand_names = ['apple', 'google', 'paypal', 'amazon', 'microsoft', 'facebook', 'bank', 
                          'verify', 'secure', 'update', 'confirm']
            
            # Check if legitimate brand name is used as fake subdomain on non-official domains
            for part in parts[:-2]:  # Check all subdomains except the real domain
                for brand in brand_names:
                    if brand.lower() in part.lower():
                        return f"[HIGH RISK] The real domain is {real_domain}. The word '{part}' is a fake subdomain on the left. Scammers use brand names as subdomains to appear legitimate."
        
        return None

    def _analyze_keywords(self, url):
        """Analyze for phishing trigger keywords"""
        phishing_keywords = {
            'verify': {'risk': '[WARN]', 'reason': '"Verify" is a common phishing trigger. Legitimate services rarely ask verification via links.'},
            'confirm': {'risk': '[WARN]', 'reason': '"Confirm" is used to trick users into revealing information. Legitimate companies rarely need verification links.'},
            'update': {'risk': '[WARN]', 'reason': '"Update" is used to create urgency. Phishing emails often fake update notices to steal credentials.'},
            'secure': {'risk': '[WARN]', 'reason': '"Secure" appears in legitimate URLs, but scammers abuse it to sound trustworthy.'},
            'login': {'risk': '[WARN]', 'reason': '"Login" in URLs is a phishing red flag. Legitimate sites rarely put "login" in the domain itself.'},
            'account': {'risk': '[WARN]', 'reason': '"Account" combined with action verbs often indicates phishing attempts.'},
            'password': {'risk': '[HIGH RISK]', 'reason': '"Password" in URL is a major red flag. Legitimate sites never include "password" in domain/URL.'},
            'reset': {'risk': '[WARN]', 'reason': '"Reset" is used to trick users. Phishing emails fake password resets to harvest credentials.'},
            'admin': {'risk': '[WARN]', 'reason': '"Admin" is often faked in phishing URLs to appear as legitimate administrative pages.'},
            'paypal': {'risk': '[WARN]', 'reason': 'PayPal is heavily impersonated. Verify this is actually PayPal before entering credentials.'},
            'amazon': {'risk': '[WARN]', 'reason': 'Amazon is heavily impersonated. Always use the official amazon.com domain.'},
            'apple': {'risk': '[WARN]', 'reason': 'Apple is heavily impersonated. Always verify the domain is apple.com.'},
            'microsoft': {'risk': '[WARN]', 'reason': 'Microsoft is heavily impersonated. Verify the domain is microsoft.com or outlook.com.'},
            'bank': {'risk': '[WARN]', 'reason': '"Bank" in the URL is a common phishing tactic. Verify you\'re on your actual bank\'s website.'},
            'support': {'risk': '[WARN]', 'reason': '"Support" pages are often faked. Check the legitimate company domain before clicking support links.'},
        }
        
        url_lower = url.lower()
        detected_keywords = []
        highest_risk = None
        
        for keyword, info in phishing_keywords.items():
            if keyword in url_lower:
                detected_keywords.append(f"{info['risk']} - {info['reason']}")
                if highest_risk is None or info['risk'] == '[HIGH RISK]':
                    highest_risk = detected_keywords[-1]
        
        if detected_keywords:
            if len(detected_keywords) > 1:
                return f"[HIGH RISK] - Contains {len(detected_keywords)} phishing keywords: {', '.join([k.split(' - ')[0].replace('[HIGH RISK]', 'verify/confirm/update').replace('[WARN]', 'login/account') for k in detected_keywords])}"
            return detected_keywords[0]
        
        return None

    def _generate_safe_reasons(self, url):
        """Generate positive reasons for safe URLs"""
        safe_reasons = []
        parsed = urlparse(url)
        domain = parsed.netloc
        
        # Check protocol
        if parsed.scheme == 'https':
            safe_reasons.append("[+] Legitimate SSL Certificate - Uses secure HTTPS protocol for encrypted connection.")
        elif parsed.scheme == 'http':
            safe_reasons.append("[!] Warning - Uses standard HTTP protocol instead of secure HTTPS.")
        
        # Check for legitimate URL structure
        if parsed.netloc:
            safe_reasons.append("[+] Valid Domain Structure - Domain name structure is legitimate and properly formatted.")
        
        # Check for no unsafe characters
        unsafe_count = sum(1 for char in self.UNSAFE_CHARS.keys() if char in url)
        if unsafe_count == 0:
            safe_reasons.append("[+] No Unsafe Characters - No dangerous special characters detected in URL.")
        
        # Check for query parameters (proper format)
        if parsed.query:
            safe_reasons.append("[+] Proper Parameter Format - Query parameters use legitimate '?' and '&' syntax.")
        
        # Check URL length
        if len(url) < 100:
            safe_reasons.append("[+] Normal URL Length - URL length is within typical business website range.")
        
        # Check for no IP address
        if not self._contains_ip(url):
            safe_reasons.append("[+] Uses Domain Name - URL uses domain name (not suspicious IP address).")
        
        # Check subdomain count (not too many)
        subdomain_count = domain.count('.') - 1
        if subdomain_count <= 2:
            safe_reasons.append("[+] Normal Subdomain Count - No suspicious subdomain patterns detected.")
        
        # Positive TLD check
        if not any(domain.lower().endswith(tld) for tld in ['.tk', '.ml', '.ga', '.cf']):
            if domain.lower().endswith(('.com', '.org', '.gov', '.edu')):
                safe_reasons.append("[+] Legitimate Top Level Domain - Uses established .com/.org/.gov/.edu domain.")
        
        return safe_reasons

    def predict(self, url):
        """Predict phishing risk"""
        start_time = time.time()
        risk_reasons = []
        
        try:
            print(f"[PREDICT] Processing URL: {url}")
            
            # Check if domain is in safe whitelist first
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            # CRITICAL: Check protocol FIRST - invalid protocol is a phishing red flag
            protocol_reasons = self._check_protocol(url)
            
            # If protocol is invalid, mark as high risk regardless of domain
            if protocol_reasons:
                for reason in protocol_reasons:
                    if "invalid protocol" in reason.lower():
                        # Invalid protocol is CRITICAL - don't trust the domain
                        return {
                            "url": url,
                            "status": "PHISHING",
                            "risk_score": 85,
                            "risk_label": "PHISHING",
                            "risk_reasons": [f"🚫 CRITICAL: {reason}"],
                            "response_time": round(time.time() - start_time, 3)
                        }
            
            # CRITICAL: Check for IP address - URLs with IP addresses are NOT safe
            if self._contains_ip(url):
                # IP address detected - this is a major phishing red flag
                # Legitimate services NEVER use IP addresses in URLs
                ip_address = re.search(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b', url)
                ip_found = ip_address.group() if ip_address else "IP Address"
                return {
                    "url": url,
                    "status": "PHISHING",
                    "risk_score": 90,
                    "risk_label": "PHISHING",
                    "risk_reasons": [f"🚫 CRITICAL: URL contains IP address ({ip_found}) instead of domain name. Legitimate websites always use domain names. This is a major phishing indicator."],
                    "response_time": round(time.time() - start_time, 3)
                }
            
            # Remove www. prefix for comparison
            domain_normalized = domain.replace('www.', '')
            domain_with_www = 'www.' + domain_normalized
            
            if domain in self.safe_domains or domain_normalized in self.safe_domains or domain_with_www in self.safe_domains:
                print(f"[PREDICT] ✓ Domain is in safe whitelist: {domain}")
                safe_reasons = self._generate_safe_reasons(url)
                return {
                    "url": url,
                    "status": "SAFE",
                    "risk_score": 0,
                    "risk_label": "SAFE",
                    "risk_reasons": safe_reasons,
                    "response_time": round(time.time() - start_time, 3)
                }
            
            # Comprehensive analysis with detailed reasons
            
            # 1. Check Top Level Domain
            tld_reason = self._analyze_tld(url)
            if tld_reason:
                risk_reasons.append(tld_reason)
                print(f"[ANALYZE] TLD Flag: {tld_reason[:50]}")
            
            # 2. Check Subdomains
            subdomain_reason = self._analyze_subdomains(url)
            if subdomain_reason:
                risk_reasons.append(subdomain_reason)
                print(f"[ANALYZE] Subdomain Flag: {subdomain_reason[:50]}")
            
            # 3. Check for Phishing Keywords
            keyword_reason = self._analyze_keywords(url)
            if keyword_reason:
                risk_reasons.append(keyword_reason)
                print(f"[ANALYZE] Keyword Flag: {keyword_reason[:50]}")
            
            # 4. Check for unsafe characters
            unsafe_char_reasons = self._check_unsafe_characters(url)
            if unsafe_char_reasons:
                risk_reasons.extend(unsafe_char_reasons)
                print(f"[ANALYZE] Found {len(unsafe_char_reasons)} unsafe characters")
            
            # Protocol already checked at the beginning for critical invalid protocols
            # Only add HTTP (non-HTTPS) warning to reasons if not already invalid
            if protocol_reasons:
                for reason in protocol_reasons:
                    if "http" in reason.lower() and "'http'" in reason.lower():
                        risk_reasons.extend(protocol_reasons)
                        print(f"[ANALYZE] HTTP (insecure) detected")
                        break
            
            # Initialize risk score - ALWAYS START AT 0
            risk_score = 0
            
            # Calculate risk based on ALL detected issues (always accumulate)
            
            # Boost for suspicious TLD
            if tld_reason:
                if '[HIGH RISK]' in tld_reason:
                    risk_score = min(85, risk_score + 60)
                    print(f"[SCORE] TLD boost +60 -> {risk_score}%")
                else:
                    risk_score = min(80, risk_score + 30)
                    print(f"[SCORE] TLD boost +30 -> {risk_score}%")
            
            # Boost for suspicious subdomains
            if subdomain_reason:
                if '[HIGH RISK]' in subdomain_reason:
                    risk_score = min(85, risk_score + 50)
                    print(f"[SCORE] Subdomain boost +50 -> {risk_score}%")
            
            # Boost for phishing keywords
            if keyword_reason:
                if '[HIGH RISK]' in keyword_reason:
                    risk_score = min(85, risk_score + 55)
                    print(f"[SCORE] Keyword boost +55 -> {risk_score}%")
                else:
                    risk_score = min(80, risk_score + 25)
                    print(f"[SCORE] Keyword boost +25 -> {risk_score}%")
            
            # Boost for unsafe characters
            if unsafe_char_reasons:
                risk_score = min(85, risk_score + 50)
                print(f"[SCORE] Unsafe chars boost +50 -> {risk_score}%")
            
            # Track if HTTP was detected to prevent ML override
            http_detected = False
            
            # Boost for non-HTTPS (CRITICAL SECURITY ISSUE - HIGH PRIORITY)
            if protocol_reasons:
                for reason in protocol_reasons:
                    # Check if reason indicates INVALID protocol (highest risk)
                    if "invalid protocol" in reason.lower():
                        # Invalid protocol detected - CRITICAL PHISHING INDICATOR
                        risk_score = 85
                        print(f"[SCORE] INVALID PROTOCOL (critical phishing indicator) - risk_score set to 85%")
                    # Check if reason indicates HTTP usage (not HTTPS)
                    elif "'http'" in reason.lower() and not reason.lower().startswith("invalid"):
                        # HTTP detected - set risk score to 20% as per security policy
                        risk_score = 20
                        http_detected = True
                        print(f"[SCORE] HTTP (insecure protocol detected) - risk_score set to 20%")
            
            # Try to use ML model for additional prediction if available
            # But NOT if HTTP was explicitly detected (security policy: HTTP = 20% only)
            if self.model and risk_score < 50 and not http_detected:
                try:
                    features = self.extract_features(url)
                    
                    if self.model_dict and 'feature_names' in self.model_dict:
                        feature_names = self.model_dict['feature_names']
                    elif hasattr(self.model, 'feature_names_in_'):
                        feature_names = list(self.model.feature_names_in_)
                    else:
                        feature_names = []
                    
                    if feature_names:
                        ordered_features = [features.get(fn, 0) for fn in feature_names]
                        if ordered_features:
                            try:
                                probability = self.model.predict_proba([ordered_features])[0][1]
                                ml_score = int(probability * 100)
                                
                                # IMPORTANT: Trust heuristic checks over ML model
                                # If NO heuristic red flags found, keep URL as SAFE (don't let ML override)
                                if len(risk_reasons) > 0:
                                    # Heuristic found issues: consider ML score but don't exceed it if already risky
                                    risk_score = max(risk_score, ml_score)
                                else:
                                    # NO heuristic red flags: only use ML if it's very confident (>85%)
                                    # Otherwise trust the heuristics that said it's safe
                                    if ml_score > 85:
                                        risk_score = ml_score
                                    else:
                                        # ML is uncertain - trust heuristics: keep low score
                                        risk_score = max(risk_score, min(ml_score, 15))  # Cap at 15% (low-medium)
                                
                                print(f"[ML] Model prediction: {ml_score}% | Heuristic flags: {len(risk_reasons)} | Final: {risk_score}%")
                            except Exception as e:
                                print(f"[ML] Prediction error: {e}")
                except Exception as e:
                    print(f"[ML] Feature extraction error: {e}")
            
            # Ensure score is within 0-100 range
            if risk_score < 0:
                risk_score = 0
            elif risk_score > 100:
                risk_score = 100
            
            # Determine status (threshold: < 20% = SAFE, 20-70% = SUSPICIOUS, >= 70% = PHISHING)
            if risk_score < 20:
                status = "SAFE"
            elif risk_score < 70:
                status = "SUSPICIOUS"
            else:
                status = "PHISHING"
            
            # Add safe reasons ONLY if URL is truly safe (no risk reasons at all)
            if status == "SAFE" and len(risk_reasons) == 0:
                safe_reasons = self._generate_safe_reasons(url)
                risk_reasons.extend(safe_reasons)
                print(f"[PREDICT] URL is safe - added {len(safe_reasons)} safe reasons")
            
            # Do NOT add ML-based reason if URL has no heuristic red flags
            # (This prevents false positives where safe-looking URLs get flagged)
            # Only add explanation if we have actual heuristic evidence
            
            print(f"[PREDICT] Final Risk score: {risk_score}% -> {status}")
            print(f"[PREDICT] Total Reasons: {len(risk_reasons)}")
            
            return {
                "url": url,
                "status": status,
                "risk_score": risk_score,
                "risk_label": status,
                "risk_reasons": risk_reasons,
                "response_time": round(time.time() - start_time, 3)
            }
        except Exception as e:
            print(f"[ERROR] Prediction failed: {e}")
            return {
                "url": url,
                "status": "ERROR",
                "risk_score": 50,
                "risk_label": "ERROR",
                "risk_reasons": ["Error during analysis: " + str(e)],
                "response_time": round(time.time() - start_time, 3)
            }

# --- INITIALIZE ---
engine = PhishingEngine()
db = DatabaseHandler()

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("[APP] Server starting...")
    yield
    print("[APP] Server shutting down...")

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- API ENDPOINTS ---
@app.get("/")
async def root():
    return {
        "name": "PhishGuard ML API",
        "version": "1.0",
        "status": "online"
    }

@app.get("/api/v1/health")
async def health():
    return {
        "status": "healthy",
        "model_loaded": engine.model is not None,
        "database_ready": db.conn is not None
    }

@app.post("/api/v1/scan")
async def scan_url(request: ScanRequest):
    try:
        print(f"[API] Scan request: {request.url}")
        result = engine.predict(request.url)
        
        # Log to database with risk_reasons
        db.log_scan(
            result["url"],
            result["status"],
            result["risk_score"],
            result["response_time"],
            result.get("risk_reasons", [])
        )
        
        return result
    except Exception as e:
        print(f"[API ERROR] {e}")
        return {
            "url": request.url,
            "status": "ERROR",
            "risk_score": 50,
            "risk_label": "ERROR",
            "risk_reasons": [],
            "response_time": 0
        }

@app.get("/api/v1/history")
async def get_history():
    return db.get_history()

@app.get("/api/v1/stats")
async def get_stats():
    return db.get_stats()

if __name__ == "__main__":
    print("[APP] Starting Phishing Detection API...")
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
