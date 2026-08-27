#!/usr/bin/env python3
"""
OmniSuite Worker
==================
Always-on Railway worker that automates the full SaaS lifecycle:
  1. CWS Queue Monitor    — hourly (detects review completion, auto-publishes)
  2. Health Check          — every 6 hours (validates extensions + license server)
  3. Review Scanner        — daily at 8am EST (checks ratings, detects bug patterns)
  4. Autonomous Factory    — weekly Sun 2am (generates new Chrome extensions)
  5. AI Support Agent      — every 30 min (reads inbox, auto-resolves tickets)
  6. Autonomous Updater    — nightly 3am (self-healing bug fixer)
  7. System Monitor        — every 4 hours (backups, health digest)
  8. Play Publisher        — weekly Wed 4am (publishes Android AABs to Google Play)
  9. Edge Publisher        — weekly Thu 4am (publishes Chrome exts to Microsoft Edge)
 10. Opera Publisher       — weekly Fri 4am (packages Chrome exts for Opera Store)
 11. Website Sync          — daily 6am (updates landing page counts + changelog)
 12. CEO Board Meeting     — hourly (accelerated strategic progress)

v6.0 Hardened Edition:
 - Self-healing watchdog with automatic scheduler restart
 - Signal handlers for graceful shutdown
 - Startup integrity checks for critical data files
 - Global exception isolation per job
 - Memory leak guard (auto-restart after excessive memory use)
"""
import asyncio
import gc
import json
import logging
import os
import signal
import sys
import tempfile
import time
import traceback
from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    stream=sys.stdout
)
logger = logging.getLogger("worker")

# ============================================
# Atomic File I/O (shared utility)
# ============================================

def atomic_write_json(filepath, data, indent=2):
    """
    Atomically write JSON data to a file using temp-file-then-rename.
    Prevents data corruption from crashes or power loss.
    """
    dir_path = os.path.dirname(filepath) or '.'
    os.makedirs(dir_path, exist_ok=True)
    
    fd, tmp_path = tempfile.mkstemp(dir=dir_path, suffix='.tmp', prefix='.atomic_')
    try:
        with os.fdopen(fd, 'w') as f:
            json.dump(data, f, indent=indent)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_path, filepath)
    except Exception:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise


# ============================================
# Self-Healing Constants
# ============================================
MAX_MEMORY_MB = 512          # Auto-restart if memory exceeds this
MAX_CONSECUTIVE_FAILURES = 5 # Per job, before sending critical alert
STARTUP_VALIDATION_FILES = [
    "data/last_heartbeat.txt",
    "data/worker_start_epoch.txt",
]

# Track consecutive job failures for circuit-breaking
_job_failure_counts = {}


# ============================================
# Job Runner with Circuit Breaker
# ============================================

async def _run_job(name: str, module_path: str):
    """Universal job runner with heartbeat tracking, circuit breaker, and structured error reporting."""
    global _job_failure_counts
    
    start = datetime.now()
    try:
        mod = __import__(module_path, fromlist=["run"])
        await mod.run()
        elapsed = (datetime.now() - start).total_seconds()
        record_heartbeat(name, True, f"completed in {elapsed:.1f}s")
        # Reset failure counter on success
        _job_failure_counts[name] = 0
    except Exception as e:
        elapsed = (datetime.now() - start).total_seconds()
        error_report = {
            "job": name,
            "error_type": type(e).__name__,
            "message": str(e),
            "elapsed_s": round(elapsed, 1),
            "timestamp": datetime.now().isoformat()
        }
        record_heartbeat(name, False, str(error_report))
        logger.error(f"{name} job failed: {error_report}", exc_info=True)
        
        # Circuit breaker: track consecutive failures
        _job_failure_counts[name] = _job_failure_counts.get(name, 0) + 1
        
        if _job_failure_counts[name] >= MAX_CONSECUTIVE_FAILURES:
            try:
                from services.notifications import send_alert
                await send_alert(
                    f"🔴 **CIRCUIT BREAKER: {name}**\n\n"
                    f"Job has failed **{_job_failure_counts[name]}** consecutive times.\n"
                    f"Last error: `{type(e).__name__}: {str(e)[:200]}`\n\n"
                    f"Investigate immediately."
                )
            except Exception:
                pass  # Don't let notification failures cascade
    finally:
        # Force garbage collection after heavy jobs
        gc.collect()


