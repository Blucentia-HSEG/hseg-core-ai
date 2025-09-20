"""
HSEG Enterprise-Level Visualization Dashboard
============================================
Industrial-grade visualization suite for workplace culture assessment data
Designed for executive reporting and organizational insights
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
import plotly.figure_factory as ff
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

# Set professional styling
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("Set2")

class HSEGDashboard:
    def __init__(self, data_path):
        """Initialize dashboard with data loading and preprocessing"""
        self.data = pd.read_csv(data_path)
        self.process_data()
        self.define_scales()

    def process_data(self):
        """Clean and prepare data for analysis"""
        # Convert submission_date to datetime
        self.data['submission_date'] = pd.to_datetime(self.data['submission_date'])

        # Define HSEG categories and their questions
        self.categories = {
            'Power Abuse & Suppression': ['q1', 'q2', 'q3', 'q4'],
            'Discrimination & Exclusion': ['q5', 'q6', 'q7'],
            'Manipulative Work Culture': ['q8', 'q9', 'q10'],
            'Failure of Accountability': ['q11', 'q12', 'q13', 'q14'],
            'Mental Health Harm': ['q15', 'q16', 'q17', 'q18'],
            'Erosion of Voice & Autonomy': ['q19', 'q20', 'q21', 'q22']
        }

        # Calculate category scores with weights
        self.weights = {
            'Power Abuse & Suppression': 3.0,
            'Discrimination & Exclusion': 2.5,
            'Manipulative Work Culture': 2.0,
            'Failure of Accountability': 3.0,
            'Mental Health Harm': 2.5,
            'Erosion of Voice & Autonomy': 2.0
        }

        # Calculate weighted scores for each category
        for category, questions in self.categories.items():
            self.data[f'{category}_score'] = self.data[questions].mean(axis=1) * self.weights[category]

        # Calculate overall HSEG score
        category_cols = [f'{cat}_score' for cat in self.categories.keys()]
        self.data['hseg_total_score'] = self.data[category_cols].sum(axis=1)

        # Define risk tiers
        self.data['risk_tier'] = pd.cut(
            self.data['hseg_total_score'],
            bins=[0, 30, 45, 60, 75, 100],
            labels=['Crisis', 'At Risk', 'Mixed', 'Safe', 'Thriving'],
            include_lowest=True
        )

    def define_scales(self):
        """Define measurement scales for interpretation"""
        self.likert_scale = {
            1: "Strongly Disagree/Often/Severe",
            2: "Disagree/Sometimes/Moderate",
            3: "Agree/Rarely/Mild",
            4: "Strongly Agree/Never/None"
        }

        self.risk_colors = {
            'Crisis': '#d32f2f',
            'At Risk': '#ff9800',
            'Mixed': '#ffc107',
            'Safe': '#4caf50',
            'Thriving': '#2e7d32'
        }

    def create_executive_summary(self):
        """Generate executive summary dashboard"""
        fig = make_subplots(
            rows=2, cols=3,
            subplot_titles=(
                'Overall Risk Distribution', 'Risk by Domain', 'Risk by Organization Size',
                'Mental Health Impact Trends', 'Key Risk Indicators', 'Response Volume by Month'
            ),
            specs=[[{"type": "pie"}, {"type": "bar"}, {"type": "scatter"}],
                   [{"type": "scatter"}, {"type": "bar"}, {"type": "bar"}]]
        )

        # 1. Overall Risk Distribution (Pie)
        risk_counts = self.data['risk_tier'].value_counts()
        fig.add_trace(
            go.Pie(
                labels=risk_counts.index,
                values=risk_counts.values,
                marker_colors=[self.risk_colors[tier] for tier in risk_counts.index],
                name="Risk Distribution"
            ),
            row=1, col=1
        )

        # 2. Risk by Domain (Bar)
        domain_risk = self.data.groupby(['domain', 'risk_tier']).size().unstack(fill_value=0)
        for tier in domain_risk.columns:
            fig.add_trace(
                go.Bar(
                    x=domain_risk.index,
                    y=domain_risk[tier],
                    name=tier,
                    marker_color=self.risk_colors[tier],
                    showlegend=False
                ),
                row=1, col=2
            )

        # 3. Risk by Organization Size (Scatter)
        org_size_risk = self.data.groupby('employee_count').agg({
            'hseg_total_score': 'mean',
            'response_id': 'count'
        }).reset_index()

        fig.add_trace(
            go.Scatter(
                x=org_size_risk['employee_count'],
                y=org_size_risk['hseg_total_score'],
                mode='markers',
                marker=dict(
                    size=org_size_risk['response_id']/5,
                    color=org_size_risk['hseg_total_score'],
                    colorscale='RdYlGn',
                    showscale=True
                ),
                name="Org Size vs Risk"
            ),
            row=1, col=3
        )

        # 4. Mental Health Trends (Time series)
        mental_health_trend = self.data.groupby(self.data['submission_date'].dt.to_period('M')).agg({
            'q15': 'mean',  # Anxiety
            'q16': 'mean',  # Depression
            'q17': 'mean'   # Burnout
        }).reset_index()

        for col, label in [('q15', 'Anxiety'), ('q16', 'Depression'), ('q17', 'Burnout')]:
            fig.add_trace(
                go.Scatter(
                    x=mental_health_trend['submission_date'].astype(str),
                    y=mental_health_trend[col],
                    mode='lines+markers',
                    name=label
                ),
                row=2, col=1
            )

        # 5. Key Risk Indicators (Bar)
        risk_indicators = {}
        for category, questions in self.categories.items():
            risk_indicators[category] = self.data[questions].mean().mean()

        fig.add_trace(
            go.Bar(
                x=list(risk_indicators.keys()),
                y=list(risk_indicators.values()),
                marker_color=['#d32f2f' if v < 2.5 else '#ff9800' if v < 3.0 else '#4caf50' for v in risk_indicators.values()],
                name="Risk Indicators"
            ),
            row=2, col=2
        )

        # 6. Response Volume (Bar)
        monthly_responses = self.data.groupby(self.data['submission_date'].dt.to_period('M')).size()
        fig.add_trace(
            go.Bar(
                x=monthly_responses.index.astype(str),
                y=monthly_responses.values,
                marker_color='#1f77b4',
                name="Response Volume"
            ),
            row=2, col=3
        )

        fig.update_layout(
            height=800,
            title_text="HSEG Workplace Culture Assessment - Executive Dashboard",
            title_x=0.5,
            showlegend=True
        )

        return fig

    def create_detailed_risk_analysis(self):
        """Create detailed risk breakdown analysis"""
        fig = make_subplots(
            rows=3, cols=2,
            subplot_titles=(
                'Risk Distribution by Category', 'Organization Risk Heatmap',
                'Position Level Risk Analysis', 'Department Risk Comparison',
                'Tenure vs Risk Correlation', 'Gender Risk Disparities'
            ),
            specs=[[{"type": "bar"}, {"type": "heatmap"}],
                   [{"type": "box"}, {"type": "violin"}],
                   [{"type": "scatter"}, {"type": "bar"}]]
        )

        # 1. Risk by Category (Horizontal Bar)
        category_scores = {}
        for category, questions in self.categories.items():
            category_scores[category] = self.data[questions].mean().mean()

        categories = list(category_scores.keys())
        scores = list(category_scores.values())
        colors = ['#d32f2f' if s < 2.5 else '#ff9800' if s < 3.0 else '#4caf50' for s in scores]

        fig.add_trace(
            go.Bar(
                y=categories,
                x=scores,
                orientation='h',
                marker_color=colors,
                name="Category Risk"
            ),
            row=1, col=1
        )

        # 2. Organization Risk Heatmap
        org_domain_risk = self.data.groupby(['organization_name', 'domain'])['hseg_total_score'].mean().unstack(fill_value=0)

        fig.add_trace(
            go.Heatmap(
                z=org_domain_risk.values,
                x=org_domain_risk.columns,
                y=org_domain_risk.index,
                colorscale='RdYlGn',
                name="Org Risk Heatmap"
            ),
            row=1, col=2
        )

        # 3. Position Level Box Plot
        for position in self.data['position_level'].unique():
            if pd.notna(position):
                data_subset = self.data[self.data['position_level'] == position]['hseg_total_score']
                fig.add_trace(
                    go.Box(
                        y=data_subset,
                        name=position,
                        boxpoints='outliers'
                    ),
                    row=2, col=1
                )

        # 4. Department Violin Plot
        departments = self.data['department'].value_counts().head(6).index
        for dept in departments:
            data_subset = self.data[self.data['department'] == dept]['hseg_total_score']
            fig.add_trace(
                go.Violin(
                    y=data_subset,
                    name=dept,
                    box_visible=True
                ),
                row=2, col=2
            )

        # 5. Tenure vs Risk Scatter
        tenure_mapping = {'<1_year': 0.5, '1-3_years': 2, '3-7_years': 5, '7+_years': 10}
        self.data['tenure_numeric'] = self.data['tenure_range'].map(tenure_mapping)

        fig.add_trace(
            go.Scatter(
                x=self.data['tenure_numeric'],
                y=self.data['hseg_total_score'],
                mode='markers',
                marker=dict(
                    color=self.data['hseg_total_score'],
                    colorscale='RdYlGn',
                    size=8,
                    opacity=0.6
                ),
                name="Tenure vs Risk"
            ),
            row=3, col=1
        )

        # 6. Gender Risk Analysis
        gender_risk = self.data.groupby('gender_identity')['hseg_total_score'].mean()
        fig.add_trace(
            go.Bar(
                x=gender_risk.index,
                y=gender_risk.values,
                marker_color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728'][:len(gender_risk)],
                name="Gender Risk"
            ),
            row=3, col=2
        )

        fig.update_layout(
            height=1200,
            title_text="Detailed Risk Analysis - HSEG Assessment",
            title_x=0.5,
            showlegend=False
        )

        return fig

    def create_mental_health_dashboard(self):
        """Create focused mental health impact visualization"""
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                'Mental Health Score Distribution', 'Burnout Severity by Domain',
                'Anxiety/Depression Correlation', 'Mental Health Support Effectiveness'
            )
        )

        # 1. Mental Health Distribution
        mental_health_scores = self.data[['q15', 'q16', 'q17', 'q18']].mean(axis=1)
        fig.add_trace(
            go.Histogram(
                x=mental_health_scores,
                nbinsx=20,
                marker_color='rgba(255, 100, 100, 0.7)',
                name="MH Distribution"
            ),
            row=1, col=1
        )

        # 2. Burnout by Domain
        burnout_by_domain = self.data.groupby('domain')['q17'].mean().sort_values()
        fig.add_trace(
            go.Bar(
                x=burnout_by_domain.index,
                y=burnout_by_domain.values,
                marker_color=['#d32f2f', '#ff9800', '#4caf50'],
                name="Burnout by Domain"
            ),
            row=1, col=2
        )

        # 3. Anxiety/Depression Correlation
        fig.add_trace(
            go.Scatter(
                x=self.data['q15'],  # Anxiety
                y=self.data['q16'],  # Depression
                mode='markers',
                marker=dict(
                    color=self.data['q17'],  # Burnout
                    colorscale='Reds',
                    size=8,
                    showscale=True,
                    colorbar=dict(title="Burnout Level")
                ),
                name="Anxiety vs Depression"
            ),
            row=2, col=1
        )

        # 4. Mental Health Support
        support_effectiveness = self.data.groupby('q18').agg({
            'q15': 'mean',
            'q16': 'mean',
            'q17': 'mean'
        })

        for col, label in [('q15', 'Anxiety'), ('q16', 'Depression'), ('q17', 'Burnout')]:
            fig.add_trace(
                go.Scatter(
                    x=support_effectiveness.index,
                    y=support_effectiveness[col],
                    mode='lines+markers',
                    name=label
                ),
                row=2, col=2
            )

        fig.update_layout(
            height=800,
            title_text="Mental Health Impact Analysis - HSEG Assessment",
            title_x=0.5
        )

        return fig

    def create_demographic_insights(self):
        """Create demographic breakdown analysis"""
        fig = make_subplots(
            rows=2, cols=3,
            subplot_titles=(
                'Risk by Age Group', 'Risk by Gender', 'Risk by Education Level',
                'Supervision Impact', 'Organization Size Effect', 'Response Patterns by Demo'
            )
        )

        # 1. Age Group Analysis
        age_risk = self.data.groupby('age_range')['hseg_total_score'].mean().sort_values()
        fig.add_trace(
            go.Bar(
                x=age_risk.index,
                y=age_risk.values,
                marker_color='lightblue',
                name="Age Risk"
            ),
            row=1, col=1
        )

        # 2. Gender Analysis
        gender_risk = self.data.groupby('gender_identity')['hseg_total_score'].mean()
        fig.add_trace(
            go.Bar(
                x=gender_risk.index,
                y=gender_risk.values,
                marker_color='lightgreen',
                name="Gender Risk"
            ),
            row=1, col=2
        )

        # 3. Education Level
        education_order = ['High school or equivalent', 'Some college/Associate degree', 'Bachelor\'s degree', 'Graduate/Professional degree']
        education_data = self.data[self.data['hseg_total_score'].notna()]

        fig.add_trace(
            go.Box(
                y=education_data['hseg_total_score'],
                x=education_data['age_range'],
                name="Education Risk"
            ),
            row=1, col=3
        )

        # 4. Supervision Impact
        supervision_risk = self.data.groupby('supervises_others')['hseg_total_score'].mean()
        fig.add_trace(
            go.Bar(
                x=['Non-Supervisor', 'Supervisor'],
                y=[supervision_risk[False], supervision_risk[True]],
                marker_color=['orange', 'red'],
                name="Supervision Impact"
            ),
            row=2, col=1
        )

        # 5. Organization Size Effect
        size_bins = pd.cut(self.data['employee_count'], bins=5, labels=['Very Small', 'Small', 'Medium', 'Large', 'Very Large'])
        size_risk = self.data.groupby(size_bins)['hseg_total_score'].mean()

        fig.add_trace(
            go.Scatter(
                x=size_risk.index,
                y=size_risk.values,
                mode='lines+markers',
                marker_size=10,
                name="Size Effect"
            ),
            row=2, col=2
        )

        # 6. Response Patterns
        demo_counts = self.data.groupby(['domain', 'position_level']).size().unstack(fill_value=0)

        fig.add_trace(
            go.Heatmap(
                z=demo_counts.values,
                x=demo_counts.columns,
                y=demo_counts.index,
                colorscale='Blues',
                name="Response Patterns"
            ),
            row=2, col=3
        )

        fig.update_layout(
            height=800,
            title_text="Demographic Analysis - HSEG Assessment",
            title_x=0.5,
            showlegend=False
        )

        return fig

    def generate_statistical_summary(self):
        """Generate comprehensive statistical summary"""
        summary = {}

        # Overall statistics
        summary['total_responses'] = len(self.data)
        summary['date_range'] = f"{self.data['submission_date'].min().strftime('%Y-%m-%d')} to {self.data['submission_date'].max().strftime('%Y-%m-%d')}"
        summary['organizations'] = self.data['organization_name'].nunique()

        # Risk distribution
        summary['risk_distribution'] = self.data['risk_tier'].value_counts().to_dict()
        summary['average_hseg_score'] = self.data['hseg_total_score'].mean()
        summary['median_hseg_score'] = self.data['hseg_total_score'].median()

        # Category scores
        summary['category_scores'] = {}
        for category, questions in self.categories.items():
            summary['category_scores'][category] = {
                'mean': self.data[questions].mean().mean(),
                'std': self.data[questions].mean(axis=1).std(),
                'critical_responses': (self.data[questions].mean(axis=1) < 2.0).sum()
            }

        # High-risk indicators
        summary['critical_findings'] = {
            'severe_burnout': (self.data['q17'] == 1).sum(),
            'frequent_anxiety': (self.data['q15'] == 1).sum(),
            'safety_concerns': (self.data['q1'] <= 2).sum(),
            'discrimination_reports': (self.data['q7'] <= 2).sum()
        }

        # Domain analysis
        summary['domain_analysis'] = {}
        for domain in self.data['domain'].unique():
            domain_data = self.data[self.data['domain'] == domain]
            summary['domain_analysis'][domain] = {
                'responses': len(domain_data),
                'avg_score': domain_data['hseg_total_score'].mean(),
                'high_risk_percent': (domain_data['risk_tier'].isin(['Crisis', 'At Risk'])).mean() * 100
            }

        return summary

    def export_dashboard(self, output_dir="hseg_visualizations"):
        """Export all visualizations and summary"""
        import os
        os.makedirs(output_dir, exist_ok=True)

        # Generate all visualizations
        exec_dashboard = self.create_executive_summary()
        risk_analysis = self.create_detailed_risk_analysis()
        mental_health = self.create_mental_health_dashboard()
        demographic = self.create_demographic_insights()

        # Save as HTML files
        exec_dashboard.write_html(f"{output_dir}/executive_summary.html")
        risk_analysis.write_html(f"{output_dir}/detailed_risk_analysis.html")
        mental_health.write_html(f"{output_dir}/mental_health_analysis.html")
        demographic.write_html(f"{output_dir}/demographic_insights.html")

        # Generate and save statistical summary
        summary = self.generate_statistical_summary()

        with open(f"{output_dir}/statistical_summary.txt", 'w') as f:
            f.write("HSEG WORKPLACE CULTURE ASSESSMENT - STATISTICAL SUMMARY\n")
            f.write("=" * 60 + "\n\n")

            f.write(f"OVERVIEW:\n")
            f.write(f"Total Responses: {summary['total_responses']:,}\n")
            f.write(f"Date Range: {summary['date_range']}\n")
            f.write(f"Organizations: {summary['organizations']}\n")
            f.write(f"Average HSEG Score: {summary['average_hseg_score']:.2f}\n")
            f.write(f"Median HSEG Score: {summary['median_hseg_score']:.2f}\n\n")

            f.write("RISK DISTRIBUTION:\n")
            for tier, count in summary['risk_distribution'].items():
                percentage = (count / summary['total_responses']) * 100
                f.write(f"{tier}: {count:,} ({percentage:.1f}%)\n")
            f.write("\n")

            f.write("CATEGORY ANALYSIS:\n")
            for category, stats in summary['category_scores'].items():
                f.write(f"{category}:\n")
                f.write(f"  Mean Score: {stats['mean']:.2f}\n")
                f.write(f"  Std Dev: {stats['std']:.2f}\n")
                f.write(f"  Critical Responses: {stats['critical_responses']}\n\n")

            f.write("CRITICAL FINDINGS:\n")
            for finding, count in summary['critical_findings'].items():
                percentage = (count / summary['total_responses']) * 100
                f.write(f"{finding.replace('_', ' ').title()}: {count:,} ({percentage:.1f}%)\n")
            f.write("\n")

            f.write("DOMAIN ANALYSIS:\n")
            for domain, stats in summary['domain_analysis'].items():
                f.write(f"{domain}:\n")
                f.write(f"  Responses: {stats['responses']:,}\n")
                f.write(f"  Avg Score: {stats['avg_score']:.2f}\n")
                f.write(f"  High Risk %: {stats['high_risk_percent']:.1f}%\n\n")

        print(f"✅ Dashboard exported to {output_dir}/")
        print(f"📊 Executive Summary: {output_dir}/executive_summary.html")
        print(f"🔍 Risk Analysis: {output_dir}/detailed_risk_analysis.html")
        print(f"🧠 Mental Health: {output_dir}/mental_health_analysis.html")
        print(f"👥 Demographics: {output_dir}/demographic_insights.html")
        print(f"📈 Statistics: {output_dir}/statistical_summary.txt")


def main():
    """Main execution function"""
    print("🚀 HSEG Enterprise Dashboard Generator")
    print("=" * 50)

    # Initialize dashboard
    dashboard = HSEGDashboard("data/hseg_data.csv")

    # Display key statistics
    summary = dashboard.generate_statistical_summary()
    print(f"\n📊 Dataset Overview:")
    print(f"   • Total Responses: {summary['total_responses']:,}")
    print(f"   • Organizations: {summary['organizations']}")
    print(f"   • Date Range: {summary['date_range']}")
    print(f"   • Average Risk Score: {summary['average_hseg_score']:.2f}/100")

    # Generate and export all visualizations
    dashboard.export_dashboard()

    print("\n✨ Enterprise dashboard generation complete!")


if __name__ == "__main__":
    main()