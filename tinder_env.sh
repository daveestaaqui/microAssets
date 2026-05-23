#!/bin/bash
# Environment variables for Tinder Automation Bot
# Copy this file to tinder_env.sh and fill in your credentials

# Tinder Credentials
export TINDER_USERNAME="your_email_or_username"
export TINDER_PASSWORD="your_password"

# Optional: Add 2FA token if required
# export TINDER_2FA_CODE="..."

# Session settings
export TINDER_ACCOUNT_TYPE="plus"
export TINDER_SWIPE_LIMIT="0"  # 0 = infinite, or set a number
export TINDER_PAUSE_BETWEEN_SWIPE="2"

echo "Tinder Bot environment configured"
echo "Username: $TINDER_USERNAME"