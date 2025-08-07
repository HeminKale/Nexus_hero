# Deployment & Testing Checklist

## 🚀 **Complete Multi-Tenant CRM Deployment Guide**

This checklist ensures your **Craft App** multi-tenant system is properly deployed and tested before going live.

---

## 📋 **Migration Deployment Sequence**

### **Step 1: Migration 001 - Core Schema & RLS**
```sql
-- Copy and paste the content from:
-- supabase/migrations/001_core_schema_rls.sql
-- into Supabase SQL Editor and run it
```

**✅ Verification:**
- [ ] `system` and `tenant` schemas created
- [ ] All tables created with proper relationships
- [ ] RLS policies enabled on all tables
- [ ] No SQL errors during execution

### **Step 2: Migration 002 - Helper Functions & Triggers**
```sql
-- Copy and paste the content from:
-- supabase/migrations/002_helper_functions_triggers.sql
-- into Supabase SQL Editor and run it
```

**✅ Verification:**
- [ ] All functions created successfully
- [ ] Trigger for `auth.users` created
- [ ] Performance indexes created
- [ ] Function grants applied correctly

### **Step 3: JWT Configuration (Critical!)**
1. **Go to Supabase Dashboard** → **Authentication** → **Settings**
2. **Find**: "JWT Custom Claims Function"
3. **Enter**: `system.jwt_claims`
4. **Save** the settings

**✅ Verification:**
- [ ] JWT Custom Claims Function configured
- [ ] No errors in Supabase dashboard

### **Step 4: Migration 003 - JWT Setup & Dynamic Objects**
```sql
-- Copy and paste the content from:
-- supabase/migrations/003_jwt_setup_dynamic_objects.sql
-- into Supabase SQL Editor and run it
```

**✅ Verification:**
- [ ] JWT claims function created
- [ ] Dynamic object creation functions created
- [ ] All utility functions created
- [ ] Performance indexes and constraints added

### **Step 5: Migration 004 - Permission Sets & Page Layouts**
```sql
-- Copy and paste the content from:
-- supabase/migrations/004_permission_sets_page_layouts.sql
-- into Supabase SQL Editor and run it
```

**✅ Verification:**
- [ ] Permission set functions created
- [ ] Page layout table and functions created
- [ ] All utility functions created
- [ ] Constraints and indexes added

---

## 🧪 **End-to-End Testing Checklist**

### **Test 1: Tenant & User Creation**

#### **1.1 Create Test Tenant**
```sql
-- Create a test tenant
SELECT system.create_tenant('Test Company', 'test-company', 'test.example.com');
```

**Expected Result:** Returns a UUID

#### **1.2 Verify Tenant Creation**
```sql
-- Check tenant was created
SELECT * FROM system.tenants WHERE slug = 'test-company';
```

**Expected Result:** One row with tenant details

### **Test 2: User Sign-Up & JWT**

#### **2.1 Sign Up a Test User**
1. **Go to your Next.js app** (or Supabase Auth UI)
2. **Sign up** with email: `test@example.com`
3. **Verify** the user appears in `auth.users`

#### **2.2 Verify User Mapping**
```sql
-- Check if user was mapped to tenant
SELECT u.*, t.name as tenant_name 
FROM system.users u 
JOIN system.tenants t ON u.tenant_id = t.id 
WHERE u.email = 'test@example.com';
```

**Expected Result:** User mapped to your test tenant

#### **2.3 Test JWT Claims**
```sql
-- Test JWT claims function
SELECT system.jwt_claims();
```

**Expected Result:** `{"tenant_id": "uuid-of-your-tenant"}`

#### **2.4 Verify JWT in Client**
```javascript
// In your Next.js app
const { data } = await supabase.auth.getSession();
console.log('JWT Token:', data.session.access_token);

// Decode at jwt.io to verify it contains:
// {
//   "sub": "user-uuid",
//   "tenant_id": "tenant-uuid",  // ← This should be present!
//   "exp": 1234567890,
//   "iat": 1234567890
// }
```

