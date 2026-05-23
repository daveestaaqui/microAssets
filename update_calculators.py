import os
import re

calc_files = [
    "ai-estimator.html",
    "ai-sdr-labor-savings-calculator.html",
    "lead-value-calculator.html",
    "proptech-roi-calculator.html",
    "roi-calculator.html",
    "stack-auditor.html",
    "wholesale-assignment-fee-calculator.html"
]

new_nav = """    <nav id="mainNav">
        <div class="nav-inner">
            <a href="index.html" class="nav-logo">
                <img src="logo.png" alt="SporlyWorks Logo" style="height:32px;">
                <span class="company-name" style="font-family:'DM Serif Display',serif; font-size:20px; color:#d4af37; margin-left:12px;">SPORLYWORKS</span>
            </a>
            <div class="nav-links" id="navLinks">
                <a href="index.html#tools" style="color:#a3a3a3; text-decoration:none; font-weight:500;">Featured Tools</a>
                <a href="ai-estimator.html" style="color:#a3a3a3; text-decoration:none; font-weight:500;">AI Estimator</a>
                <a href="stack-auditor.html" style="color:#a3a3a3; text-decoration:none; font-weight:500;">Stack Auditor</a>
            </div>
            <a href="index.html#tools" class="nav-cta" style="background:linear-gradient(135deg, #d4af37, #aa8c2c); color:#000; padding:10px 24px; border-radius:99px; text-decoration:none; font-weight:600;">Explore Tools</a>
        </div>
    </nav>"""

new_footer = """    <footer style="padding: 80px 24px 40px; background: #0a0a0a; border-top: 1px solid rgba(255,255,255,0.08); text-align: center; margin-top: 80px;">
        <div class="container">
            <a href="index.html" style="display:inline-flex; align-items:center; gap:12px; text-decoration:none; font-family:'DM Serif Display',serif; color:#d4af37; font-size:24px; margin-bottom:24px;">
                <img src="logo.png" alt="SporlyWorks" style="height:32px;">
                <span>SPORLYWORKS</span>
            </a>
            <div style="display:flex; justify-content:center; gap:32px; margin-bottom:32px;">
                <a href="index.html#tools" style="color:#a3a3a3; text-decoration:none;">All Tools</a>
                <a href="mailto:support@sporlyworks.com" style="color:#a3a3a3; text-decoration:none;">Partner with Us</a>
            </div>
            <p style="color:#666; font-size:14px;">&copy; 2026 SporlyWorks. Elevating B2B Growth.</p>
        </div>
    </footer>"""

for f in calc_files:
    if not os.path.exists(f):
        print(f"Skipping {f}, not found.")
        continue
    
    with open(f, 'r') as file:
        content = file.read()
    
    # Replace nav
    content = re.sub(r'<nav class="nav">.*?</nav>', new_nav, content, flags=re.DOTALL)
    content = re.sub(r'<nav id="mainNav">.*?</nav>', new_nav, content, flags=re.DOTALL) # in case it was already replaced
    
    # Replace hardcoded calculator div with glass-panel
    content = re.sub(
        r'<div class="calculator"[^>]*>', 
        '<div class="calculator glass-panel">', 
        content
    )
    
    # Inject footer before </body> if not exists
    if '<footer>' not in content:
        content = content.replace('</body>', new_footer + '\n</body>')
    else:
        content = re.sub(r'<footer.*?</footer>', new_footer, content, flags=re.DOTALL)
        
    # Make hero text aligned with new design
    content = re.sub(r'<section class="hero"[^>]*>', '<section class="hero" style="min-height: 40vh; padding: 120px 24px 60px; text-align: center;">', content)
        
    with open(f, 'w') as file:
        file.write(content)
    print(f"Updated {f}")

