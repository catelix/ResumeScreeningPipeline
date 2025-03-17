#!/usr/bin/env python3
"""
Generate 100 sample Irish CVs in PDF format for testing the resume screening pipeline.
"""

import os
import random
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib import colors

# Irish data for CV generation
IRISH_FIRST_NAMES = [
    "Liam", "Conor", "Sean", "Finn", "Oisin", "Cillian", "Jack", "James", "Daniel", "Noah",
    "Aoife", "Saoirse", "Siobhan", "Niamh", "Ciara", "Aisling", "Caoimhe", "Eimear", "Orla", "Roisin",
    "Patrick", "Michael", "Ryan", "Eoin", "Darragh", "Fionn", "Tadhg", "Cathal", "Seamus", "Declan",
    "Emma", "Sarah", "Ava", "Sophie", "Emily", "Grace", "Lucy", "Ella", "Amelia", "Chloe"
]

IRISH_LAST_NAMES = [
    "Murphy", "Kelly", "O'Sullivan", "Walsh", "Smith", "O'Brien", "Byrne", "Ryan", "O'Connor", "O'Neill",
    "O'Reilly", "Doyle", "McCarthy", "Gallagher", "Doherty", "Kennedy", "Lynch", "Murray", "Quinn", "Moore",
    "McLoughlin", "O'Doherty", "Brennan", "Connolly", "O'Connell", "Fitzgerald", "Flanagan", "Burke", "Collins", "Clarke",
    "Johnston", "Hughes", "O'Farrell", "Duffy", "O'Shea", "Nolan", "Boyle", "Healy", "Moran", "McGrath"
]

IRISH_CITIES = [
    "Dublin", "Cork", "Galway", "Limerick", "Waterford", "Drogheda", "Dundalk", "Swords", "Bray", "Navan",
    "Kilkenny", "Ennis", "Carlow", "Tralee", "Newbridge", "Portlaoise", "Mullingar", "Wexford", "Letterkenny", "Athlone",
    "Celbridge", "Clonmel", "Greystones", "Malahide", "Leixlip", "Arklow", "Cobh", "Maynooth", "Ballina", "Mallow"
]

IRISH_COUNTIES = [
    "Dublin", "Cork", "Galway", "Limerick", "Waterford", "Meath", "Louth", "Kildare", "Wicklow", "Westmeath",
    "Kilkenny", "Clare", "Carlow", "Kerry", "Laois", "Wexford", "Donegal", "Offaly", "Cavan", "Monaghan",
    "Tipperary", "Mayo", "Sligo", "Roscommon", "Longford", "Leitrim"
]

IRISH_STREET_NAMES = [
    "Main Street", "Church Street", "High Street", "Castle Street", "Bridge Street", "Mill Road", "River Road", "Abbey Road",
    "Market Street", "O'Connell Street", "Grafton Street", "Henry Street", "Parnell Street", "Baggot Street", "Dawson Street",
    "Patrick Street", "Eyre Square", "Shop Street", "Quay Street", "William Street", "Thomas Street", "James Street",
    "College Road", "University Road", "Park Avenue", "Strand Road", "Harbour View", "Seafront Drive", "Mountain View",
    "Meadow Lane", "Oak Drive", "Willow Close", "Cedar Court", "Maple Avenue", "Ash Grove"
]

IRISH_PHONE_PREFIXES = ["083", "085", "086", "087", "089"]  # Mobile prefixes

EMAIL_DOMAINS = ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "eircom.net", "icloud.com"]

EDUCATION_INSTITUTIONS = [
    "Trinity College Dublin", "University College Dublin", "Dublin City University", "University College Cork",
    "National University of Ireland, Galway", "University of Limerick", "Maynooth University",
    "Technological University Dublin", "Cork Institute of Technology", "Waterford Institute of Technology",
    "Galway-Mayo Institute of Technology", "Limerick Institute of Technology", "Institute of Technology Sligo",
    "Dundalk Institute of Technology", "Institute of Technology Carlow", "Letterkenny Institute of Technology",
    "National College of Ireland", "Dublin Business School", "Griffith College Dublin", "Dublin Institute of Technology"
]

DEGREES = [
    "Bachelor of Arts", "Bachelor of Science", "Bachelor of Commerce", "Bachelor of Business Studies",
    "Bachelor of Engineering", "Higher Diploma", "Master of Arts", "Master of Science",
    "Master of Business Administration", "PhD", "Leaving Certificate", "Advanced Certificate",
    "Higher Certificate", "Ordinary Bachelor Degree", "Honours Bachelor Degree"
]

