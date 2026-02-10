from dotenv import load_dotenv
load_dotenv()

import requests
from datetime import datetime
import os
import logging

import mimetypes
from collections import defaultdict

from PIL import Image, ImageDraw, ImageFont

# Configuration
PLANNING_CENTER_APP_ID = os.getenv('PC_APP_ID')
PLANNING_CENTER_SECRET = os.getenv('PC_SECRET')
WHATSAPP_API_TOKEN = os.getenv('WHATSAPP_API_TOKEN')
WHATSAPP_PHONE_NUMBER_ID = os.getenv('WHATSAPP_PHONE_NUMBER_ID')
TARGET_PHONE_NUMBER = os.getenv('TARGET_PHONE_NUMBER')

# Paths
FONT_REGULAR_PATH = "fonts/Lora-Regular.ttf"
FONT_BOLD_PATH = "fonts/Lora-Bold.ttf"
TEMPLATE_DIR = "postcard"
TEXT_COLOR = "#9c8b6a"  # Refined gold/tan for names and date
SECTION_HEADER_COLOR = "#756a54"  # Darker brown for section headers (Cumpleaños, Aniversario)

# WhatsApp Message Template Names (must be approved in Meta Business Suite)
WA_TEMPLATE_CONGRATULATION = "congratulation_msg"  # Template with image header and count parameters
WA_TEMPLATE_NOTIFICATION = "notification_msg"       # Template for notifications (no celebrations or errors)

# Spanish Month Mapping
MONTHS_ES = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
    5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
    9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
}

def send_whatsapp_template(template_name, parameters=None, media_id=None):
    """Send a WhatsApp message using a template.
    
    Args:
        template_name: Name of the approved WhatsApp template
        parameters: List of text parameters for the template body
        media_id: Optional media ID for templates with image headers
    
    Returns:
        bool: True if successful, False otherwise
    """
    if not WHATSAPP_API_TOKEN or not WHATSAPP_PHONE_NUMBER_ID:
        print("❌ Error: WhatsApp credentials not configured.")
        return False

    url = f"https://graph.facebook.com/v21.0/{WHATSAPP_PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    clean_number = ''.join(filter(str.isdigit, TARGET_PHONE_NUMBER))
    
    # Build template components
    components = []
    
    # Add header component if media is provided
    if media_id:
        components.append({
            "type": "header",
            "parameters": [{
                "type": "image",
                "image": {"id": media_id}
            }]
        })
    
    # Add body component with parameters
    if parameters:
        components.append({
            "type": "body",
            "parameters": [{"type": "text", "text": str(p)} for p in parameters]
        })
    
    payload = {
        "messaging_product": "whatsapp",
        "to": clean_number,
        "type": "template",
        "template": {
            "name": template_name,
            "language": {"code": "en"},
            "components": components
        }
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30, verify=True)
        if response.status_code == 200:
            print(f"✅ WhatsApp template '{template_name}' sent successfully to {clean_number}")
            return True
        else:
            logging.error(f"Error sending WhatsApp template: {response.status_code}")
            return False
    except requests.RequestException as e:
        logging.error(f"Exception sending WhatsApp template: {e}")
        return False



def get_birthdays_today():
    """Fetch people from Planning Center with today's birthdays."""
    auth = (PLANNING_CENTER_APP_ID, PLANNING_CENTER_SECRET)
    base_url = "https://api.planningcenteronline.com/people/v2"

    today = datetime.now()
    month = today.month
    day = today.day

    birthdays = []

    # Fetch people with birthdays
    birthday_url = f"{base_url}/birthday_people"
    try:
        response = requests.get(birthday_url, auth=auth, timeout=30, verify=True)
    except requests.RequestException as e:
        logging.error(f"Network error fetching birthdays: {e}")
        return birthdays

    if response.status_code == 200:
        try:
            data = response.json()
        except ValueError:
            logging.error("Invalid JSON in birthday response")
            return birthdays
        people_list = data.get('data', {}).get('attributes', {}).get('people', [])
        if not isinstance(people_list, list):
            logging.error("Unexpected birthday response structure")
            return birthdays
        for person in people_list:
            birthdate_str = person.get('birthdate')
            if birthdate_str:
                bdate = None
                for fmt in ('%Y-%m-%d', '%m-%d'):
                    try:
                        bdate = datetime.strptime(birthdate_str, fmt)
                        break
                    except ValueError:
                        continue
                if bdate and bdate.month == month and bdate.day == day:
                    birthdays.append({'name': person.get('name')})
    else:
        logging.error(f"Error fetching birthdays: HTTP {response.status_code}")
    
    return birthdays


