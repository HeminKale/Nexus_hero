# JWT Setup Guide for Multi-Tenant Isolation

## 🎯 **Why JWT Setup Is Critical**

Your friend is absolutely right! JWT setup is the **foundation** of our multi-tenant security. Here's why:

### **The Problem:**
- Supabase **auth** issues a JWT for every authenticated user
- Our **RLS policies** rely on `auth.jwt()->>'tenant_id'` to isolate rows
- By default, Supabase JWT only has core claims like `sub` (user ID), **NOT** `tenant_id`

### **The Solution:**
- We add **custom claims** via a Postgres function that Supabase calls
- This function returns JSON with our extra fields (like `tenant_id`)
- RLS policies automatically filter data based on these claims

## 🚀 **Step-by-Step JWT Setup**

### **Step 1: Run Migration 003 (Production-Ready)**
```bash
# Copy and paste the content from:
# supabase/migrations/003_jwt_setup_dynamic_objects.sql
# into Supabase SQL Editor and run it
```

**✨ Production-Ready Features Included:**
- ✅ **Name length limits** (40 chars + `__a` suffix)
- ✅ **Duplicate prevention** for objects, fields, and picklist values
- ✅ **Separate RLS policies** (SELECT/INSERT/UPDATE/DELETE)
- ✅ **Performance indexes** on `tenant_id` columns
- ✅ **Enhanced error handling** and validation

### **Step 2: Configure Supabase Dashboard**

1. **Go to Supabase Dashboard** → Your Project
2. **Navigate to**: Authentication → Settings
3. **Find**: "JWT Custom Claims Function"
4. **Enter**: `system.jwt_claims`
5. **Save** the settings

### **Step 3: Test JWT Claims**

Run this query in Supabase SQL Editor:
```sql
-- Test JWT claims function
SELECT system.jwt_claims();
```

**Expected Result:**
```json
{
  "tenant_id": "uuid-of-tenant"
}
```

### **Step 4: Verify JWT in Client**

```javascript
// In your Next.js app
const { data } = await supabase.auth.getSession();
console.log('JWT Token:', data.session.access_token);

// Decode at jwt.io to see:
{
  "sub": "user-uuid",
  "tenant_id": "tenant-uuid",  // ← This should be present!
  "exp": 1234567890,
  "iat": 1234567890
}
```

## 🔐 **How RLS Works with JWT**

### **Before JWT Setup:**
```sql
-- This would return NO DATA because tenant_id is NULL
SELECT * FROM tenant.objects;
-- Result: Empty (RLS blocks access)
```

### **After JWT Setup:**
```sql
-- This returns only tenant-specific data
SELECT * FROM tenant.objects;
-- Result: Only objects for current user's tenant
```

### **Enhanced RLS Policy Example:**
```sql
-- From our production-ready migration
CREATE POLICY "select_tenant_isolation_products__a"
ON products__a FOR SELECT
USING (tenant_id = (auth.jwt()->>'tenant_id')::uuid);

CREATE POLICY "insert_tenant_isolation_products__a"
ON products__a FOR INSERT
WITH CHECK (tenant_id = (auth.jwt()->>'tenant_id')::uuid);
```

## 🧪 **Testing the Complete Flow**

### **1. Create a Test User**
```sql
-- Insert a test tenant
INSERT INTO system.tenants (name, slug) 
VALUES ('Test Company', 'test-company');

-- Insert a test user (this will be done by the trigger)
-- But you can also do it manually:
INSERT INTO system.users (id, email, tenant_id, role)
VALUES (
  'your-auth-user-id', 
  'test@example.com', 
  (SELECT id FROM system.tenants WHERE slug = 'test-company'),
  'admin'
);
```

### **2. Test JWT Claims**
```sql
-- This should return the tenant_id
SELECT system.jwt_claims();
```

### **3. Test RLS Isolation**
```sql
-- This should only return data for your tenant
SELECT * FROM tenant.objects;
```

## 🛠️ **Dynamic Object Creation with JWT**

