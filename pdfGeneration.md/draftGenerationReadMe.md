# 📋 **Complete Certificate Generation System Documentation**

## 🏗️ **Project Structure Overview**

```
Craft App - Copy/
├── 📁 app/
│   ├── 📁 api/
│   │   ├── 📁 excel/
│   │   │   └── 📄 parse/route.ts          # Excel file parsing endpoint
│   │   └── 📁 pdf/
│   │       ├── 📄 extract-fields/route.ts  # PDF field extraction endpoint
│   │       └── 📄 generate/route.ts        # PDF generation endpoint
│   └── 📁 commonfiles/
│       └── 📁 core/
│           ├── 📁 components/
│           │   ├── 📁 custom/
│           │   │   ├── 📄 CertificateGeneratorTab.tsx      # Single certificate generation
│   │   │   ├── 📄 CertificateGeneratorTabExcel.tsx        # Bulk Excel processing
│   │   │   └── 📄 certificateSoftCopy.tsx                 # Client management interface
│   │   ├── 📁 Application/
│   │   │   └── 📄 CustomTabRenderer.tsx                   # Dynamic component loader
│   │   └── 📁 settings/
│   │       └── 📄 HomeTab.tsx                             # Tab management UI
│           ├── 📁 lib/
│           │   └── 📄 supabase.ts                         # Supabase client configuration
│           └── 📁 providers/
│               └── 📄 SupabaseProvider.tsx                # Tenant context provider
├── 📁 services/
│   └── 📁 pdf-service/
│       ├── 📄 main.py                                     # FastAPI main application
│       └── 📁 rise/
│           └── 📄 generate_certificate.py                 # Core PDF generation logic
├── 📁 supabase/
│   └── 📁 migrations/
│       ├── 📄 100_add_draft_creation_bridge_function.sql  # Draft creation RPC
│       ├── 📄 120_add_drafts_bridge_function.sql          # Draft reading RPC
│       └── 📄 131_add_client_bridge_function.sql          # Client creation RPC
└── 📄 package.json                                        # Dependencies (jszip, xlsx)
```

---

## 🔧 **Core Components & Their Functions**

### **1. Frontend Components**

#### **📄 `CertificateGeneratorTab.tsx`**
**Purpose:** Single certificate generation interface
**Key Features:**
- Client selection dropdown (from `clients__a` table)
- Certificate type selection
- Word document upload for form fields
- Field extraction and PDF generation
- Individual PDF download

**Data Flow:**
1. User selects client and type
2. Uploads Word form document
3. System extracts form fields via `/api/pdf/extract-fields`
4. Generates PDF via `/api/pdf/generate`
5. Downloads individual certificate

**State Management:**
```typescript
const [selectedClient, setSelectedClient] = useState<string>('');
const [selectedType, setSelectedType] = useState<string>('');
const [formFile, setFormFile] = useState<File | null>(null);
const [extractedFields, setExtractedFields] = useState<any>(null);
```

#### **📄 `CertificateGeneratorTabExcel.tsx`**
**Purpose:** Bulk certificate generation from Excel files
**Key Features:**
- Excel file upload with column normalization
- Template selection toggle (Auto vs Custom)
- Bulk client and draft record creation
- Progress tracking for large datasets
- ZIP file download with all certificates
- **NEW**: Logo file upload support (ZIP/folder)
- **NEW**: Country parameter support
- **NEW**: Enhanced optional fields handling

**Data Flow:**
1. User uploads Excel file with client data
2. User uploads logo files (ZIP or individual files)
3. System parses Excel via `/api/excel/parse`
4. Creates/updates client records via `create_tenant_client()`
5. Creates draft records via `create_tenant_draft()`
6. Generates PDFs for each record with logo matching
7. Bundles all PDFs into ZIP download

**State Management:**
```typescript
const [excelFile, setExcelFile] = useState<File | null>(null);
const [logoFiles, setLogoFiles] = useState<File[]>([]);
const [useCustomTemplate, setUseCustomTemplate] = useState(false);
const [templateFile, setTemplateFile] = useState<File | null>(null);
const [progress, setProgress] = useState<{current: number, total: number, stage: string}>();
```

**Enhanced Column Mapping:**
```typescript
interface ExcelRow {
  "Company Name"?: string;
  "Address"?: string;
  "ISO Standard"?: string;
  "Scope"?: string;
  "Certificate Number"?: string;
  "Original Issue Date"?: string;
  "Issue Date"?: string;
  "Surveillance Date"?: string;
  "Recertification Date"?: string;
  "Size"?: string;                    // "high", "low", or blank
  "Accreditation"?: string;           // "yes", "no", or blank
  "Logo"?: string;                    // filename to match with uploaded logo
  "Country"?: string;                 // "Other" or blank
  // NEW: Optional Fields
  "Initial Registration Date"?: string;
  "Surveillance Due Date"?: string;
  "Expiry Date"?: string;
}
```