### **Test 3: RLS & Tenant Isolation**

#### **3.1 Test RLS Isolation**
```sql
-- This should only return data for your tenant
SELECT * FROM tenant.objects;
SELECT * FROM tenant.permission_sets;
```

**Expected Result:** Only data for your tenant (or empty if no data yet)

#### **3.2 Test Cross-Tenant Isolation**
```sql
-- Try to access another tenant's data (should fail)
SELECT * FROM tenant.objects WHERE tenant_id != (auth.jwt()->>'tenant_id')::uuid;
```

**Expected Result:** No data returned (RLS working)

### **Test 4: Dynamic Object Creation**

#### **4.1 Create a Test Object**
```sql
-- Create a test object
SELECT tenant.create_object('Products', 'Products', 'Product catalog');
```

**Expected Result:** Returns object UUID

#### **4.2 Verify Object Creation**
```sql
-- Check object was created
SELECT * FROM tenant.objects WHERE name = 'products__a';
```

**Expected Result:** One row with object details

#### **4.3 Verify Table Creation**
```sql
-- Check if actual table was created
SELECT table_name FROM information_schema.tables 
WHERE table_name = 'products__a' AND table_schema = 'public';
```

**Expected Result:** Table exists

#### **4.4 Test RLS on Dynamic Table**
```sql
-- Test RLS on the new table
SELECT * FROM products__a;
```

**Expected Result:** No data (empty table, but accessible)

### **Test 5: Field Management**

#### **5.1 Add Fields to Object**
```sql
-- Get object ID first
SELECT id FROM tenant.objects WHERE name = 'products__a';

-- Add fields (replace OBJECT_ID with actual UUID)
SELECT tenant.add_field('OBJECT_ID', 'sku', 'SKU', 'text', true);
SELECT tenant.add_field('OBJECT_ID', 'price', 'Price', 'number', false);
SELECT tenant.add_field('OBJECT_ID', 'category', 'Category', 'picklist', false);
```

**Expected Result:** Returns field UUIDs

#### **5.2 Verify Field Creation**
```sql
-- Check fields were created
SELECT * FROM tenant.fields WHERE object_id = 'OBJECT_ID';
```

**Expected Result:** Multiple rows with field details

#### **5.3 Verify Column Creation**
```sql
-- Check if columns were added to table
SELECT column_name FROM information_schema.columns 
WHERE table_name = 'products__a' AND column_name IN ('sku__a', 'price__a', 'category__a');
```

**Expected Result:** Columns exist

### **Test 6: Permission Sets**

#### **6.1 Create Permission Set**
```sql
-- Create a test permission set
SELECT tenant.create_permission_set('Sales Manager', 'Can manage sales objects');
```

**Expected Result:** Returns permission set UUID

#### **6.2 Verify Permission Set**
```sql
-- Check permission set was created
SELECT * FROM tenant.permission_sets WHERE name = 'Sales Manager__a';
```

**Expected Result:** One row with permission set details

#### **6.3 Assign Permission Set to User**
```sql
-- Get user ID and permission set ID
SELECT id FROM system.users WHERE email = 'test@example.com';
SELECT id FROM tenant.permission_sets WHERE name = 'Sales Manager__a';

-- Assign permission set (replace USER_ID and PERM_SET_ID)
SELECT tenant.assign_permission_set_to_user('USER_ID', 'PERM_SET_ID');
```

**Expected Result:** No errors

#### **6.4 Verify Assignment**
```sql
-- Check assignment was created
SELECT * FROM tenant.user_permission_sets WHERE user_id = 'USER_ID';
```

**Expected Result:** One row with assignment details

### **Test 7: Page Layouts**

