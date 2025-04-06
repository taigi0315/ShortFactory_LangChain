import praw
from typing import List, Dict, Optional
import os
from dotenv import load_dotenv
from .reddit_categories import REDDIT_CATEGORIES
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import time

class RedditFetcher:
    def __init__(self):
        load_dotenv()
        self.reddit = praw.Reddit(
            client_id=os.getenv('REDDIT_CLIENT_ID'),
            client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
            user_agent=os.getenv('REDDIT_USER_AGENT')
        )
        
        # Google Sheets 설정
        scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        
        # credentials.json 파일의 절대 경로 설정
        credentials_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'google_credentials.json')
        try:
            creds = ServiceAccountCredentials.from_json_keyfile_name(credentials_path, scope)
            self.sheets_client = gspread.authorize(creds)
            spreadsheet = self.sheets_client.open(os.getenv('GOOGLE_SHEET_NAME'))
            
            # 특정 시트 이름으로 접근
            worksheet_name = 'reddit_story'
            try:
                self.sheet = spreadsheet.worksheet(worksheet_name)
                print(f"Successfully connected to worksheet: {worksheet_name}")
            except gspread.WorksheetNotFound:
                # 시트가 없으면 새로 생성
                self.sheet = spreadsheet.add_worksheet(worksheet_name, 1000, 12)  # 열 개수를 12로 증가
                # 헤더 추가
                self.sheet.append_row([
                    'Title',
                    'URL',
                    'Score',
                    'Comments',
                    'Content',
                    'Status',
                    'Subreddit',
                    'Category',
                    'Created Date',
                    'Updated Date'
                ])
                print(f"Created new worksheet: {worksheet_name}")
                
        except Exception as e:
            print(f"Error initializing Google Sheets: {str(e)}")
            print(f"Credentials path: {credentials_path}")
            raise

    def get_categories(self) -> Dict[str, Dict]:
        """사용 가능한 카테고리 목록을 반환합니다."""
        return REDDIT_CATEGORIES

    def get_subreddits_by_category(self, category: str) -> List[Dict]:
        """특정 카테고리의 서브레딧 목록을 반환합니다."""
        if category not in REDDIT_CATEGORIES:
            raise ValueError(f"Unknown category: {category}")
        return REDDIT_CATEGORIES[category]["subreddits"]

    def fetch_popular_posts(
        self, 
        subreddit_name: str, 
        top_limit: int = 10, 
        time_filter: str = 'month'
    ) -> List[Dict]:
        """
        Reddit에서 인기 있는 게시물을 가져옵니다.
        
        Args:
            subreddit_name (str): 서브레딧 이름
            top_limit (int): 가져올 게시물 수
            time_filter (str): 시간 필터 ('day', 'week', 'month', 'year', 'all')
            
        Returns:
            List[Dict]: 게시물 정보 리스트
        """
        subreddit = self.reddit.subreddit(subreddit_name)

        # 인기 많은 순으로 정렬 (score와 댓글 수를 모두 고려)
        popular_posts = sorted(
            subreddit.top(time_filter=time_filter, limit=top_limit * 3),
            key=lambda post: (post.score, post.num_comments),
            reverse=True
        )[:top_limit]

        results = []
        for post in popular_posts:
            post_data = {
                'title': post.title,
                'url': f"https://www.reddit.com{post.permalink}",
                'score': post.score,
                'num_comments': post.num_comments,
                'content': post.selftext.strip(),
                'subreddit': subreddit_name,
                'created_utc': post.created_utc
            }
            results.append(post_data)

        return results

    def fetch_posts_from_category(
        self,
        category: str,
        posts_per_subreddit: int = 3,
        time_filter: str = 'month'
    ) -> Dict[str, List[Dict]]:
        """
        특정 카테고리의 모든 서브레딧에서 게시물을 가져옵니다.
        
        Args:
            category (str): 카테고리 이름
            posts_per_subreddit (int): 각 서브레딧당 가져올 게시물 수
            time_filter (str): 시간 필터
            
        Returns:
            Dict[str, List[Dict]]: 서브레딧별 게시물 목록
        """
        if category not in REDDIT_CATEGORIES:
            raise ValueError(f"Unknown category: {category}")

        results = {}
        for subreddit_info in REDDIT_CATEGORIES[category]["subreddits"]:
            subreddit_name = subreddit_info["name"]
            try:
                posts = self.fetch_popular_posts(
                    subreddit_name,
                    top_limit=posts_per_subreddit,
                    time_filter=time_filter
                )
                results[subreddit_name] = posts
                # 각 서브레딧의 게시물을 가져온 후 바로 시트에 업데이트
                self.update_google_sheet(posts, category)
            except Exception as e:
                print(f"Error fetching posts from r/{subreddit_name}: {str(e)}")
                results[subreddit_name] = []
            time.sleep(1)

        return results

    def update_google_sheet(self, posts: List[Dict], category: str = '') -> None:
        """
        게시물 정보를 Google Sheets에 업데이트합니다.
        
        Args:
            posts (List[Dict]): 게시물 정보 리스트
            category (str): 게시물의 카테고리
        """
        # 시트에 이미 있는 URL 목록 가져오기
        existing_urls = self.sheet.col_values(2)  # URL은 2번째 열
        
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        for post in posts:
            # 중복 체크
            if post['url'] not in existing_urls:
                # 시트에 새 행 추가
                self.sheet.append_row([
                    post['title'],
                    post['url'],
                    post['score'],
                    post['num_comments'],
                    post['content'],
                    'New',  # 상태
                    post['subreddit'],
                    category,  # 카테고리 추가
                    datetime.fromtimestamp(post['created_utc']).strftime('%Y-%m-%d %H:%M:%S'),
                    current_time  # 업데이트 시간 추가
                ])

    def get_production_posts(self) -> List[Dict]:
        """
        상태가 'production'인 게시물을 가져옵니다.
        
        Returns:
            List[Dict]: production 상태의 게시물 리스트
        """
        # 모든 행 가져오기
        all_records = self.sheet.get_all_records()
        
        # production 상태인 게시물만 필터링
        production_posts = [
            record for record in all_records 
            if record.get('Status', '').lower() == 'production'
        ]
        
        return production_posts

    def print_posts(self, posts: List[Dict]) -> None:
        """
        게시물 정보를 보기 좋게 출력합니다.
        
        Args:
            posts (List[Dict]): 게시물 정보 리스트
        """
        for i, post in enumerate(posts, 1):
            print(f"🔖 {i}. {post['title']}")
            print(f"🔗 {post['url']}")
            print(f"👍 Upvotes: {post['score']} | 💬 Comments: {post['num_comments']}")
            print(f"📖 Content Preview: {post['content'][:300]}...\n{'='*60}\n")

    def print_category_posts(self, category_posts: Dict[str, List[Dict]]) -> None:
        """
        카테고리별 게시물을 보기 좋게 출력합니다.
        
        Args:
            category_posts (Dict[str, List[Dict]]): 서브레딧별 게시물 목록
        """
        for subreddit, posts in category_posts.items():
            print(f"\n{'='*80}")
            print(f"📌 r/{subreddit}")
            print(f"{'='*80}\n")
            self.print_posts(posts) 
