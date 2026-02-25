"""LangChain tools for analyzing the Titanic dataset."""

from langchain.tools import Tool
from langchain.pydantic_v1 import BaseModel, Field
from typing import Optional
import pandas as pd
import logging

from backend.data_loader import data_loader
from backend.visualization import chart_generator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TitanicTools:
    """Collection of tools for analyzing the Titanic dataset."""
    
    def __init__(self):
        """Initialize tools with the dataset."""
        self.df = data_loader.get_data()
    
    def get_dataset_summary(self, input: str = "") -> str:
        """Get a comprehensive summary of the Titanic dataset.
        
        Args:
            input: Unused, kept for LangChain compatibility.
            
        Returns:
            String containing dataset summary.
        """
        try:
            summary = data_loader.get_summary()
            
            result = f"""Dataset Summary:
- Total Passengers: {summary['total_passengers']}
- Total Survived: {summary['total_survived']}
- Survival Rate: {summary['survival_rate']}
- Passenger Classes: {summary['passenger_classes']}
- Embarkation Ports: {summary['embarked_ports']}
- Age Range: {summary['age_range']['min']:.1f} to {summary['age_range']['max']:.1f} years (mean: {summary['age_range']['mean']:.1f})
- Fare Range: ${summary['fare_range']['min']:.2f} to ${summary['fare_range']['max']:.2f} (mean: ${summary['fare_range']['mean']:.2f})
"""
            return result
        except Exception as e:
            logger.error(f"Error in get_dataset_summary: {e}")
            return f"Error getting dataset summary: {str(e)}"
    
    def calculate_gender_distribution(self, input: str = "") -> str:
        """Calculate the distribution of passengers by gender.
        
        Args:
            input: Unused, kept for LangChain compatibility.
            
        Returns:
            String containing gender distribution statistics.
        """
        try:
            total = len(self.df)
            male_count = len(self.df[self.df['Sex'] == 'male'])
            female_count = len(self.df[self.df['Sex'] == 'female'])
            
            male_pct = (male_count / total) * 100
            female_pct = (female_count / total) * 100
            
            result = f"""Gender Distribution:
- Male: {male_count} passengers ({male_pct:.2f}%)
- Female: {female_count} passengers ({female_pct:.2f}%)
- Total: {total} passengers
"""
            return result
        except Exception as e:
            logger.error(f"Error in calculate_gender_distribution: {e}")
            return f"Error calculating gender distribution: {str(e)}"
    
    def calculate_survival_rate(self, input: str = "") -> str:
        """Calculate overall survival rate and by different categories.
        
        Args:
            input: Unused, kept for LangChain compatibility.
            
        Returns:
            String containing survival rate statistics.
        """
        try:
            overall_survival = self.df['Survived'].mean() * 100
            total_survived = self.df['Survived'].sum()
            total = len(self.df)
            
            result = f"""Survival Statistics:
- Overall Survival Rate: {overall_survival:.2f}%
- Survived: {int(total_survived)} passengers
- Perished: {int(total - total_survived)} passengers

Survival by Gender:
"""
            # By gender
            for gender in ['male', 'female']:
                gender_df = self.df[self.df['Sex'] == gender]
                survival_rate = gender_df['Survived'].mean() * 100
                survived = gender_df['Survived'].sum()
                total_gender = len(gender_df)
                result += f"- {gender.capitalize()}: {survival_rate:.2f}% ({int(survived)}/{total_gender})\n"
            
            result += "\nSurvival by Class:\n"
            # By class
            for pclass in sorted(self.df['Pclass'].unique()):
                class_df = self.df[self.df['Pclass'] == pclass]
                survival_rate = class_df['Survived'].mean() * 100
                survived = class_df['Survived'].sum()
                total_class = len(class_df)
                result += f"- Class {pclass}: {survival_rate:.2f}% ({int(survived)}/{total_class})\n"
            
            return result
        except Exception as e:
            logger.error(f"Error in calculate_survival_rate: {e}")
            return f"Error calculating survival rate: {str(e)}"
    
    def calculate_average_fare(self, input: str = "") -> str:
        """Calculate average fare statistics.
        
        Args:
            input: Unused, kept for LangChain compatibility.
            
        Returns:
            String containing fare statistics.
        """
        try:
            avg_fare = self.df['Fare'].mean()
            median_fare = self.df['Fare'].median()
            min_fare = self.df['Fare'].min()
            max_fare = self.df['Fare'].max()
            
            result = f"""Fare Statistics:
- Average Fare: ${avg_fare:.2f}
- Median Fare: ${median_fare:.2f}
- Minimum Fare: ${min_fare:.2f}
- Maximum Fare: ${max_fare:.2f}

Average Fare by Class:
"""
            for pclass in sorted(self.df['Pclass'].unique()):
                class_avg = self.df[self.df['Pclass'] == pclass]['Fare'].mean()
                result += f"- Class {pclass}: ${class_avg:.2f}\n"
            
            return result
        except Exception as e:
            logger.error(f"Error in calculate_average_fare: {e}")
            return f"Error calculating average fare: {str(e)}"
    
    def calculate_age_statistics(self, input: str = "") -> str:
        """Calculate age-related statistics.
        
        Args:
            input: Unused, kept for LangChain compatibility.
            
        Returns:
            String containing age statistics.
        """
        try:
            age_data = self.df['Age'].dropna()
            
            result = f"""Age Statistics:
- Average Age: {age_data.mean():.2f} years
- Median Age: {age_data.median():.2f} years
- Minimum Age: {age_data.min():.2f} years
- Maximum Age: {age_data.max():.2f} years
- Standard Deviation: {age_data.std():.2f} years
- Total passengers with age data: {len(age_data)} out of {len(self.df)}
"""
            return result
        except Exception as e:
            logger.error(f"Error in calculate_age_statistics: {e}")
            return f"Error calculating age statistics: {str(e)}"
    
    def get_embarkation_distribution(self, input: str = "") -> str:
        """Get distribution of passengers by embarkation port.
        
        Args:
            input: Unused, kept for LangChain compatibility.
            
        Returns:
            String containing embarkation distribution.
        """
        try:
            embark_counts = self.df['Embarked'].value_counts()
            total_with_data = embark_counts.sum()
            
            port_names = {
                'S': 'Southampton',
                'C': 'Cherbourg',
                'Q': 'Queenstown'
            }
            
            result = "Embarkation Port Distribution:\n"
            for port, count in embark_counts.items():
                port_name = port_names.get(port, port)
                percentage = (count / total_with_data) * 100
                result += f"- {port_name} ({port}): {count} passengers ({percentage:.2f}%)\n"
            
            return result
        except Exception as e:
            logger.error(f"Error in get_embarkation_distribution: {e}")
            return f"Error getting embarkation distribution: {str(e)}"
    
    def get_class_distribution(self, input: str = "") -> str:
        """Get distribution of passengers by class.
        
        Args:
            input: Unused, kept for LangChain compatibility.
            
        Returns:
            String containing class distribution.
        """
        try:
            class_counts = self.df['Pclass'].value_counts().sort_index()
            total = len(self.df)
            
            result = "Passenger Class Distribution:\n"
            for pclass, count in class_counts.items():
                percentage = (count / total) * 100
                result += f"- Class {pclass}: {count} passengers ({percentage:.2f}%)\n"
            
            return result
        except Exception as e:
            logger.error(f"Error in get_class_distribution: {e}")
            return f"Error getting class distribution: {str(e)}"
    
    def get_family_statistics(self, input: str = "") -> str:
        """Get statistics about families (siblings/spouses and parents/children).
        
        Args:
            input: Unused, kept for LangChain compatibility.
            
        Returns:
            String containing family statistics.
        """
        try:
            # Create family size column
            df_copy = self.df.copy()
            df_copy['FamilySize'] = df_copy['SibSp'] + df_copy['Parch'] + 1
            
            alone = len(df_copy[df_copy['FamilySize'] == 1])
            with_family = len(df_copy[df_copy['FamilySize'] > 1])
            
            result = f"""Family Statistics:
- Passengers traveling alone: {alone} ({(alone/len(df_copy)*100):.2f}%)
- Passengers with family: {with_family} ({(with_family/len(df_copy)*100):.2f}%)
- Average family size: {df_copy['FamilySize'].mean():.2f} people
- Largest family: {df_copy['FamilySize'].max()} people
- Average siblings/spouses: {df_copy['SibSp'].mean():.2f}
- Average parents/children: {df_copy['Parch'].mean():.2f}
"""
            return result
        except Exception as e:
            logger.error(f"Error in get_family_statistics: {e}")
            return f"Error getting family statistics: {str(e)}"