#### **7.1 Create Page Layout**
```sql
-- Get object ID
SELECT id FROM tenant.objects WHERE name = 'products__a';

-- Create page layout (replace OBJECT_ID)
SELECT tenant.create_page_layout(
    'OBJECT_ID', 
    'Standard Layout', 
    '{"sections": [{"name": "General", "fields": ["name", "sku__a", "price__a"]}]}'::jsonb
);
```

**Expected Result:** Returns layout UUID

#### **7.2 Verify Page Layout**
```sql
-- Check layout was created
SELECT * FROM tenant.page_layouts WHERE name = 'Standard Layout__a';
```

**Expected Result:** One row with layout details

### **Test 8: Data Operations**

#### **8.1 Insert Test Data**
```sql
-- Insert test record
INSERT INTO products__a (name, sku__a, price__a, category__a, tenant_id)
VALUES ('Test Product', 'SKU001', 99.99, 'Electronics', (auth.jwt()->>'tenant_id')::uuid);
```

**Expected Result:** One row inserted

#### **8.2 Query Test Data**
```sql
-- Query the data
SELECT * FROM products__a;
```

**Expected Result:** One row with test data

#### **8.3 Test Tenant Isolation**
```sql
-- Try to insert data for different tenant (should fail)
INSERT INTO products__a (name, sku__a, tenant_id)
VALUES ('Wrong Tenant Product', 'SKU002', '00000000-0000-0000-0000-000000000000');
```

**Expected Result:** Error or no insertion (RLS working)

---

## 🔍 **Advanced Testing Scenarios**

### **Test 9: Multi-User Isolation**

#### **9.1 Create Second User**
1. **Sign up** another user: `user2@example.com`
2. **Verify** they get mapped to the same tenant
3. **Test** they can only see their tenant's data

### **Test 10: Permission Enforcement**

#### **10.1 Test Object Permissions**
```sql
-- Test permission checking
SELECT tenant.check_object_permission('OBJECT_ID', 'read');
SELECT tenant.check_object_permission('OBJECT_ID', 'create');
```

### **Test 11: Performance Testing**

#### **11.1 Test Index Performance**
```sql
-- Test queries use indexes
EXPLAIN ANALYZE SELECT * FROM tenant.objects WHERE tenant_id = (auth.jwt()->>'tenant_id')::uuid;
```

**Expected Result:** Uses index scan

---

## 🚨 **Troubleshooting Common Issues**

### **Issue: JWT claims return empty `{}`**
**Solution:**
1. Check if user exists in `system.users`
2. Verify `tenant_id` is set for the user
3. Ensure JWT function is configured in Supabase dashboard

### **Issue: RLS blocks all access**
**Solution:**
1. Verify JWT contains `tenant_id`
2. Check RLS policies are enabled
3. Ensure table has `tenant_id` column

### **Issue: Can't create objects/fields**
**Solution:**
1. Verify user has proper permissions
2. Check function grants are set
3. Ensure user is authenticated

### **Issue: Functions return permission errors**
**Solution:**
1. Check function grants to `authenticated` role
2. Verify user is properly authenticated
3. Check tenant_id is set correctly

---

## ✅ **Final Verification Checklist**

- [ ] All 4 migrations executed successfully
- [ ] JWT Custom Claims Function configured
- [ ] Tenant creation works
- [ ] User sign-up and mapping works
- [ ] JWT contains `tenant_id`
- [ ] RLS policies working (tenant isolation)
- [ ] Dynamic object creation works
- [ ] Field creation works
- [ ] Permission sets work
- [ ] Page layouts work
- [ ] Data operations work
- [ ] Multi-user isolation works
- [ ] Performance is acceptable

---

## 🎉 **Success!**

If all tests pass, your **Craft App** multi-tenant system is ready for production!

**Next Steps:**
1. **Build UI components** using the functions
2. **Implement authentication flow**
3. **Create object/field management UI**
4. **Add permission management interface**
5. **Deploy to production**

---

**Your multi-tenant CRM is now fully functional and production-ready!** 🚀 