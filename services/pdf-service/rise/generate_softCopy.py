from docx import Document
import fitz  # PyMuPDF
from typing import Dict
import os
import tempfile
import requests
import json
from PIL import Image
import qrcode
# FastAPI imports removed since they're not needed anymore

def generate_certification_qr_code(cert_data: dict, size: int = 300) -> Image.Image:
    """
    Generate a QR code containing certification information that opens a URL when scanned.
    
    Args:
        cert_data: Dictionary containing certification information
        size: Size of the QR code image in pixels
    
    Returns:
        PIL Image object of the generated QR code
    """
    # Create a URL with certification data as query parameters
    # Using a temporary URL that works immediately (you can change this later)
    base_url = "https://salesqr.github.io/certificate-verification/"
    
    # Build query parameters
    params = []
    if cert_data.get("certificate_number"):
        params.append(f"cert={cert_data['certificate_number']}")
    if cert_data.get("company_name"):
        params.append(f"company={cert_data['company_name']}")
    if cert_data.get("certificate_standard"):
        params.append(f"standard={cert_data['certificate_standard']}")
    if cert_data.get("issue_date"):
        params.append(f"issue={cert_data['issue_date']}")
    if cert_data.get("expiry_date"):
        params.append(f"expiry={cert_data['expiry_date']}")
    
    # Create the final URL
    if params:
        qr_url = f"{base_url}?{'&'.join(params)}"
    else:
        qr_url = base_url
    
    
    # Create QR code instance with minimal border for better space utilization
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,  # Medium error correction
        box_size=12,  # Increased box size for better visibility
        border=1  # Minimal border (1 box) to eliminate white space
    )
    
    # Add the URL to the QR code
    qr.add_data(qr_url)
    qr.make(fit=True)
    
    # Create image from the QR code
    qr_image = qr.make_image(fill_color="black", back_color="white")
    
    # Resize to desired size
    qr_image = qr_image.resize((size, size), Image.Resampling.NEAREST)
    
    return qr_image

def add_qr_code_to_pdf(pdf_document, qr_image: Image.Image, x: float, y: float, width: float, height: float):
    """
    Add QR code image to PDF at specified coordinates.
    
    Args:
        pdf_document: PyMuPDF document object
        qr_image: PIL Image object of the QR code
        x, y: Top-left coordinates
        width, height: Dimensions for the QR code
    """
    # Convert PIL image to bytes
    img_bytes = qr_image.tobytes()
    
    # Get image dimensions
    img_width, img_height = qr_image.size
    
    # Calculate scaling to fill the entire specified dimensions (no white borders)
    scale_x = width / img_width
    scale_y = height / img_height
    scale = max(scale_x, scale_y)  # Use max to fill entire area
    
    # Calculate final dimensions
    final_width = img_width * scale
    final_height = img_height * scale
    
    # Position QR code to fill the entire allocated area (no centering)
    qr_x = x
    qr_y = y
    
    # Create a temporary file for the QR code image
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
        qr_image.save(tmp_file.name, 'PNG')
        tmp_file_path = tmp_file.name
    
    try:
        # Add image to PDF
        for page_num in range(len(pdf_document)):
            page = pdf_document[page_num]
            page.insert_image(
                rect=[qr_x, qr_y, qr_x + width, qr_y + height],  # Use exact allocated dimensions
                filename=tmp_file_path
            )
    finally:
        # Clean up temporary file
        if os.path.exists(tmp_file_path):
            os.unlink(tmp_file_path)

def find_font_path(font_basename: str) -> str | None:
    """Return full path to a font file in ../fonts (case-insensitive), or None."""
    fonts_dir = os.path.join(os.path.dirname(__file__), "..", "fonts")
    if not os.path.isdir(fonts_dir):
        return None
    for fn in os.listdir(fonts_dir):
        if fn.lower() == font_basename.lower():
            return os.path.join(fonts_dir, fn)
    return None

def resolve_font(preferred_font: str, fallback_font: str = "Times-Roman") -> Dict[str, str | None]:
    """
    Resolve font to either a built-in name or a file path.
    Returns: {"fontname": "Times-Roman", "fontfile": None} or {"fontname": None, "fontfile": "/path/to/font.ttf"}
    """
    builtin = {
        "Times-Roman", "Times-Bold", "Times-Italic", "Times-BoldItalic",
        "Helvetica", "Helvetica-Bold", "Helvetica-Oblique",
        "Courier", "Courier-Bold", "Courier-Oblique", "Courier-BoldOblique",
        "Symbol", "ZapfDingbats"
    }

    if preferred_font in builtin:
        return {"fontname": preferred_font, "fontfile": None}

    fonts_dir = os.path.join(os.path.dirname(__file__), "..", "fonts")
    if os.path.exists(fonts_dir):
        for file in os.listdir(fonts_dir):
            if preferred_font.lower() in file.lower():
                return {"fontname": None, "fontfile": os.path.join(fonts_dir, file)}

    # fallback
    return {"fontname": fallback_font if fallback_font in builtin else "Times-Roman", "fontfile": None}

def _font_obj(resolved_font: Dict[str, str | None]):
    """Create font object from resolved font dict."""
    if resolved_font["fontfile"]:
        return fitz.Font(file=resolved_font["fontfile"])
    return fitz.Font(fontname=resolved_font["fontname"])

# ISO Standards Mapping - Convert short names to full versions with years
ISO_STANDARDS_MAPPING = {
    # Quality & Management
    "ISO 9001": "ISO 9001:2015",
    "9001": "ISO 9001:2015",
    "ISO 14001": "ISO 14001:2015",
    "14001": "ISO 14001:2015",
    "ISO 45001": "ISO 45001:2018",
    "45001": "ISO 45001:2018",
    "ISO 50001": "ISO 50001:2018",
    "50001": "ISO 50001:2018",
    "ISO 31000": "ISO 31000:2018",
    "31000": "ISO 31000:2018",

    # Food Safety
    "ISO 22000": "ISO 22000:2018",
    "22000": "ISO 22000:2018",
    "ISO/TS 22002-1": "ISO/TS 22002-1:2009",
    "22002-1": "ISO/TS 22002-1:2009",
    "ISO 22005": "ISO 22005:2007",
    "22005": "ISO 22005:2007",

    # Laboratory & Testing
    "ISO/IEC 17025": "ISO/IEC 17025:2017",
    "17025": "ISO/IEC 17025:2017",
    "ISO 15189": "ISO 15189:2022",
    "15189": "ISO 15189:2022",

    # Information Security & IT
    "ISO/IEC 27001": "ISO/IEC 27001:2022",
    "27001": "ISO/IEC 27001:2022",
    "ISO/IEC 27002": "ISO/IEC 27002:2022",
    "27002": "ISO/IEC 27002:2022",
    "ISO/IEC 20000-1": "ISO/IEC 20000-1:2018",
    "20000-1": "ISO/IEC 20000-1:2018",
    "ISO/IEC 22301": "ISO/IEC 22301:2019",
    "22301": "ISO/IEC 22301:2019",

    # Manufacturing & Industrial
    "ISO 13485": "ISO 13485:2016",
    "13485": "ISO 13485:2016",
    "IATF 16949": "IATF 16949:2016",
    "16949": "IATF 16949:2016",
    "ISO 3834-2": "ISO 3834-2:2021",
    "3834-2": "ISO 3834-2:2021",

    # Environment & Sustainability
    "ISO 14064-1": "ISO 14064-1:2018",
    "14064-1": "ISO 14064-1:2018",
    "ISO 14046": "ISO 14046:2014",
    "14046": "ISO 14046:2014",
    "ISO 20121": "ISO 20121:2012",
    "20121": "ISO 20121:2012",

    # Asset, Facility, and Supply Chain
    "ISO 55001": "ISO 55001:2014",
    "55001": "ISO 55001:2014",
    "ISO 28000": "ISO 28000:2022",
    "28000": "ISO 28000:2022",

    # Aerospace
    "AS 9100D": "AS 9100D:2016",
    "9100D": "AS 9100D:2016",

    # Other Notable Standards
    "ISO 37001": "ISO 37001:2016",
    "37001": "ISO 37001:2016",
    "ISO 19600": "ISO 19600:2014",
    "19600": "ISO 19600:2014",
    "ISO 29993": "ISO 29993:2017",
    "29993": "ISO 29993:2017",
}

# ISO Standards Code Mapping - For certification codes
ISO_STANDARDS_CODES = {
    "ISO 9001:2015": "CM-MS-7842",
    "ISO 14001:2015": "CM-MS-7836", 
    "ISO 45001:2018": "CM-MS-7832",
    "ISO 22000:2018": "CM-MS-7822",
    "ISO/IEC 27001:2022": "CM-MS-7820",
    "ISO 37001:2016": "CM-MS-7804",
    "ISO/IEC 22301:2019": "CM-MS-7807",
    "ISO 50001:2018": "CM-MS-7814",
    "ISO 20001:2018": "CM-MS-7811",
}

