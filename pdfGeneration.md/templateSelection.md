# Template Selection Logic Documentation

This document provides a comprehensive overview of the template selection logic for all three PDF generation systems: Certificate, Softcopy, and Printable.

## File References

- **Main Logic**: `services/pdf-service/main.py`
- **Certificate Generation**: `services/pdf-service/rise/generate_certificate.py`
- **Softcopy Generation**: `services/pdf-service/rise/generate_softCopy.py`
- **Printable Generation**: `services/pdf-service/rise/generate_printable.py`

---

## 1. CERTIFICATE Template Selection Logic

**Source**: `services/pdf-service/main.py` (lines 240-331)

### Priority Order (Highest to Lowest):

### 1.1 EXTRA LINE OVERRIDE (Highest Priority)
When `Extra Line` is present, it **forces large template selection** regardless of content length:

| **Condition** | **Template Name** | **template_type** |
|---------------|-------------------|-------------------|
| Extra Line + Country="Other" + Accreditation="no" | `templateDraftLargeNonAccOther` | `large_nonaccredited_other` |
| Extra Line + Country="Other" + Size="high" | `template_draft_large_other` | `large_other` |
| Extra Line + Country="Other" + Size≠"high" | `template_draft_large_other_eco` | `large_other_eco` |
| Extra Line + Default Country + Logo exists + Accreditation="no" | `templateDraftLogoNonAcc` | `logo_nonaccredited` |
| Extra Line + Default Country + Logo exists + Accreditation="yes" | `templateDraftLogo` | `logo` |
| Extra Line + Default Country + Accreditation="no" | `templateDraftLargeNonAcc` | `large_nonaccredited` |
| Extra Line + Default Country + Size="high" | `template_draft_large` | `large` |
| Extra Line + Default Country + Size≠"high" | `templateDraftLargeEco` | `large_eco` |

### 1.2 NORMAL TEMPLATE SELECTION (When No Extra Line)

#### A. Country = "Other" Templates:

| **Condition** | **Content Length** | **Template Name** | **template_type** |
|---------------|-------------------|-------------------|-------------------|
| Country="Other" + Logo exists + Accreditation="no" | Any | `templateDraftLogoNonAccOther` | `logo_nonaccredited_other` |
| Country="Other" + Logo exists + Accreditation="yes" | Any | `templateDraftLogoOther` | `logo_other` |
| Country="Other" + Accreditation="no" | ≤11 lines | `templateDraftStandardNonAccOther` | `standard_nonaccredited_other` |
| Country="Other" + Accreditation="no" | >11 lines | `templateDraftLargeNonAccOther` | `large_nonaccredited_other` |
| Country="Other" + Size="high" + Accreditation≠"no" | ≤11 lines | `template_draft_other` | `standard_other` |
| Country="Other" + Size="high" + Accreditation≠"no" | >11 lines | `template_draft_large_other` | `large_other` |
| Country="Other" + Size≠"high" + Accreditation≠"no" | ≤11 lines | `template_draft_other_eco` | `standard_other_eco` |
| Country="Other" + Size≠"high" + Accreditation≠"no" | >11 lines | `template_draft_large_other_eco` | `large_other_eco` |

#### B. Default Country Templates:

| **Condition** | **Content Length** | **Template Name** | **template_type** |
|---------------|-------------------|-------------------|-------------------|
| Logo exists in lookup + Accreditation="no" | Any | `templateDraftLogoNonAcc` | `logo_nonaccredited` |
| Logo exists in lookup + Accreditation="yes" | Any | `templateDraftLogo` | `logo` |
| Logo specified but not found | Any | Falls through to regular logic | - |
| Accreditation="no" | ≤11 lines | `templateDraftStandardNonAcc` | `standard_nonaccredited` |
| Accreditation="no" | >11 lines | `templateDraftLargeNonAcc` | `large_nonaccredited` |
| Size="high" + Accreditation≠"no" | ≤11 lines | `template_draft` | `standard` |
| Size="high" + Accreditation≠"no" | >11 lines | `template_draft_large` | `large` |
| Size≠"high" + Accreditation≠"no" | ≤11 lines | `templateDraftStandardEco` | `standard_eco` |
| Size≠"high" + Accreditation≠"no" | >11 lines | `templateDraftLargeEco` | `large_eco` |

---

## 2. SOFTCOPY Template Selection Logic

**Source**: `services/pdf-service/main.py` (lines 598-690)

### Priority Order (Highest to Lowest):

### 2.1 EXTRA LINE OVERRIDE (Highest Priority)
When `Extra Line` is present, it **forces large template selection** regardless of content length:

| **Condition** | **Template Name** | **template_type** |
|---------------|-------------------|-------------------|
| Extra Line + Country="Other" + Logo exists + Accreditation="no" | `templateSoftCopyLogoOtherNonAcc` | `logo_other_nonaccredited` |
| Extra Line + Country="Other" + Logo exists + Accreditation="yes" | `templateSoftCopyLogoOther` | `logo_other` |
| Extra Line + Country="Other" + Accreditation="no" | `templateSoftCopyLargeNonAccOther` | `large_nonaccredited_other` |
| Extra Line + Country="Other" + Size="high" | `template_softCopy_large_other` | `large_other` |
| Extra Line + Country="Other" + Size≠"high" | `template_softCopy_large_other_eco` | `large_other_eco` |
| Extra Line + Default Country + Logo exists + Accreditation="no" | `templateSoftCopyLogoNonAcc` | `logo_nonaccredited` |
| Extra Line + Default Country + Logo exists + Accreditation="yes" | `templateSoftCopyLogo` | `logo` |
| Extra Line + Default Country + Accreditation="no" | `templateSoftCopyLargeNonAcc` | `large_nonaccredited` |
| Extra Line + Default Country + Size="high" | `template_SoftCopy_large` | `large` |
| Extra Line + Default Country + Size≠"high" | `templateSoftCopyLargeEco` | `large_eco` |

### 2.2 NORMAL TEMPLATE SELECTION (When No Extra Line)

#### A. Country = "Other" Templates:

| **Condition** | **Content Length** | **Template Name** | **template_type** |
|---------------|-------------------|-------------------|-------------------|
| Country="Other" + Logo exists + Accreditation="no" | Any | `templateSoftCopyLogoOtherNonAcc` | `logo_other_nonaccredited` |
| Country="Other" + Logo exists + Accreditation="yes" | Any | `templateSoftCopyLogoOther` | `logo_other` |
| Country="Other" + Accreditation="no" | ≤11 lines | `templateSoftCopyStandardNonAccOther` | `standard_nonaccredited_other` |
| Country="Other" + Accreditation="no" | >11 lines | `templateSoftCopyLargeNonAccOther` | `large_nonaccredited_other` |
| Country="Other" + Size="high" + Accreditation≠"no" | ≤11 lines | `template_softCopy_other` | `standard_other` |
| Country="Other" + Size="high" + Accreditation≠"no" | >11 lines | `template_softCopy_large_other` | `large_other` |
| Country="Other" + Size≠"high" + Accreditation≠"no" | ≤11 lines | `template_softCopy_other_eco` | `standard_other_eco` |
| Country="Other" + Size≠"high" + Accreditation≠"no" | >11 lines | `template_softCopy_large_other_eco` | `large_other_eco` |

#### B. Default Country Templates:

| **Condition** | **Content Length** | **Template Name** | **template_type** |
|---------------|-------------------|-------------------|-------------------|
| Logo exists in lookup + Accreditation="no" | Any | `templateSoftCopyLogoNonAcc` | `logo_nonaccredited` |
| Logo exists in lookup + Accreditation="yes" | Any | `templateSoftCopyLogo` | `logo` |
| Logo specified but not found | Any | Falls through to regular logic | - |
| Accreditation="no" | ≤11 lines | `templateSoftCopyStandardNonAcc` | `standard_nonaccredited` |
| Accreditation="no" | >11 lines | `templateSoftCopyLargeNonAcc` | `large_nonaccredited` |
| Size="high" + Accreditation≠"no" | ≤11 lines | `template_softCopy` | `standard` |
| Size="high" + Accreditation≠"no" | >11 lines | `template_SoftCopy_large` | `large` |
| Size≠"high" + Accreditation≠"no" | ≤11 lines | `templateSoftCopyStandardEco` | `standard_eco` |
| Size≠"high" + Accreditation≠"no" | >11 lines | `templateSoftCopyLargeEco` | `large_eco` |

---

## 3. PRINTABLE Template Selection Logic

**Source**: `services/pdf-service/main.py` (lines 921-1025)

### Priority Order (Highest to Lowest):

### 3.1 EXTRA LINE OVERRIDE (Highest Priority)
When `Extra Line` is present, it **forces large template selection** regardless of content length:

| **Condition** | **Template Name** | **template_type** |
|---------------|-------------------|-------------------|
| Extra Line + Country="Other" + Logo exists + Accreditation="no" | `templatePrintableLogoOtherNonAcc` | `logo_other_nonaccredited` |
| Extra Line + Country="Other" + Logo exists + Accreditation="yes" | `templatePrintableLogoOther` | `logo_other` |
| Extra Line + Country="Other" + Accreditation="no" | `templateprintableLargeOtherNonAcc` | `large_other_nonaccredited` |
| Extra Line + Country="Other" + Size="high" | `templateprintableLargeOther` | `large_other` |
| Extra Line + Country="Other" + Size≠"high" | `templateprintableLargeOtherEco` | `large_other_eco` |
| Extra Line + Default Country + Logo exists + Accreditation="no" | `templatePrintableLogoNonAcc` | `logo_nonaccredited` |
| Extra Line + Default Country + Logo exists + Accreditation="yes" | `templatePrintableLogo` | `logo` |
| Extra Line + Default Country + Accreditation="no" | `templateprintableLargeNonAcc` | `large_nonaccredited` |
| Extra Line + Default Country + Size="high" | `templateprintableLarge` | `large` |
| Extra Line + Default Country + Size≠"high" | `templateprintableLargeEco` | `large_eco` |

### 3.2 NORMAL TEMPLATE SELECTION (When No Extra Line)

#### A. Country = "Other" Templates:

| **Condition** | **Content Length** | **Template Name** | **template_type** |
|---------------|-------------------|-------------------|-------------------|
| Country="Other" + Logo exists + Accreditation="no" | Any | `templatePrintableLogoOtherNonAcc` | `logo_other_nonaccredited` |
| Country="Other" + Logo exists + Accreditation="yes" | Any | `templatePrintableLogoOther` | `logo_other` |
| Country="Other" + Accreditation="no" | ≤11 lines | `templatePrintableOtherNonAcc` | `standard_other_nonaccredited` |
| Country="Other" + Accreditation="no" | >11 lines | `templateprintableLargeOtherNonAcc` | `large_other_nonaccredited` |
| Country="Other" + Size="high" + Accreditation≠"no" | ≤11 lines | `templatePrintableStandardOther` | `standard_other` |
| Country="Other" + Size="high" + Accreditation≠"no" | >11 lines | `templateprintableLargeOther` | `large_other` |
| Country="Other" + Size≠"high" + Accreditation≠"no" | ≤11 lines | `templatePrintableStandardOtherEco` | `standard_other_eco` |
| Country="Other" + Size≠"high" + Accreditation≠"no" | >11 lines | `templateprintableLargeOtherEco` | `large_other_eco` |

#### B. Default Country Templates:

| **Condition** | **Content Length** | **Template Name** | **template_type** |
|---------------|-------------------|-------------------|-------------------|
| Logo exists in lookup + Accreditation="no" | Any | `templatePrintableLogoNonAcc` | `logo_nonaccredited` |
| Logo exists in lookup + Accreditation="yes" | Any | `templatePrintableLogo` | `logo` |
| Logo specified but not found | Any | Falls through to regular logic | - |
| Accreditation="no" | ≤11 lines | `templatePrintableStandardNonAcc` | `standard_nonaccredited` |
| Accreditation="no" | >11 lines | `templateprintableLargeNonAcc` | `large_nonaccredited` |
| Size="high" + Accreditation≠"no" | ≤11 lines | `templatePrintableStandard` | `standard` |
| Size="high" + Accreditation≠"no" | >11 lines | `templateprintableLarge` | `large` |
| Size≠"high" + Accreditation≠"no" | ≤11 lines | `templatePrintableStandardEco` | `standard_eco` |
| Size≠"high" + Accreditation≠"no" | >11 lines | `templateprintableLargeEco` | `large_eco` |

---

## 4. Key Parameters

### 4.1 Common Parameters (All Systems)
- **Content Length**: `estimated_lines = max(1, (scope_words * 8) // 60)`
- **Threshold**: 11 lines (≤11 = standard, >11 = large)
- **Extra Line**: Forces large template selection
- **Logo**: Takes priority over all other parameters (except Extra Line)
- **Country**: "Other" vs Default country templates
- **Accreditation**: "No" vs "Yes" templates
- **Size**: "High" vs Low/Blank templates

### 4.2 Template Selection Flow (All Systems)
```
1. Check Extra Line → If present, force large template
2. Check Country → If "Other", use other country templates
3. Check Logo → If exists, use logo template (4 variants based on Country + Accreditation)
4. Check Accreditation → If "no", use non-accredited templates
5. Check Size → If "high", use standard templates
6. Default → Use eco templates
```

---

## 5. Logo Template Variants Summary

