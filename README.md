# Automated Resume Screening Pipeline for Fast Food HR

## Description
This project implements an automated pipeline to screen resumes in PDF format for fast food industry recruitment. It extracts relevant information from resumes, classifies candidates based on their experience and skills, and simulates the process of sending survey emails and interview invitations.

## Features
- Automatic monitoring of input folder for new resume PDFs
- PDF text extraction (including support for scanned documents)
- Natural Language Processing (NLP) to identify relevant keywords
- Structured data extraction (name, email, phone, experience, skills)
- Candidate classification based on resume content and survey responses
- Simulated email communication for surveys and interview invitations
- Visualization of screening results with charts and graphs
- Customizable scoring system for visa status and availability preferences
- Mock survey responses generation with specific distributions

## Prerequisites
- Python 3.9+
- Required Python libraries (see `requirements.txt`)
- SpaCy English model (`en_core_web_sm`)

## Installation

1. Clone the repository or download the source code:
```
git clone https://github.com/your-username/resume-screening-pipeline.git
cd resume-screening-pipeline
```

2. Create and activate a virtual environment (recommended):
```
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the required dependencies:
```
pip install -r requirements.txt
```

4. Download the SpaCy English model:
```
python -m spacy download en_core_web_sm
```

5. Configure email settings (optional):
```
cp .env.example .env
# Edit .env with your email credentials
```

## Project Structure
- `./input_cv/`: Place resume PDFs in this folder for processing
- `./input_cv/processed/`: Processed PDFs are moved here
- `./output/`: Contains output files (CSV data and visualizations)
- `cv_triage_pipeline.py`: Main script that runs the entire pipeline
- `keywords.txt`: List of keywords to look for in resumes
- `sample_responses.csv`: Sample survey responses for simulation with specific distributions
- `convert_to_pdf.py`: Script to generate sample Irish CVs
- `requirements.txt`: List of required Python packages

## Usage

1. Place resume PDFs in the `./input_cv/` folder.

2. Run the script:
```
python cv_triage_pipeline.py
```

3. Check the output:
   - `./output/extracted_resumes.csv`: Raw data extracted from resumes
   - `./output/output_candidates.csv`: Classified candidates with priority levels
   - `./output/screening_results.png`: Bar chart of candidates by priority
   - `./output/keyword_distribution.png`: Pie chart of top keywords found

## Pipeline Workflow

1. **Receiving Resumes**: The script monitors the `./input_cv/` folder for new PDF files.

2. **Converting PDFs to Structured Data**: Text is extracted from PDFs and structured into a CSV with relevant fields.

3. **Analysis and Initial Screening**: NLP techniques identify relevant keywords and classify resumes as "relevant" if they contain at least 2-3 mentions of keywords.

4. **Automated Survey Email**: The script simulates sending a survey email to candidates who pass the initial screening.

5. **Automated Classification**: Candidates are classified into High, Medium, and Low priority based on their resume content and survey responses.
   - **Availability Scoring**: Full availability (4 points), Morning shifts (3 points), Night shifts (1 point)
   - **Visa Status Scoring**: Irish citizens (4 points), Stamp 4 (3 points), EU citizens (3 points), Stamp 1G (2 points), Stamp 2 (1 point), Stamp 1 (0 points)
   - **Course/Training Scoring**: Food handling/HACCP (3 points), Food safety/Customer service (2 points), Other training (1 point)

6. **Automated Interview Invitation**: The script simulates sending interview invitations to classified candidates.

## Mock Survey Responses

The `sample_responses.csv` file contains mock survey responses for candidates with specific distributions:
- **Response Rate**: 80% of candidates (80 out of 100)
- **Availability Distribution**:
  - 50% Morning shifts
  - 30% Night shifts
  - 20% Full availability
- **Visa Status Distribution**:
  - 70% Stamp 2 (limited work rights, typically students)
  - 30% Stamp 4 (broader work permissions)

This distribution allows for testing the resume screening pipeline with realistic scenarios for fast food HR recruitment in Ireland.

## Limitations
- Text extraction may be less accurate for poorly formatted or heavily designed PDFs
- The name extraction algorithm is simplified and may not work for all resume formats
- Email functionality is simulated and requires configuration for actual sending
- The keyword matching is basic and doesn't account for semantic similarity

## Future Improvements
- Integration with email providers (Gmail, Outlook) for actual email sending
- Integration with Google Forms or Typeform for real survey responses
- More sophisticated NLP for better information extraction
- OCR improvements for better handling of scanned documents
- Web interface for managing the pipeline
- Integration with applicant tracking systems

## License
[MIT License](LICENSE)

## Author
Your Name