async def run_cws_monitor():    await _run_job("cws_monitor", "jobs.cws_monitor")
async def run_health_check():   await _run_job("health_check", "jobs.health_check")
async def run_review_scanner():  await _run_job("review_scanner", "jobs.review_scanner")
async def run_autonomous_factory(): await _run_job("autonomous_factory", "jobs.autonomous_factory")
async def run_support_agent():   await _run_job("support_agent", "jobs.support_agent")


async def run_autonomous_updater(): await _run_job("autonomous_updater", "jobs.autonomous_updater")
async def run_system_monitor():     await _run_job("system_monitor", "jobs.system_monitor")
async def run_play_publisher():     await _run_job("play_publisher", "jobs.play_publisher")
async def run_edge_publisher():     await _run_job("edge_publisher", "jobs.edge_publisher")
async def run_opera_publisher():    await _run_job("opera_publisher", "jobs.opera_publisher")
async def run_website_sync():       await _run_job("website_sync", "jobs.website_sync")
async def run_funnel_intelligence(): await _run_job("funnel_intelligence", "jobs.funnel_intelligence")
async def run_ceo_board_meeting():   await _run_job("ceo_board_meeting", "jobs.ceo_board_meeting")


# ============================================
# Dead-Man's Switch
# ============================================

async def run_deadman_switch():
    """Dead-man's switch: alert if no heartbeat recorded in 12+ hours."""
    try:
        data_dir = os.path.join(os.path.dirname(__file__), "data")
        heartbeat_file = os.path.join(data_dir, "last_heartbeat.txt")
        
        if os.path.exists(heartbeat_file):
            with open(heartbeat_file) as f:
                last_beat = float(f.read().strip())
            hours_silent = (time.time() - last_beat) / 3600
            
            if hours_silent > 12:
                from services.notifications import send_alert
                await send_alert(
                    f"🚨 **DEAD-MAN'S SWITCH TRIGGERED**\n\n"
                    f"No successful job heartbeat in **{hours_silent:.1f} hours**\n"
                    f"Last heartbeat: {datetime.fromtimestamp(last_beat).isoformat()}\n\n"
                    f"The worker may be stuck or crashed. Investigate immediately."
                )
                logger.critical(f"Dead-man's switch: {hours_silent:.1f}h since last heartbeat")
            else:
                logger.info(f"Dead-man's switch: OK ({hours_silent:.1f}h since last heartbeat)")
        else:
            logger.warning("Dead-man's switch: No heartbeat file found (first run?)")
    except Exception as e:
        logger.error(f"Dead-man's switch error: {e}")


# ============================================
# Memory Guard
# ============================================

async def run_memory_guard():
    """Monitor memory usage and force restart if exceeding threshold."""
    try:
        import resource
        usage = resource.getrusage(resource.RUSAGE_SELF)
        if sys.platform == "darwin":
            mem_mb = usage.ru_maxrss / (1024 * 1024)
        else:
            mem_mb = usage.ru_maxrss / 1024
        
        if mem_mb > MAX_MEMORY_MB:
            logger.critical(f"🔴 MEMORY GUARD: {mem_mb:.0f}MB exceeds {MAX_MEMORY_MB}MB limit. Triggering restart.")
            try:
                from services.notifications import send_alert
                await send_alert(
                    f"🔴 **MEMORY GUARD: Auto-Restart**\n\n"
                    f"Worker memory: **{mem_mb:.0f}MB** (limit: {MAX_MEMORY_MB}MB)\n"
                    f"Forcing restart to prevent OOM kill."
                )
            except Exception:
                pass
            # Exit with code that Railway will auto-restart
            os._exit(1)
        elif mem_mb > MAX_MEMORY_MB * 0.8:
            logger.warning(f"⚠️ Memory warning: {mem_mb:.0f}MB (80% of {MAX_MEMORY_MB}MB limit)")
            gc.collect()  # Try to free memory
    except Exception as e:
        logger.error(f"Memory guard error: {e}")


