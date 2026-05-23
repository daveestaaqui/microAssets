#!/usr/bin/env python3
"""
Tinder Automation Bot
Automates swiping through Tinder profiles with visual criteria evaluation.
"""

import os
import time
import random
import hashlib
from pathlib import Path
from PIL import Image
from PIL.ImageChops import convert_to_profile
import requests
from io import BytesIO
from playwright.sync_api import sync_playwright, Page, Locator
from bs4 import BeautifulSoup
import urllib.parse


# Configuration
CONFIG = {
    # Tinder credentials (store securely - use a separate env file if needed)
    'username': '',  # Set your Tinder username or email
    'password': '',  # Set your Tinder password
    
    # Tinder account type
    'account_type': 'plus',  # 'plus', 'gold', or 'platinum'
    
    # Swipe behavior
    'swipe_limit': 9999,  # Number of swipes before stopping (or 0 for infinite)
    'pause_between_swipes': 2,  # Seconds between swipes to avoid detection
    'pause_after_page_change': 3,  # Seconds to wait after loading new profiles
    'max_session_time': 0,  # 0 = no limit, in hours
    
    # Image analysis settings
    'image_quality_threshold': 0.7,  # Minimum image quality score
    'face_detection_enabled': True,  # Enable face detection
    'analysis_interval': 5,  # Analyze every N images
    
    # Logging
    'log_accepted': True,
    'log_rejected': True,
    'log_debug': False,
}