def get_person_household(person_id):
    """Fetch the household ID for a specific person."""
    auth = (PLANNING_CENTER_APP_ID, PLANNING_CENTER_SECRET)
    url = f"https://api.planningcenteronline.com/people/v2/people/{person_id}/households"
    
    try:
        response = requests.get(url, auth=auth, timeout=30, verify=True)
    except requests.RequestException as e:
        logging.error(f"Network error fetching household for person {person_id}: {e}")
        return None
    
    if response.status_code == 200:
        try:
            data = response.json()
        except ValueError:
            logging.error(f"Invalid JSON in household response for person {person_id}")
            return None
        households = data.get('data', [])
        if isinstance(households, list) and households:
            return households[0].get('id')
    return None


def get_anniversaries_today():
    """Fetch couples with anniversaries today, grouped by household."""
    auth = (PLANNING_CENTER_APP_ID, PLANNING_CENTER_SECRET)
    base_url = "https://api.planningcenteronline.com/people/v2"
    
    today = datetime.now()
    today_month = today.month
    today_day = today.day
    
    # Fetch people from anniversary list
    anniversary_url = f"{base_url}/lists/4700166/people"
    try:
        response = requests.get(anniversary_url, auth=auth, timeout=30, verify=True)
    except requests.RequestException as e:
        logging.error(f"Network error fetching anniversaries: {e}")
        return []
    
    if response.status_code != 200:
        logging.error(f"Error fetching anniversaries: HTTP {response.status_code}")
        return []
    
    try:
        people_data = response.json()
    except ValueError:
        logging.error("Invalid JSON in anniversary response")
        return []
    
    # Group people by household ID
    household_groups = defaultdict(list)
    people_without_households = []
    
    for person in people_data.get('data', []):
        attrs = person['attributes']
        anniversary = attrs.get('anniversary')
        person_id = person['id']
        
        # Skip if no anniversary or anniversary doesn't match today
        if not anniversary:
            continue
        
        try:
            anniv_date = datetime.strptime(anniversary, '%Y-%m-%d')
            if anniv_date.month != today_month or anniv_date.day != today_day:
                continue
        except ValueError:
            continue
        
        # Fetch household ID from API
        household_id = get_person_household(person_id)
        
        person_info = {
            'id': person_id,
            'name': attrs['name'],
            'first_name': attrs.get('first_name'),
            'last_name': attrs.get('last_name'),
            'anniversary': anniversary
        }
        
        if household_id:
            household_groups[household_id].append(person_info)
        else:
            people_without_households.append(person_info)
    
    # Extract couples and format their names
    anniversaries = []
    for household_id, members in household_groups.items():
        if len(members) == 2:
            if members[0]['anniversary'] == members[1]['anniversary']:
                # Format names - if same last name, show "First1 & First2 LastName"
                person1 = members[0]
                person2 = members[1]
                
                if person1.get('last_name') and person1['last_name'] == person2.get('last_name'):
                    couple_name = f"{person1['first_name']} & {person2['first_name']} {person1['last_name']}"
                else:
                    couple_name = f"{person1['name']} & {person2['name']}"
                
                anniversaries.append({'name': couple_name})
        elif len(members) == 1:
            anniversaries.append({'name': members[0]['name']})
    
    # Add singles
    for person in people_without_households:
        anniversaries.append({'name': person['name']})
    
    return anniversaries

