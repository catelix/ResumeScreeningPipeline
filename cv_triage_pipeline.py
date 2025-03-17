#!/usr/bin/env python3
"""
Automated Resume Screening Pipeline for Fast Food HR
This script automates the process of screening resumes for fast food industry recruitment.
"""

import os
import time
import fitz  # PyMuPDF
import pandas as pd
import smtplib
import re
import logging
import matplotlib.pyplot as plt
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from datetime import datetime, timedelta
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("pipeline.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("ResumeScreening")

# Load environment variables for email configuration
load_dotenv()

# Constants
INPUT_DIR = "./input_cv/"
OUTPUT_DIR = "./output/"
PROCESSED_DIR = "./input_cv/processed/"
KEYWORDS_FILE = "keywords.txt"
OUTPUT_CSV = os.path.join(OUTPUT_DIR, "output_candidates.csv")
SURVEY_RESPONSES = "sample_responses.csv"
INTERVIEW_DATE = (datetime.now() + timedelta(days=14)).strftime("%d/%m/%Y")
INTERVIEW_TIME = "10:00 AM"

# Create necessary directories if they don't exist
os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)

# Try to initialize NLP tools, but continue without them if not available
try:
    import nltk
    import spacy
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    try:
        spacy_model = spacy.load("en_core_web_sm")
        nlp_available = True
        logger.info("NLP tools initialized successfully")
    except:
        logger.warning("spaCy model not available, continuing without NLP capabilities")
        spacy_model = None
        nlp_available = False
except ImportError:
    logger.warning("NLP libraries not available, continuing without NLP capabilities")
    nlp_available = False
    spacy_model = None


def load_keywords():
    """Load keywords from the keywords file."""
    try:
        with open(KEYWORDS_FILE, 'r') as f:
            keywords = [line.strip().lower() for line in f if line.strip()]
        logger.info(f"Loaded {len(keywords)} keywords")
        return keywords
    except FileNotFoundError:
        logger.error(f"Keywords file not found: {KEYWORDS_FILE}")
        # Fallback keywords
        default_keywords = [
            "attendant", "cook", "fast food", "mcdonald's", "burger king",
            "customer service", "food handling", "cashier", "restaurant"
        ]
        logger.info(f"Using {len(default_keywords)} default keywords")
        return default_keywords