---

## 🎯 **Enhanced Template Selection Logic**

### **Template Selection Matrix**

#### **Country = "Other":**
| Size | Accreditation | Logo | Scope Lines | Template Name | Template Type |
|------|---------------|------|-------------|---------------|---------------|
| **"high"** | != "no" | ❌ | ≤11 | `template_draft_other` | `standard_other` |
| **"high"** | != "no" | ❌ | >11 | `template_draft_large_other` | `large_other` |
| **"low"** or **blank** | != "no" | ❌ | ≤11 | `template_draft_other_eco` | `standard_other_eco` |
| **"low"** or **blank"** | != "no" | ❌ | >11 | `template_draft_large_other_eco` | `large_other_eco` |
| **any** | **"no"** | ❌ | ≤11 | `templateDraftStandardNonAccOther` | `standard_nonaccredited_other` |
| **any"** | **"no"** | ❌ | >11 | `templateDraftLargeNonAccOther` | `large_nonaccredited_other` |

#### **Country = blank (Default):**
| Size | Accreditation | Logo | Scope Lines | Template Name | Template Type |
|------|---------------|------|-------------|---------------|---------------|
| **any** | any | ✅ | any | `templateDraftLogo` | `logo` |
| **any** | **"no"** | ❌ | ≤11 | `templateDraftStandardNonAcc` | `standard_nonaccredited` |
| **any** | **"no"** | ❌ | >11 | `templateDraftLargeNonAcc` | `large_nonaccredited` |
| **"high"** | != "no" | ❌ | ≤11 | `template_draft` | `standard` |
| **"high"** | != "no" | ❌ | >11 | `template_draft_large` | `large` |
| **"low"** or **blank"** | != "no" | ❌ | ≤11 | `templateDraftStandardEco` | `standard_eco` |
| **"low"** or **blank"** | != "no" | ❌ | >11 | `templateDraftLargeEco` | `large_eco` |

---

## 🔤 **ISO Standards Mapping System**

### **ISO Standards Expansion**
The system automatically expands short ISO standard names to full versions:

```python
ISO_STANDARDS_MAPPING = {
    "9001": "ISO 9001:2015 - Quality Management Systems",
    "14001": "ISO 14001:2015 - Environmental Management Systems",
    "45001": "ISO 45001:2018 - Occupational Health and Safety Management Systems",
    "22000": "ISO 22000:2018 - Food Safety Management Systems",
    "27001": "ISO 27001:2022 - Information Security Management Systems",
    "37001": "ISO 37001:2016 - Anti-bribery Management Systems",
    "22301": "ISO 22301:2019 - Business Continuity Management Systems",
    "50001": "ISO 50001:2018 - Energy Management Systems",
    "20001": "ISO 20000-1:2018 - IT Service Management Systems"
}
```

### **ISO Standards Certification Codes**
The system maps ISO standards to specific certification codes:

```python
ISO_STANDARDS_CODES = {
    "9001:2015": "CM-MS-7842",
    "14001:2015": "CM-MS-7836", 
    "45001:2015": "CM-MS-7832",
    "22000:2018": "CM-MS-7822",
    "27001:2022": "CM-MS-7820",
    "37001:2016": "CM-MS-7804",
    "22301:2019": "CM-MS-7807",
    "50001:2018": "CM-MS-7814",
    "20001:2018": "CM-MS-7811"
}
```

**Helper Function:**
```python
def get_iso_standard_code(iso_standard: str) -> str:
    """Get certification code for ISO standard"""
    return ISO_STANDARDS_CODES.get(iso_standard, "")
```

---

## 📝 **Enhanced Optional Fields System**

### **New Field Sequence (8 Fields Total)**
```python
# Field Sequence (from top to bottom)
1. "Certificate Number"           # Always present
2. "Initial Registration Date"     # Optional - not always present
3. "Original Issue Date"          # Always present  
4. "Issue Date"                   # Always present
5. "Surveillance Group"           # Only 1 of 3 fields present:
   - "Surveillance Date"
   - "Surveillance Due Date"      # NEW FIELD
   - "Expiry Date"                # NEW FIELD
6. "Recertification Date"         # Always present
```

### **Surveillance Group Logic**
- **Only 1 field** from the surveillance group will be present at a time
- System automatically detects which field is present and renders it
- Maintains existing missing field handling logic

### **Dynamic Scope Coordinates**
- **When Initial Registration Date is present**: Scope height is reduced by 16 units
- **When Initial Registration Date is NOT present**: Standard scope coordinates are used
- This ensures proper spacing and prevents overlap

