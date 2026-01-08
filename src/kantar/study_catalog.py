"""
Study catalog for discovering and managing Kantar survey studies.

This module scans the Kantar survey source directory and builds an index
of available studies, markets, and associated files.
"""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


@dataclass
class MarketInfo:
    """Information about a market within a study."""
    market_code: str
    pptx_files: List[Path]
    excel_files: List[Path]
    market_path: Path

    @property
    def has_concept_presentation(self) -> bool:
        """Check if market has at least one PPTX file."""
        return len(self.pptx_files) > 0

    @property
    def has_ground_truth(self) -> bool:
        """Check if market has at least one Excel file."""
        return len(self.excel_files) > 0

    @property
    def is_complete(self) -> bool:
        """Check if market has both PPTX and Excel files."""
        return self.has_concept_presentation and self.has_ground_truth


@dataclass
class StudyInfo:
    """Information about a Kantar study."""
    study_id: str
    study_name: str
    study_path: Path
    markets: Dict[str, MarketInfo]

    @property
    def market_codes(self) -> List[str]:
        """Get list of all market codes in this study."""
        return sorted(self.markets.keys())

    @property
    def complete_markets(self) -> List[str]:
        """Get list of markets with both PPTX and Excel files."""
        return [code for code, market in self.markets.items() if market.is_complete]

    def get_market(self, market_code: str) -> Optional[MarketInfo]:
        """Get market info by code."""
        return self.markets.get(market_code.upper())


class StudyCatalog:
    """
    Catalog of available Kantar studies and markets.

    Scans the data/kantar-survey-source directory and indexes all studies,
    markets, and associated files.
    """

    def __init__(self, base_path: Optional[Path] = None):
        """
        Initialize the study catalog.

        Args:
            base_path: Path to kantar-survey-source directory. If None, uses default.
        """
        if base_path is None:
            # Default to data/kantar-survey-source relative to project root
            project_root = Path(__file__).parent.parent.parent
            base_path = project_root / "data" / "kantar-survey-source"

        self.base_path = Path(base_path)
        self.studies: Dict[str, StudyInfo] = {}

        if self.base_path.exists():
            self._scan_studies()
        else:
            logger.warning(f"Kantar survey source directory not found: {self.base_path}")

    def _scan_studies(self):
        """Scan the base directory and catalog all studies."""
        logger.info(f"Scanning for Kantar studies in: {self.base_path}")

        for study_dir in self.base_path.iterdir():
            if not study_dir.is_dir() or study_dir.name.startswith('.'):
                continue

            study_info = self._scan_study(study_dir)
            if study_info and study_info.markets:
                self.studies[study_info.study_id] = study_info
                logger.info(
                    f"Found study: {study_info.study_id} "
                    f"({len(study_info.markets)} markets, "
                    f"{len(study_info.complete_markets)} complete)"
                )

    def _scan_study(self, study_path: Path) -> Optional[StudyInfo]:
        """
        Scan a study directory and extract study information.

        Args:
            study_path: Path to study directory

        Returns:
            StudyInfo object or None if invalid
        """
        study_name = study_path.name

        # Extract study ID from directory name (format: ID_QN_Name)
        parts = study_name.split('_', 2)
        if len(parts) >= 1:
            study_id = parts[0]
        else:
            study_id = study_name

        markets = {}

        # Scan for market directories
        for market_dir in study_path.iterdir():
            if not market_dir.is_dir() or market_dir.name.startswith('.'):
                continue

            # Market code is the directory name (e.g., "US", "UK", "AT")
            market_code = market_dir.name.upper()

            # Find PPTX and Excel files
            pptx_files = list(market_dir.glob("*.pptx"))
            excel_files = list(market_dir.glob("*.xlsx"))

            # Filter out temporary Excel files
            excel_files = [f for f in excel_files if not f.name.startswith('~$')]

            if pptx_files or excel_files:
                markets[market_code] = MarketInfo(
                    market_code=market_code,
                    pptx_files=pptx_files,
                    excel_files=excel_files,
                    market_path=market_dir
                )

        return StudyInfo(
            study_id=study_id,
            study_name=study_name,
            study_path=study_path,
            markets=markets
        )

    def list_studies(self) -> List[str]:
        """Get list of all study IDs."""
        return sorted(self.studies.keys())

    def get_study(self, study_id: str) -> Optional[StudyInfo]:
        """
        Get study information by ID.

        Args:
            study_id: Study ID (can be full name or just the ID part)

        Returns:
            StudyInfo object or None if not found
        """
        # Try exact match first
        if study_id in self.studies:
            return self.studies[study_id]

        # Try matching against study IDs
        for sid, study in self.studies.items():
            if study_id in sid or sid in study_id:
                return study

        return None

    def list_markets(self, study_id: str) -> List[str]:
        """
        Get list of market codes for a study.

        Args:
            study_id: Study ID

        Returns:
            List of market codes
        """
        study = self.get_study(study_id)
        return study.market_codes if study else []

    def get_ground_truth_path(self, study_id: str, market_code: str) -> Optional[Path]:
        """
        Get path to ground truth Excel file for a specific market.

        Args:
            study_id: Study ID
            market_code: Market code (e.g., "US")

        Returns:
            Path to Excel file or None if not found
        """
        study = self.get_study(study_id)
        if not study:
            return None

        market = study.get_market(market_code)
        if not market or not market.excel_files:
            return None

        # Return first Excel file (should typically be only one)
        return market.excel_files[0]

    def get_concept_presentation_path(self, study_id: str, market_code: str) -> Optional[Path]:
        """
        Get path to concept presentation PPTX file for a specific market.

        Args:
            study_id: Study ID
            market_code: Market code (e.g., "US")

        Returns:
            Path to PPTX file or None if not found
        """
        study = self.get_study(study_id)
        if not study:
            return None

        market = study.get_market(market_code)
        if not market or not market.pptx_files:
            return None

        # Return first PPTX file (should typically be only one)
        return market.pptx_files[0]

    def get_market_info(self, study_id: str, market_code: str) -> Optional[MarketInfo]:
        """
        Get complete market information.

        Args:
            study_id: Study ID
            market_code: Market code

        Returns:
            MarketInfo object or None if not found
        """
        study = self.get_study(study_id)
        if not study:
            return None

        return study.get_market(market_code)

    def print_summary(self):
        """Print a summary of all available studies and markets."""
        print("\n=== Kantar Study Catalog ===\n")
        print(f"Base path: {self.base_path}\n")

        if not self.studies:
            print("No studies found.")
            return

        for study_id in sorted(self.studies.keys()):
            study = self.studies[study_id]
            print(f"Study: {study.study_name}")
            print(f"  ID: {study_id}")
            print(f"  Markets: {len(study.markets)}")
            print(f"  Complete markets: {len(study.complete_markets)}")

            for market_code in study.market_codes:
                market = study.markets[market_code]
                status = "✓" if market.is_complete else "✗"
                print(f"    {status} {market_code}: "
                      f"{len(market.pptx_files)} PPTX, "
                      f"{len(market.excel_files)} Excel")
            print()


def main():
    """CLI entry point for testing the catalog."""
    logging.basicConfig(level=logging.INFO)

    catalog = StudyCatalog()
    catalog.print_summary()


if __name__ == "__main__":
    main()
