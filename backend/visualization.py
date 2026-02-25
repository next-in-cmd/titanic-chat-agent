"""Visualization tools for generating charts from Titanic data."""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import io
import base64
from typing import Optional, Tuple
import logging

from backend.config import CHART_DPI, CHART_FIGSIZE

# Use non-interactive backend for server environments
matplotlib.use('Agg')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ChartGenerator:
    """Generate various charts from the Titanic dataset."""
    
    def __init__(self):
        """Initialize the chart generator."""
        plt.style.use('seaborn-v0_8-darkgrid')
    
    def _fig_to_base64(self, fig) -> str:
        """Convert matplotlib figure to base64 string.
        
        Args:
            fig: Matplotlib figure object.
            
        Returns:
            Base64 encoded string of the figure.
        """
        buf = io.BytesIO()
        fig.savefig(buf, format='png', dpi=CHART_DPI, bbox_inches='tight')
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')
        buf.close()
        plt.close(fig)
        return img_base64
    
    def create_histogram(
        self, 
        data: pd.Series, 
        title: str, 
        xlabel: str, 
        bins: int = 30,
        color: str = '#3498db'
    ) -> str:
        """Create a histogram.
        
        Args:
            data: Pandas Series containing the data.
            title: Chart title.
            xlabel: X-axis label.
            bins: Number of bins.
            color: Bar color.
            
        Returns:
            Base64 encoded string of the chart.
        """
        fig, ax = plt.subplots(figsize=CHART_FIGSIZE)
        
        # Remove NaN values
        clean_data = data.dropna()
        
        ax.hist(clean_data, bins=bins, color=color, edgecolor='black', alpha=0.7)
        ax.set_title(title, fontsize=16, fontweight='bold')
        ax.set_xlabel(xlabel, fontsize=12)
        ax.set_ylabel('Frequency', fontsize=12)
        ax.grid(True, alpha=0.3)
        
        return self._fig_to_base64(fig)
    
    def create_bar_chart(
        self, 
        labels: list, 
        values: list, 
        title: str, 
        xlabel: str, 
        ylabel: str,
        color: str = '#2ecc71'
    ) -> str:
        """Create a bar chart.
        
        Args:
            labels: List of labels for x-axis.
            values: List of values for y-axis.
            title: Chart title.
            xlabel: X-axis label.
            ylabel: Y-axis label.
            color: Bar color.
            
        Returns:
            Base64 encoded string of the chart.
        """
        fig, ax = plt.subplots(figsize=CHART_FIGSIZE)
        
        bars = ax.bar(labels, values, color=color, edgecolor='black', alpha=0.7)
        ax.set_title(title, fontsize=16, fontweight='bold')
        ax.set_xlabel(xlabel, fontsize=12)
        ax.set_ylabel(ylabel, fontsize=12)
        ax.grid(True, alpha=0.3, axis='y')
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.1f}',
                   ha='center', va='bottom', fontsize=10)
        
        return self._fig_to_base64(fig)
    
    def create_pie_chart(
        self, 
        labels: list, 
        values: list, 
        title: str,
        colors: Optional[list] = None
    ) -> str:
        """Create a pie chart.
        
        Args:
            labels: List of labels.
            values: List of values.
            title: Chart title.
            colors: Optional list of colors.
            
        Returns:
            Base64 encoded string of the chart.
        """
        if colors is None:
            colors = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6', '#1abc9c']
        
        fig, ax = plt.subplots(figsize=CHART_FIGSIZE)
        
        wedges, texts, autotexts = ax.pie(
            values, 
            labels=labels, 
            autopct='%1.1f%%',
            colors=colors[:len(labels)],
            startangle=90,
            textprops={'fontsize': 12}
        )
        
        # Make percentage text bold
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        
        ax.set_title(title, fontsize=16, fontweight='bold')
        
        return self._fig_to_base64(fig)
    
    def create_grouped_bar_chart(
        self,
        df: pd.DataFrame,
        title: str,
        xlabel: str,
        ylabel: str
    ) -> str:
        """Create a grouped bar chart.
        
        Args:
            df: DataFrame with data for grouped bars.
            title: Chart title.
            xlabel: X-axis label.
            ylabel: Y-axis label.
            
        Returns:
            Base64 encoded string of the chart.
        """
        fig, ax = plt.subplots(figsize=CHART_FIGSIZE)
        
        df.plot(kind='bar', ax=ax, color=['#3498db', '#e74c3c'], edgecolor='black', alpha=0.7)
        ax.set_title(title, fontsize=16, fontweight='bold')
        ax.set_xlabel(xlabel, fontsize=12)
        ax.set_ylabel(ylabel, fontsize=12)
        ax.legend(title='', fontsize=10)
        ax.grid(True, alpha=0.3, axis='y')
        plt.xticks(rotation=45, ha='right')
        
        return self._fig_to_base64(fig)


# Global instance
chart_generator = ChartGenerator()
