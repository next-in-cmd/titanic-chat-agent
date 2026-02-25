"""Data loader for Titanic dataset."""

import pandas as pd
from pathlib import Path
from typing import Optional
import logging

from backend.config import TITANIC_CSV_PATH

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TitanicDataLoader:
    """Singleton class to load and manage Titanic dataset."""
    
    _instance: Optional['TitanicDataLoader'] = None
    _df: Optional[pd.DataFrame] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TitanicDataLoader, cls).__new__(cls)
        return cls._instance
    
    def load_data(self, csv_path: Optional[Path] = None) -> pd.DataFrame:
        """Load the Titanic dataset from CSV file.
        
        Args:
            csv_path: Path to the CSV file. If None, uses default path.
            
        Returns:
            DataFrame containing the Titanic dataset.
        """
        if self._df is not None:
            logger.info("Returning cached dataset")
            return self._df
        
        path = csv_path or TITANIC_CSV_PATH
        
        try:
            logger.info(f"Loading dataset from {path}")
            self._df = pd.read_csv(path)
            logger.info(f"Dataset loaded successfully: {len(self._df)} rows, {len(self._df.columns)} columns")
            return self._df
        except FileNotFoundError:
            logger.error(f"Dataset file not found at {path}")
            raise
        except Exception as e:
            logger.error(f"Error loading dataset: {e}")
            raise
    
    def get_data(self) -> pd.DataFrame:
        """Get the loaded dataset or load it if not already loaded.
        
        Returns:
            DataFrame containing the Titanic dataset.
        """
        if self._df is None:
            return self.load_data()
        return self._df
    
    def get_summary(self) -> dict:
        """Get a summary of the dataset.
        
        Returns:
            Dictionary containing dataset summary information.
        """
        df = self.get_data()
        
        return {
            "total_passengers": len(df),
            "total_survived": int(df['Survived'].sum()),
            "survival_rate": f"{(df['Survived'].mean() * 100):.2f}%",
            "columns": list(df.columns),
            "missing_values": df.isnull().sum().to_dict(),
            "passenger_classes": sorted(df['Pclass'].unique().tolist()),
            "embarked_ports": df['Embarked'].dropna().unique().tolist(),
            "age_range": {
                "min": float(df['Age'].min()) if not df['Age'].isna().all() else None,
                "max": float(df['Age'].max()) if not df['Age'].isna().all() else None,
                "mean": float(df['Age'].mean()) if not df['Age'].isna().all() else None
            },
            "fare_range": {
                "min": float(df['Fare'].min()),
                "max": float(df['Fare'].max()),
                "mean": float(df['Fare'].mean())
            }
        }


# Global instance
data_loader = TitanicDataLoader()