### **Coordinate Systems**
```python
# Large Template: 6 field positions
large_optional_key_coordinates = [
    fitz.Rect(362.1, 522, 446.4, 530),  # Row 1: ABCDXXXX
    fitz.Rect(362.1, 538, 446.4, 548),  # Row 2: ABCDXXXX
    fitz.Rect(362.1, 556, 446.4, 566),  # Row 3: 2024-01-01
    fitz.Rect(362.1, 574, 446.4, 584),  # Row 4: 2024-01-01
    fitz.Rect(362.1, 592, 446.4, 602),  # Row 5: 2024-01-01
    fitz.Rect(362.1, 610, 446.4, 620)   # Row 6: 2024-01-01
]

# Standard Template: 6 field positions  
standard_optional_key_coordinates = [
    fitz.Rect(362.1, 499.1, 446.4, 507.1),  # Row 1
    fitz.Rect(362.1, 516.9, 446.4, 524.9),  # Row 2
    fitz.Rect(362.1, 535.1, 446.4, 543.1),  # Row 3
    fitz.Rect(362.1, 553.9, 446.4, 561.9),  # Row 4
    fitz.Rect(362.1, 571.6, 446.4, 579.6),  # Row 5
    fitz.Rect(362.1, 589.3, 446.4, 597.3)   # Row 6
]
```

---

## 🖼️ **Enhanced Logo System**

### **Logo File Handling**
- **Excel Column**: `"Logo"` now accepts **filenames** instead of "yes"/"no"
- **File Upload**: Users can upload a folder or ZIP file containing logos
- **Logo Matching**: System matches Excel filename with uploaded logo file
- **Fallback**: If logo not found, uses regular template selection

### **Logo Upload Methods**
1. **Individual Files**: Upload multiple logo files
2. **ZIP Archive**: Upload ZIP file containing logos
3. **Folder Upload**: Upload entire folder of logo files

### **Logo Processing Flow**
```python
# 1. Extract logo files from form data
logo_files = form_data.getlist('logo_files')

# 2. Create logo lookup dictionary
logo_lookup = {file.name: file for file in logo_files}

# 3. Check if logo filename exists in Excel data
logo_filename = field_data.get("Logo", "").strip()

# 4. If logo found, override template selection
if logo_filename and logo_filename in logo_lookup:
    template_name = "templateDraftLogo"
    template_type = "logo"
```

### **Logo Insertion Functions**
```python
def insert_logo_into_pdf(page, logo_file, logo_rect):
    """Insert logo into PDF with smart positioning"""
    try:
        logo_image = convert_file_to_image(logo_file)
        insert_logo_with_smart_positioning(page, logo_image, logo_rect)
        print(f"✅ [LOGO] Logo inserted successfully: {logo_file.name}")
    except Exception as e:
        print(f"❌ [LOGO] Failed to insert logo: {e}")

def convert_file_to_image(file):
    """Convert uploaded file to PIL Image"""
    # Handles PNG, JPG, JPEG formats
    # Converts to PIL Image for processing

def insert_logo_with_smart_positioning(page, logo_image, logo_rect):
    """Smart logo insertion that handles different aspect ratios"""
    # Maintains aspect ratio
    # Fits within specified rectangle
    # Centers logo appropriately
```

---

## 🎨 **Enhanced Text Formatting System**

### **Font Weight Preservation**
The system preserves bold text formatting using marker-based detection:

```python
def detect_font_weight(text: str) -> str:
    """Detect font weight markers in text"""
    if "**" in text or "__" in text:
        return "bold"
    return "normal"

def get_font_for_text(text: str, base_font: str) -> str:
    """Get appropriate font based on text content"""
    if detect_font_weight(text) == "bold":
        return "Times-Bold"  # Bold font
    return base_font         # Regular font
```

### **Line Break Preservation**
- **Excel `cmd + enter`**: Creates `\n` characters
- **Multiple breaks**: `\n\n` creates blank lines
- **Empty line handling**: Preserves empty lines during word wrapping
- **Professional spacing**: Maintains intended layout from Excel

### **Company Name Dynamic Font Sizing**
```python
# Dynamic font sizing based on line count
company_lines_count = len([line for line in company_processed_lines if line.strip()])

if company_lines_count <= 1:
    company_font_size = 35  # Single line - start with 35pt
else:
    company_font_size = 30  # Multiple lines - start with 30pt

# Still applies auto-reduction to minimum 8pt
while company_font_size >= 8:
    # ... font size calculation logic
```