def overlay_text_on_template(template_path, text, output_path):
    """Overlay text on a template image using Pillow with dynamic font sizing."""
    try:
        if not os.path.exists(template_path):
            print(f"❌ Template not found: {template_path}")
            return False

        img = Image.open(template_path)
        draw = ImageDraw.Draw(img)
        
        W, H = img.size
        
        # Define safe text area (avoiding template title and footer)
        # Top ~22% is template title, shifting up to center content better
        y_start = int(H * 0.25)   # Adjusted to 25% as requested
        y_end = int(H * 0.80)     # Adjusted to 80% as requested
        available_height = y_end - y_start
        
        # Split into lines but keep blank lines for section separation
        lines = text.split('\n')
        num_lines = len(lines)
        
        if num_lines == 0:
            return True  # Nothing to draw
        
        # Identify section headers (will be bold)
        section_headers = {"Cumpleaños", "Aniversario"}
        
        # Calculate optimal font sizes based on available space
        # Dynamic sizing based on number of lines
        # Increased max size to 80 as requested
        base_font_size = min(100, max(30, int(available_height / (num_lines * 1.3))))
        section_font_size = int(base_font_size * 1.2)  # Section headers slightly larger
        name_font_size = base_font_size
        date_font_size = int(base_font_size * 0.9)  # Date slightly smaller
        
        try:
            section_font = ImageFont.truetype(FONT_BOLD_PATH, section_font_size)
            name_font = ImageFont.truetype(FONT_REGULAR_PATH, name_font_size)
            date_font = ImageFont.truetype(FONT_REGULAR_PATH, date_font_size)
        except Exception as e:
            print(f"⚠️ Could not load Lora fonts, using default: {e}")
            section_font = ImageFont.load_default()
            name_font = ImageFont.load_default()
            date_font = ImageFont.load_default()

        # Calculate standard line heights for consistency
        # Using a reference string "Ag" to get a consistent height across all lines
        ref_bbox_section = draw.textbbox((0, 0), "Ag", font=section_font)
        section_h = ref_bbox_section[3] - ref_bbox_section[1]
        
        ref_bbox_name = draw.textbbox((0, 0), "Ag", font=name_font)
        name_h = ref_bbox_name[3] - ref_bbox_name[1]

        # Calculate total content height for vertical centering (excluding date)
        total_content_height = 0
        line_heights = []
        date_line_index = -1
        
        for i, line in enumerate(lines):
            # Check if this is the date line (last non-empty line)
            is_date = False
            if i == len(lines) - 1 and line.strip():
                is_date = True
                date_line_index = i
            
            # Determine which font and fixed height to use
            if is_date:
                current_font = date_font
                h = 0
                spacing_after = 0
                # Don't include date in total height - it will be positioned separately
                line_heights.append((0, 0, None))
                continue
            elif line in section_headers:
                current_font = section_font
                h = section_h
                spacing_after = 8  # Less spacing after section headers
            # Check if this is a blank line (section separator)
            elif line == "" or not line.strip():
                # Skip blank lines but add extra spacing
                line_heights.append((0, 35, None))  # Extra spacing between sections
                total_content_height += 35
                continue
            else:
                current_font = name_font
                h = name_h
                spacing_after = 15  # Normal spacing between names
            
            line_heights.append((h, spacing_after, current_font))
            total_content_height += h + spacing_after
        
        # Center content vertically within the safe area
        y_offset = y_start + (available_height - total_content_height) / 2
        y_offset = max(y_start, y_offset)  # Ensure we don't go above start
        
        # Render all lines except the date
        for i, line in enumerate(lines):
            # Skip the date line - we'll render it separately at the bottom
            if i == date_line_index:
                continue
                
            h, spacing_after, current_font = line_heights[i]
            
            # Skip blank lines (they only contribute spacing)
            if current_font is None:
                y_offset += spacing_after
                continue
            
            bbox = draw.textbbox((0, 0), line, font=current_font)
            w = bbox[2] - bbox[0]
            
            # Center horizontally
            x_pos = (W - w) / 2
            
            # Use darker color for section headers
            text_color = SECTION_HEADER_COLOR if line in section_headers else TEXT_COLOR
            
            draw.text((x_pos, y_offset), line, font=current_font, fill=text_color)
            
            y_offset += h + spacing_after
            
            # Safety check: stop if we're about to exceed the safe area
            if y_offset > y_end:
                print(f"⚠️ Warning: Truncating text, too many names to fit")
                break
        
        # Render date at fixed position above "Salmo 103" (around 82% of height)
        if date_line_index >= 0:
            date_line = lines[date_line_index]
            date_y = int(H * 0.82)  # Fixed position above scripture
            
            bbox = draw.textbbox((0, 0), date_line, font=date_font)
            w = bbox[2] - bbox[0]
            x_pos = (W - w) / 2
            
            draw.text((x_pos, date_y), date_line, font=date_font, fill=TEXT_COLOR)

        # Handle simplified saving based on extension
        if output_path.lower().endswith(('.jpg', '.jpeg')):
            img = img.convert('RGB')
            img.save(output_path, quality=85)
        else:
            img.save(output_path)
            
        return True
    except Exception as e:
        print(f"❌ Error in Pillow overlay: {e}")
        return False

