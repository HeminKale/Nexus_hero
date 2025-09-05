# Deployment Issues Resolution Guide

## Issues Resolved

### 1. **500 Internal Server Error - Soft Copy Generation**

**Problem:**
- Frontend was sending JSON data with unescaped `\r\n` (Windows line break) characters
- Python service couldn't parse the malformed JSON, causing `SyntaxError: Bad escaped character in JSON at position 8`
- Error: `Invalid JSON data format`

**Root Cause:**
- Excel data contained Windows line breaks (`\r\n`) that weren't properly escaped before `JSON.stringify()`
- Frontend component `softCopyGeneratorExcel.tsx` was sending raw data without cleaning

**Solution:**
- Added data cleaning in `softCopyGeneratorExcel.tsx` before JSON serialization:
  ```typescript
  const cleanJsonData = Object.fromEntries(
    Object.entries(jsonData).map(([key, value]) => [
      key,
      typeof value === 'string' 
        ? value.replace(/\r\n/g, ' ').replace(/\r/g, ' ').replace(/\n/g, ' ').trim()
        : value
    ])
  );
  ```

### 2. **404 Not Found Error - Certificate Generation**

**Problem:**
- Frontend was calling `/api/pdf/generate` endpoint
- Nginx was configured to route `/api/pdf/*` directly to Python service (port 8000)
- Python service only had `/generate-certificate` endpoint, not `/generate`
- Result: 404 Not Found

**Root Cause:**
- Mismatch between frontend API calls and actual Python endpoints
- Nginx proxy configuration was correct, but frontend was calling wrong endpoint

**Solution:**
- Updated both frontend components to call correct endpoint:
  - `CertificateGeneratorTab.tsx`: Changed from `/api/pdf/generate` to `/api/pdf/generate-certificate`
  - `CertificateGeneratorTabExcel.tsx`: Changed from `/api/pdf/generate` to `/api/pdf/generate-certificate`

### 3. **Authentication Token Mismatch**

**Problem:**
- Python service expected `INTERNAL_TOKEN=None` but was receiving string `"None"`
- Token comparison was failing: `"None" != None`

**Root Cause:**
- Environment variable loaded as string `"None"` from `.env.local`
- String comparison logic wasn't handling this case

**Solution:**
- Updated authentication logic in `main.py`:
  ```python
  expected_token = INTERNAL_TOKEN if INTERNAL_TOKEN != "None" else None
  received_token = token if token != "None" else None
  if received_token != expected_token:
      # Handle authentication failure
  ```

## Deployment Care Instructions

### 1. **Environment Variables**
- Always ensure `.env.local` exists in `/root/Nexus/.env.local`
- Set `INTERNAL_TOKEN=None` (not `"None"` as string)
- Set `PDF_SERVICE_URL=http://157.173.222.165:8000` (VPS IP, not localhost)
- Restart services after environment changes: `pm2 restart nexus-app --update-env`

### 2. **API Endpoint Mapping**
- **Frontend → Nginx → Python Service:**
  - `/api/pdf/generate-softcopy` → Python `/generate-softcopy`
  - `/api/pdf/generate-certificate` → Python `/generate-certificate`
  - `/api/pdf/generate-printable` → Python `/generate-printable`
- **Never use `/api/pdf/generate`** - this endpoint doesn't exist in Python service

### 3. **Data Cleaning Requirements**
- Always clean Excel data before JSON serialization:
  - Remove `\r\n`, `\r`, `\n` characters
  - Trim whitespace
  - Handle empty strings properly

### 4. **Deployment Steps**
1. **Update Code:**
   ```bash
   # Copy updated files to server
   scp "local/path/file.tsx" root@157.173.222.165:/root/Nexus/app/path/file.tsx
   ```

2. **Rebuild Next.js:**
   ```bash
   ssh root@157.173.222.165 "cd /root/Nexus && npm run build"
   ```

3. **Restart Services:**
   ```bash
   ssh root@157.173.222.165 "pm2 restart nexus-app --update-env && pm2 restart pdf-service"
   ```

4. **Verify Endpoints:**
   ```bash
   # Test public endpoints return 405 (not 404)
   curl -s -o /dev/null -w '%{http_code}' https://americoworld.com/api/pdf/generate-certificate
   curl -s -o /dev/null -w '%{http_code}' https://americoworld.com/api/pdf/generate-softcopy
   ```

### 5. **Nginx Configuration**
- **Current Setup:** `/api/pdf/*` routes to Python service (port 8000)
- **Other routes:** Route to Next.js app (port 3000)
- **No changes needed** - configuration is correct

### 6. **Python Service Management**
- Always activate virtual environment: `source .venv/bin/activate`
- Use PM2 with environment variables: `INTERNAL_TOKEN=None pm2 start main.py --name pdf-service`
- Check logs: `pm2 logs pdf-service`

### 7. **Common Pitfalls to Avoid**
- ❌ Don't use `localhost:8000` in production `.env.local`
- ❌ Don't call `/api/pdf/generate` (doesn't exist)
- ❌ Don't skip data cleaning for Excel imports
- ❌ Don't forget to rebuild Next.js after code changes
- ❌ Don't forget to restart services after environment changes

### 8. **Testing Checklist**
- [ ] Public endpoints return 405 (not 404)
- [ ] Authentication logs show "Tokens match: True"
- [ ] Excel data is cleaned before JSON serialization
- [ ] Both soft copy and certificate generation work
- [ ] PM2 services are online and healthy

### 9. **File Locations**
- **Frontend:** `/root/Nexus/app/commonfiles/core/components/custom/`
- **Python Service:** `/root/Nexus/services/pdf-service/`
- **Environment:** `/root/Nexus/.env.local`
- **Nginx Config:** `/etc/nginx/sites-available/nexus`

### 10. **Emergency Rollback**
- If issues occur, revert to previous working commit
- Restart all services: `pm2 restart all`
- Check logs: `pm2 logs --lines 50`

---

**Last Updated:** January 5, 2025
**Resolved Issues:** 500 Soft Copy Error, 404 Certificate Error, Authentication Token Mismatch
**Status:** ✅ All Issues Resolved