def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file."""
    try:
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text()
        return text
    except Exception as e:
        logger.error(f"Error extracting text from {pdf_path}: {e}")
        return ""


def extract_contact_info(text):
    """Extract name, email, and phone from the resume text."""
    # Simple regex patterns for extraction
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    phone_pattern = r'\b(?:\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b'
    
    # Extract email and phone
    email = re.search(email_pattern, text)
    email = email.group(0) if email else ""
    
    phone = re.search(phone_pattern, text)
    phone = phone.group(0) if phone else ""
    
    # Extract name (simplified approach - first 2-3 words at the beginning)
    lines = text.strip().split('\n')
    name = ""
    for line in lines[:5]:  # Check first few lines
        if line.strip() and not re.search(email_pattern, line) and not re.search(phone_pattern, line):
            # Take first 2-3 words as name
            name_parts = line.strip().split()[:3]
            name = ' '.join(name_parts)
            break
    
    return name, email, phone


def extract_experience_and_skills(text, keywords):
    """Extract experience and skills from the resume text."""
    # Simple approach: look for sections like "Experience", "Skills", etc.
    sections = re.split(r'\n\s*(?:EXPERIENCE|SKILLS|EDUCATION|WORK HISTORY|EMPLOYMENT|PROFESSIONAL EXPERIENCE)(?:\s*|:)', 
                       text, flags=re.IGNORECASE)
    
    # Get experience (simplified)
    experience = ""
    if len(sections) > 1:
        experience = sections[1].strip()[:500]  # Limit to 500 chars
    
    # Skills section
    skills_section = ""
    for i, section in enumerate(sections):
        if i > 0 and re.search(r'SKILLS|QUALIFICATIONS', sections[i-1], re.IGNORECASE):
            skills_section = section.strip()[:500]  # Limit to 500 chars
            break
    
    # If no clear skills section, use the last section
    if not skills_section and len(sections) > 2:
        skills_section = sections[-1].strip()[:500]
    
    return experience, skills_section


def count_relevant_keywords(text, keywords):
    """Count the number of relevant keywords in the text."""
    text_lower = text.lower()
    count = 0
    found_keywords = []
    
    for keyword in keywords:
        if keyword.lower() in text_lower:
            count += 1
            found_keywords.append(keyword)
    
    return count, found_keywords


def process_resume(pdf_path, keywords):
    """Process a single resume PDF."""
    logger.info(f"Processing resume: {pdf_path}")
    
    # Extract text from PDF
    text = extract_text_from_pdf(pdf_path)
    if not text:
        logger.warning(f"No text extracted from {pdf_path}")
        return None
    
    # Extract contact information
    name, email, phone = extract_contact_info(text)
    
    # Extract experience and skills
    experience, skills = extract_experience_and_skills(text, keywords)
    
    # Count relevant keywords
    keyword_count, found_keywords = count_relevant_keywords(text, keywords)
    
    # Check if resume is relevant (at least 2 keywords)
    is_relevant = keyword_count >= 2
    
    # Create a dictionary with the extracted information
    resume_data = {
        "name": name,
        "email": email,
        "phone": phone,
        "experience": experience,
        "skills": skills,
        "keyword_count": keyword_count,
        "found_keywords": ", ".join(found_keywords),
        "is_relevant": is_relevant,
        "file_name": os.path.basename(pdf_path)
    }
    
    logger.info(f"Extracted data from {pdf_path}: {name}, {email}, Keywords: {keyword_count}")
    return resume_data


def send_survey_email(candidate):
    """Simulate sending a survey email to a candidate."""
    if not candidate["email"]:
        logger.warning(f"No email found for {candidate['name']}")
        return False
    
    # Email configuration
    sender_email = os.getenv("EMAIL_SENDER", "hr@fastfood.example.com")
    password = os.getenv("EMAIL_PASSWORD", "")
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    
    # Create message
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = candidate["email"]
    message["Subject"] = "Fast Food Job Application - Next Steps"
    
    # Email body
    body = f"""Hello {candidate['name']},

Thank you for your interest in joining our fast food team. Your resume has been reviewed and we would like to invite you to complete a short survey to help us better understand your availability and qualifications.

Please complete the survey at the following link:
https://forms.example.com/fast-food-survey

We look forward to learning more about you.

Best regards,
Fast Food HR Team
"""
    
    message.attach(MIMEText(body, "plain"))
    
    # Simulate sending email (don't actually send in this demo)
    try:
        # In a real scenario, you would uncomment the following:
        # with smtplib.SMTP(smtp_server, smtp_port) as server:
        #     server.starttls()
        #     server.login(sender_email, password)
        #     server.send_message(message)
        logger.info(f"[SIMULATION] Survey email sent to {candidate['email']}")
        return True
    except Exception as e:
        logger.error(f"Error sending survey email to {candidate['email']}: {e}")
        return False


def send_interview_email(candidate, priority):
    """Simulate sending an interview invitation email to a candidate."""
    if not candidate["email"]:
        logger.warning(f"No email found for {candidate['name']}")
        return False
    
    # Email configuration
    sender_email = os.getenv("EMAIL_SENDER", "hr@fastfood.example.com")
    password = os.getenv("EMAIL_PASSWORD", "")
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    
    # Create message
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = candidate["email"]
    message["Subject"] = "Fast Food Job Application - Interview Invitation"
    
    # Email body
    body = f"""Hello {candidate['name']},

Thank you for completing our survey. We are pleased to invite you to an interview for the position.

Interview Details:
Date: {INTERVIEW_DATE}
Time: {INTERVIEW_TIME}
Location: Fast Food Restaurant, 123 Main Street

Please confirm your attendance by replying to this email.

Best regards,
Fast Food HR Team