# ISO Standards Descriptions Mapping - For separate use
ISO_STANDARDS_DESCRIPTIONS = {
    "ISO 9001:2015": "Quality Management System",
    "ISO 14001:2015": "Environmental Management System",
    "ISO 45001:2018": "Occupational Health & Safety",
    "ISO 50001:2018": "Energy Management System",
    "ISO 31000:2018": "Risk Management Guidelines",
    "ISO 22000:2018": "Food Safety Management System",
    "ISO/TS 22002-1:2009": "Prerequisite programs on food safety",
    "ISO 22005:2007": "Traceability in the feed and food chain",
    "ISO/IEC 17025:2017": "Testing and Calibration Laboratories",
    "ISO 15189:2022": "Medical Laboratories – Quality and Competence",
    "ISO/IEC 27001:2022": "Information Security Management System",
    "ISO/IEC 27002:2022": "Information Security Controls",
    "ISO/IEC 20000-1:2018": "IT Service Management System",
    "ISO/IEC 22301:2019": "Business Continuity Management System",
    "ISO 13485:2016": "Medical Devices – Quality Management System",
    "IATF 16949:2016": "Automotive Quality Management System",
    "ISO 3834-2:2021": "Quality requirements for fusion welding",
    "ISO 14064-1:2018": "Greenhouse Gases",
    "ISO 14046:2014": "Water Footprint",
    "ISO 20121:2012": "Event Sustainability Management System",
    "ISO 55001:2014": "Asset Management System",
    "ISO 28000:2022": "Security Management Systems for Supply Chain",
    "AS 9100D:2016": "Aerospace Quality (based on ISO 9001:2015)",
    "ISO 37001:2016": "Anti-bribery Management System",
    "ISO 19600:2014": "Compliance Management System",
    "ISO 29993:2017": "Learning Services",
}

def expand_iso_standard(iso_text: str) -> str:
    """Expand ISO standard name to full version with year if available."""
    if not iso_text:
        return iso_text

    # Clean the input text
    cleaned_text = iso_text.strip()

    # First, try exact match
    if cleaned_text in ISO_STANDARDS_MAPPING:
        return ISO_STANDARDS_MAPPING[cleaned_text]

    # If no exact match, try to find partial matches
    # This handles cases where users might enter variations
    for short_name, full_name in ISO_STANDARDS_MAPPING.items():
        # Check if the input contains the standard number
        if short_name.lower() in cleaned_text.lower():
            return full_name

    # If still no match, try to extract just the number and match
    # This handles cases like "37001" when we have "37001" in mapping
    import re
    number_match = re.search(r'(\d+(?:-\d+)?)', cleaned_text)
    if number_match:
        number = number_match.group(1)
        if number in ISO_STANDARDS_MAPPING:
            return ISO_STANDARDS_MAPPING[number]

    # If no match found, return original text
    return iso_text

def get_iso_standard_code(iso_standard: str) -> str:
    """
    Get the certification code for a given ISO standard.
    Example: "ISO 9001:2015" -> "CM-MS-7842"
    Returns empty string if no code mapping exists.
    """
    if not iso_standard:
        return ""
    
    # First expand the ISO standard if it's a short name
    expanded_iso = expand_iso_standard(iso_standard)
    
    # Look up the code in the mapping
    return ISO_STANDARDS_CODES.get(expanded_iso, "")

def get_text_height(text: str, fontsize: float, fontname: str, max_width: float) -> float:
    """Estimate the height of a text block when wrapped to fit max_width."""
    font = fitz.Font(fontname=fontname)
    words = text.split()
    lines = []
    current_line = ""
    for word in words:
        test_line = current_line + (" " if current_line else "") + word
        if font.text_length(test_line, fontsize) <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    return len(lines) * fontsize * 1.2  # Approximate line height with spacing

def insert_centered_textbox(
    page: fitz.Page,
    rect: fitz.Rect,
    text: str,
    fontname: str,
    fontsize: float,
    color: tuple
) -> None:
    """Insert text centered both vertically and horizontally in the given rectangle."""
    # Calculate text height and center it vertically
    text_height = get_text_height(text, fontsize, fontname, rect.width)
    start_y = rect.y0 + (rect.height - text_height) / 2
    box = fitz.Rect(rect.x0, start_y, rect.x1, start_y + text_height)

    page.insert_textbox(
        box,
        text,
        fontsize=fontsize,
        fontname=fontname,
        color=color,
        align=1  # Centered
    )

def render_optional_fields(page, values, key_coords, value_coords, font_settings):
    """
    Render optional fields with dynamic positioning based on available data.

    Args:
        page: PDF page object
        values: Dictionary of field values
        key_coords: List of 6 key coordinates
        value_coords: List of 6 value coordinates
        font_settings: Font configuration dictionary
    
    Returns:
        dict: Contains 'issue_date_coords' with the actual Issue Date coordinates used
    """
    # Define field order (top to bottom) and their display labels
    fields = [
        "Certificate Number",        # seq 1 - TOP (always present)
        "Initial Registration Date", # seq 2 (optional - not always present)
        "Original Issue Date",       # seq 3 (always present)
        "Issue Date",               # seq 4 (always present)
        "Surveillance Group",       # seq 5 (only 1 of 3 fields present)
        "Recertification Date"      # seq 6 - BOTTOM (always present)
    ]
    
    # Define the surveillance group fields (only 1 will be present)
    surveillance_group_fields = [
        "Surveillance/ Expiry Date",
        "Surveillance Due Date", 
        "Expiry Date"
    ]
    
    # Custom display labels for PDF rendering
    display_labels = {
        "Certificate Number": "Certificate No.",
        "Initial Registration Date": "Initial Registration Date",
        "Original Issue Date": "Original Issue Date",
        "Issue Date": "Issue Date", 
        "Surveillance/ Expiry Date": "Surveillance/ Expiry Date",
        "Surveillance Due Date": "Surveillance Due Date",
        "Expiry Date": "Expiry Date",
        "Recertification Date": "Recertification Date"
    }

    # Filter available fields (non-empty) with special handling for surveillance group
    available_fields = []
    for field in fields:
        if field == "Surveillance Group":
            # Handle surveillance group - find which field is present
            surveillance_value = None
            surveillance_label = None
            
            for surveillance_field in surveillance_group_fields:
                if surveillance_field in values and values[surveillance_field]:
                    surveillance_value = values[surveillance_field]
                    surveillance_label = surveillance_field
                    break
            
            if surveillance_value and surveillance_label:
                available_fields.append((surveillance_label, surveillance_value))
        else:
            value = values.get(field, "").strip()
            if value:  # Only include non-empty fields
                available_fields.append((field, value))

    # Calculate starting position using formula: (6 - available_count) + 1
    total_fields = 6
    available_count = len(available_fields)
    starting_position = (total_fields - available_count) + 1

    # Debug logging
    

    # ✅ ADDED: Track Issue Date coordinates for dynamic revision positioning
    issue_date_coords = None

    # Render from starting position
    for i, (field, value) in enumerate(available_fields):
        coord_index = starting_position - 1 + i  # Convert to 0-based index

        if coord_index < len(key_coords):  # Prevent overflow
            # Prepare text with custom display labels
            key_text = display_labels[field]  # Use custom display label
            value_text = f":{value}"            # Colon + value (no space)

            # Debug logging for each field
            

            # FIX: Extract (x, y) coordinates from rectangles
            key_x = key_coords[coord_index].x0
            key_y = key_coords[coord_index].y0
            value_x = value_coords[coord_index].x0
            value_y = value_coords[coord_index].y0

            # ✅ ADDED: Capture Issue Date coordinates for dynamic revision positioning
            if field == "Issue Date":
                issue_date_coords = value_coords[coord_index]
                print(f"🔍 [DYNAMIC] Issue Date found at position {coord_index + 1}, coordinates: {issue_date_coords}")

            # Insert at respective coordinates using (x, y) points
            page.insert_text(
                (key_x, key_y),
                key_text,
                fontsize=font_settings['fontsize'],
                fontname=font_settings['fontname'],
                color=font_settings['color']
            )

            page.insert_text(
                (value_x, value_y),
                value_text,
                fontsize=font_settings['fontsize'],
                fontname=font_settings['fontname'],
                color=font_settings['color']
            )

            print(f"   ✅ Rendered successfully at position {coord_index + 1}")
        else:
            print(f"⚠️ [SOFTCOPY] Warning: Coordinate index {coord_index} out of bounds")

    # ✅ ADDED: Return Issue Date coordinates for dynamic revision positioning
    return {
        "issue_date_coords": issue_date_coords
    }