### **Create Objects from UI:**
```javascript
// In your React component
const createObject = async (objectName, label, description) => {
  const { data, error } = await supabase.rpc('tenant.create_object', {
    _object_name: objectName,
    _label: label,
    _description: description
  });
  
  if (error) {
    console.error('Error creating object:', error);
    return;
  }
  
  console.log('Object created:', data);
};
```

### **Add Fields to Objects:**
```javascript
const addField = async (objectId, fieldName, label, fieldType) => {
  const { data, error } = await supabase.rpc('tenant.add_field', {
    _object_id: objectId,
    _field_name: fieldName,
    _label: label,
    _field_type: fieldType,
    _is_required: false
  });
  
  if (error) {
    console.error('Error adding field:', error);
    return;
  }
  
  console.log('Field added:', data);
};
```

## 🔍 **Troubleshooting**

### **Problem: JWT claims return empty `{}`**
**Solution:**
1. Check if user exists in `system.users`
2. Verify `tenant_id` is set for the user
3. Ensure JWT function is configured in Supabase dashboard

### **Problem: RLS blocks all access**
**Solution:**
1. Verify JWT contains `tenant_id`
2. Check RLS policies are enabled
3. Ensure table has `tenant_id` column

### **Problem: Can't create objects/fields**
**Solution:**
1. Verify user has proper permissions
2. Check function grants are set
3. Ensure user is authenticated

### **Problem: "Object with name already exists"**
**Solution:**
- This is a **safety feature** preventing duplicate objects
- Use a different name or check existing objects first

### **Problem: "Field with name already exists"**
**Solution:**
- This is a **safety feature** preventing duplicate fields
- Use a different field name or check existing fields first

## 📋 **Verification Checklist**

- [ ] Migration 003 executed successfully
- [ ] JWT Custom Claims Function set to `system.jwt_claims`
- [ ] `SELECT system.jwt_claims()` returns tenant_id
- [ ] JWT token contains `tenant_id` claim
- [ ] RLS policies working (tenant isolation)
- [ ] Can create objects with `__a` suffix
- [ ] Can add fields to objects
- [ ] All functions have proper grants
- [ ] Performance indexes created on tenant_id columns
- [ ] Unique constraints prevent duplicates

## 🎉 **What You Get After JWT Setup**

### **✅ Complete Multi-Tenant Isolation**
- Users can only see their tenant's data
- Automatic filtering via RLS
- No cross-tenant data leakage

### **✅ Dynamic Object Creation**
- Create objects with `__a` suffix
- Automatic table creation
- RLS policies applied automatically
- **Performance optimized** with indexes

### **✅ Field Management**
- Add custom fields with `__a` suffix
- Picklist support with duplicate prevention
- Validation rules
- **Enhanced error handling**

### **✅ Security by Default**
- JWT-based authentication
- Tenant isolation at database level
- **Separate RLS policies** for granular control
- No manual filtering needed in code

### **✅ Production-Ready Features**
- **Name length limits** prevent database issues
- **Duplicate prevention** maintains data integrity
- **Performance indexes** optimize queries
- **Enhanced error messages** for better debugging

## 🚀 **Next Steps After JWT Setup**

1. **Test the complete flow** with sample data
2. **Build UI components** for object/field creation
3. **Implement permission system** with the existing tables
4. **Add layout builder** functionality
5. **Create user management** interface

## 🔧 **Production Considerations**

### **Performance:**
- Each object creates a new table (Postgres handles thousands of tables well)
- Indexes on `tenant_id` optimize RLS performance
- Consider monitoring table count for very large deployments

### **Maintenance:**
- Regular backups include all dynamic tables
- Monitor for any naming conflicts (handled automatically)
- Consider archiving old objects if needed

### **Scaling:**
- System designed for multi-tenant SaaS
- Each tenant's data is completely isolated
- Can scale horizontally with additional Supabase projects

---

**Your multi-tenant system is now production-ready!** 🎯

The JWT setup ensures that every user automatically gets isolated to their tenant, and all the dynamic object creation functions work seamlessly with proper security, performance, and data integrity. 