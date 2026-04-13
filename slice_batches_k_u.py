import process_grid_icons
import os

batches = {
    "k_1776014970783.png": ["reading-mode", "reading-time-badge", "reddit-redirect", "youtube-pip"],
    "l_1776014985577.png": ["screenshot-capture", "domain-details", "wayback-machine-quick", "website-monitor-pro"],
    "m_1776015000419.png": ["dark-mode-pro", "youtube-playback-speed", "youtube-comment-exporter", "youtube-shorts-blocker"],
    "n_1776015011207.png": ["password-manager", "ip-address-finder", "vpn-quick-toggle", "tab-suspender"],
    "o_1776015022823.png": ["session-manager", "image-downloader", "color-blindness-simulator", "seo-meta-inspector"],
    "p_1776015057363.png": ["meta-tag-analyzer", "http-headers", "rss-feed-reader", "ad-blocker-pro"],
    "q_1776015073098.png": ["popup-blocker", "javascript-toggle", "css-minifier", "html-minifier"],
    "r_1776015086908.png": ["js-minifier", "auto-refresh", "session-saver", "history-cleaner"],
    "s_1776015101863.png": ["notes-sync", "to-do-list", "pomodoro-timer", "unit-converter"],
    "t_1776015116690.png": ["currency-converter", "timezone-converter", "calculator-pro", "weather-quick"],
    "u_": ["dictionary-lookup", "translator-quick", "font-changer", "volume-booster"]
}

base_dir = "/Users/davidmahler/.gemini/antigravity/brain/6bdc5fa9-3872-4ab1-895b-625bd4f05588"
out_dir = "/Users/davidmahler/Desktop/microAssets"

for fname_suffix, ext_names in batches.items():
    for f in os.listdir(base_dir):
        if f.startswith("icons_strict_batch_") and fname_suffix in f:
            full_path = os.path.join(base_dir, f)
            print(f"Slicing {f}...")
            process_grid_icons.slice_grid(full_path, out_dir, ext_names)

print("Batches K-U sliced successfully!")
