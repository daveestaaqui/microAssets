# Tinder Automation Bot

A Python-based automation tool for interacting with Tinder profiles using browser automation (Playwright).

## ⚠️ Disclaimer

**Use at your own risk.** This tool may violate Tinder's Terms of Service. Using automation tools can result in:
- Account suspension or banning
- Loss of paid subscriptions (Plus, Gold, Platinum)
- Legal consequences in some jurisdictions

Use responsibly and at your own risk.

## Requirements

- Python 3.8+
- Chrome/Chromium browser
- Stable internet connection

## Installation

1. **Clone or download the bot** to your desired location

2. **Install dependencies:**
```bash
pip install -r requirements_tinder.txt
playwright install
```

3. **Configure credentials:**
   - Copy `tinder_env_template.sh` to `tinder_env.sh`
   - Fill in your Tinder username/password
   - Source the environment file:
   ```bash
   source tinder_env.sh
   # or on Windows:
   set TINDER_USERNAME=your_username
   set TINDER_PASSWORD=your_password
   ```

## Usage

```bash
# Basic run with environment variables
python tinder_automation.py

# Or configure directly in the script's CONFIG dict
python tinder_automation.py
```

## Configuration Options

Edit the `CONFIG` dictionary in `tinder_automation.py`:

| Option | Default | Description |
|--------|---------|-------------|
| `swipe_limit` | 9999 | Max swipes (0 = infinite) |
| `pause_between_swipes` | 2 | Seconds between swipes |
| `pause_after_page_change` | 3 | Wait after loading new profiles |
| `max_session_time` | 0 | Max runtime in hours (0 = no limit) |
| `image_quality_threshold` | 0.7 | Min image quality score |
| `account_type` | 'plus' | 'free', 'plus', 'gold', 'platinum' |
| `log_debug` | False | Enable debug logging |

## Profile Evaluation Criteria

The bot evaluates profiles based on:

1. **Image Quality** - Rejects blurry or low-quality images
2. **Bio Analysis** - Checks for:
   - Age indicators (rejects if suggesting elderly)
   - Health keywords (gym, fitness, workout, etc.)
   - Unhealthy keywords (hospital, illness, obese, etc.)

## Features

- ✅ Browser automation using Playwright
- ✅ Profile image quality analysis
- ✅ Bio text analysis
- ✅ Swipe action automation
- ✅ Session statistics tracking
- ✅ Configurable swipe limits
- ✅ Anti-detection browser arguments

## Troubleshooting

### CAPTCHA appears
- Complete the CAPTCHA manually
- The bot will resume after authentication

### Login issues
- Ensure 2FA is configured correctly
- Check browser cookies/cache
- Try different account types

### "Could not load profiles"
- Tinder may be blocking automated access
- Try manually logging in first
- Check if account is banned/flagged

## Customization

### Adjusting Accept Rate

The default accept rate is 60%. Modify in `_start_swiping`:

```python
# Change this value to adjust acceptance rate
if random.random() > 0.4:  # 0.4 = 60% accept rate
    self._handle_swipe(profile, 'like', f"Profile {swipe_count}")
else:
    self._handle_swipe(profile, 'pass', f"Profile {swipe_count}")
```

### Adding Custom Bio Filters

Edit `_check_health_indicators` to add/remove keywords:

```python
unhealthy_keywords = ['cancer', 'sick', 'hospital', 'illness', 'diet', 'obese',
                      'smoker', 'drinking', 'party']
healthy_keywords = ['gym', 'fitness', 'workout', 'healthy', 'active', 
                    'runner', 'hiker', 'cooking', 'travel']
```

## Statistics

The bot tracks and displays:
- Total profiles viewed
- Likes (accepts)
- Passes (rejects)
- Supers (premium swipes)
- Accept rate percentage

## Files

- `tinder_automation.py` - Main bot script
- `tinder_env_template.sh` - Environment variable template
- `requirements_tinder.txt` - Python dependencies

## License

MIT License - Use at your own risk.

## Support

For issues or questions, review the code comments or check the troubleshooting section.