| **System** | **Logo Templates** | **Status** |
|------------|-------------------|------------|
| **Certificate** | `templateDraftLogo`, `templateDraftLogoNonAcc`, `templateDraftLogoOther`, `templateDraftLogoNonAccOther` | ✅ **COMPLETED** |
| **Softcopy** | `templateSoftCopyLogo`, `templateSoftCopyLogoNonAcc`, `templateSoftCopyLogoOther`, `templateSoftCopyLogoOtherNonAcc` | ✅ **COMPLETED** |
| **Printable** | `templatePrintableLogo`, `templatePrintableLogoNonAcc`, `templatePrintableLogoOther`, `templatePrintableLogoOtherNonAcc` | ✅ **COMPLETED** |

### 5.1 Logo Template Logic
- **Logo templates take priority** over all other parameters (except Extra Line)
- **No content length differentiation** - logo templates work for any content length
- **No size differentiation** - logo templates work for any size (high/low/blank)
- **Country and Accreditation differentiation** - 4 different logo templates based on these parameters

---

## 6. Implementation Files Updated

### 6.1 Main Logic (`services/pdf-service/main.py`)
- **Certificate**: Lines 240-331
- **Softcopy**: Lines 598-690  
- **Printable**: Lines 921-1025

### 6.2 Generation Files
- **Certificate**: `services/pdf-service/rise/generate_certificate.py` (lines 446, 478, 551)
- **Softcopy**: `services/pdf-service/rise/generate_softCopy.py` (lines 694, 879)
- **Printable**: `services/pdf-service/rise/generate_printable.py` (lines 699)

### 6.3 Changes Made
1. **Template Type Selection**: Added support for new logo template types
2. **Scope Layout Logic**: Updated to include new logo template types in dynamic coordinate selection
3. **Extra Line Processing**: Updated to handle new logo template types
4. **Logo Insertion Logic**: Updated to handle new logo template types

---

## 7. Template Naming Convention

### 7.1 Certificate Templates
- **Base**: `templateDraft`
- **Logo**: `templateDraftLogo`
- **Non-Accredited**: `templateDraftLogoNonAcc`
- **Other Country**: `templateDraftLogoOther`
- **Other Country Non-Accredited**: `templateDraftLogoNonAccOther`

### 7.2 Softcopy Templates
- **Base**: `templateSoftCopy`
- **Logo**: `templateSoftCopyLogo`
- **Non-Accredited**: `templateSoftCopyLogoNonAcc`
- **Other Country**: `templateSoftCopyLogoOther`
- **Other Country Non-Accredited**: `templateSoftCopyLogoOtherNonAcc`

### 7.3 Printable Templates
- **Base**: `templatePrintable`
- **Logo**: `templatePrintableLogo`
- **Non-Accredited**: `templatePrintableLogoNonAcc`
- **Other Country**: `templatePrintableLogoOther`
- **Other Country Non-Accredited**: `templatePrintableLogoOtherNonAcc`

---

## 8. Certification Code Logic

### 8.1 Overview
The certification code logic maps ISO standards to specific certification codes (CM-MS-XXXX format) and renders them on certificates with different positioning based on accreditation status.

### 8.2 ISO Standards Code Mapping
```python
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
```

### 8.3 Certification Code Positioning Logic

| **Accreditation Status** | **X-Coordinates** | **Y-Coordinates** | **Position** |
|-------------------------|-------------------|-------------------|--------------|
| **Accredited** (`accreditation != "no"`) | 253-285 | 757-762 | **Standard Position** |
| **Non-Accredited** (`accreditation = "no"`) | 300-332 | 757-762 | **Moved Right (+47pt)** |

### 8.4 Implementation Details
- **Font**: 5pt Helvetica (`helv`)
- **Color**: Black (0, 0, 0)
- **Position**: Below ISO Standard text
- **Logic**: Always renders certification code, but uses different x-coordinates based on accreditation status
- **Fallback**: If no certification code found, skips rendering gracefully

### 8.5 Files Updated
- **Certificate**: `services/pdf-service/rise/generate_certificate.py` (lines 1667-1732)
- **Softcopy**: `services/pdf-service/rise/generate_softCopy.py` (lines 1343-1375)
- **Printable**: `services/pdf-service/rise/generate_printable.py` (lines 1467-1501)

### 8.6 Key Changes Made
1. **Removed hiding logic**: Certification codes are no longer hidden for non-accredited certificates
2. **Added coordinate differentiation**: Non-accredited certificates use different x-coordinates (moved right by 47pt)
3. **Maintained consistency**: All three generation systems use identical logic
4. **Preserved functionality**: All existing features remain intact

---

*Last Updated: Template selection logic implementation completed for all three PDF generation systems with proper Country and Accreditation differentiation for logo templates. Certification code logic updated to use different coordinates for non-accredited certificates instead of hiding them.*
