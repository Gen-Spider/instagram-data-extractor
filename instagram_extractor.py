#!/usr/bin/env python3
"""
Instagram Data Extractor
Extracts posts, followers, following, and profile data from Instagram
"""

import os
import json
import time
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd
from tqdm import tqdm
from PIL import Image
from instagrapi import Client
from instagrapi.exceptions import (
    BadPassword, ReloginAttemptExceeded, ChallengeRequired,
    FeedbackRequired, PleaseWaitFewMinutes, LoginRequired
)
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class InstagramExtractor:
    def __init__(self):
        self.client = Client()
        self.username = os.getenv('INSTAGRAM_USERNAME')
        self.password = os.getenv('INSTAGRAM_PASSWORD')
        self.session_file = os.getenv('SESSION_FILE', 'instagram_session.json')
        self.output_dir = Path(os.getenv('OUTPUT_DIR', './extracted_data'))
        self.request_delay = int(os.getenv('REQUEST_DELAY', '2'))
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('instagram_extractor.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Create output directories
        self.setup_directories()
    
    def setup_directories(self):
        """Create necessary directories for data storage"""
        directories = [
            self.output_dir,
            self.output_dir / 'profiles',
            self.output_dir / 'posts',
            self.output_dir / 'stories',
            self.output_dir / 'media',
            self.output_dir / 'json_data'
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def login(self) -> bool:
        """Login to Instagram with session management"""
        try:
            # Try to load existing session
            if os.path.exists(self.session_file):
                self.client.load_settings(self.session_file)
                self.client.login(self.username, self.password)
                self.logger.info("Logged in using existing session")
                return True
        except Exception as e:
            self.logger.warning(f"Failed to load session: {e}")
        
        try:
            # Fresh login
            self.client.login(self.username, self.password)
            self.client.dump_settings(self.session_file)
            self.logger.info("Successfully logged in with fresh session")
            return True
            
        except BadPassword:
            self.logger.error("Invalid username or password")
        except ReloginAttemptExceeded:
            self.logger.error("Too many login attempts")
        except ChallengeRequired as e:
            self.logger.error(f"Challenge required: {e}")
        except Exception as e:
            self.logger.error(f"Login failed: {e}")
        
        return False
    
    def get_user_info(self, username: str) -> Optional[Dict]:
        """Get user profile information"""
        try:
            time.sleep(self.request_delay)
            user_info = self.client.user_info_by_username(username)
            
            # Convert to serializable format
            user_data = {
                'pk': str(user_info.pk),
                'username': user_info.username,
                'full_name': user_info.full_name,
                'biography': user_info.biography,
                'external_url': user_info.external_url,
                'follower_count': user_info.follower_count,
                'following_count': user_info.following_count,
                'media_count': user_info.media_count,
                'is_private': user_info.is_private,
                'is_verified': user_info.is_verified,
                'profile_pic_url': user_info.profile_pic_url,
                'extracted_at': datetime.now().isoformat()
            }
            
            self.logger.info(f"Retrieved user info for {username}")
            return user_data
            
        except Exception as e:
            self.logger.error(f"Failed to get user info for {username}: {e}")
            return None
    
    def download_media(self, media_url: str, filename: str) -> bool:
        """Download media file from URL"""
        try:
            import requests
            response = requests.get(media_url, stream=True)
            response.raise_for_status()
            
            filepath = self.output_dir / 'media' / filename
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            return True
        except Exception as e:
            self.logger.error(f"Failed to download media {filename}: {e}")
            return False
    
    def get_user_posts(self, username: str, limit: int = 100) -> List[Dict]:
        """Extract user posts"""
        try:
            user_id = self.client.user_id_from_username(username)
            medias = self.client.user_medias(user_id, amount=limit)
            
            posts_data = []
            
            for media in tqdm(medias, desc=f"Processing {username}'s posts"):
                time.sleep(self.request_delay)
                
                post_data = {
                    'id': str(media.id),
                    'code': media.code,
                    'taken_at': media.taken_at.isoformat() if media.taken_at else None,
                    'media_type': str(media.media_type),
                    'caption': media.caption_text if hasattr(media, 'caption_text') else '',
                    'like_count': media.like_count,
                    'comment_count': media.comment_count,
                    'play_count': getattr(media, 'play_count', 0),
                    'thumbnail_url': str(media.thumbnail_url) if media.thumbnail_url else '',
                    'resources': []
                }
                
                # Download media files
                if os.getenv('DOWNLOAD_PHOTOS', 'true').lower() == 'true':
                    if media.media_type == 1:  # Photo
                        filename = f"{username}_{media.id}.jpg"
                        if self.download_media(str(media.thumbnail_url), filename):
                            post_data['local_file'] = f"media/{filename}"
                
                if os.getenv('DOWNLOAD_VIDEOS', 'true').lower() == 'true':
                    if media.media_type == 2:  # Video
                        filename = f"{username}_{media.id}.mp4"
                        if hasattr(media, 'video_url') and self.download_media(str(media.video_url), filename):
                            post_data['local_file'] = f"media/{filename}"
                
                posts_data.append(post_data)
            
            self.logger.info(f"Retrieved {len(posts_data)} posts for {username}")
            return posts_data
            
        except Exception as e:
            self.logger.error(f"Failed to get posts for {username}: {e}")
            return []
    
    def get_followers(self, username: str, limit: int = 1000) -> List[Dict]:
        """Extract followers list"""
        try:
            user_id = self.client.user_id_from_username(username)
            followers = self.client.user_followers(user_id, amount=limit)
            
            followers_data = []
            for follower_id, follower_info in tqdm(followers.items(), desc=f"Processing {username}'s followers"):
                time.sleep(self.request_delay / 2)  # Faster for follower lists
                
                follower_data = {
                    'pk': str(follower_info.pk),
                    'username': follower_info.username,
                    'full_name': follower_info.full_name,
                    'is_private': follower_info.is_private,
                    'is_verified': follower_info.is_verified,
                    'follower_count': getattr(follower_info, 'follower_count', 0),
                    'following_count': getattr(follower_info, 'following_count', 0),
                    'profile_pic_url': str(follower_info.profile_pic_url) if follower_info.profile_pic_url else ''
                }
                
                followers_data.append(follower_data)
            
            self.logger.info(f"Retrieved {len(followers_data)} followers for {username}")
            return followers_data
            
        except Exception as e:
            self.logger.error(f"Failed to get followers for {username}: {e}")
            return []
    
    def get_following(self, username: str, limit: int = 1000) -> List[Dict]:
        """Extract following list"""
        try:
            user_id = self.client.user_id_from_username(username)
            following = self.client.user_following(user_id, amount=limit)
            
            following_data = []
            for following_id, following_info in tqdm(following.items(), desc=f"Processing {username}'s following"):
                time.sleep(self.request_delay / 2)
                
                following_user_data = {
                    'pk': str(following_info.pk),
                    'username': following_info.username,
                    'full_name': following_info.full_name,
                    'is_private': following_info.is_private,
                    'is_verified': following_info.is_verified,
                    'follower_count': getattr(following_info, 'follower_count', 0),
                    'following_count': getattr(following_info, 'following_count', 0),
                    'profile_pic_url': str(following_info.profile_pic_url) if following_info.profile_pic_url else ''
                }
                
                following_data.append(following_user_data)
            
            self.logger.info(f"Retrieved {len(following_data)} following for {username}")
            return following_data
            
        except Exception as e:
            self.logger.error(f"Failed to get following for {username}: {e}")
            return []
    
    def extract_user_data(self, username: str) -> Dict:
        """Extract complete user data"""
        self.logger.info(f"Starting data extraction for {username}")
        
        # Get user profile info
        user_info = self.get_user_info(username)
        if not user_info:
            return {}
        
        # Extract all data
        extracted_data = {
            'user_info': user_info,
            'posts': self.get_user_posts(username),
            'followers': self.get_followers(username),
            'following': self.get_following(username),
            'extraction_timestamp': datetime.now().isoformat()
        }
        
        # Save to JSON
        output_file = self.output_dir / 'json_data' / f"{username}_data.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(extracted_data, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Data extraction completed for {username}. Saved to {output_file}")
        return extracted_data
    
    def generate_csv_reports(self, username: str, data: Dict):
        """Generate CSV reports from extracted data"""
        try:
            # Posts CSV
            if data.get('posts'):
                posts_df = pd.DataFrame(data['posts'])
                posts_df.to_csv(self.output_dir / f"{username}_posts.csv", index=False)
            
            # Followers CSV
            if data.get('followers'):
                followers_df = pd.DataFrame(data['followers'])
                followers_df.to_csv(self.output_dir / f"{username}_followers.csv", index=False)
            
            # Following CSV
            if data.get('following'):
                following_df = pd.DataFrame(data['following'])
                following_df.to_csv(self.output_dir / f"{username}_following.csv", index=False)
            
            self.logger.info(f"CSV reports generated for {username}")
            
        except Exception as e:
            self.logger.error(f"Failed to generate CSV reports: {e}")

def main():
    """Main function"""
    extractor = InstagramExtractor()
    
    # Login
    if not extractor.login():
        print("Failed to login. Please check your credentials.")
        return
    
    # Get target username from user
    target_username = input("Enter the Instagram username to extract data from: ").strip()
    
    if not target_username:
        print("No username provided.")
        return
    
    try:
        # Extract data
        data = extractor.extract_user_data(target_username)
        
        if data:
            # Generate CSV reports
            extractor.generate_csv_reports(target_username, data)
            
            print(f"\nData extraction completed for @{target_username}")
            print(f"Results saved in: {extractor.output_dir}")
            print(f"- Profile info: {len(data.get('user_info', {}))} fields")
            print(f"- Posts: {len(data.get('posts', []))} items")
            print(f"- Followers: {len(data.get('followers', []))} users")
            print(f"- Following: {len(data.get('following', []))} users")
        else:
            print("Failed to extract data. Check logs for details.")
            
    except KeyboardInterrupt:
        print("\nExtraction interrupted by user.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()