# ============================================
# Heartbeat Recording
# ============================================

def record_heartbeat(job_name, success, details=""):
    """Relay heartbeat to system monitor and update dead-man's switch file."""
    if success:
        try:
            data_dir = os.path.join(os.path.dirname(__file__), "data")
            os.makedirs(data_dir, exist_ok=True)
            heartbeat_path = os.path.join(data_dir, "last_heartbeat.txt")
            atomic_write_json(heartbeat_path, None)  # Can't use for plain text
            # Use simple write for a single float — corruption is harmless
            with open(heartbeat_path, "w") as f:
                f.write(str(time.time()))
        except Exception:
            pass
    try:
        from jobs.system_monitor import record_heartbeat as _record
        _record(job_name, success, details)
    except Exception:
        pass


# ============================================
# Startup Validation
# ============================================

async def startup_check():
    """Run on startup to validate configuration and send status."""
    from services.notifications import send_info
    
    logger.info("=" * 50)
    logger.info("🏗️  OmniSuite Worker v6.0 (Hardened) starting...")
    logger.info("=" * 50)
    
    # Write uptime epoch for system monitor
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    os.makedirs(data_dir, exist_ok=True)
    with open(os.path.join(data_dir, "worker_start_epoch.txt"), "w") as f:
        f.write(str(time.time()))
    
    # Validate critical data files integrity
    integrity_issues = []
    for critical_file in ["pending_bugs.json", "refund_audit.json"]:
        filepath = os.path.join(data_dir, critical_file)
        if os.path.exists(filepath):
            try:
                with open(filepath) as f:
                    json.load(f)
            except json.JSONDecodeError:
                integrity_issues.append(f"⚠️ Corrupted: {critical_file}")
                # Auto-recover from backup
                backup_dir = os.path.join(data_dir, "backups")
                if os.path.isdir(backup_dir):
                    backups = sorted([
                        b for b in os.listdir(backup_dir)
                        if b.startswith(critical_file) and b.endswith('.bak')
                    ], reverse=True)
                    for bak in backups:
                        try:
                            import shutil
                            shutil.copy2(os.path.join(backup_dir, bak), filepath)
                            integrity_issues.append(f"  ↳ Restored from {bak}")
                            break
                        except Exception:
                            continue
    
    # Validate env vars
    config = {
        "CWS_CLIENT_ID": bool(os.environ.get("CWS_CLIENT_ID")),
        "CWS_CLIENT_SECRET": bool(os.environ.get("CWS_CLIENT_SECRET")),
        "CWS_REFRESH_TOKEN": bool(os.environ.get("CWS_REFRESH_TOKEN")),
        "CWS_ITEM_IDS": bool(os.environ.get("CWS_ITEM_IDS")),
        "DISCORD_WEBHOOK_URL": bool(os.environ.get("DISCORD_WEBHOOK_URL")),
        "LICENSE_SERVER_URL": bool(os.environ.get("LICENSE_SERVER_URL")),
    }
    
    missing = [k for k, v in config.items() if not v]
    
    if missing:
        logger.warning(f"⚠️  Missing env vars: {', '.join(missing)}")
        logger.warning("Some jobs may not function correctly")
    else:
        logger.info("✅ All environment variables configured")
    
    # Count extensions
    try:
        item_ids = json.loads(os.environ.get("CWS_ITEM_IDS", "{}"))
        ext_count = len(item_ids)
    except json.JSONDecodeError:
        ext_count = 0
    
    logger.info(f"📦 Monitoring {ext_count} Chrome extensions")
    logger.info(f"🛡️ Hardened features: atomic writes, circuit breakers, memory guard, self-healing")
    logger.info(f"⏰ Schedule: 14 jobs active (including guards)")
    logger.info(f"   CWS Monitor:      hourly")
    logger.info(f"   Health Check:     every 6 hours")
    logger.info(f"   Review Scanner:   daily 8 AM")
    logger.info(f"   Factory:          Sun 2 AM")
    logger.info(f"   Support Agent:    every 30 min")
    logger.info(f"   Bug Fixer:        daily 3 AM")
    logger.info(f"   System Monitor:   every 4 hours")
    logger.info(f"   Play Publisher:   Wed 4 AM")
    logger.info(f"   Edge Publisher:   Thu 4 AM")
    logger.info(f"   Opera Publisher:  Fri 4 AM")
    logger.info(f"   Website Sync:     daily 6 AM")
    logger.info(f"   CEO Meeting:      hourly")
    logger.info(f"   Dead-Man Switch:  hourly")
    logger.info(f"   Memory Guard:     every 30 min")
    
    # Send startup notification
    integrity_note = ""
    if integrity_issues:
        integrity_note = "\n\n**Integrity Issues:**\n" + "\n".join(integrity_issues)
    
    await send_info(
        f"**OmniSuite Worker v6.0 started** 🏗️\n\n"
        f"Monitoring **{ext_count}** extensions\n"
        f"Config: {len(config) - len(missing)}/{len(config)} env vars set\n"
        f"{'⚠️ Missing: ' + ', '.join(missing) if missing else '✅ All configured'}"
        f"{integrity_note}"
    )