def generate_softcopy(base_pdf_path: str, output_pdf_path: str, values: Dict[str, str], template_type: str = "standard") -> Dict[str, any]:
    """
    Generate soft copy PDF with the SAME advanced logic as generate_certificate.

    Args:
        base_pdf_path: Path to the PDF template
        output_pdf_path: Path where the generated PDF will be saved
        values: Dictionary of field values
        template_type: "standard" or "large" template type
    
    Returns:
        Dict containing success status and overflow warnings
    """

    
    # Initialize tracking for overflow warnings
    overflow_warnings = []
    doc = fitz.open(base_pdf_path)
    page = doc[0]

    # --- Register Bodoni (BOD_R.TTF) once and use a clean alias ---
    bodoni_alias = "BodoniMT-Regular"     # no spaces, PostScript-like
    bodoni_path = find_font_path("BOD_R.TTF")
    bodoni_registered = False

    try:
        if bodoni_path:
            # Make the font available by a no-space alias for the whole doc
            doc.insert_font(fontname=bodoni_alias, fontfile=bodoni_path)
            bodoni_registered = True
        else:
            pass  # Will use Times-Roman as fallback
    except Exception as e:
        bodoni_registered = False

    # --- Configuration ---
    color = (0, 0, 0)  # Black text
    fontname = "Times-Bold"  # Use bold font
    
    # ✅ ADDED: Font weight preservation system
    def detect_font_weight(text):
        """
        Detect font weight from text formatting.
        Excel doesn't preserve bold formatting, but we can implement
        a marker system for future enhancement.
        """
        # For now, return default font
        # Future enhancement: Parse Excel formatting or use markers like **bold** or __bold__
        return "Times-Bold"
    
    def process_bold_text(text):
        """
        Process text with bold markers and return segments with font information.
        Returns list of tuples: (text_segment, font_name, is_bold)
        """
        if not text:
            return [(text, "Times-Bold", False)]
        
        segments = []
        current_text = text
        
        # Process **bold** markers
        while '**' in current_text:
            parts = current_text.split('**', 2)
            if len(parts) >= 3:
                # Add normal text before bold
                if parts[0]:
                    segments.append((parts[0], "Times-Roman", False))
                # Add bold text
                segments.append((parts[1], "Times-Bold", True))
                # Continue with remaining text
                current_text = parts[2]
            else:
                break
        
        # Process __bold__ markers
        while '__' in current_text:
            parts = current_text.split('__', 2)
            if len(parts) >= 3:
                # Add normal text before bold
                if parts[0]:
                    segments.append((parts[0], "Times-Roman", False))
                # Add bold text
                segments.append((parts[1], "Times-Bold", True))
                # Continue with remaining text
                current_text = parts[2]
            else:
                break
        
        # Add any remaining normal text
        if current_text:
            segments.append((current_text, "Times-Roman", False))
        
        # If no bold markers found, return original text with default font
        if not segments:
            segments.append((text, "Times-Bold", False))
        
        return segments

    def get_font_for_text(text, default_font="Times-Bold"):
        """
        Get appropriate font for text based on content analysis.
        This is now a legacy function - use process_bold_text for full processing.
        """
        # Check for bold markers
        if '**' in text or '__' in text:
            return "Times-Bold"  # Will be processed by process_bold_text
        else:
            return default_font

    def render_mixed_format_text(page, position, text, font_size, color, max_width=None):
        """
        Render text with mixed bold/normal formatting at the specified position.
        Returns the total width used for positioning calculations.
        """
        if not text:
            return 0
        
        segments = process_bold_text(text)
        current_x = position[0]
        total_width = 0
        
        for segment_text, font_name, is_bold in segments:
            if not segment_text:
                continue
                
            # Calculate text width
            font_obj = fitz.Font(fontname=font_name)
            text_width = font_obj.text_length(segment_text, font_size)
            
            # Check if we need to wrap (if max_width is specified)
            if max_width and current_x + text_width > position[0] + max_width:
                # For now, just render what fits - could implement word wrapping here
                pass
            
            # Render the text segment
            page.insert_text(
                (current_x, position[1]),
                segment_text,
                fontsize=font_size,
                fontname=font_name,
                color=color
            )
            
            # Move position for next segment
            current_x += text_width
            total_width += text_width
        
        return total_width

    # ✅ ADDED: Logo processing
    logo_lookup = values.get("logo_lookup", {})
    logo_filename = values.get("Logo", "").strip()
    
    # Process logo if specified and available
    logo_image = None
    if logo_filename and logo_lookup and logo_filename in logo_lookup:
        try:
            # Convert uploaded file to PIL Image
            from PIL import Image
            import io
            
            logo_file = logo_lookup[logo_filename]
            if hasattr(logo_file, 'file'):
                # Reset file pointer
                logo_file.file.seek(0)
                # Read file content
                logo_content = logo_file.file.read()
                # Convert to PIL Image
                logo_image = Image.open(io.BytesIO(logo_content))
            else:
                logo_image = None
        except Exception as logo_error:
            logo_image = None
    else:
        logo_image = None

    # Standard template coordinates
    standard_coords = {
        "management_system": fitz.Rect(87.9, 185, 580, 226.6),
        "Company Name and Address": fitz.Rect(87.9, 222.6, 580, 315),
        "ISO Standard": fitz.Rect(194.9, 334, 460.3, 370),
        "Scope": {
            "short": fitz.Rect(87.9, 386, 580, 475),    # <24 lines
            "long": fitz.Rect(87.9, 373, 580, 486)      # 24-30 lines
        },
        "certification_code": fitz.Rect(253, 757, 285, 762)  # ✅ UPDATED: Certification code coordinates
    }
    
    # Large template coordinates (for >11 lines)
    large_coords = {
        "management_system": fitz.Rect(87.9, 185, 580, 226.6),  # Same as standard
        "Company Name and Address": fitz.Rect(87.9, 222.6, 580, 295),  # Same as standard
        "ISO Standard": fitz.Rect(194.9, 300, 460.3, 336),  # Same as standard
        "Scope": fitz.Rect(85, 354, 577, 536),  # Much larger for >30 lines
        "certification_code": fitz.Rect(253, 757, 285, 762)  # ✅ UPDATED: Certification code coordinates
    }
    
    # Logo template coordinates (when Logo = "yes")
    logo_coords = {
        "management_system": fitz.Rect(87.9, 185, 580, 226.6),  # Same as standard
        "logo": fitz.Rect(87.9, 226.6, 580, 262.6),  # Logo area: below management_system, above company name
        "Company Name and Address": fitz.Rect(87.9, 262.6, 580, 355),  # Lowered y-coordinates
        "ISO Standard": fitz.Rect(194.9, 374, 460.3, 410),  # Lowered y-coordinates
        "Scope": {
            "short": fitz.Rect(87.9, 426, 580, 515),    # Lowered y-coordinates, y2 remains same
            "long": fitz.Rect(87.9, 413, 580, 526)      # Lowered y-coordinates, y2 remains same
        },
        "certification_code": fitz.Rect(253, 757, 285, 762)  # ✅ UPDATED: Certification code coordinates
    }

    # ✅ ADDED: Defensive checks for coordinate dictionaries
    if standard_coords is None:
        print(f"⚠️ [SOFTCOPY] standard_coords is None - cannot continue")
        raise ValueError("standard_coords is None - cannot generate soft copy")
    
    if large_coords is None:
        print(f"⚠️ [SOFTCOPY] large_coords is None - cannot continue")
        raise ValueError("large_coords is None - cannot generate soft copy")
    
    if logo_coords is None:
        print(f"⚠️ [SOFTCOPY] logo_coords is None - cannot continue")
        raise ValueError("logo_coords is None - cannot generate soft copy")
    
    # Select coordinates based on template type
    if template_type in ["standard", "standard_eco", "standard_nonaccredited"]:
        coords = standard_coords
    elif template_type in ["large", "large_eco", "large_nonaccredited"]:
        coords = large_coords
    elif template_type in ["logo", "logo_nonaccredited", "logo_other", "logo_other_nonaccredited"]:
        # ✅ ADDED: Logo template coordinates for all logo variants
        coords = logo_coords
    else:
        # Fallback to standard coordinates for unknown template types
        coords = standard_coords
    
    # ✅ ADDED: Defensive check for selected coords
    if coords is None:
        raise ValueError("Selected coords is None - cannot generate soft copy")
       

    font_starts = {
        "Company Name and Address": 45,  # Company Name starts from 45pt
        "Scope": 20,
        "ISO Standard": 80,
        "management_system": 15,  # Management system line font size
        "optional_fields": 15,  # New: Font size for optional fields
    }

    # --- Optional Fields Configuration ---
    # ✅ ADDED: Template-specific optional field coordinates
    
    # Large template optional field coordinates (6 fields)
    large_optional_key_coordinates = [
        fitz.Rect(175.5, 522, 343, 530),    # Row 1: Certificate Number
        fitz.Rect(175.5, 538, 343, 548),    # Row 2: Initial Registration Date
        fitz.Rect(175.5, 556, 343, 566),    # Row 3: Original Issue Date
        fitz.Rect(175.5, 574, 343, 584),    # Row 4: Issue Date
        fitz.Rect(175.5, 592, 343, 602),    # Row 5: Surveillance Group (only 1 field present)
        fitz.Rect(175.5, 610, 343, 620)     # Row 6: Recertification Date
    ]

    large_optional_value_coordinates = [
        fitz.Rect(362.1, 522, 446.4, 530),    # Row 1: Certificate Number value
        fitz.Rect(362.1, 538, 446.4, 548),    # Row 2: Initial Registration Date value
        fitz.Rect(362.1, 556, 446.4, 566),    # Row 3: Original Issue Date value
        fitz.Rect(362.1, 574, 446.4, 584),    # Row 4: Issue Date value
        fitz.Rect(362.1, 592, 446.4, 602),    # Row 5: Surveillance Group value (only 1 field present)
        fitz.Rect(362.1, 610, 446.4, 620)     # Row 6: Recertification Date value
    ]

    # Standard template optional field coordinates (6 fields for ≤11 lines)
    # Positioned higher up on the page for shorter content
    standard_optional_key_coordinates = [
        fitz.Rect(175.5, 499.1, 343, 509.1),    # Row 1: Certificate Number
        fitz.Rect(175.5, 516.9, 343, 526.9),    # Row 2: Initial Registration Date
        fitz.Rect(175.5, 535.1, 343, 545.1),    # Row 3: Original Issue Date
        fitz.Rect(175.5, 553.9, 343, 563.9),    # Row 4: Issue Date
        fitz.Rect(175.5, 571.6, 343, 581.6),    # Row 5: Surveillance Group (only 1 field present)
        fitz.Rect(175.5, 589.3, 343, 599.3)     # Row 6: Recertification Date
    ]

    standard_optional_value_coordinates = [
        fitz.Rect(362.1, 499.1, 446.4, 509.1),    # Row 1: Value for Certificate Number
        fitz.Rect(362.1, 516.9, 446.4, 526.9),    # Row 2: Value for Initial Registration Date
        fitz.Rect(362.1, 535.1, 446.4, 545.1),    # Row 3: Value for Original Issue Date
        fitz.Rect(362.1, 553.9, 446.4, 563.9),    # Row 4: Value for Issue Date
        fitz.Rect(362.1, 571.6, 446.4, 581.6),    # Row 5: Value for Surveillance Group (only 1 field present)
        fitz.Rect(362.1, 589.3, 446.4, 599.3)     # Row 6: Value for Recertification Date
    ]

    # Select optional field coordinates based on template type
    if template_type in ["standard", "standard_eco", "standard_nonaccredited"]:
        optional_key_coordinates = standard_optional_key_coordinates
        optional_value_coordinates = standard_optional_value_coordinates
    elif template_type in ["large", "large_eco", "large_nonaccredited"]:
        optional_key_coordinates = large_optional_key_coordinates
        optional_value_coordinates = large_optional_value_coordinates
    elif template_type == "logo":
        # Logo template uses standard optional field coordinates
        optional_key_coordinates = standard_optional_key_coordinates
        optional_value_coordinates = standard_optional_value_coordinates
    else:
        # Fallback to standard coordinates for unknown template types
        optional_key_coordinates = standard_optional_key_coordinates
        optional_value_coordinates = standard_optional_value_coordinates

    # ✅ ADDED: Adjust scope coordinates based on whether Initial Registration Date is present
    # This affects the available space for scope text
    initial_registration_date = values.get("Initial Registration Date", "")
    if initial_registration_date and template_type == "large":
        # When Initial Registration Date is present, reduce scope height to accommodate the extra field
        print(f"🔍 [SOFTCOPY] Initial Registration Date present - adjusting scope coordinates for large template")
        # Adjust scope coordinates: reduce height by 16 units (same as field spacing)
        original_scope = coords["Scope"]
        adjusted_scope = fitz.Rect(
            original_scope.x0, 
            original_scope.y0, 
            original_scope.x1, 
            original_scope.y1 - 16  # Reduce height by 16 units
        )
        coords["Scope"] = adjusted_scope
        print(f"🔍 [SOFTCOPY] Scope coordinates adjusted: {original_scope} → {adjusted_scope}")
    else:
        print(f"🔍 [SOFTCOPY] Using standard scope coordinates (Initial Registration Date not present)")

    # Font settings for optional fields
    # Use Bodoni if registered, otherwise standard Times
    resolved_optional_fontname = bodoni_alias if bodoni_registered else "Times-Roman"
    
    optional_font_settings = {
        "fontname": resolved_optional_fontname,  # Clean alias, no file paths
        "fontsize": 13,  # Fixed: Changed from 15 to 13 (reduced font size)
        "color": (0, 0, 0) # Black
    }
    
    # Optional: Validate that the font is actually available
    def _assert_valid_fontname(name: str):
        try:
            _ = fitz.Font(fontname=name)
        except Exception as e:
            raise RuntimeError(f"Font alias '{name}' is not available: {e}")
    
    # Validate the font before proceeding
    _assert_valid_fontname(resolved_optional_fontname)
    
    # --- End Optional Fields Configuration ---

    # ✅ ADDED: Template-specific Revision field configuration
    
    # Large template revision field coordinates (matching Issue Date Y coordinates)
    large_revision_coordinates = fitz.Rect(446, 574, 456, 584)
    
    # Standard template revision field coordinates (matching Issue Date Y coordinates)
    # Positioned to match Issue Date field positioning
    standard_revision_coordinates = fitz.Rect(446, 553.9, 456, 563.9)
    
    # Select revision field coordinates based on template type
    if template_type == "standard":
        revision_coordinates = standard_revision_coordinates
    else:  # large template
        revision_coordinates = large_revision_coordinates
    
    # ✅ ADDED: Validate that coordinates are properly set
    if not optional_key_coordinates or not optional_value_coordinates:
        raise ValueError(f"Optional field coordinates not properly configured for template type: {template_type}")
    
    if not revision_coordinates:
        raise ValueError(f"Revision field coordinates not properly configured for template type: {template_type}")
    
    
    
    # Font settings for revision field (same as optional fields)
    revision_font_settings = {
        "fontname": resolved_optional_fontname,
        "fontsize": 15,
        "color": (0, 0, 0)
    }

    # --- End Configuration ---

    # Extract additional soft copy specific fields
    certificate_number = values.get("Certificate Number", "")
    original_issue_date = values.get("Original Issue Date", "")
    issue_date = values.get("Issue Date", "")
    surveillance_date = values.get("Surveillance/ Expiry Date", "")
    recertification_date = values.get("Recertification Date", "")
    # ✅ ADDED: Extract Revision field
    revision = values.get("Revision", "")

    # Validate mandatory field
    if not certificate_number:
        raise ValueError("Certificate Number is mandatory for soft copy generation")

    # Determine Scope coordinates based on content length
    scope_text = values.get("Scope", "")
    scope_words = len(scope_text.split())

    # Calculate estimated lines for Scope (approximate calculation)
    estimated_lines = max(1, (scope_words * 8) // 60)  # Rough estimate: 8 chars per word, 60 chars per line

    # Determine which coordinate set to use (lines win over words)
    if template_type in ["standard", "standard_eco", "standard_nonaccredited"]:
        # Standard template: dynamic coordinates based on content length
        if estimated_lines >= 24:  # Long content condition
            scope_rect = coords["Scope"]["long"]
            scope_layout = "long"
        else:  # Short content condition
            scope_rect = coords["Scope"]["short"]
            scope_layout = "short"
    elif template_type in ["large", "large_eco", "large_nonaccredited"]:
        # Large template: fixed large coordinates
        scope_rect = coords["Scope"]
        scope_layout = "large"
    elif template_type in ["logo", "logo_nonaccredited", "logo_other", "logo_other_nonaccredited"]:
        # Logo template: dynamic coordinates based on content length
        if estimated_lines >= 24:  # Long content condition
            scope_rect = coords["Scope"]["long"]
            scope_layout = "long"
        else:  # Short content condition
            scope_rect = coords["Scope"]["short"]
            scope_layout = "short"
            print(f"🎯 [SOFTCOPY] Scope: {estimated_lines} lines (<24) -> selected SHORT scope coordinates")
            print(f"🔍 [SOFTCOPY] Logo template - Short content: {scope_words} words, ~{estimated_lines} lines")
            print(f"🔍 [SOFTCOPY] Using coordinates: {scope_rect}")
    else:
        # Fallback to standard coordinates for unknown template types
        if estimated_lines >= 24:
            scope_rect = coords["Scope"]["long"]
            scope_layout = "long"
        else:
            scope_rect = coords["Scope"]["short"]
            scope_layout = "short"
        print(f"⚠️ [SOFTCOPY] Unknown template type '{template_type}' -> fallback to standard scope coordinates")
        print(f"🔍 [SOFTCOPY] Fallback template - Content: {scope_words} words, ~{estimated_lines} lines")
        print(f"🔍 [SOFTCOPY] Using coordinates: {scope_rect}")

    # Store original scope coordinates before modification for Extra Line processing
    original_scope_coords = coords["Scope"].copy() if isinstance(coords["Scope"], dict) else coords["Scope"]
    
    # Add Scope coordinates to the main coords dictionary
    coords["Scope"] = scope_rect

    # ✅ NEW: Adjust scope coordinates when Extra Line is present
    extra_line = values.get("Extra Line", "").strip()
    if extra_line:
        print(f"🔍 [SOFTCOPY] Extra Line present - adjusting scope coordinates")
        
        # Adjust scope coordinates: reduce height by 10pt
        if template_type in ["large", "large_eco", "large_nonaccredited"]:
            # Large template scope adjustment
            original_scope = coords["Scope"]
            adjusted_scope = fitz.Rect(
                original_scope.x0,      # x0: 85 (unchanged)
                original_scope.y0,      # y0: 351 (unchanged)  
                original_scope.x1,      # x1: 577 (unchanged)
                original_scope.y1 - 10  # y1: 536 - 10 = 526 (reduced by 10pt)
            )
            coords["Scope"] = adjusted_scope
            print(f"🔍 [SOFTCOPY] Large template scope adjusted: {original_scope} → {adjusted_scope}")
            
        elif template_type in ["standard", "standard_eco", "standard_nonaccredited"]:
            # Standard template scope adjustment (both short and long)
            original_short = original_scope_coords["short"]
            original_long = original_scope_coords["long"]
            
            adjusted_short = fitz.Rect(
                original_short.x0,      # x0: 87.9 (unchanged)
                original_short.y0,      # y0: 386 (unchanged)
                original_short.x1,      # x1: 580 (unchanged)
                original_short.y1 - 10  # y1: 475 - 10 = 465 (reduced by 10pt)
            )
            
            adjusted_long = fitz.Rect(
                original_long.x0,       # x0: 87.9 (unchanged)
                original_long.y0,       # y0: 373 (unchanged)
                original_long.x1,       # x1: 580 (unchanged)
                original_long.y1 - 10   # y1: 486 - 10 = 476 (reduced by 10pt)
            )
            
            # Update the original coordinates dictionary
            original_scope_coords["short"] = adjusted_short
            original_scope_coords["long"] = adjusted_long
            print(f"🔍 [SOFTCOPY] Standard template scope adjusted: short={adjusted_short}, long={adjusted_long}")
            
        elif template_type == "logo":
            # Logo template scope adjustment (same as standard)
            original_short = original_scope_coords["short"]
            original_long = original_scope_coords["long"]
            
            adjusted_short = fitz.Rect(
                original_short.x0,      # x0: 87.9 (unchanged)
                original_short.y0,      # y0: 426 (unchanged)
                original_short.x1,      # x1: 580 (unchanged)
                original_short.y1 - 10  # y1: 515 - 10 = 505 (reduced by 10pt)
            )
            
            adjusted_long = fitz.Rect(
                original_long.x0,       # x0: 87.9 (unchanged)
                original_long.y0,       # y0: 413 (unchanged)
                original_long.x1,       # x1: 580 (unchanged)
                original_long.y1 - 10   # y1: 526 - 10 = 516 (reduced by 10pt)
            )
            
            # Update the original coordinates dictionary
            original_scope_coords["short"] = adjusted_short
            original_scope_coords["long"] = adjusted_long
            print(f"🔍 [SOFTCOPY] Logo template scope adjusted: short={adjusted_short}, long={adjusted_long}")
            
    else:
        print(f"🔍 [SOFTCOPY] No Extra Line - using standard scope coordinates")

    # Management system will be generated during ISO Standard field processing
    # (same timing as certificate generation)

    # Process each field
    for field, text in values.items():
        if field in ["Certificate Number", "Original Issue Date", "Issue Date", "Surveillance/ Expiry Date", "Recertification Date", "Initial Registration Date", "Surveillance Due Date", "Expiry Date"]:
            # Skip individual processing - handled by batch renderer
            print(f"🔍 [SOFTCOPY] Skipping individual processing for '{field}' - will be handled by optional fields renderer")
            continue
        elif field == "Company Name":
            # Handle Company Name and Address together - SAME LOGIC AS generate_certificate
            company_text = text
            address_text = values.get("Address", "")

            # ENHANCED DEBUG: Detailed address processing analysis
           
            # Check for Excel line breaks in both company and address text
            # Line break detection logic (print statements removed)

            # PRE-PROCESS: Apply line break logic BEFORE font size calculation
            # This ensures both font calculation and rendering use the same processed text

            # Process Company Name with line break preservation - SAME LOGIC AS generate_certificate
            def process_text_with_line_breaks(input_text, field_name):
                if not input_text:
                    return []

                # ✅ UPDATED: Split by actual line breaks and PRESERVE empty lines
                lines = input_text.split('\n')
                processed_lines = []

                for line in lines:
                    # Preserve empty lines to maintain spacing from Excel
                    processed_lines.append(line)  # Keep original line (including empty ones)

                return processed_lines

            # Pre-process both company and address text to handle line breaks
            company_processed_lines = process_text_with_line_breaks(company_text, "Company")
            address_processed_lines = process_text_with_line_breaks(address_text, "Address")
            
            # ✅ ADDED: Determine address alignment based on Excel column or line count
            address_alignment_column = values.get("Address alignment", "").strip().lower()
            address_lines_count = len(address_processed_lines)
            
            if address_alignment_column == "center":
                address_alignment = "center"
                print(f"🔍 [SOFTCOPY] Address: Excel column specifies CENTERED alignment")
            elif address_alignment_column == "left":
                address_alignment = "left"
                print(f"🔍 [SOFTCOPY] Address: Excel column specifies LEFT alignment")
            else:
                # Default logic: always center unless Excel column specifies otherwise
                address_alignment = "center"  # Default: always center
                print(f"🔍 [SOFTCOPY] Address: No Excel column value - using CENTERED alignment (default)")

           

            rect = coords["Company Name and Address"]
           

            # Check if address text is empty or None
            # Address validation logic (print statements removed)

            # ✅ UPDATED: Dynamic Company Name font sizing based on line count
            # First, determine if Company Name will be single line or multi-line
            company_lines_count = len([line for line in company_processed_lines if line.strip()])
            
            # Set initial font size based on line count
            if company_lines_count <= 1:
                company_font_size = 35  # Single line - start with 35pt
            else:
                company_font_size = 30  # Multiple lines - start with 30pt
            
            address_font_size = 13.6
            
            # Variables to store the final wrapped lines and font sizes
            final_company_lines = []
            final_address_lines = []
            
            # ✅ IMPROVED: Different logic for single line vs multi-line company names
            if company_lines_count <= 1:
                # NO cmd+enter in Excel: Force single line, use font reduction only
                
                while company_font_size >= 8:  # Minimum font size
                    # Check if entire company name fits in one line at current font size
                    font_obj = fitz.Font(fontname=fontname)
                    text_width = font_obj.text_length(company_text, company_font_size)
                    
                    if text_width <= rect.width - 10:  # Leave margin
                        # Text fits in one line - use this font size
                        final_company_lines = [company_text]  # Single line
                        break
                    else:
                        # Text too wide - reduce font size and try again
                        company_font_size -= 1
                
                # If we reached minimum font size and still doesn't fit, use the minimum
                if company_font_size < 8:
                    company_font_size = 8
                    final_company_lines = [company_text]
                
            else:
                # cmd+enter present in Excel: Allow word wrapping up to 2 lines
                
                while company_font_size >= 8:  # Minimum font size
                    company_lines = []
                    
                    # Process each pre-processed line with word wrapping
                    for processed_line in company_processed_lines:
                        if not processed_line.strip():  # Empty line - preserve it
                            company_lines.append("")  # Add empty line to maintain spacing
                            continue
                        
                        # Non-empty line - apply word wrapping
                        words = processed_line.split()
                        current_line = ""
                        
                        for word in words:
                            test_line = current_line + (" " if current_line else "") + word
                            font_obj = fitz.Font(fontname=fontname)
                            if font_obj.text_length(test_line, company_font_size) <= rect.width - 10:  # Leave margin
                                current_line = test_line
                            else:
                                if current_line:
                                    company_lines.append(current_line)
                                current_line = word
                        
                        if current_line:
                            company_lines.append(current_line)
                    
                    # ✅ UPDATED: Allow Company Name to use up to 2 lines (after line breaks + word wrapping)
                    if len(company_lines) <= 2:
                        final_company_lines = company_lines.copy()
                        break
                    
                    # Reduce Company Name font size
                    company_font_size -= 1

            # Calculate Company Name height
            # Consistent line spacing: 1.05 for all templates
            company_height = len(final_company_lines) * company_font_size * 1.05  # Consistent spacing for all templates

            # Now find font size for Address to fit in remaining space
            remaining_height = rect.height - company_height - 2  # Leave margin
           

            address_font_size_attempts = 0
            while address_font_size >= 6:  # Minimum font size
                address_font_size_attempts += 1

                # Process Address using pre-processed lines with word wrapping
                address_lines = []

                # Process each pre-processed address line with word wrapping
                for processed_line in address_processed_lines:
                    if not processed_line.strip():  # Empty line - preserve it
                        address_lines.append("")  # Add empty line to maintain spacing
                        continue
                    
                    # Non-empty line - apply word wrapping
                    words = processed_line.split()
                    current_line = ""

                    for word in words:
                        test_line = current_line + (" " if current_line else "") + word
                        font_obj = fitz.Font(fontname=fontname)
                        test_width = font_obj.text_length(test_line, address_font_size)
                        if test_width <= rect.width - 10:  # Leave margin
                            current_line = test_line
                        else:
                            if current_line:
                                address_lines.append(current_line)
                            current_line = word

                    if current_line:
                        address_lines.append(current_line)

                # Calculate Address height
                address_height = len(address_lines) * address_font_size * 1.0

                # Check if Address fits in remaining space
                if address_height <= remaining_height:
                    final_address_lines = address_lines.copy()
                    break
                else:
                    print(f"❌ [SOFTCOPY] Address too tall: {address_height:.1f}pt > {remaining_height:.1f}pt, reducing font size")

                # Reduce Address font size
                address_font_size -= 0.5

            # Now render Company Name and Address dynamically
            if final_company_lines or final_address_lines:

                # ENHANCED DEBUG: Final rendering analysis
                

                # Calculate total height
                total_height = company_height + address_height

                # No top margin - start at exact rectangle top
                start_y = rect.y0  # Start at exact top of box

                # Render Company Name first (starts from top)
                current_y = start_y
                for i, line in enumerate(final_company_lines):
                    line_height = company_font_size * 1.05  # Consistent spacing for all templates
                    y_pos = current_y + line_height/2  # Adjust for baseline
                    center_x = (rect.x0 + rect.x1) / 2
                    
                    # ✅ UPDATED: Handle empty lines (preserve spacing from Excel)
                    if line.strip():  # Non-empty line - render text
                        # ✅ ENHANCED: Use mixed format text rendering for bold detection
                        if '**' in line or '__' in line:
                            # Calculate total width for centering
                            segments = process_bold_text(line)
                            total_width = 0
                            for segment_text, _, _ in segments:
                                if segment_text:
                                    font_obj = fitz.Font(fontname="Times-Bold" if "**" in segment_text or "__" in segment_text else "Times-Roman")
                                    total_width += font_obj.text_length(segment_text, company_font_size)
                            
                            x_pos = center_x - total_width / 2
                            render_mixed_format_text(page, (x_pos, y_pos), line, company_font_size, color)
                        else:
                            # Standard rendering for non-bold text
                            line_width = font_obj.text_length(line, company_font_size)
                            x_pos = center_x - line_width / 2
                            
                            # ✅ ADDED: Dynamic font selection for Company Name
                            dynamic_font = get_font_for_text(line, fontname)
                            page.insert_text(
                                (x_pos, y_pos),
                                line,
                                fontsize=company_font_size,
                                fontname=dynamic_font,
                                color=color
                            )
                    # Empty line - just advance position (creates blank space)
                    
                    current_y += line_height

                # Render Address below Company Name
                if final_address_lines:
                    # Add spacing between company and address
                    current_y += 3  # 3pt spacing (consistent with certificate generation)

                    for i, line in enumerate(final_address_lines):
                        line_height = address_font_size * 1.05  # Consistent spacing for all templates
                        y_pos = current_y + line_height/2  # Adjust for baseline
                        
                        # ✅ ADDED: Dynamic alignment based on address line count
                        if address_alignment == "center":
                            center_x = (rect.x0 + rect.x1) / 2
                            line_width = font_obj.text_length(line, address_font_size)
                            x_pos = center_x - line_width / 2
                        else:  # left-aligned
                            x_pos = rect.x0 + 5  # Small left margin


                        # ✅ UPDATED: Handle empty lines (preserve spacing from Excel)
                        if line.strip():  # Non-empty line - render text
                            # ✅ ENHANCED: Use mixed format text rendering for bold detection
                            if '**' in line or '__' in line:
                                # Calculate total width for alignment
                                segments = process_bold_text(line)
                                total_width = 0
                                for segment_text, _, _ in segments:
                                    if segment_text:
                                        font_obj = fitz.Font(fontname="Times-Bold" if "**" in segment_text or "__" in segment_text else "Times-Roman")
                                        total_width += font_obj.text_length(segment_text, address_font_size)
                                
                                # Apply alignment based on address_alignment setting
                                if address_alignment == "center":
                                    x_pos = center_x - total_width / 2
                                else:  # left-aligned
                                    x_pos = rect.x0 + 5  # Small left margin
                                
                                render_mixed_format_text(page, (x_pos, y_pos), line, address_font_size, color)
                            else:
                                # Standard rendering for non-bold text
                                # x_pos is already calculated above based on alignment
                                
                                # ✅ ADDED: Dynamic font selection for Address
                                dynamic_font = get_font_for_text(line, fontname)
                                page.insert_text(
                                    (x_pos, y_pos),
                                    line,
                                    fontsize=address_font_size,
                                    fontname=dynamic_font,
                                    color=color
                                )
                        # Empty line - just advance position (creates blank space)

                        current_y += line_height

               
            else:
                print(f"⚠️ [SOFTCOPY] No company or address lines to render")

        elif field == "ISO Standard":
            # Handle ISO Standard with SAME LOGIC AS generate_certificate
            # Expand ISO standard if needed
            expanded_text = expand_iso_standard(text)
            if expanded_text != text:
                text = expanded_text

            # After processing ISO Standard, render the management system line
            iso_standard_text = text

            # Get the description from the mapping using the expanded version
            system_name = ISO_STANDARDS_DESCRIPTIONS.get(expanded_text, "Management System")

            # Capitalize first letters of each word in system_name
            system_name_caps = ' '.join(word.capitalize() for word in system_name.split())

            # Create the management system line
            management_line = f"This is to certify that the {system_name_caps} of"

            # Get the management_system rectangle
            management_rect = coords["management_system"]

            # Calculate center position for the text
            center_x = (management_rect.x0 + management_rect.x1) / 2
            center_y = (management_rect.y0 + management_rect.y1) / 2 + 15/3  # Adjust for baseline

            # Calculate text width for centering
            font_obj = fitz.Font(fontname="Times-BoldItalic")  # Use bold italic font
            text_width = font_obj.text_length(management_line, 15)
            start_x = center_x - text_width / 2

            # Insert the management system text
            page.insert_text(
                (start_x, center_y),
                management_line,
                fontsize=15,
                fontname="Times-BoldItalic", # Bold italic font
                color=(0, 0, 0)  # Black color
            )

            # Print font size for management system

            # Update the text to use expanded version for display
            text = expanded_text

            rect = coords["ISO Standard"]
            start_size = font_starts.get("ISO Standard", 80)
            font_size = start_size

            # Reduce font size if it doesn't fit, but ensure minimum size
            while font_size >= 12:  # Increased minimum from 10 to 12
                text_height = get_text_height(text, font_size, fontname, rect.width)
                limit = rect.height

                if text_height <= limit:
                    break
                font_size -= 1

            # Perfect centering for ISO Standard - both horizontal and vertical
            center_x = (rect.x0 + rect.x1) / 2
            center_y = (rect.y0 + rect.y1) / 2 + font_size/3  # Adjust for baseline

            # ✅ ENHANCED: Use mixed format text rendering for bold detection
            if '**' in text or '__' in text:
                # Calculate total width for centering
                segments = process_bold_text(text)
                total_width = 0
                for segment_text, _, _ in segments:
                    if segment_text:
                        font_obj = fitz.Font(fontname="Times-Bold" if "**" in segment_text or "__" in segment_text else "Times-Roman")
                        total_width += font_obj.text_length(segment_text, font_size)
                
                start_x = center_x - total_width / 2
                render_mixed_format_text(page, (start_x, center_y), text, font_size, color)
            else:
                # Standard rendering for non-bold text
                font_obj = fitz.Font(fontname=fontname)
                text_width = font_obj.text_length(text, font_size)
                start_x = center_x - text_width / 2

                page.insert_text(
                    (start_x, center_y),
                    text,
                    fontsize=font_size,
                    fontname=fontname,
                    color=color
                )

            # Print font size for ISO Standard
            print(f"📏 [SOFTCOPY] ISO Standard: {font_size}pt (centered)")
            
            # ✅ MODIFIED: Render certification code below ISO Standard with different coordinates for non-accredited
            try:
                # Check accreditation status - use different coordinates for non-accredited
                accreditation = (values.get("Accreditation") or values.get("accreditation") or "").strip().lower()
                
                # Get the certification code for this ISO standard
                cert_code = get_iso_standard_code(text)
                if cert_code:
                    print(f"🔍 [SOFTCOPY] ISO Standard '{text}' maps to certification code: '{cert_code}'")
                    
                    # ✅ NEW: Use different coordinates based on accreditation status
                    if accreditation == "no":
                        # Non-accredited: Move code to the right
                        code_rect = fitz.Rect(335, 757, 390, 762)  # Updated coordinates
                        print(f"🔍 [SOFTCOPY] Non-accredited certificate - using right position")
                    else:
                        # Accredited: Use original position
                        code_rect = coords["certification_code"]  # Original: (253, 757, 285, 762)
                        print(f"🔍 [SOFTCOPY] Accredited certificate - using standard position")
                    
                    # ✅ FIXED: Use reliable font that's available in PyMuPDF
                    reliable_font = "helv"  # Helvetica - always available in PyMuPDF
                    
                    # Insert certification code with specified font settings
                    page.insert_text(
                        (code_rect.x0, code_rect.y0),
                        cert_code,
                        fontsize=5,  # 5pt as specified
                        fontname=reliable_font,  # Use reliable font
                        color=(0, 0, 0)  # Black color
                        )
                    
                    print(f"✅ [SOFTCOPY] Certification code '{cert_code}' rendered at coordinates {code_rect}")
                    print(f"📏 [SOFTCOPY] Certification code: 5pt {reliable_font} font")
                else:
                    print(f"⚠️ [SOFTCOPY] No certification code found for ISO Standard: '{text}'")
            except Exception as code_error:
                print(f"⚠️ [SOFTCOPY] Error rendering certification code: {code_error}")
                print(f"⚠️ [SOFTCOPY] Soft copy will be generated without certification code")

        elif field == "Scope":
            # Handle Scope with SAME ADVANCED LOGIC AS generate_certificate
            # Scope text now uses justification (left and right alignment) for professional appearance
            rect = coords["Scope"]
            
            
            # Template-specific starting font size for Scope
            if template_type == "standard" and scope_layout == "short":
                start_size = 15  # Standard template short scope: max 15pt
            else:
                start_size = font_starts.get("Scope", 20)  # Large template or standard long scope: max 20pt
            
            font_size = start_size
            iteration_count = 0

            # Reduce font size if it doesn't fit, but ensure minimum size
            while font_size >= 12:  # Increased minimum from 10 to 12
                iteration_count += 1
                text_height = get_text_height(text, font_size, fontname, rect.width)
                limit = rect.height
                

                if text_height <= limit:
                    break
                font_size -= 1

            # PowerPoint-style centering with automatic font size reduction
            original_font_size = font_size
            
            # Reduce font size until text fits within box boundaries
            font_size = original_font_size
            iteration_count = 0
            min_font_size = 4  # Allow font size to go below 8pt if needed

            while font_size >= min_font_size:  # Changed from 8 to 4
                iteration_count += 1

                # Enhanced text processing with bullet point detection AND line break preservation
                lines = []
                
                # Split text by actual line breaks first
                if '\n' in text:
                    # Handle line breaks properly
                    text_lines = text.split('\n')
                    for text_line in text_lines:
                        if text_line.strip():  # Only process non-empty lines
                            # Process each line for word wrapping and bullet points
                            words = text_line.strip().split()
                            current_line = ""
                            
                            for word in words:
                                # Check if word starts with bullet point indicators
                                is_bullet_point = any(word.startswith(indicator) for indicator in ['-', '•', '>', '→', '▪', '▫', '*'])
                                
                                # If it's a bullet point and we have content, start a new line
                                if is_bullet_point and current_line:
                                    lines.append(current_line)
                                    # Replace * with • for display (in font size calculation)
                                    if word.startswith('*'):
                                        # ✅ Safe string handling for bullet point slice
                                        safe_word = str(word) if word is not None else ""
                                        print(f"🔄 [SOFTCOPY BULLET] Will replace '{safe_word}' with '•{safe_word[1:]}' in final rendering")
                                    current_line = word
                                    continue
                                
                                test_line = current_line + (" " if current_line else "") + word
                                font_obj = fitz.Font(fontname=fontname)
                                
                                if font_obj.text_length(test_line, font_size) <= rect.width:
                                    current_line = test_line
                                else:
                                    if current_line:
                                        lines.append(current_line)
                                    current_line = word
                            
                            if current_line:
                                lines.append(current_line)
                else:
                    # No line breaks, process as single block
                    words = text.split()
                    current_line = ""
                    
                    for word in words:
                        # Check if word starts with bullet point indicators
                        is_bullet_point = any(word.startswith(indicator) for indicator in ['-', '•', '>', '→', '▪', '▫', '*'])
                        
                        # If it's a bullet point and we have content, start a new line
                        if is_bullet_point and current_line:
                            lines.append(current_line)
                            # Replace * with • for display (in font size calculation)
                            if word.startswith('*'):
                                # ✅ Safe string handling for bullet point slice
                                safe_word = str(word) if word is not None else ""
                                print(f"[BULLET] Will replace '{safe_word}' with '•{safe_word[1:]}' in final rendering")
                            current_line = word
                            continue
                        
                        test_line = current_line + (" " if current_line else "") + word
                        font_obj = fitz.Font(fontname=fontname)
                        
                        if font_obj.text_length(test_line, font_size) <= rect.width:
                            current_line = test_line
                        else:
                            if current_line:
                                lines.append(current_line)
                            current_line = word
                    
                    if current_line:
                        lines.append(current_line)

                # Calculate total height of all lines
                # Template-specific line spacing: 1.1 for large/logo, 1.2 for standard
                if template_type in ["large", "large_eco", "large_nonaccredited", "logo", "logo_nonaccredited", "logo_other", "logo_other_nonaccredited"]:
                    line_height = font_size * 1.1  # Tight spacing for large/logo templates
                else:  # standard templates
                    line_height = font_size * 1.2  # Loose spacing for standard templates
                total_height = len(lines) * line_height
                
                

                # Check if text fits vertically within box boundaries
                if total_height <= rect.height:  # No margin
                    break
                font_size -= 1

            # Check if we hit the minimum font size and still have overflow
            if font_size == min_font_size and total_height > rect.height:
                # Calculate how much overflow we have
                overflow_amount = total_height - rect.height
                overflow_percentage = (overflow_amount / rect.height) * 100
                
                # Add to overflow warnings
                company_name = values.get("Company Name", "Unknown Company")
                iso_standard = values.get("ISO Standard", "Unknown Standard")
                
                warning_msg = f"[OVERFLOW] {company_name} - {iso_standard}: Scope text exceeds coordinates by {overflow_percentage:.1f}% (font size reduced to {min_font_size}pt)"
                overflow_warnings.append({
                    "company_name": company_name,
                    "iso_standard": iso_standard,
                    "overflow_percentage": overflow_percentage,
                    "final_font_size": min_font_size,
                    "message": warning_msg
                })
                
                # Force text to fit by truncating if necessary
                max_lines = int(rect.height / min_font_size)
                
                if len(lines) > max_lines:
                    lines = lines[:max_lines]


            # Now draw the text with the fitting font size using enhanced processing
            # Process text to handle line breaks and bullet points properly
            
            # Replace all asterisks with bullet points for display
            text = text.replace('*', '•')
            
            lines = []
            
            # Split text by actual line breaks first
            if '\n' in text:
                # Handle line breaks properly
                text_lines = text.split('\n')
                for text_line in text_lines:
                    if text_line.strip():  # Only process non-empty lines
                        # Process each line for word wrapping and bullet points
                        words = text_line.strip().split()
                        current_line = ""
                        
                        for word in words:
                            # Check if word starts with bullet point indicators
                            is_bullet_point = any(word.startswith(indicator) for indicator in ['-', '•', '>', '→', '▪', '▫', '*'])
                            
                            # If it's a bullet point and we have content, start a new line
                            if is_bullet_point and current_line:
                                lines.append(current_line)
                                # Replace * with • for display
                                display_word = word.replace('*', '•')
                                if word != display_word:
                                    print(f"🔄 [SOFTCOPY BULLET] Replaced '{word}' with '{display_word}'")
                                current_line = display_word
                                continue
                            
                            test_line = current_line + (" " if current_line else "") + word
                            font_obj = fitz.Font(fontname=fontname)
                            if font_obj.text_length(test_line, font_size) <= rect.width:
                                current_line = test_line
                            else:
                                if current_line:
                                    lines.append(current_line)
                                current_line = word
                        
                        if current_line:
                            lines.append(current_line)
            else:
                # No line breaks, process as single block
                words = text.split()
                current_line = ""
                
                for word in words:
                    # Check if word starts with bullet point indicators
                    is_bullet_point = any(word.startswith(indicator) for indicator in ['-', '•', '>', '→', '▪', '▫', '*'])
                    
                    # If it's a bullet point and we have content, start a new line
                    if is_bullet_point and current_line:
                        lines.append(current_line)
                        # Replace * with • for display
                        display_word = word.replace('*', '•')
                        current_line = display_word
                        continue
                    
                    test_line = current_line + (" " if current_line else "") + word
                    font_obj = fitz.Font(fontname=fontname)
                    if font_obj.text_length(test_line, font_size) <= rect.width:
                        current_line = test_line
                    else:
                        if current_line:
                            lines.append(current_line)
                        current_line = word
                
                if current_line:
                    lines.append(current_line)


            # Calculate total height and position vertically based on template type
            # Template-specific line spacing: 1.1 for large/logo, 1.2 for standard
            if template_type in ["large", "large_eco", "large_nonaccredited", "logo", "logo_nonaccredited", "logo_other", "logo_other_nonaccredited"]:
                line_height = font_size * 1.1  # Tight spacing for large/logo templates
            else:  # standard templates
                line_height = font_size * 1.2  # Loose spacing for standard templates
            total_height = len(lines) * line_height
            
            if template_type in ["large", "large_eco", "large_nonaccredited"]:
                # Large template: start from top with no margin
                start_y = rect.y0
                
                # Check if text would overflow bottom
                if start_y + total_height > rect.y1:
                    # If overflow, adjust to fit within bounds
                    start_y = rect.y1 - total_height - 2  # 2pt margin from bottom
            else:
                # Standard template: keep current centering logic
                start_y = rect.y0 + (rect.height - total_height) / 2 + line_height/2  # Adjust for baseline
            
            # Debug output for line break processing
            has_line_breaks = '\n' in text
            if '\n' in text:
                line_break_positions = [i for i, char in enumerate(text) if char == '\n']

           

            # Final summary with template context
            
            # ✅ SIMPLIFIED: Scope rendering with consistent centering
            current_y = start_y
            
            
            # Render each line centered for consistent appearance
            for i, line in enumerate(lines):
                if not line.strip():  # Skip empty lines
                    current_y += line_height
                    continue
                
                # Check if this is the last non-empty line
                is_last_line = i == len(lines) - 1 or all(not lines[j].strip() for j in range(i + 1, len(lines)))
                
                if is_last_line:
                    # ✅ LAST LINE: Center align for balanced appearance
                    center_x = (rect.x0 + rect.x1) / 2
                    
                    # ✅ ENHANCED: Use mixed format text rendering for bold detection
                    if '**' in line or '__' in line:
                        # Calculate total width for centering
                        segments = process_bold_text(line)
                        total_width = 0
                        for segment_text, _, _ in segments:
                            if segment_text:
                                font_obj = fitz.Font(fontname="Times-Bold" if "**" in segment_text or "__" in segment_text else "Times-Roman")
                                total_width += font_obj.text_length(segment_text, font_size)
                        
                        start_x = center_x - total_width / 2
                        render_mixed_format_text(page, (start_x, current_y), line, font_size, color)
                    else:
                        # Standard rendering for non-bold text
                        font_obj = fitz.Font(fontname=fontname)
                        text_width = font_obj.text_length(line, font_size)
                        start_x = center_x - text_width / 2
                        
                        page.insert_text(
                            (start_x, current_y),
                            line,
                            fontsize=font_size,
                            fontname=fontname,
                            color=color
                        )
                else:
                    # ✅ INTERMEDIATE LINES: Center align for consistency
                    center_x = (rect.x0 + rect.x1) / 2
                    
                    # ✅ ENHANCED: Use mixed format text rendering for bold detection
                    if '**' in line or '__' in line:
                        # Calculate total width for centering
                        segments = process_bold_text(line)
                        total_width = 0
                        for segment_text, _, _ in segments:
                            if segment_text:
                                font_obj = fitz.Font(fontname="Times-Bold" if "**" in segment_text or "__" in segment_text else "Times-Roman")
                                total_width += font_obj.text_length(segment_text, font_size)
                        
                        start_x = center_x - total_width / 2
                        render_mixed_format_text(page, (start_x, current_y), line, font_size, color)
                    else:
                        # Standard rendering for non-bold text
                        font_obj = fitz.Font(fontname=fontname)
                        text_width = font_obj.text_length(line, font_size)
                        start_x = center_x - text_width / 2
                        page.insert_text(
                            (start_x, current_y),
                            line,
                            fontsize=font_size,
                            fontname=fontname,
                            color=color
                        )
                
                # Update current_y consistently for all lines
                # Template-specific line spacing: 1.1 for large/logo, 1.2 for standard
                if template_type in ["large", "large_eco", "large_nonaccredited", "logo", "logo_nonaccredited", "logo_other", "logo_other_nonaccredited"]:
                    current_y += font_size * 1.1  # Tight spacing for large/logo templates
                else:  # standard templates
                    current_y += font_size * 1.2  # Loose spacing for standard templates

            # Print font size for Scope
            print(f"📏 [SOFTCOPY] Scope: {font_size}pt")

    # Render optional fields with dynamic positioning
    optional_fields_result = render_optional_fields(
        page=page,
        values=values,
        key_coords=optional_key_coordinates,
        value_coords=optional_value_coordinates,
        font_settings=optional_font_settings
    )
    
    # ✅ ADDED: Extract Issue Date coordinates for dynamic revision positioning
    issue_date_coords = optional_fields_result.get("issue_date_coords")
    if issue_date_coords:
        print(f"🔍 [DYNAMIC] Retrieved Issue Date coordinates: {issue_date_coords}")
    else:
        print(f"⚠️ [DYNAMIC] Issue Date coordinates not found - using fallback")

    # ✅ ADDED: Shared Logo Functions for Phase 5
    def insert_logo_into_pdf(page, logo_file, logo_rect):
        """
        Insert logo into PDF with smart positioning
        """
        try:
            # Convert logo file to image
            logo_image = convert_file_to_image(logo_file)
            
            # Use smart positioning logic
            insert_logo_with_smart_positioning(page, logo_image, logo_rect)
            
            print(f"✅ [LOGO] Logo inserted successfully: {logo_file.filename if hasattr(logo_file, 'filename') else 'unknown'}")
        except Exception as e:
            print(f"❌ [LOGO] Failed to insert logo: {e}")

    def convert_file_to_image(file):
        """
        Convert uploaded file to PIL Image
        """
        try:
            from PIL import Image
            import io
            
            if hasattr(file, 'file'):
                # Reset file pointer
                file.file.seek(0)
                # Read file content
                file_content = file.file.read()
                # Convert to PIL Image
                logo_image = Image.open(io.BytesIO(file_content))
                return logo_image
            else:
                raise ValueError("File object has no file attribute")
        except Exception as e:
            print(f"❌ [LOGO] Error converting file to image: {e}")
            raise

    def insert_logo_with_smart_positioning(page, logo_image, logo_rect):
        """
        Smart logo insertion that handles different aspect ratios
        """
        try:
            # Convert PIL Image to bytes for PyMuPDF
            img_byte_arr = io.BytesIO()
            logo_image.save(img_byte_arr, format='PNG')
            img_byte_arr = img_byte_arr.getvalue()
            
            # Insert logo into PDF at specified coordinates
            page.insert_image(logo_rect, stream=img_byte_arr)
            print(f"🔍 [SOFTCOPY] Logo inserted successfully at coordinates: {logo_rect}")
        except Exception as e:
            print(f"❌ [SOFTCOPY] Error inserting logo: {e}")

    # ✅ UPDATED: Insert logo if available and using logo template
    if logo_image and template_type == "logo":
        try:
            # Get logo coordinates from logo_coords
            logo_rect = logo_coords.get("logo")
            if logo_rect:
                # Use the new shared logo function
                insert_logo_with_smart_positioning(page, logo_image, logo_rect)
            else:
                print("⚠️ [SOFTCOPY] Logo coordinates not found in logo_coords")
        except Exception as logo_insert_error:
            print(f"❌ [SOFTCOPY] Error inserting logo: {logo_insert_error}")

    # ✅ ADDED: Render Revision field with dynamic positioning
    if revision and revision.strip():
        try:
            # ✅ DYNAMIC: Use Issue Date coordinates if available, otherwise fallback to static
            if issue_date_coords:
                # Use dynamic coordinates based on actual Issue Date position
                revision_x = 446  # Keep same X coordinates as before
                revision_y = issue_date_coords.y0  # Use Issue Date Y position
                print(f"🔍 [DYNAMIC] Using dynamic revision coordinates: ({revision_x}, {revision_y})")
            else:
                # Fallback to static coordinates
                revision_x = revision_coordinates.x0
                revision_y = revision_coordinates.y0
                print(f"🔍 [DYNAMIC] Using fallback revision coordinates: ({revision_x}, {revision_y})")
            
            # Insert revision text at specified coordinates
            page.insert_text(
                (revision_x, revision_y),
                revision,
                fontsize=revision_font_settings["fontsize"],
                fontname=revision_font_settings["fontname"],
                color=revision_font_settings["color"]
            )
            print(f"✅ [DYNAMIC] Revision field rendered successfully at ({revision_x}, {revision_y})")
        except Exception as e:
            print(f"⚠️ [SOFTCOPY] Warning: Could not render Revision field: {e}")
    else:
        print(f"🔍 [SOFTCOPY] No Revision field to render (empty or missing)")

    # Success message with optional fields summary
    optional_fields_list = [
        'Certificate Number', 
        'Initial Registration Date',
        'Original Issue Date', 
        'Issue Date', 
        'Surveillance/ Expiry Date',
        'Surveillance Due Date',
        'Expiry Date',
        'Recertification Date'
    ]
    optional_fields_count = len([f for f in optional_fields_list if values.get(f, '').strip()])
    
    # ✅ ADDED: Process Extra Line field
    extra_line_text = values.get("Extra Line", "").strip()
    if extra_line_text:
        print(f"🔍 [SOFTCOPY] Processing Extra Line: '{extra_line_text}'")
        
        # Calculate Extra Line position (0pt gap below scope)
        # Use the same scope_rect that was used for scope rendering
        if template_type in ["large", "large_eco", "large_nonaccredited"]:
            scope_rect = coords["Scope"]  # Single rectangle for large templates
        else:
            # For standard/logo templates, use the stored original coordinates
            if estimated_lines >= 24:
                scope_rect = original_scope_coords["long"]
            else:
                scope_rect = original_scope_coords["short"]
        
        extra_line_y = scope_rect.y1  # 0pt gap - directly below scope
        
        # Create Extra Line rectangle
        extra_line_rect = fitz.Rect(
            scope_rect.x0,      # Same x0 as scope
            extra_line_y,       # 0pt gap - directly below scope
            scope_rect.x1,      # Same x1 as scope  
            extra_line_y + 10   # 10pt height for text
        )
        
        # Render Extra Line text with center alignment and bold font
        try:
            if '**' in extra_line_text or '__' in extra_line_text:
                # Use mixed format rendering for bold text with center alignment
                render_mixed_format_text(page, (extra_line_rect.x0, extra_line_rect.y0), extra_line_text, 12, (0, 0, 0), extra_line_rect.width)
            else:
                # Center-aligned bold text rendering
                center_x = (extra_line_rect.x0 + extra_line_rect.x1) / 2
                font_obj = fitz.Font(fontname="Times-Bold")
                text_width = font_obj.text_length(extra_line_text, 12)
                start_x = center_x - text_width / 2
                
                page.insert_text(
                    (start_x, extra_line_rect.y0),
                    extra_line_text,
                    fontsize=12,
                    fontname="Times-Bold",
                    color=(0, 0, 0)
                )
            
            print(f"🔍 [SOFTCOPY] Extra Line rendered at: {extra_line_rect}")
        except Exception as extra_line_error:
            print(f"❌ [SOFTCOPY] Error rendering Extra Line: {extra_line_error}")
            print(f"🔍 [SOFTCOPY] Extra Line coordinates: {extra_line_rect}")
            print(f"🔍 [SOFTCOPY] Extra Line text: '{extra_line_text}'")
            # Continue without Extra Line rather than failing completely
    else:
        print(f"🔍 [SOFTCOPY] No Extra Line - skipping")
    
    # Generate and add QR code with certification information
    
    # ✅ FIXED: Validate and format dates before QR code generation
    def format_date_for_qr(date_string):
        """Format date string to ensure it's valid for QR code"""
        if not date_string or date_string.strip() == '':
            return ''
        
        # If date is already in YYYY-MM-DD format, return as-is
        if '-' in date_string and len(date_string.split('-')) == 3:
            return date_string
        
        # If date is in DD/MM/YYYY format, convert to YYYY-MM-DD
        if '/' in date_string and len(date_string.split('/')) == 3:
            try:
                parts = date_string.split('/')
                day, month, year = parts[0], parts[1], parts[2]
                # Validate parts are numbers
                if day.isdigit() and month.isdigit() and year.isdigit():
                    return f"{year}-{month}-{day}"
            except (ValueError, IndexError):
                pass
        
        # If conversion fails, return original (will be handled by verification page)
        return date_string
    
    # ✅ ADDED: Get expiry date from surveillance group (same logic as optional fields)
    def get_expiry_date_for_qr(values):
        """Get expiry date from surveillance group fields for QR code"""
        surveillance_group_fields = [
            "Surveillance/ Expiry Date",
            "Surveillance Due Date", 
            "Expiry Date"
        ]
        
        for field in surveillance_group_fields:
            if field in values and values[field]:
                print(f"🔍 [SOFTCOPY] QR Code using surveillance field: '{field}' = '{values[field]}'")
                return values[field]
        return ""
    
    # Prepare certification data for QR code with validated dates
    cert_data = {
        "certification_body": "Americo",  # Always Americo
        "accreditation_body": "UAF",  # Always UAF
        "certificate_number": values.get("Certificate Number", ""),
        "company_name": values.get("Company Name", ""),
        "certificate_standard": values.get("ISO Standard", ""),
        "issue_date": format_date_for_qr(values.get("Issue Date", "")),
        "expiry_date": format_date_for_qr(get_expiry_date_for_qr(values))  # ✅ FIXED: Use surveillance group logic
    }
    
    # ✅ ADDED: Log the formatted dates for debugging
    
    
    try:
        # Generate QR code with larger size for better space utilization
        qr_image = generate_certification_qr_code(cert_data, size=400)
        
        # Debug: Show what data is being encoded
        qr_text = "\n".join([f"{key}: {value}" for key, value in cert_data.items() if value])
        
        
        # ✅ ADDED: Template-specific QR code coordinates
        
        # ✅ UPDATED: Large template QR code coordinates (using x=488.7)
        if template_type in ["large", "large_eco", "large_nonaccredited"]:
            qr_x = 488.7  # Use same X position as standard templates
            qr_y = 541    # Keep same Y position
            qr_width = 78.7   # Keep same width
            qr_height = 74    # Keep same height
        else:  # standard template
            # ✅ UPDATED: Standard template QR code coordinates (expanded to remove white spaces)
            qr_x = 488.7  # Move left by 10pt to expand width
            qr_y = 514    # Updated Y position as requested
            qr_width = 78.7   # Increase width by 10pt (68.7 + 10)
            qr_height = 74    # Increase height by 10pt (64 + 10)
        
        # Add QR code to PDF at template-specific coordinates
        add_qr_code_to_pdf(
            pdf_document=doc,
            qr_image=qr_image,
            x=qr_x,
            y=qr_y,
            width=qr_width,
            height=qr_height
        )
        
        
        
    except Exception as e:
        print(f"⚠️ [SOFTCOPY] Warning: Could not add QR code: {e}")
        print(f"⚠️ [SOFTCOPY] PDF will be generated without QR code")

    doc.save(output_pdf_path)
    doc.close()
    
    print(f"✅ [SOFTCOPY] Soft copy PDF generated successfully: {output_pdf_path}")
    
    # Return tracking information
    return {
        "success": True,
        "output_path": output_pdf_path,
        "overflow_warnings": overflow_warnings,
        "template_type": template_type
    }


