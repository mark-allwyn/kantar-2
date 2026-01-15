"""
Checkpoint management for resumable synthetic data generation.

Provides checkpoint saving/loading for long-running generation processes.
"""

import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime
from dataclasses import asdict, is_dataclass

logger = logging.getLogger(__name__)


def _convert_to_serializable(obj):
    """
    Convert dataclasses and other non-serializable objects to JSON-serializable format.

    Args:
        obj: Object to convert

    Returns:
        JSON-serializable version of the object
    """
    if is_dataclass(obj) and not isinstance(obj, type):
        return asdict(obj)
    elif isinstance(obj, list):
        return [_convert_to_serializable(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: _convert_to_serializable(value) for key, value in obj.items()}
    else:
        return obj


class CheckpointManager:
    """
    Manages checkpoints for resumable generation.

    Features:
    - Save generation state at intervals
    - Resume from last checkpoint
    - Clean up old checkpoints
    - Track metadata and configuration
    """

    def __init__(self, checkpoint_dir: Optional[Path] = None):
        """
        Initialize checkpoint manager.

        Args:
            checkpoint_dir: Directory for checkpoint files (default: data/checkpoints/)
        """
        if checkpoint_dir is None:
            checkpoint_dir = Path("data/checkpoints")

        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)

    def save_checkpoint(self,
                        job_id: str,
                        completed_respondents: List[Dict],
                        total_respondents: int,
                        generation_config: Dict[str, Any],
                        metadata: Optional[Dict] = None) -> Path:
        """
        Save a checkpoint.

        Args:
            job_id: Unique job identifier (e.g., "61405445-01_US_50resp")
            completed_respondents: List of completed respondent data
            total_respondents: Total number of respondents to generate
            generation_config: Generation configuration (study_id, market, model, etc.)
            metadata: Optional additional metadata

        Returns:
            Path to checkpoint file
        """
        # Convert dataclasses to serializable format
        serializable_respondents = _convert_to_serializable(completed_respondents)

        checkpoint_data = {
            'job_id': job_id,
            'checkpoint_time': datetime.now().isoformat(),
            'completed': len(completed_respondents),
            'total': total_respondents,
            'progress_pct': (len(completed_respondents) / total_respondents) * 100,
            'generation_config': generation_config,
            'metadata': metadata or {},
            'respondent_data': serializable_respondents
        }

        checkpoint_file = self.checkpoint_dir / f"{job_id}_checkpoint.json"

        with open(checkpoint_file, 'w') as f:
            json.dump(checkpoint_data, f, indent=2)

        logger.info(f"Checkpoint saved: {checkpoint_file}")
        logger.info(f"  Progress: {len(completed_respondents)}/{total_respondents} respondents")

        return checkpoint_file

    def load_checkpoint(self, job_id: str) -> Optional[Dict]:
        """
        Load checkpoint for a job.

        Args:
            job_id: Job identifier

        Returns:
            Checkpoint data dict or None if not found
        """
        checkpoint_file = self.checkpoint_dir / f"{job_id}_checkpoint.json"

        if not checkpoint_file.exists():
            return None

        with open(checkpoint_file) as f:
            checkpoint_data = json.load(f)

        logger.info(f"Checkpoint loaded: {checkpoint_file}")
        logger.info(f"  Progress: {checkpoint_data['completed']}/{checkpoint_data['total']} respondents")
        logger.info(f"  Last saved: {checkpoint_data['checkpoint_time']}")

        return checkpoint_data

    def has_checkpoint(self, job_id: str) -> bool:
        """
        Check if checkpoint exists for a job.

        Args:
            job_id: Job identifier

        Returns:
            True if checkpoint exists
        """
        checkpoint_file = self.checkpoint_dir / f"{job_id}_checkpoint.json"
        return checkpoint_file.exists()

    def delete_checkpoint(self, job_id: str) -> bool:
        """
        Delete checkpoint for a job.

        Args:
            job_id: Job identifier

        Returns:
            True if deleted, False if not found
        """
        checkpoint_file = self.checkpoint_dir / f"{job_id}_checkpoint.json"

        if checkpoint_file.exists():
            checkpoint_file.unlink()
            logger.info(f"Checkpoint deleted: {checkpoint_file}")
            return True

        return False

    def list_checkpoints(self) -> List[Dict[str, Any]]:
        """
        List all available checkpoints.

        Returns:
            List of checkpoint summaries with job_id, progress, and timestamp
        """
        checkpoints = []

        for checkpoint_file in self.checkpoint_dir.glob("*_checkpoint.json"):
            try:
                with open(checkpoint_file) as f:
                    data = json.load(f)

                checkpoints.append({
                    'job_id': data['job_id'],
                    'completed': data['completed'],
                    'total': data['total'],
                    'progress_pct': data['progress_pct'],
                    'checkpoint_time': data['checkpoint_time'],
                    'file_path': str(checkpoint_file)
                })
            except Exception as e:
                logger.warning(f"Failed to read checkpoint {checkpoint_file}: {e}")

        # Sort by checkpoint time (newest first)
        checkpoints.sort(key=lambda x: x['checkpoint_time'], reverse=True)

        return checkpoints

    def clean_old_checkpoints(self, keep_days: int = 7) -> int:
        """
        Delete checkpoints older than specified days.

        Args:
            keep_days: Keep checkpoints from last N days

        Returns:
            Number of checkpoints deleted
        """
        from datetime import timedelta

        cutoff_date = datetime.now() - timedelta(days=keep_days)
        deleted = 0

        for checkpoint_file in self.checkpoint_dir.glob("*_checkpoint.json"):
            try:
                with open(checkpoint_file) as f:
                    data = json.load(f)

                checkpoint_time = datetime.fromisoformat(data['checkpoint_time'])

                if checkpoint_time < cutoff_date:
                    checkpoint_file.unlink()
                    logger.info(f"Deleted old checkpoint: {checkpoint_file}")
                    deleted += 1
            except Exception as e:
                logger.warning(f"Failed to process checkpoint {checkpoint_file}: {e}")

        if deleted > 0:
            logger.info(f"Cleaned up {deleted} old checkpoints")

        return deleted


def create_job_id(study_id: str, market_code: str, num_respondents: int) -> str:
    """
    Create a unique job ID for checkpoint tracking.

    Args:
        study_id: Study identifier
        market_code: Market code
        num_respondents: Target respondent count

    Returns:
        Unique job ID string
    """
    return f"{study_id}_{market_code}_{num_respondents}resp"


def create_job_id_custom(output_name: str, num_respondents: int) -> str:
    """
    Create job ID for custom concept generation.

    Args:
        output_name: Output file name prefix
        num_respondents: Target respondent count

    Returns:
        Unique job ID string
    """
    return f"{output_name}_{num_respondents}resp"