# ============================================
# Graceful Shutdown
# ============================================

_scheduler = None

def _handle_shutdown(signum, frame):
    """Handle SIGTERM/SIGINT gracefully."""
    sig_name = signal.Signals(signum).name if hasattr(signal, 'Signals') else str(signum)
    logger.info(f"Received {sig_name}. Shutting down gracefully...")
    if _scheduler:
        _scheduler.shutdown(wait=False)
    sys.exit(0)


# ============================================
# Main Entry Point with Self-Healing
# ============================================

def main():
    """Main entry point — sets up scheduler with self-healing watchdog."""
    global _scheduler
    
    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGTERM, _handle_shutdown)
    signal.signal(signal.SIGINT, _handle_shutdown)
    
    max_restarts = 5
    restart_count = 0
    
    while restart_count < max_restarts:
        try:
            _run_scheduler()
            break  # Normal exit
        except Exception as e:
            restart_count += 1
            logger.critical(
                f"🔴 SCHEDULER CRASH #{restart_count}/{max_restarts}: {type(e).__name__}: {e}\n"
                f"{traceback.format_exc()}"
            )
            if restart_count < max_restarts:
                wait_time = min(30 * restart_count, 120)  # Exponential backoff, max 2 min
                logger.info(f"Restarting scheduler in {wait_time}s...")
                time.sleep(wait_time)
            else:
                logger.critical("Max restarts exceeded. Worker is dead.")
                sys.exit(1)


