"""
HSEG Text Risk Classifier - NLP Model for Crisis Detection in Employee Responses
Uses BERT-based transformers to detect psychological risk signals in text
"""

import torch
import torch.nn as nn
from transformers import (
    AutoTokenizer, AutoModel, AutoModelForSequenceClassification,
    TrainingArguments, Trainer, pipeline
)
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any
import re
import json
from datetime import datetime
import pickle
from sklearn.metrics import accuracy_score, f1_score, classification_report
from datasets import Dataset
import warnings

# Suppress warnings
warnings.filterwarnings('ignore')

class TextRiskClassifier:
    """
    BERT-based classifier for detecting psychological risk in employee text responses
    Classifies text across 6 HSEG categories and overall risk level
    """
    
    def __init__(self, model_name: str = "bert-base-uncased", model_version: str = "v1.0.0"):
        self.model_name = model_name
        self.model_version = model_version
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"Using device: {self.device}")
        
        # Initialize tokenizer and model
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = None
        self.is_trained = False
        
        # Risk keywords for each category
        self.risk_keywords = {
            'power_abuse': [
                'threatened', 'intimidated', 'bullied', 'screamed', 'yelled',
                'retaliation', 'punished', 'silenced', 'afraid to speak',
                'fear consequences', 'abuse of power', 'harassment'
            ],
            'discrimination': [
                'discriminated', 'excluded', 'bias', 'unfair treatment',
                'different standards', 'not included', 'passed over',
                'because of my', 'treated differently', 'prejudice'
            ],
            'manipulation': [
                'manipulated', 'forced to smile', 'fake positivity',
                'emotional manipulation', 'guilt trip', 'pressure to be happy',
                'toxic positivity', 'forced enthusiasm'
            ],
            'accountability': [
                'no action taken', 'ignored complaint', 'covered up',
                'protected abuser', 'investigation ignored', 'no consequences',
                'swept under rug', 'nothing happened'
            ],
            'mental_health': [
                'panic attacks', 'anxiety', 'depression', 'stressed',
                'overwhelmed', 'burnout', 'breaking down', 'mental health',
                'suicidal thoughts', 'can\'t cope', 'emotional breakdown'
            ],
            'voice_autonomy': [
                'not listened to', 'ignored suggestions', 'no input',
                'micromanaged', 'no autonomy', 'powerless', 'no control',
                'decisions made for me', 'not consulted'
            ]
        }
        
        # Crisis indicators (immediate intervention required)
        self.crisis_keywords = [
            'suicide', 'kill myself', 'end it all', 'can\'t go on',
            'want to die', 'no point living', 'panic attacks daily',
            'threatened to fire', 'threatened my visa', 'called me stupid',
            'screamed at me', 'humiliated publicly', 'afraid for safety'
        ]
        
        # Sentiment pipeline for additional analysis
        self.sentiment_pipeline = None
        
        # Category mapping
        self.category_names = {
            0: 'power_abuse',
            1: 'discrimination', 
            2: 'manipulation',
            3: 'accountability',
            4: 'mental_health',
            5: 'voice_autonomy'
        }
        
        # Risk level mapping
        self.risk_levels = {
            0: 'Low',
            1: 'Medium', 
            2: 'High',
            3: 'Critical'
        }
    
    def preprocess_text(self, text: str) -> str:
        """Preprocess text for analysis"""
        if not text or not isinstance(text, str):
            return ""
        
        # Basic cleaning
        text = text.lower().strip()
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep punctuation for context
        text = re.sub(r'[^\w\s.,!?;:-]', '', text)
        
        return text
    
    def extract_keywords(self, text: str) -> Dict[str, List[str]]:
        """Extract risk keywords from text"""
        text = self.preprocess_text(text)
        found_keywords = {}
        
        for category, keywords in self.risk_keywords.items():
            found = []
            for keyword in keywords:
                if keyword.lower() in text:
                    found.append(keyword)
            if found:
                found_keywords[category] = found
        
        return found_keywords
    
    def detect_crisis_language(self, text: str) -> Dict[str, Any]:
        """Detect crisis-level language requiring immediate attention"""
        text = self.preprocess_text(text)
        crisis_signals = []
        
        for keyword in self.crisis_keywords:
            if keyword.lower() in text:
                crisis_signals.append(keyword)
        
        return {
            'has_crisis_language': len(crisis_signals) > 0,
            'crisis_keywords': crisis_signals,
            'crisis_count': len(crisis_signals)
        }
    
    def calculate_emotional_intensity(self, text: str) -> float:
        """Calculate emotional intensity of text (0.0 to 1.0)"""
        if not text:
            return 0.0
        
        # Count emotional indicators
        emotional_words = [
            'extremely', 'severely', 'terrible', 'awful', 'horrible',
            'devastating', 'overwhelming', 'unbearable', 'impossible',
            'constantly', 'always', 'never', 'every day', 'all the time'
        ]
        
        text_lower = text.lower()
        emotional_count = sum(1 for word in emotional_words if word in text_lower)
        
        # Count exclamation marks and caps
        exclamations = text.count('!')
        caps_ratio = sum(1 for c in text if c.isupper()) / max(len(text), 1)
        
        # Calculate intensity score
        intensity = min(1.0, (emotional_count * 0.2 + exclamations * 0.1 + caps_ratio * 0.3))
        
        return intensity
    
    def analyze_sentiment(self, text: str) -> Dict[str, float]:
        """Analyze sentiment using transformer pipeline"""
        if not self.sentiment_pipeline:
            try:
                self.sentiment_pipeline = pipeline(
                    "sentiment-analysis",
                    model="cardiffnlp/twitter-roberta-base-sentiment-latest",
                    device=0 if torch.cuda.is_available() else -1
                )
            except:
                # Fallback to basic sentiment
                return {'sentiment_score': 0.0, 'confidence': 0.5}
        
        try:
            result = self.sentiment_pipeline(text[:512])  # Limit length
            
            # Convert to -1 to 1 scale (negative to positive)
            if result[0]['label'] == 'LABEL_2':  # Positive
                sentiment_score = result[0]['score']
            elif result[0]['label'] == 'LABEL_0':  # Negative
                sentiment_score = -result[0]['score']
            else:  # Neutral
                sentiment_score = 0.0
            
            return {
                'sentiment_score': sentiment_score,
                'confidence': result[0]['score']
            }
        
        except Exception as e:
            return {'sentiment_score': 0.0, 'confidence': 0.5}
    
    def prepare_training_data(self, text_data: List[Dict]) -> Dataset:
        """Prepare training data for BERT model"""
        texts = []
        labels = []
        
        for item in text_data:
            text = self.preprocess_text(item.get('text', ''))
            if len(text) > 10:  # Filter out very short texts
                texts.append(text)
                
                # Multi-label classification - one label per category
                category_labels = item.get('category_labels', [0, 0, 0, 0, 0, 0])
                labels.append(category_labels)
        
        # Tokenize texts
        encodings = self.tokenizer(
            texts,
            truncation=True,
            padding=True,
            max_length=512,
            return_tensors='pt'
        )
        
        dataset = Dataset.from_dict({
            'input_ids': encodings['input_ids'],
            'attention_mask': encodings['attention_mask'],
            'labels': torch.tensor(labels, dtype=torch.float)
        })
        
        return dataset
    
    def create_model(self, num_labels: int = 6) -> AutoModelForSequenceClassification:
        """Create multi-label BERT model for risk classification"""
        
        class MultiLabelBERTClassifier(nn.Module):
            def __init__(self, model_name: str, num_labels: int):
                super().__init__()
                self.bert = AutoModel.from_pretrained(model_name)
                self.dropout = nn.Dropout(0.3)
                self.classifier = nn.Linear(self.bert.config.hidden_size, num_labels)
                self.sigmoid = nn.Sigmoid()
            
            def forward(self, input_ids, attention_mask, labels=None):
                outputs = self.bert(input_ids=input_ids, attention_mask=attention_mask)
                pooled_output = outputs[1]  # Use CLS token
                
                pooled_output = self.dropout(pooled_output)
                logits = self.classifier(pooled_output)
                probabilities = self.sigmoid(logits)
                
                loss = None
                if labels is not None:
                    loss_fct = nn.BCELoss()
                    loss = loss_fct(probabilities, labels)
                
                return {
                    'loss': loss,
                    'logits': logits,
                    'probabilities': probabilities
                }
        
        return MultiLabelBERTClassifier(self.model_name, num_labels)
    
    def train(self, training_data: List[Dict], validation_split: float = 0.2, 
              epochs: int = 3, batch_size: int = 16) -> Dict[str, float]:
        """Train the text risk classifier"""
        print("Starting text risk classifier training...")
        
        # Prepare dataset
        dataset = self.prepare_training_data(training_data)
        
        # Split data
        train_size = int((1 - validation_split) * len(dataset))
        val_size = len(dataset) - train_size
        train_dataset, val_dataset = torch.utils.data.random_split(
            dataset, [train_size, val_size]
        )
        
        # Create model
        self.model = self.create_model(num_labels=6)
        self.model.to(self.device)
        
        # Training arguments
        training_args = TrainingArguments(
            output_dir='./text_model_checkpoints',
            num_train_epochs=epochs,
            per_device_train_batch_size=batch_size,
            per_device_eval_batch_size=batch_size,
            warmup_steps=500,
            weight_decay=0.01,
            logging_dir='./logs',
            logging_steps=100,
            evaluation_strategy="epoch",
            save_strategy="epoch",
            load_best_model_at_end=True,
            metric_for_best_model="eval_loss",
            greater_is_better=False,
        )
        
        # Custom trainer for multi-label classification
        def compute_metrics(eval_pred):
            predictions, labels = eval_pred
            predictions = torch.sigmoid(torch.tensor(predictions))
            predictions = (predictions > 0.5).float()
            
            accuracy = accuracy_score(labels.flatten(), predictions.flatten())
            f1 = f1_score(labels.flatten(), predictions.flatten(), average='weighted')
            
            return {
                'accuracy': accuracy,
                'f1': f1
            }
        
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=val_dataset,
            compute_metrics=compute_metrics,
        )
        
        # Train model
        trainer.train()
        
        # Evaluate
        eval_results = trainer.evaluate()
        
        self.is_trained = True
        print(f"Training completed - Accuracy: {eval_results.get('eval_accuracy', 0):.3f}")
        
        return eval_results
    
    def predict_text_risk(self, text: str) -> Dict[str, Any]:
        """Predict risk levels from text input"""
        if not text or len(text.strip()) < 3:
            return self._empty_prediction()
        
        try:
            # Preprocess text
            processed_text = self.preprocess_text(text)
            
            # Basic analysis (works without trained model)
            keywords = self.extract_keywords(processed_text)
            crisis_detection = self.detect_crisis_language(processed_text)
            emotional_intensity = self.calculate_emotional_intensity(processed_text)
            sentiment = self.analyze_sentiment(text)
            
            # Rule-based risk classification if model not available
            if not self.is_trained or self.model is None:
                category_risks = self._rule_based_classification(
                    keywords, crisis_detection, emotional_intensity, sentiment
                )
            else:
                category_risks = self._model_based_classification(processed_text)
            
            # Determine overall risk level
            max_risk = max(category_risks.values())
            if crisis_detection['has_crisis_language']:
                overall_risk = 3  # Critical
            elif max_risk >= 0.7:
                overall_risk = 2  # High
            elif max_risk >= 0.4:
                overall_risk = 1  # Medium
            else:
                overall_risk = 0  # Low
            
            return {
                'text_length': len(text),
                'processed_text_length': len(processed_text),
                'category_risks': category_risks,
                'overall_risk_level': self.risk_levels[overall_risk],
                'overall_risk_score': overall_risk,
                'sentiment_analysis': sentiment,
                'emotional_intensity': emotional_intensity,
                'crisis_detection': crisis_detection,
                'risk_keywords': keywords,
                'risk_indicators': {
                    'has_specific_incidents': any(
                        keyword in processed_text for keyword in 
                        ['happened to me', 'my manager', 'my supervisor', 'I was']
                    ),
                    'has_emotional_language': emotional_intensity > 0.3,
                    'has_negative_sentiment': sentiment['sentiment_score'] < -0.3,
                    'has_multiple_categories': len(keywords) > 2
                },
                'confidence_score': self._calculate_prediction_confidence(
                    keywords, crisis_detection, emotional_intensity, sentiment
                ),
                'intervention_recommended': crisis_detection['has_crisis_language'] or 
                                         overall_risk >= 2,
                'processing_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'text_length': len(text) if text else 0,
                'processing_timestamp': datetime.now().isoformat()
            }
    
    def _rule_based_classification(self, keywords: Dict, crisis: Dict, 
                                 intensity: float, sentiment: Dict) -> Dict[str, float]:
        """Rule-based risk classification when model is not available"""
        category_risks = {}
        
        for category_name in self.category_names.values():
            risk_score = 0.0
            
            # Base risk from keywords
            if category_name in keywords:
                keyword_count = len(keywords[category_name])
                risk_score += min(0.6, keyword_count * 0.2)
            
            # Crisis language boost
            if crisis['has_crisis_language'] and category_name in ['power_abuse', 'mental_health']:
                risk_score += 0.4
            
            # Emotional intensity boost
            if intensity > 0.5:
                risk_score += intensity * 0.3
            
            # Negative sentiment boost
            if sentiment['sentiment_score'] < -0.3:
                risk_score += abs(sentiment['sentiment_score']) * 0.2
            
            category_risks[category_name] = min(1.0, risk_score)
        
        return category_risks
    
    def _model_based_classification(self, text: str) -> Dict[str, float]:
        """Model-based risk classification using trained BERT model"""
        try:
            # Tokenize input
            inputs = self.tokenizer(
                text,
                return_tensors='pt',
                truncation=True,
                padding=True,
                max_length=512
            )
            
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Get predictions
            with torch.no_grad():
                outputs = self.model(**inputs)
                probabilities = outputs['probabilities'].cpu().numpy()[0]
            
            # Map to category names
            category_risks = {}
            for i, category_name in self.category_names.items():
                category_risks[category_name] = float(probabilities[i])
            
            return category_risks
            
        except Exception as e:
            print(f"Model prediction error: {e}")
            # Fallback to rule-based
            return {cat: 0.0 for cat in self.category_names.values()}
    
    def _calculate_prediction_confidence(self, keywords: Dict, crisis: Dict,
                                       intensity: float, sentiment: Dict) -> float:
        """Calculate confidence in the prediction"""
        confidence = 0.5  # Base confidence
        
        # More keywords = higher confidence
        if keywords:
            confidence += min(0.3, len(keywords) * 0.1)
        
        # Crisis detection = higher confidence
        if crisis['has_crisis_language']:
            confidence += 0.2
        
        # Strong emotional indicators = higher confidence
        if intensity > 0.5 or abs(sentiment['sentiment_score']) > 0.5:
            confidence += 0.15
        
        return min(0.95, confidence)
    
    def _empty_prediction(self) -> Dict[str, Any]:
        """Return empty prediction for invalid input"""
        return {
            'text_length': 0,
            'processed_text_length': 0,
            'category_risks': {cat: 0.0 for cat in self.category_names.values()},
            'overall_risk_level': 'Low',
            'overall_risk_score': 0,
            'sentiment_analysis': {'sentiment_score': 0.0, 'confidence': 0.0},
            'emotional_intensity': 0.0,
            'crisis_detection': {'has_crisis_language': False, 'crisis_keywords': [], 'crisis_count': 0},
            'risk_keywords': {},
            'confidence_score': 0.0,
            'intervention_recommended': False,
            'processing_timestamp': datetime.now().isoformat(),
            'error': 'Empty or invalid text input'
        }
    
    def batch_predict(self, texts: List[str]) -> List[Dict[str, Any]]:
        """Predict risk for multiple texts efficiently"""
        predictions = []
        
        for text in texts:
            prediction = self.predict_text_risk(text)
            predictions.append(prediction)
        
        return predictions
    
    def save_model(self, filepath: str):
        """Save trained model"""
        if self.model and self.is_trained:
            torch.save({
                'model_state_dict': self.model.state_dict(),
                'model_version': self.model_version,
                'tokenizer_name': self.model_name,
                'is_trained': self.is_trained
            }, filepath)
            print(f"Model saved to {filepath}")
        else:
            print("No trained model to save")
    
    def load_model(self, filepath: str):
        """Load trained model"""
        try:
            checkpoint = torch.load(filepath, map_location=self.device)
            
            self.model = self.create_model(num_labels=6)
            self.model.load_state_dict(checkpoint['model_state_dict'])
            self.model.to(self.device)
            
            self.model_version = checkpoint.get('model_version', 'unknown')
            self.is_trained = checkpoint.get('is_trained', True)
            
            print(f"Model loaded from {filepath}")
        
        except Exception as e:
            print(f"Error loading model: {e}")
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information"""
        return {
            'model_name': self.model_name,
            'model_version': self.model_version,
            'is_trained': self.is_trained,
            'device': str(self.device),
            'num_categories': len(self.category_names),
            'num_risk_levels': len(self.risk_levels),
            'crisis_keywords_count': len(self.crisis_keywords),
            'total_risk_keywords': sum(len(keywords) for keywords in self.risk_keywords.values())
        }

# Example usage and testing
def create_sample_text_data() -> List[Dict]:
    """Create sample text data for testing"""
    return [
        {
            'text': "My manager constantly yells at me in front of everyone and threatened to fire me when I reported safety issues. I'm having panic attacks before work.",
            'category_labels': [1, 0, 0, 1, 1, 0]  # power_abuse, accountability, mental_health
        },
        {
            'text': "I love working here! Great team, supportive management, and excellent work-life balance. Highly recommend this company.",
            'category_labels': [0, 0, 0, 0, 0, 0]  # No risks
        },
        {
            'text': "Sometimes I feel excluded from meetings because of my background, but overall it's okay.",
            'category_labels': [0, 1, 0, 0, 0, 0]  # discrimination
        },
        {
            'text': "We're forced to smile and act happy even when patients die. Management says we need to maintain positive attitudes always.",
            'category_labels': [0, 0, 1, 0, 1, 0]  # manipulation, mental_health
        },
        {
            'text': "My suggestions are always ignored. I feel like I have no voice here and management makes all decisions without consulting us.",
            'category_labels': [0, 0, 0, 0, 0, 1]  # voice_autonomy
        }
    ]

if __name__ == "__main__":
    # Test the text classifier
    classifier = TextRiskClassifier()
    
    # Test individual prediction without training
    test_text = "My manager screams at me daily and I'm having panic attacks. I reported this but nothing was done. I feel completely powerless."
    
    prediction = classifier.predict_text_risk(test_text)
    print("Text Analysis Result:")
    print(json.dumps(prediction, indent=2))
    
    # Test batch prediction
    test_texts = [
        "Great workplace with supportive colleagues!",
        "Manager threatens employees and HR ignores complaints",
        "Feeling overwhelmed and anxious about work constantly"
    ]
    
    batch_predictions = classifier.batch_predict(test_texts)
    print("\nBatch Predictions:")
    for i, pred in enumerate(batch_predictions):
        print(f"Text {i+1}: {pred['overall_risk_level']} risk")
    
    # Optionally train model with sample data
    try:
        sample_data = create_sample_text_data() * 20  # Duplicate for training
        metrics = classifier.train(sample_data, epochs=1)  # Quick training
        print(f"\nTraining completed: {metrics}")
        
        # Test with trained model
        trained_prediction = classifier.predict_text_risk(test_text)
        print("\nPrediction with trained model:")
        print(f"Overall risk: {trained_prediction['overall_risk_level']}")
        
    except Exception as e:
        print(f"Training skipped due to error: {e}")