FAST_FOOD_COMPANIES = [
    "McDonald's", "Burger King", "Supermac's", "KFC", "Subway", "Domino's Pizza", "Apache Pizza",
    "Eddie Rocket's", "Four Star Pizza", "Abrakebabra", "O'Brien's Sandwich Bar", "Boojum",
    "Bunsen", "Five Guys", "Nando's", "Costa Coffee", "Starbucks", "Insomnia Coffee", "Cafe Sol",
    "Jump Juice Bar", "Chopped", "Freshii", "Camile Thai", "Wagamama", "Milano", "Papa John's"
]

FAST_FOOD_POSITIONS = [
    "Crew Member", "Team Member", "Cashier", "Server", "Barista", "Cook", "Line Cook", "Food Preparation Worker",
    "Kitchen Assistant", "Shift Supervisor", "Shift Manager", "Assistant Manager", "Restaurant Manager",
    "Customer Service Representative", "Drive-Thru Operator", "Host/Hostess", "Delivery Driver",
    "Catering Assistant", "Front of House Staff", "Back of House Staff"
]

FAST_FOOD_SKILLS = [
    "customer service", "food preparation", "food safety", "cash handling", "order taking",
    "kitchen experience", "cleaning", "teamwork", "communication", "time management",
    "fast-paced environment", "inventory management", "HACCP", "food hygiene", "POS systems",
    "conflict resolution", "upselling", "multitasking", "problem-solving", "training",
    "scheduling", "stock rotation", "menu knowledge", "allergen awareness", "health and safety",
    "first aid", "cooking", "baking", "food presentation", "quality control"
]

EDUCATION_SUBJECTS = [
    "Business", "Marketing", "Hospitality Management", "Culinary Arts", "Food Science",
    "Nutrition", "Hotel Management", "Tourism", "Communications", "English",
    "Mathematics", "Computer Science", "Information Technology", "Accounting", "Finance",
    "Human Resources", "Psychology", "Sociology", "Languages", "Arts"
]