def _run_scheduler():
    """Internal scheduler setup — isolated for self-healing restarts."""
    global _scheduler
    
    scheduler = AsyncIOScheduler(timezone="America/New_York")
    _scheduler = scheduler
    
    # Job 1: CWS Queue Monitor — every 60 minutes
    scheduler.add_job(
        run_cws_monitor,
        IntervalTrigger(minutes=60),
        id="cws_monitor",
        name="CWS Queue Monitor",
        max_instances=1,
        misfire_grace_time=300
    )
    
    # Job 2: Health Check — every 6 hours
    scheduler.add_job(
        run_health_check,
        IntervalTrigger(hours=6),
        id="health_check",
        name="Extension Health Check",
        max_instances=1,
        misfire_grace_time=600
    )
    
    # Job 3: Review Scanner — daily at 8 AM EST
    scheduler.add_job(
        run_review_scanner,
        CronTrigger(hour=8, minute=0),
        id="review_scanner",
        name="Review Scanner",
        max_instances=1,
        misfire_grace_time=3600
    )
    
    # Job 4: Autonomous SaaS Factory — weekly on Sunday at 2:00 AM EST
    scheduler.add_job(
        run_autonomous_factory,
        CronTrigger(day_of_week='sun', hour=2, minute=0),
        id="autonomous_factory",
        name="Autonomous SaaS Factory",
        max_instances=1,
        misfire_grace_time=3600
    )
    
    # Job 5: Support Agent — no-op (migrated to Cloudflare Email Worker)
    scheduler.add_job(
        run_support_agent,
        IntervalTrigger(minutes=30),
        id="support_agent",
        name="Support Agent (Cloudflare No-Op)",
        max_instances=1,
        misfire_grace_time=300
    )
    
    # Job 6: Autonomous Bug Fixer — Nightly at 3:00 AM EST
    scheduler.add_job(
        run_autonomous_updater,
        CronTrigger(hour=3, minute=0),
        id="autonomous_updater",
        name="Self-Healing AI Bug Updater",
        max_instances=1,
        misfire_grace_time=3600
    )
    
    # Job 7: System Monitor & Backup — every 4 hours
    scheduler.add_job(
        run_system_monitor,
        IntervalTrigger(hours=4),
        id="system_monitor",
        name="System Monitor & Backup",
        max_instances=1,
        misfire_grace_time=600
    )
    
    # Job 8: Play Publisher — weekly Wednesday at 4:00 AM EST
    scheduler.add_job(
        run_play_publisher,
        CronTrigger(day_of_week='wed', hour=4, minute=0),
        id="play_publisher",
        name="Google Play Publisher",
        max_instances=1,
        misfire_grace_time=3600
    )
    
    # Job 9: Edge Publisher — weekly Thursday at 4:00 AM EST
    scheduler.add_job(
        run_edge_publisher,
        CronTrigger(day_of_week='thu', hour=4, minute=0),
        id="edge_publisher",
        name="Microsoft Edge API Publisher",
        max_instances=1,
        misfire_grace_time=3600
    )
    
    # Job 10: Opera Publisher — weekly Friday at 4:00 AM EST
    scheduler.add_job(
        run_opera_publisher,
        CronTrigger(day_of_week='fri', hour=4, minute=0),
        id="opera_publisher",
        name="Opera ZIP Packager",
        max_instances=1,
        misfire_grace_time=3600
    )
    
    # Job 11: Website Auto-Sync — daily at 6:00 AM EST
    scheduler.add_job(
        run_website_sync,
        CronTrigger(hour=6, minute=0),
        id="website_sync",
        name="Website Auto-Sync",
        max_instances=1,
        misfire_grace_time=3600
    )
    
    # Job 14: Funnel Intelligence — every 4 hours
    scheduler.add_job(
        run_funnel_intelligence,
        IntervalTrigger(hours=4),
        id="funnel_intelligence",
        name="Funnel Intelligence",
        max_instances=1,
        misfire_grace_time=600
    )
    
    # Job 15: CEO Board Meeting — hourly (Accelerated Progress)
    # scheduler.add_job(
    #     run_ceo_board_meeting,
    #     IntervalTrigger(minutes=60),
    #     id="ceo_board_meeting",
    #     name="Digital CEO Board Meeting",
    #     max_instances=1,
    #     misfire_grace_time=600
    # )
    
    # Job 12: Dead-Man's Switch — hourly check that jobs are running
    scheduler.add_job(
        run_deadman_switch,
        IntervalTrigger(hours=1),
        id="deadman_switch",
        name="Dead-Man's Switch",
        max_instances=1,
        misfire_grace_time=600
    )
    
    # Job 13: Memory Guard — every 30 minutes
    scheduler.add_job(
        run_memory_guard,
        IntervalTrigger(minutes=30),
        id="memory_guard",
        name="Memory Guard",
        max_instances=1,
        misfire_grace_time=300
    )
    
    # Setup event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    scheduler.start()
    logger.info("Scheduler started — 13 jobs active (including dead-man's switch + memory guard)")
    
    loop.run_until_complete(startup_check())
    
    # Keep running forever
    try:
        loop.run_forever()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Shutdown requested")
        scheduler.shutdown()


if __name__ == "__main__":
    main()