def create_titanic_tools() -> list:
    """Create a list of LangChain tools for the Titanic dataset.
    
    Returns:
        List of Tool objects.
    """
    titanic_tools = TitanicTools()
    
    tools = [
        Tool(
            name="get_dataset_summary",
            func=titanic_tools.get_dataset_summary,
            description="Get a comprehensive summary of the Titanic dataset including total passengers, survival rate, age range, fare range, and available columns. Use this when user asks for general information or overview."
        ),
        Tool(
            name="calculate_gender_distribution",
            func=titanic_tools.calculate_gender_distribution,
            description="Calculate and return the distribution of passengers by gender (male/female) with counts and percentages. Use this when user asks about gender, male, female, or sex distribution."
        ),
        Tool(
            name="calculate_survival_rate",
            func=titanic_tools.calculate_survival_rate,
            description="Calculate survival rates overall and broken down by gender and class. Use this when user asks about survival, who survived, survival rate, or death statistics."
        ),
        Tool(
            name="calculate_average_fare",
            func=titanic_tools.calculate_average_fare,
            description="Calculate fare statistics including average, median, min, max, and average by class. Use this when user asks about ticket prices, fares, or costs."
        ),
        Tool(
            name="calculate_age_statistics",
            func=titanic_tools.calculate_age_statistics,
            description="Calculate age-related statistics including average, median, min, max, and standard deviation. Use this when user asks about passenger ages."
        ),
        Tool(
            name="get_embarkation_distribution",
            func=titanic_tools.get_embarkation_distribution,
            description="Get the distribution of passengers by embarkation port (Southampton, Cherbourg, Queenstown). Use this when user asks about where passengers boarded or embarkation ports."
        ),
        Tool(
            name="get_class_distribution",
            func=titanic_tools.get_class_distribution,
            description="Get the distribution of passengers across different classes (1st, 2nd, 3rd). Use this when user asks about passenger classes or class distribution."
        ),
        Tool(
            name="get_family_statistics",
            func=titanic_tools.get_family_statistics,
            description="Get statistics about families including passengers traveling alone vs with family, family sizes, siblings/spouses, and parents/children. Use this when user asks about families, traveling alone, or relationships."
        ),
    ]
    
    return tools
