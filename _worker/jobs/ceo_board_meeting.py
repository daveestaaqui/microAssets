import subprocess
import os
import logging

logger = logging.getLogger(__name__)

async def run():
    """
    Executes the Digital CEO Board Meeting.
    This job triggers the Board Coordinator script which orchestrates all sub-agents.
    """
    # The script is located in the root/_scripts directory
    # Worker runs from root/_worker/worker.py, so we go up one level
    script_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "_scripts", "sporlyworks_board_coordinator.py")
    
    logger.info(f"🚀 Starting Digital CEO Board Meeting: {script_path}")
    
    try:
        # Run as a separate process to maintain isolation
        result = subprocess.run(["python3", script_path], capture_output=True, text=True)
        if result.returncode == 0:
            logger.info("✅ Board Meeting completed successfully.")
        else:
            logger.error(f"❌ Board Meeting failed with return code {result.returncode}")
            logger.error(f"STDOUT: {result.stdout}")
            logger.error(f"STDERR: {result.stderr}")
    except Exception as e:
        logger.error(f"💥 Failed to execute Board Meeting: {e}")