def upload_media_to_whatsapp(image_path):
    """Upload media to WhatsApp to get a media ID."""
    url = f"https://graph.facebook.com/v21.0/{WHATSAPP_PHONE_NUMBER_ID}/media"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_API_TOKEN}"
    }
    
    try:
        mime_type, _ = mimetypes.guess_type(image_path)
        with open(image_path, 'rb') as f:
            files = {
                'file': (os.path.basename(image_path), f, mime_type),
                'messaging_product': (None, 'whatsapp'),
                'type': (None, mime_type)
            }
            response = requests.post(url, headers=headers, files=files, timeout=60, verify=True)
            
        if response.status_code == 200:
            media_id = response.json().get('id')
            return media_id
        else:
            logging.error(f"Error uploading media: {response.status_code}")
            return None
    except requests.RequestException as e:
        logging.error(f"Exception in media upload: {e}")
        return None

def generate_combined_postcard(birthdays, anniversaries, output_filename="combined_celebrations.jpg"):
    """Generate a single postcard combining birthdays and anniversaries.
    
    Args:
        birthdays: List of birthday people
        anniversaries: List of anniversary couples
        output_filename: Output file name for the postcard
    
    Returns:
        bool: True if successful, False otherwise
    """
    content = ""
    
    # Birthday section
    if birthdays:
        content += "Cumpleaños\n"
        for person in birthdays:
            content += f"{person['name']}\n"
    
    # Add spacing between sections if both exist
    if birthdays and anniversaries:
        content += "\n\n"  # Double blank line for clear section separation
    
    # Anniversary section
    if anniversaries:
        content += "Aniversario\n"
        for couple in anniversaries:
            content += f"{couple['name']}\n"
    
    # Add date at bottom
    today = datetime.now()
    month_es = MONTHS_ES[today.month]
    date_str = f"{month_es} {today.day}, {today.year}"
    content += f"\n{date_str}"
    
    # Use felicidades.png as the base template
    template_path = os.path.join(TEMPLATE_DIR, "felicidades.png")
    
    if overlay_text_on_template(template_path, content, output_filename):
        print(f"✓ Generated {output_filename}")
        return True
    else:
        print(f"❌ Failed to generate {output_filename}")
        return False

def main():
    print("=" * 60)
    print("CELEBRATION POSTCARD GENERATOR")
    print("=" * 60)

    print("\n[1] Fetching data from Planning Center...")
    
    try:
        birthdays = get_birthdays_today()
        anniversaries = get_anniversaries_today()
        
        birthday_count = len(birthdays)
        anniversary_count = len(anniversaries)
        
        print(f"✓ Found {birthday_count} birthday(s) and {anniversary_count} anniversary(ies)")
        
        # Check if we have any celebrations
        if birthday_count > 0 or anniversary_count > 0:
            print("\n[2] Generating combined postcard...")
            # Generate combined postcard
            output_file = "combined_celebrations.jpg"
            if generate_combined_postcard(birthdays, anniversaries, output_file):
                # Upload media to WhatsApp
                media_id = upload_media_to_whatsapp(output_file)
                
                if media_id:
                    # Send using congratulation_msg template (no body params, just image header)
                    print(f"\n[3] Sending via WhatsApp template '{WA_TEMPLATE_CONGRATULATION}'...")
                    send_whatsapp_template(
                        template_name=WA_TEMPLATE_CONGRATULATION,
                        media_id=media_id
                    )
                else:
                    print("❌ Failed to upload media, sending notification instead")
                    send_whatsapp_template(
                        template_name=WA_TEMPLATE_NOTIFICATION,
                        parameters=["Error uploading celebration postcard"]
                    )
            else:
                # Failed to generate postcard
                send_whatsapp_template(
                    template_name=WA_TEMPLATE_NOTIFICATION,
                    parameters=["Error generating celebration postcard"]
                )
        else:
            # No celebrations found
            print("\n[2] No celebrations found for today")
            send_whatsapp_template(
                template_name=WA_TEMPLATE_NOTIFICATION,
                parameters=["No celebrations found for today"]
            )
    
    except Exception as e:
        print(f"\n❌ Error during execution: {e}")
        # Send sanitized error notification (no internal details via WhatsApp)
        send_whatsapp_template(
            template_name=WA_TEMPLATE_NOTIFICATION,
            parameters=["An error occurred in the celebration script. Check logs for details."]
        )

    print("\n" + "=" * 60)
    print("PROCESS COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    required_vars = ['PC_APP_ID', 'PC_SECRET', 'WHATSAPP_API_TOKEN', 'WHATSAPP_PHONE_NUMBER_ID', 'TARGET_PHONE_NUMBER']
    missing = [v for v in required_vars if not os.getenv(v)]
    if missing:
        print(f"❌ Error: Missing required environment variables: {', '.join(missing)}")
        print("   Please ensure all variables are set in your .env file.")
        print("   See .env.example for the required format.")
    else:
        main()