Priority: {priority}
"""
    
    message.attach(MIMEText(body, "plain"))
    
    # Simulate sending email (don't actually send in this demo)
    try:
        # In a real scenario, you would uncomment the following:
        # with smtplib.SMTP(smtp_server, smtp_port) as server:
        #     server.starttls()
        #     server.login(sender_email, password)
        #     server.send_message(message)
        logger.info(f"[SIMULATION] Interview email sent to {candidate['email']} (Priority: {priority})")
        return True
    except Exception as e:
        logger.error(f"Error sending interview email to {candidate['email']}: {e}")
        return False


def classify_candidates(resumes_df, survey_df):
    """Classify candidates based on resume and survey data."""
    # Merge resume and survey data
    if survey_df is not None and not survey_df.empty:
        merged_df = pd.merge(resumes_df, survey_df, on="email", how="left", suffixes=("", "_survey"))
    else:
        # If no survey data, just use resume data
        merged_df = resumes_df.copy()
        merged_df["availability"] = "Unknown"
        merged_df["courses"] = "Unknown"
        merged_df["visa"] = "Unknown"
    
    # Calculate priority score
    def calculate_priority(row):
        score = 0
        
        # Resume factors
        if row["is_relevant"]:
            score += 2
        score += min(row["keyword_count"], 5)  # Max 5 points for keywords
        
        # Survey factors (if available)
        # Availability scoring
        if "availability" in row and pd.notna(row["availability"]):
            availability = str(row["availability"]).lower()
            if availability == "full availability":
                score += 4  # Highest value for full availability
            elif availability == "morning":
                score += 3  # High demand for morning shifts
            elif availability == "night":
                score += 1  # Lower demand for night shifts
            else:
                score += 1  # Default score for other availabilities
        
        # Course/training scoring
        if "courses" in row and pd.notna(row["courses"]):
            courses = str(row["courses"]).lower()
            if "food handling" in courses or "haccp" in courses:
                score += 3  # Highest value for food safety certifications
            elif "food safety" in courses:
                score += 2  # Medium value for food safety knowledge
            elif "customer service" in courses:
                score += 2  # Medium value for customer service training
            elif courses != "none" and courses != "unknown":
                score += 1  # Some value for any other training
        
        # Visa status scoring
        if "visa" in row and pd.notna(row["visa"]):
            visa_status = str(row["visa"]).lower()
            if visa_status == "stamp 4":
                score += 3  # Stamp 4 (broader work permissions)
            elif visa_status == "stamp 2":
                score += 1  # Stamp 2 (limited work rights, typically students)
            elif visa_status == "irish":
                score += 4  # Irish citizens (no visa issues)
            elif visa_status == "ue":
                score += 3  # EU citizens (freedom of movement)
            elif visa_status == "stamp 1g":
                score += 2  # Stamp 1G (graduate visa)
            elif visa_status == "stamp 1":
                score += 0  # Stamp 1 (may have work restrictions)
        
        return score
    
    # Apply scoring
    merged_df["priority_score"] = merged_df.apply(calculate_priority, axis=1)
    
    # Classify based on score - adjusted thresholds for new scoring system
    def get_priority_level(score):
        if score >= 10:
            return "High"
        elif score >= 6:
            return "Medium"
        else:
            return "Low"
    
    merged_df["priority"] = merged_df["priority_score"].apply(get_priority_level)
    
    return merged_df


def visualize_results(classified_df):
    """Create a visualization of the screening results."""
    try:
        # Count candidates by priority
        priority_counts = classified_df["priority"].value_counts()
        
        # Create a bar chart
        plt.figure(figsize=(10, 6))
        bars = plt.bar(priority_counts.index, priority_counts.values, color=["green", "orange", "red"])
        
        # Add labels and title
        plt.xlabel("Priority Level")
        plt.ylabel("Number of Candidates")
        plt.title("Resume Screening Results by Priority")
        
        # Add count labels on top of bars
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                    f"{height:.0f}",
                    ha="center", va="bottom")
        
        # Save the chart
        chart_path = os.path.join(OUTPUT_DIR, "screening_results.png")
        plt.savefig(chart_path)
        logger.info(f"Results visualization saved to {chart_path}")
        
        # Create a pie chart of keyword distribution
        plt.figure(figsize=(10, 6))
        keyword_data = {}
        
        # Extract all keywords found
        for keywords_str in classified_df["found_keywords"]:
            if pd.notna(keywords_str) and keywords_str:
                for keyword in keywords_str.split(", "):
                    if keyword in keyword_data:
                        keyword_data[keyword] += 1
                    else:
                        keyword_data[keyword] = 1
        
        # Sort and take top 10 keywords
        top_keywords = dict(sorted(keyword_data.items(), key=lambda x: x[1], reverse=True)[:10])
        
        # Create pie chart
        plt.pie(top_keywords.values(), labels=top_keywords.keys(), autopct='%1.1f%%')
        plt.title("Top 10 Keywords Found in Resumes")
        
        # Save the chart
        keyword_chart_path = os.path.join(OUTPUT_DIR, "keyword_distribution.png")
        plt.savefig(keyword_chart_path)
        logger.info(f"Keyword distribution chart saved to {keyword_chart_path}")
        
    except Exception as e:
        logger.error(f"Error creating visualization: {e}")


def monitor_input_folder(keywords):
    """Monitor the input folder for new PDFs and process them."""
    logger.info(f"Monitoring {INPUT_DIR} for new PDFs...")
    
    # Get list of PDF files
    pdf_files = [f for f in os.listdir(INPUT_DIR) if f.lower().endswith('.pdf')]
    
    if not pdf_files:
        logger.warning(f"No PDF files found in {INPUT_DIR}")
        return []
    
    logger.info(f"Found {len(pdf_files)} PDF files to process")
    
    # Process each PDF
    resume_data = []
    for pdf_file in pdf_files:
        pdf_path = os.path.join(INPUT_DIR, pdf_file)
        data = process_resume(pdf_path, keywords)
        if data:
            resume_data.append(data)
            
            # Move processed file to processed directory
            processed_path = os.path.join(PROCESSED_DIR, pdf_file)
            try:
                os.rename(pdf_path, processed_path)
                logger.info(f"Moved {pdf_file} to {PROCESSED_DIR}")
            except Exception as e:
                logger.error(f"Error moving {pdf_file}: {e}")
    
    return resume_data


def load_survey_responses():
    """Load survey responses from CSV file."""
    try:
        if os.path.exists(SURVEY_RESPONSES):
            survey_df = pd.read_csv(SURVEY_RESPONSES)
            logger.info(f"Loaded {len(survey_df)} survey responses")
            return survey_df
        else:
            logger.warning(f"Survey responses file not found: {SURVEY_RESPONSES}")
            return None
    except Exception as e:
        logger.error(f"Error loading survey responses: {e}")
        return None


def main():
    """Main function to run the pipeline."""
    logger.info("Starting Resume Screening Pipeline")
    
    # Load keywords
    keywords = load_keywords()
    
    # Monitor input folder and process resumes
    resume_data = monitor_input_folder(keywords)
    
    if not resume_data:
        logger.warning("No resume data to process")
        return
    
    # Create DataFrame from resume data
    resumes_df = pd.DataFrame(resume_data)
    
    # Save extracted data to CSV
    extracted_csv = os.path.join(OUTPUT_DIR, "extracted_resumes.csv")
    resumes_df.to_csv(extracted_csv, index=False)
    logger.info(f"Saved extracted resume data to {extracted_csv}")
    
    # Simulate sending survey emails to relevant candidates
    relevant_candidates = resumes_df[resumes_df["is_relevant"] == True]
    logger.info(f"Found {len(relevant_candidates)} relevant candidates")
    
    for _, candidate in relevant_candidates.iterrows():
        send_survey_email(candidate)
    
    # Load survey responses
    survey_df = load_survey_responses()
    
    # Classify candidates
    classified_df = classify_candidates(resumes_df, survey_df)
    
    # Save classified data to CSV
    classified_df.to_csv(OUTPUT_CSV, index=False)
    logger.info(f"Saved classified candidates to {OUTPUT_CSV}")
    
    # Simulate sending interview invitations
    for _, candidate in classified_df.iterrows():
        if candidate["is_relevant"] and pd.notna(candidate["priority"]):
            send_interview_email(candidate, candidate["priority"])
    
    # Visualize results
    visualize_results(classified_df)
    
    logger.info("Resume Screening Pipeline completed successfully")


if __name__ == "__main__":
    main()