def generate_irish_address():
    """Generate a random Irish address."""
    house_number = random.randint(1, 200)
    street = random.choice(IRISH_STREET_NAMES)
    city = random.choice(IRISH_CITIES)
    county = random.choice(IRISH_COUNTIES)
    
    # Generate random Eircode (Irish postal code)
    # Format: A65 F4E2 (routing key + unique identifier)
    routing_keys = ["A41", "A42", "A45", "A63", "A67", "A75", "A81", "A82", "A83", "A84", "A85", "A86", 
                    "A91", "A92", "A94", "A96", "A98", "C15", "D01", "D02", "D03", "D04", "D05", "D06", 
                    "D07", "D08", "D09", "D10", "D11", "D12", "D13", "D14", "D15", "D16", "D17", "D18", 
                    "D20", "D22", "D24", "E21", "E25", "E32", "E34", "E41", "E45", "E53", "E91", "F12", 
                    "F23", "F26", "F28", "F31", "F35", "F42", "F45", "F52", "F56", "F91", "F92", "F93", 
                    "F94", "H12", "H14", "H18", "H23", "H53", "H54", "H62", "H65", "H71", "H91", "K32", 
                    "K34", "K36", "K45", "K56", "K67", "K78", "N37", "N39", "N41", "N91", "P12", "P14", 
                    "P17", "P24", "P25", "P31", "P32", "P36", "P42", "P43", "P47", "P51", "P56", "P61", 
                    "P67", "P72", "P75", "P81", "P85", "R14", "R21", "R32", "R35", "R42", "R45", "R51", 
                    "R56", "R93", "R95", "T12", "T23", "T34", "T45", "T56", "V14", "V15", "V23", "V31", 
                    "V35", "V42", "V92", "V93", "V94", "V95", "W12", "W23", "W34", "W91", "X35", "X42", 
                    "X91", "Y14", "Y21", "Y25", "Y34", "Y35"]
    
    routing_key = random.choice(routing_keys)
    unique_id = ''.join(random.choices('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=4))
    eircode = f"{routing_key} {unique_id}"
    
    return f"{house_number} {street}, {city}, Co. {county}, {eircode}"

def generate_irish_phone():
    """Generate a random Irish mobile phone number."""
    prefix = random.choice(IRISH_PHONE_PREFIXES)
    suffix = ''.join(random.choices('0123456789', k=7))
    return f"+353 {prefix} {suffix[:3]} {suffix[3:]}"

def generate_email(first_name, last_name):
    """Generate an email address based on name."""
    domain = random.choice(EMAIL_DOMAINS)
    formats = [
        f"{first_name.lower()}.{last_name.lower()}@{domain}",
        f"{first_name.lower()}{last_name.lower()}@{domain}",
        f"{first_name.lower()}{last_name[0].lower()}@{domain}",
        f"{first_name[0].lower()}{last_name.lower()}@{domain}",
        f"{last_name.lower()}.{first_name.lower()}@{domain}"
    ]
    return random.choice(formats)

def generate_date_of_birth():
    """Generate a random date of birth for someone between 18 and 65 years old."""
    today = datetime.now()
    max_age = today - timedelta(days=18*365)
    min_age = today - timedelta(days=65*365)
    days_range = (max_age - min_age).days
    random_days = random.randint(0, days_range)
    return (min_age + timedelta(days=random_days)).strftime("%d/%m/%Y")

def generate_education():
    """Generate random education details."""
    institution = random.choice(EDUCATION_INSTITUTIONS)
    degree = random.choice(DEGREES)
    subject = random.choice(EDUCATION_SUBJECTS)
    
    # Generate graduation year (between 1-10 years ago)
    current_year = datetime.now().year
    years_ago = random.randint(1, 10)
    graduation_year = current_year - years_ago
    
    # For some cases, add "Currently studying" instead of graduation year
    if random.random() < 0.15:  # 15% chance
        return f"{degree} in {subject}, {institution} (Currently studying)"
    
    return f"{degree} in {subject}, {institution} ({graduation_year})"

def generate_work_experience():
    """Generate random work experience in fast food."""
    experiences = []
    
    # Determine number of previous jobs (1-3)
    num_jobs = random.randint(1, 3)
    
    current_year = datetime.now().year
    end_year = current_year
    
    for _ in range(num_jobs):
        company = random.choice(FAST_FOOD_COMPANIES)
        position = random.choice(FAST_FOOD_POSITIONS)
        
        # Duration of job (6 months to 3 years)
        duration_months = random.randint(6, 36)
        start_year = end_year - (duration_months // 12)
        start_month = random.randint(1, 12)
        
        if end_year == current_year and random.random() < 0.7:  # 70% chance of current job
            date_range = f"{start_month}/{start_year} - Present"
        else:
            end_month = random.randint(1, 12)
            date_range = f"{start_month}/{start_year} - {end_month}/{end_year}"
        
        # Generate 2-4 responsibilities
        num_responsibilities = random.randint(2, 4)
        responsibilities = []
        
        possible_responsibilities = [
            f"Served {random.randint(50, 200)}+ customers daily with a focus on quality service",
            f"Prepared food items according to company standards and procedures",
            f"Maintained a clean and organized work environment",
            f"Handled cash and card transactions accurately",
            f"Trained {random.randint(2, 10)} new team members on company procedures",
            f"Resolved customer complaints and ensured customer satisfaction",
            f"Managed inventory and stock rotation",
            f"Assisted in opening and closing procedures",
            f"Operated POS systems and processed orders efficiently",
            f"Ensured compliance with food safety and hygiene standards",
            f"Participated in team meetings and contributed improvement ideas",
            f"Supported management with administrative tasks",
            f"Coordinated with kitchen staff to ensure timely order delivery",
            f"Maintained knowledge of menu items and daily specials",
            f"Achieved employee of the month {random.randint(1, 3)} times"
        ]
        
        responsibilities = random.sample(possible_responsibilities, num_responsibilities)
        
        experience = f"{position} at {company}, {date_range}\n" + "\n".join([f"• {resp}" for resp in responsibilities])
        experiences.append(experience)
        
        # Set end year for next job
        end_year = start_year - 1
    
    return "\n\n".join(experiences)

def generate_skills():
    """Generate a list of relevant skills."""
    # Select 5-10 random skills
    num_skills = random.randint(5, 10)
    selected_skills = random.sample(FAST_FOOD_SKILLS, num_skills)
    
    # Add some general skills
    general_skills = [
        "Microsoft Office", "Google Workspace", "Social Media", "Customer Relationship Management",
        "Fluent English", "Basic Irish", "Team Leadership", "Event Planning", "Sales", "Marketing"
    ]
    
    # Add 2-4 general skills
    num_general = random.randint(2, 4)
    selected_skills.extend(random.sample(general_skills, num_general))
    
    # Format as bullet points
    return "\n".join([f"• {skill}" for skill in selected_skills])

def generate_references():
    """Generate references section."""
    if random.random() < 0.7:  # 70% chance
        return "References available upon request"
    else:
        return ""

def generate_cv_content(index):
    """Generate content for a CV."""
    first_name = random.choice(IRISH_FIRST_NAMES)
    last_name = random.choice(IRISH_LAST_NAMES)
    
    address = generate_irish_address()
    phone = generate_irish_phone()
    email = generate_email(first_name, last_name)
    dob = generate_date_of_birth()
    
    # Ensure some CVs have more keywords than others for testing
    experience_quality = random.random()
    
    cv_content = f"{first_name} {last_name}\n\n"
    cv_content += f"Address: {address}\n"
    cv_content += f"Phone: {phone}\n"
    cv_content += f"Email: {email}\n"
    cv_content += f"Date of Birth: {dob}\n\n"
    
    cv_content += "PERSONAL STATEMENT\n"
    
    # Different quality personal statements based on experience_quality
    if experience_quality > 0.8:  # High quality (20%)
        cv_content += f"Dedicated and customer-focused {random.choice(FAST_FOOD_POSITIONS).lower()} with {random.randint(2, 8)} years of experience in fast food and customer service environments. Skilled in food preparation, cash handling, and maintaining high standards of food hygiene. Proven track record of working efficiently in fast-paced kitchen environments while delivering excellent customer service.\n\n"
    elif experience_quality > 0.5:  # Medium quality (30%)
        cv_content += f"Motivated individual seeking a position in the fast food industry. Experience in customer service and basic food preparation. Eager to develop skills in a professional kitchen environment.\n\n"
    else:  # Lower quality (50%)
        cv_content += f"Looking for a job that allows me to use my people skills. Hard worker who learns quickly and enjoys being part of a team. Available to work flexible hours including evenings and weekends.\n\n"
    
    cv_content += "WORK EXPERIENCE\n"
    cv_content += generate_work_experience() + "\n\n"
    
    cv_content += "EDUCATION\n"
    # Add 1-2 education entries
    num_education = random.randint(1, 2)
    for _ in range(num_education):
        cv_content += generate_education() + "\n"
    cv_content += "\n"
    
    cv_content += "SKILLS\n"
    cv_content += generate_skills() + "\n\n"
    
    references = generate_references()
    if references:
        cv_content += "REFERENCES\n"
        cv_content += references + "\n"
    
    return cv_content

def create_pdf_from_content(content, output_file):
    """Create a PDF file from the given content."""
    doc = SimpleDocTemplate(
        output_file,
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )
    
    # Define styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        name='ResumeTitle',
        parent=styles['Heading1'],
        fontSize=14,
        alignment=TA_CENTER,
        spaceAfter=12
    )
    normal_style = ParagraphStyle(
        name='ResumeNormal',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=6
    )
    section_style = ParagraphStyle(
        name='ResumeSection',
        parent=styles['Heading2'],
        fontSize=12,
        spaceAfter=6
    )
    
    # Process the content
    lines = content.split('\n')
    flowables = []
    
    # Assume first line is the name (title)
    if lines:
        flowables.append(Paragraph(lines[0], title_style))
        flowables.append(Spacer(1, 12))
    
    # Process the rest of the content
    current_section = None
    for line in lines[1:]:
        line = line.strip()
        
        # Skip empty lines
        if not line:
            flowables.append(Spacer(1, 6))
            continue
        
        # Check if this is a section header (all caps)
        if line.isupper() and len(line) > 3:
            current_section = line
            flowables.append(Paragraph(line, section_style))
        else:
            # Regular content
            flowables.append(Paragraph(line, normal_style))
    
    # Build the PDF
    doc.build(flowables)

def main():
    """Generate 100 sample Irish CVs."""
    # Create output directory if it doesn't exist
    input_cv_dir = "./input_cv"
    processed_dir = os.path.join(input_cv_dir, "processed")
    
    if not os.path.exists(input_cv_dir):
        os.makedirs(input_cv_dir)
    
    if not os.path.exists(processed_dir):
        os.makedirs(processed_dir)
    
    # Generate 100 CVs
    print(f"Generating 100 sample Irish CVs in {input_cv_dir}...")
    
    for i in range(1, 101):
        cv_content = generate_cv_content(i)
        pdf_file = os.path.join(input_cv_dir, f"Irish_CV_{i:03d}.pdf")
        
        create_pdf_from_content(cv_content, pdf_file)
        print(f"Generated CV {i}/100: {pdf_file}")
    
    print("CV generation complete!")

if __name__ == "__main__":
    main()