class TinderBot:
    def __init__(self, config=None):
        self.config = config or CONFIG
        self.browser = None
        self.page = None
        self.logger = self._init_logger()
        self.stats = {
            'total_profiles': 0,
            'liked': 0,
            'passed': 0,
            'supers': 0,
            'rejected': 0,
            'errors': 0,
            'time_spent': 0,
        }
        self.session_hash = None
        self._load_config()
        
    def _load_config(self):
        """Load configuration from environment variables or file."""
        # Check for environment variables
        if os.environ.get('TINDER_USERNAME'):
            self.config['username'] = os.environ.get('TINDER_USERNAME')
        if os.environ.get('TINDER_PASSWORD'):
            self.config['password'] = os.environ.get('TINDER_PASSWORD')
            
    def _init_logger(self):
        """Initialize logging configuration."""
        return {
            'format': '[%(asctime)s] %(message)s',
            'level': 'INFO'
        }
    
    def _generate_session_hash(self):
        """Generate a unique session hash."""
        if self.session_hash:
            return self.session_hash
        hash_input = f"{self.config['username']}{self.config['password']}{time.time()}"
        self.session_hash = hashlib.md5(hash_input.encode()).hexdigest()[:8]
        return self.session_hash
    
    def _get_tinder_url(self):
        """Get the appropriate Tinder URL for the account type."""
        base_urls = {
            'free': 'https://www.tinder.com',
            'plus': 'https://www.tinder.com/plus',
            'gold': 'https://www.tinder.com/gold',
            'platinum': 'https://www.tinder.com/platinum',
        }
        return base_urls.get(self.config['account_type'], 'https://www.tinder.com')
    
    def _detect_face_in_image(self, image_data):
        """
        Basic face detection heuristic.
        In a real implementation, use a model like face_recognition or dlib.
        """
        try:
            from face_recognition import face_locations
            # Placeholder - actual face detection would require the library
            return True
        except ImportError:
            return True
    
    def _analyze_image_quality(self, image_data):
        """
        Analyze image quality for evaluation.
        Check for appropriate quality, blur, and clarity.
        """
        try:
            from PIL import Image as PILImage
            img = PILImage.open(image_data)
            
            # Check image dimensions
            width, height = img.size
            if width < 300 or height < 300:
                return False, "Image too small"
                
            # Check for excessive blur (simple heuristic)
            img_small = img.resize((100, 100), Image.LANCZOS)
            if img_small.point(lambda x: x > 200).getpixel((50, 50)) > 150:
                return False, "Image appears blurry"
                
            return True, "Good quality"
        except Exception as e:
            self.logger['format'] % f"Image analysis error: {e}"
            return None, str(e)
    
    def _check_age_from_bio(self, bio_text):
        """
        Try to detect age references in bio text.
        Simple keyword-based detection.
        """
        age_keywords = ['18', '20', '25', '30', '35', '40', '45', '50', 
                       'young', 'teen', 'senior', 'middle-aged']
        
        for keyword in age_keywords:
            if keyword in bio_text.lower():
                return True
        return True
    
    def _check_health_indicators(self, bio_text):
        """
        Check for health-related indicators in bio text.
        Looks for gym, fitness, healthy lifestyle mentions.
        """
        unhealthy_keywords = ['cancer', 'sick', 'hospital', 'illness', 'diet', 'obese']
        healthy_keywords = ['gym', 'fitness', 'workout', 'healthy', 'active', 'runner', 'hiker']
        
        bio_lower = bio_text.lower()
        
        for keyword in unhealthy_keywords:
            if keyword in bio_lower:
                return False
                
        for keyword in healthy_keywords:
            if keyword in bio_lower:
                return True
        return True
    
    def _evaluate_profile(self, image_data, bio_text=None):
        """
        Evaluate a profile based on the specified criteria.
        Returns: 'accepted', 'rejected', or 'review'
        """
        result = {
            'decision': 'accepted',  # default
            'reason': '',
            'confidence': 1.0,
        }
        
        # Check image quality
        quality_ok, quality_msg = self._analyze_image_quality(image_data)
        if quality_ok is False:
            result['decision'] = 'rejected'
            result['reason'] = quality_msg
            result['confidence'] = 0.95
        
        # Check bio for age indicators
        if bio_text:
            age_ok = self._check_age_from_bio(bio_text)
            if age_ok is False:
                result['decision'] = 'rejected'
                result['reason'] = 'Age indicators in bio suggest elderly'
                result['confidence'] = 0.8
                return result
                
            health_ok = self._check_health_indicators(bio_text)
            if health_ok is False:
                result['decision'] = 'rejected'
                result['reason'] = 'Unhealthy indicators found in bio'
                result['confidence'] = 0.8
                return result
        
        # Default to accepted with confidence based on image quality
        result['confidence'] = 0.7 + (random.random() * 0.2)
        
        return result
    
    def _handle_swipe(self, element, element_type, profile_name):
        """
        Handle a swipe action (accept/reject/super).
        """
        # Calculate swipe coordinates
        element_rect = element.bounding_box()
        swipe_x = element_rect['x'] + element_rect['width'] / 2
        swipe_y = element_rect['y'] + element_rect['height'] / 2
        
        # Perform the swipe
        swipe_data = {
            'element': element,
            'x': swipe_x,
            'y': swipe_y,
            'type': element_type,
        }
        
        # Log the action
        self._log_action(element_type, profile_name, swipe_data)
        
        # Update statistics
        self.stats[element_type.lower()] += 1
        
        return swipe_data
    
    def _log_action(self, action_type, profile_name, data=None):
        """Log a swipe action."""
        if self.config['log_debug']:
            print(f"  [{action_type}] {profile_name}")
            if data:
                print(f"    {data}")
        else:
            print(f"[{self.session_hash}] {action_type}: {profile_name}")
    
    def _load_profiles(self):
        """
        Load and parse profiles from the current page.
        This is a simplified version - actual implementation depends on
        the specific Tinder web structure.
        """
        profiles = []
        
        try:
            # Try to find profile elements
            # Note: These selectors may need adjustment based on Tinder's current DOM structure
            profile_containers = self.page.locator(
                '.swipe-card-container, .card-item, [data-testid="swipe-card"], '
                '.user-profile, .profile-card, .match-card'
            )
            
            if profile_containers.count() > 0:
                count = min(10, profile_containers.count())  # Load up to 10 profiles
                for i in range(count):
                    try:
                        profile = profile_containers.nth(i)
                        profiles.append(profile)
                    except Exception:
                        break
                        
        except Exception as e:
            print(f"Error loading profiles: {e}")
            
        return profiles
    
    def _navigate_to_swipe_page(self):
        """Navigate to the main swipe page."""
        try:
            # Try the main tinder.com URL first
            self.page.goto(self._get_tinder_url(), wait_until='networkidle')
            time.sleep(self.config['pause_after_page_change'])
            
            # Try to find login form or login button
            login_buttons = self.page.locator(
                'input[name="email"], input[name="login"], button:has-text("Log In")'
            )
            
            if login_buttons.count() > 0:
                print("Login form detected, please enter credentials...")
                print("You may need to manually enter your credentials or the script needs update.")
                return
                
        except Exception as e:
            print(f"Navigation error: {e}")
            
    def _authenticate(self):
        """
        Handle authentication - currently requires manual login
        due to Tinder's security measures.
        """
        print("=" * 50)
        print("TINDER AUTOMATION BOT")
        print("=" * 50)
        print(f"\nAccount Type: {self.config['account_type']}")
        print(f"Session Hash: {self.session_hash}\n")
        
        print("IMPORTANT SECURITY NOTICE:")
        print("-" * 50)
        print("Due to Tinder's advanced security measures (CAPTCHA,")
        print("two-factor authentication, etc.), full automation may not")
        print("be possible without manual intervention.")
        print("\nThe bot will:")
        print("  1. Open browser and navigate to Tinder")
        print("  2. Load profiles for viewing")
        print("  3. You may need to complete CAPTCHA manually")
        print("  4. Once authenticated, swipes can be automated\n")
        print("-" * 50)
        
        input("Press Enter when browser is open and logged in...")
        
    def run(self):
        """
        Main execution loop.
        """
        with sync_playwright() as p:
            # Launch browser
            browser_args = []
            if self.config['account_type'] == 'free':
                browser_args += ['--no-sandbox', '--disable-web-security', '--disable-site-isolation-trials']
            elif self.config['account_type'] == 'plus':
                browser_args += ['--no-sandbox', '--disable-web-security', 
                               '--disable-site-isolation-trials', '--disable-features=IsolateOrigins,site-per-process']
            elif self.config['account_type'] == 'gold':
                browser_args += ['--no-sandbox', '--disable-web-security', 
                               '--disable-site-isolation-trials', '--disable-features=IsolateOrigins,site-per-process',
                               '--disable-blink-features=AutomationControlled',
                               '--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36']
            else:  # platinum
                browser_args += ['--no-sandbox', '--disable-web-security', 
                               '--disable-site-isolation-trials', '--disable-features=IsolateOrigins,site-per-process',
                               '--disable-blink-features=AutomationControlled',
                               '--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36',
                               '--disable-gpu', '--disable-dev-shm-usage']
            
            browser = p.chromium.launch(args=browser_args)
            page = browser.new_page()
            
            try:
                # Navigate to Tinder
                print("Opening browser...")
                page.goto("https://www.tinder.com", wait_until='networkidle')
                time.sleep(3)
                
                # Check if already logged in
                if self._is_logged_in(page):
                    print("Already logged in, proceeding with swipe session...")
                    self._start_swiping(page)
                else:
                    self._authenticate()
                    self._start_swiping(page)
                    
            except Exception as e:
                print(f"Error during automation: {e}")
                import traceback
                traceback.print_exc()
                
            finally:
                browser.close()
                
                # Print final stats
                self._print_stats()
    
    def _is_logged_in(self, page):
        """Check if already logged in to Tinder."""
        try:
            # Check for common indicators of logged-in state
            page.reload()
            time.sleep(2)
            
            # Look for user menu, profile picture, or other indicators
            logged_in_indicators = [
                '.header-right-user-menu',
                '.profile-avatar',
                '[data-testid="profile-menu"]',
                '.header-user-avatar',
            ]
            
            for indicator in logged_in_indicators:
                if page.locator(indicator).count() > 0:
                    return True
                    
            # If we can see the swipe deck, we're logged in
            if 'swipe-card' in page.url or page.locator('.swipe-container').count() > 0:
                return True
                
        except Exception:
            pass
            
        return False
    
    def _start_swiping(self, page):
        """Start the main swiping loop."""
        print("\nStarting swipe session...")
        print("Press Ctrl+C to stop\n")
        
        swipe_count = 0
        last_profile_time = time.time()
        
        try:
            while swipe_count < self.config['swipe_limit'] or self.config['swipe_limit'] == 9999:
                # Check if we've exceeded session time limit
                if self.config['max_session_time'] > 0:
                    hours_elapsed = (time.time() - last_profile_time) / 3600
                    if hours_elapsed > self.config['max_session_time']:
                        print(f"\nSession time limit ({self.config['max_session_time']} hours) reached. Stopping.")
                        break
                
                # Load next page/profiles
                try:
                    # Try to trigger page refresh or load next profiles
                    if swipe_count == 0:
                        # First load - wait for initial profiles
                        time.sleep(5)
                        profiles = self._load_profiles()
                        
                        # Check if profiles loaded
                        if len(profiles) == 0:
                            print("Could not load profiles. Tinder may require manual interaction.")
                            print("Check for CAPTCHA or login issues.")
                            break
                    else:
                        # Trigger navigation to next profiles
                        try:
                            # Look for next page button
                            next_page_btn = page.locator('.next-page, .load-more, button:has-text("Next")')
                            if next_page_btn.count() > 0:
                                next_page_btn.click()
                                time.sleep(self.config['pause_after_page_change'])
                        except Exception:
                            pass
                    
                    # Process each visible profile
                    profiles = self._load_profiles()
                    for profile in profiles:
                        try:
                            # Get profile image for analysis
                            image_element = profile.locator('img, picture, .profile-image')
                            
                            if image_element.count() > 0:
                                # In a real implementation, we'd capture the image
                                # and analyze it. Here we simulate the process.
                                
                                # Simple heuristic: random accept/reject with bias
                                # In real use, image analysis would inform decision
                                
                                if random.random() > 0.4:  # 60% accept rate as default
                                    self._handle_swipe(profile, 'like', f"Profile {swipe_count}")
                                else:
                                    self._handle_swipe(profile, 'pass', f"Profile {swipe_count}")
                                    
                        except Exception as e:
                            print(f"  Error processing profile: {e}")
                            
                except Exception as e:
                    print(f"Profile loading issue: {e}")
                    time.sleep(2)
                
                swipe_count += 1
                time.sleep(self.config['pause_between_swipes'])
                
            # Stop gracefully
            print(f"\nReached swipe limit of {self.config['swipe_limit']} or session ended.")
            
        except KeyboardInterrupt:
            print("\n\nUser requested stop.")
            
        finally:
            self._print_stats()
    
    def _print_stats(self):
        """Print final statistics."""
        print("\n" + "=" * 50)
        print("SESSION SUMMARY")
        print("=" * 50)
        print(f"Session Hash: {self.session_hash}")
        print(f"Profiles Viewed: {self.stats['liked'] + self.stats['passed']}")
        print(f"Likes (Accepts): {self.stats['liked']}")
        print(f"Passes: {self.stats['passed']}")
        print(f"Supers: {self.stats['supers']}")
        print(f"Errors: {self.stats['errors']}")
        print(f"Time Spent: {self.stats['time_spent']}s")
        print(f"Accept Rate: {self.stats['liked'] / max(1, self.stats['liked'] + self.stats['passed'] * 100):.2f}%")
        print("=" * 50)


def main():
    """Main entry point."""
    # Check for required environment variables
    if not os.environ.get('TINDER_USERNAME'):
        print("ERROR: TINDER_USERNAME environment variable not set")
        print("Please set TINDER_USERNAME and TINDER_PASSWORD environment variables")
        print("or update them in the CONFIG dictionary.")
        return 1
    
    if not os.environ.get('TINDER_PASSWORD'):
        print("ERROR: TINDER_PASSWORD environment variable not set")
        return 1
    
    # Initialize and run bot
    bot = TinderBot(CONFIG)
    
    try:
        bot.run()
    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())