### **Scope Text Justification**
- **Full Lines**: Get full justification (left to right alignment)
- **Last Line**: Automatically **centered** for balanced appearance
- **Professional Layout**: Creates clean, aligned text blocks
- **Custom Rendering**: Line-by-line control for optimal appearance
- **Justify from Both Margins**: Text is stretched to fill the full width of the text box, creating clean left and right edges
- **Alignment Control**: Uses `fitz.TEXT_ALIGN_JUSTIFY` for professional publication-quality text layout

---

## 📊 **Supabase Template Requirements**

### **Required Template Files (14 total)**
```
Country = "Other" (No Logo):
- templateDraftStandardNonAccOther.pdf
- templateDraftLargeNonAccOther.pdf
- template_draft_other.pdf
- template_draft_large_other.pdf
- template_draft_other_eco.pdf
- template_draft_large_other_eco.pdf

Country = blank (No Logo):
- templateDraftStandardNonAcc.pdf
- templateDraftLargeNonAcc.pdf
- template_draft.pdf
- template_draft_large.pdf
- templateDraftStandardEco.pdf
- templateDraftLargeEco.pdf

Logo Templates (Both Countries):
- templateDraftLogo.pdf
```

### **Template Selection Priority**
1. **Logo Present**: Overrides all other logic, uses logo template
2. **Country = "Other"**: Uses Other-specific base templates
3. **Accreditation = "no"**: Uses non-accredited templates
4. **Size = "high"**: Uses premium templates
5. **Size = blank/low**: Uses eco-friendly templates
6. **Scope Content**: Determines standard vs large template

---

## 🚀 **Key Features Summary**

### **✅ Implemented Features**
- **Enhanced Template Selection**: 5-parameter logic (Scope, Size, Accreditation, Logo, Country)
- **ISO Standards Mapping**: Automatic expansion and certification codes
- **Optional Fields System**: 8-field logic with surveillance group
- **Logo System**: Filename-based matching with ZIP/folder uploads
- **Text Formatting**: Font weight preservation and line break handling
- **Dynamic Font Sizing**: Company name adaptive sizing
- **Text Justification**: Professional scope layout with centered last line
- **Country Support**: "Other" country templates for international use

### **🎯 Benefits**
- **Professional Output**: Publication-quality certificate layout
- **Flexible Input**: Handles various Excel formats and logo types
- **Smart Logic**: Automatic template selection based on content
- **International Ready**: Support for different country requirements
- **Maintainable**: Clean, organized code structure
- **Scalable**: Easy to add new templates and features

---

## 📝 **Usage Examples**

### **Excel Data Example**
```excel
Company Name: Acme Corporation
Address: 123 Business St, City, Country
ISO Standard: 9001
Scope: Quality Management System implementation and maintenance according to ISO 9001:2015 standards including all processes and procedures for continuous improvement
Size: high
Accreditation: yes
Logo: acme_logo.png
Country: Other
Initial Registration Date: 2020-01-15
Surveillance Due Date: 2024-07-15
```

### **Expected Output**
- **Template**: `template_draft_other` (Country = Other, Size = high, no logo)
- **Logo**: Will be inserted if `acme_logo.png` is uploaded
- **Optional Fields**: 6 fields rendered with proper spacing
- **Scope**: Justified text with centered last line
- **Font**: Times New Roman with bold preservation

---

## 🔧 **Technical Implementation Details**

### **Backend Service (`main.py`)**
- **FastAPI**: Python-based backend service
- **Template Selection**: Intelligent logic based on 5 parameters
- **Logo Processing**: File upload handling and lookup creation
- **Field Extraction**: Excel data processing and validation

### **PDF Generation (`generate_certificate.py`)**
- **PyMuPDF**: PDF manipulation and text insertion
- **Font Management**: Custom font registration and usage
- **Logo Insertion**: Smart positioning and aspect ratio handling
- **Text Processing**: Line break preservation and word wrapping

### **Frontend Components**
- **React/Next.js**: Modern UI with drag & drop support
- **Excel Processing**: Client-side parsing and validation
- **File Upload**: Multiple file and ZIP support
- **Progress Tracking**: Real-time generation status

---

## 📚 **API Endpoints**

### **PDF Generation**
- **POST** `/api/pdf/generate` - Certificate generation with logo support
- **POST** `/api/pdf/extract-fields` - Field extraction from Word documents

### **Excel Processing**
- **POST** `/api/excel/parse` - Excel file parsing and validation

---

## 🎉 **Conclusion**

The enhanced certificate generation system now provides:
- **Professional Quality**: Publication-ready PDF output
- **Flexible Input**: Multiple file formats and logo types
- **Smart Logic**: Automatic template selection and field handling
- **International Support**: Country-specific templates and requirements
- **Maintainable Code**: Clean, organized implementation

**Ready for production use with comprehensive template support and enhanced functionality!** 🚀