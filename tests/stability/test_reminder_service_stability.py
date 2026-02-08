"""Reminder service stability test (T111 - Phase 10).

Tests reminder service stability over extended periods (24 hours).
Can be run with shorter durations for testing purposes.

Usage:
    # Run for 24 hours (production test)
    python tests/stability/test_reminder_service_stability.py --duration 24

    # Run for 1 hour (quick test)
    python tests/stability/test_reminder_service_stability.py --duration 1

    # Run for 30 minutes (development test)
    python tests/stability/test_reminder_service_stability.py --duration 0.5
"""

import argparse
import time
import os
import sys
import psutil
import logging
from datetime import datetime, timedelta
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ticklisto.services.reminder_service import ReminderService
from ticklisto.services.gmail_service import GmailService
from ticklisto.services.storage_service import StorageService
from ticklisto.services.time_zone_service import TimeZoneService
from ticklisto.models.task import Task, Priority
from ticklisto.models.reminder import ReminderSetting


class StabilityMonitor:
    """Monitor reminder service stability over time."""

    def __init__(self, duration_hours: float, log_file: str = "stability_test.log"):
        """
        Initialize stability monitor.

        Args:
            duration_hours: Test duration in hours
            log_file: Path to log file
        """
        self.duration_hours = duration_hours
        self.log_file = log_file
        self.start_time = None
        self.end_time = None
        self.check_count = 0
        self.error_count = 0
        self.memory_samples = []
        self.process = psutil.Process()

        # Set up logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def setup_services(self):
        """Set up reminder service and dependencies."""
        self.logger.info("Setting up services...")

        # Use test data files
        self.test_reminders_file = "test_stability_reminders.json"
        self.test_tasks_file = "test_stability_tasks.json"

        # Clean up any existing test files
        for f in [self.test_reminders_file, self.test_tasks_file]:
            if os.path.exists(f):
                os.remove(f)

        # Create services
        self.storage_service = StorageService()
        self.time_zone_service = TimeZoneService()
        self.gmail_service = GmailService()  # Will use mock in test mode

        self.reminder_service = ReminderService(
            gmail_service=self.gmail_service,
            storage_service=self.storage_service,
            time_zone_service=self.time_zone_service,
            reminders_file=self.test_reminders_file
        )

        self.logger.info("Services set up successfully")

    def add_test_tasks_with_reminders(self):
        """Add test tasks with reminders scheduled throughout the test period."""
        self.logger.info("Adding test tasks with reminders...")

        # Add tasks with reminders at various intervals
        base_time = datetime.now()

        for i in range(10):
            # Schedule reminders at different times during the test
            due_datetime = base_time + timedelta(minutes=10 + i * 5)

            task = Task(
                id=i + 1,
                title=f"Stability test task {i + 1}",
                description=f"Test task for stability monitoring",
                priority=Priority.MEDIUM,
                categories=["stability-test"],
                due_date=due_datetime,
                due_time=due_datetime.time(),
                reminder_settings=[
                    ReminderSetting(offset_minutes=5, label="5 minutes before")
                ]
            )

            # Schedule reminders
            reminders = self.reminder_service.schedule_reminders(task)
            self.logger.info(f"Scheduled {len(reminders)} reminder(s) for task {task.id}")

    def record_memory_usage(self):
        """Record current memory usage."""
        memory_info = self.process.memory_info()
        memory_mb = memory_info.rss / 1024 / 1024  # Convert to MB
        self.memory_samples.append({
            'timestamp': datetime.now(),
            'memory_mb': memory_mb
        })
        return memory_mb

    def check_service_health(self):
        """Check if reminder service is healthy."""
        try:
            # Check if service is running
            if not self.reminder_service._running:
                self.logger.error("Reminder service is not running!")
                self.error_count += 1
                return False

            # Check if thread is alive
            if not self.reminder_service._check_thread.is_alive():
                self.logger.error("Reminder service thread is not alive!")
                self.error_count += 1
                return False

            # Get service status
            status = self.reminder_service.get_status()
            self.logger.debug(f"Service status: {status}")

            return True

        except Exception as e:
            self.logger.error(f"Error checking service health: {e}")
            self.error_count += 1
            return False

    def run_stability_test(self):
        """Run the stability test for the specified duration."""
        self.logger.info(f"Starting {self.duration_hours} hour stability test...")
        self.logger.info(f"Test will run until {datetime.now() + timedelta(hours=self.duration_hours)}")

        self.start_time = datetime.now()
        self.end_time = self.start_time + timedelta(hours=self.duration_hours)

        # Set up services
        self.setup_services()

        # Start reminder service
        self.logger.info("Starting reminder service...")
        self.reminder_service.start()
        time.sleep(2)  # Give it time to start

        # Add test tasks
        self.add_test_tasks_with_reminders()

        # Record initial memory
        initial_memory = self.record_memory_usage()
        self.logger.info(f"Initial memory usage: {initial_memory:.2f} MB")

        # Monitor loop
        check_interval = 60  # Check every minute
        next_check = datetime.now() + timedelta(seconds=check_interval)

        try:
            while datetime.now() < self.end_time:
                # Wait until next check time
                now = datetime.now()
                if now < next_check:
                    time.sleep(1)
                    continue

                # Perform health check
                self.check_count += 1
                self.logger.info(f"Health check #{self.check_count}")

                is_healthy = self.check_service_health()
                memory_mb = self.record_memory_usage()

                self.logger.info(f"Memory usage: {memory_mb:.2f} MB")

                if not is_healthy:
                    self.logger.warning("Service health check failed!")

                # Calculate progress
                elapsed = datetime.now() - self.start_time
                remaining = self.end_time - datetime.now()
                progress = (elapsed.total_seconds() / (self.duration_hours * 3600)) * 100

                self.logger.info(f"Progress: {progress:.1f}% | Elapsed: {elapsed} | Remaining: {remaining}")

                # Schedule next check
                next_check = datetime.now() + timedelta(seconds=check_interval)

        except KeyboardInterrupt:
            self.logger.info("Test interrupted by user")

        finally:
            # Stop reminder service
            self.logger.info("Stopping reminder service...")
            self.reminder_service.stop()

            # Generate report
            self.generate_report()

            # Cleanup
            self.cleanup()

    def generate_report(self):
        """Generate stability test report."""
        self.logger.info("\n" + "=" * 80)
        self.logger.info("STABILITY TEST REPORT")
        self.logger.info("=" * 80)

        # Test duration
        actual_duration = datetime.now() - self.start_time
        self.logger.info(f"Test Duration: {actual_duration}")
        self.logger.info(f"Target Duration: {self.duration_hours} hours")

        # Health checks
        self.logger.info(f"Total Health Checks: {self.check_count}")
        self.logger.info(f"Errors Detected: {self.error_count}")
        success_rate = ((self.check_count - self.error_count) / self.check_count * 100) if self.check_count > 0 else 0
        self.logger.info(f"Success Rate: {success_rate:.2f}%")

        # Memory analysis
        if len(self.memory_samples) > 1:
            initial_memory = self.memory_samples[0]['memory_mb']
            final_memory = self.memory_samples[-1]['memory_mb']
            max_memory = max(s['memory_mb'] for s in self.memory_samples)
            avg_memory = sum(s['memory_mb'] for s in self.memory_samples) / len(self.memory_samples)

            self.logger.info(f"\nMemory Usage:")
            self.logger.info(f"  Initial: {initial_memory:.2f} MB")
            self.logger.info(f"  Final: {final_memory:.2f} MB")
            self.logger.info(f"  Maximum: {max_memory:.2f} MB")
            self.logger.info(f"  Average: {avg_memory:.2f} MB")
            self.logger.info(f"  Growth: {final_memory - initial_memory:.2f} MB ({((final_memory - initial_memory) / initial_memory * 100):.2f}%)")

            # Check for memory leak
            if final_memory > initial_memory * 1.5:
                self.logger.warning("⚠️  Potential memory leak detected (>50% growth)")
            else:
                self.logger.info("✓ No significant memory leak detected")

        # Overall result
        self.logger.info("\n" + "=" * 80)
        if self.error_count == 0 and success_rate == 100:
            self.logger.info("✓ STABILITY TEST PASSED")
        else:
            self.logger.warning("✗ STABILITY TEST FAILED")
        self.logger.info("=" * 80 + "\n")

    def cleanup(self):
        """Clean up test files."""
        self.logger.info("Cleaning up test files...")
        for f in [self.test_reminders_file, self.test_tasks_file]:
            if os.path.exists(f):
                os.remove(f)
                self.logger.info(f"Removed {f}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Reminder service stability test")
    parser.add_argument(
        '--duration',
        type=float,
        default=24.0,
        help='Test duration in hours (default: 24)'
    )
    parser.add_argument(
        '--log-file',
        type=str,
        default='stability_test.log',
        help='Log file path (default: stability_test.log)'
    )

    args = parser.parse_args()

    # Create monitor and run test
    monitor = StabilityMonitor(
        duration_hours=args.duration,
        log_file=args.log_file
    )

    monitor.run_stability_test()


if __name__ == '__main__':
    main()
