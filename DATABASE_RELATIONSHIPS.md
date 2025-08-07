# Database Relationships & Object Management

## 🗄️ Visual Database Relationship Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              SYSTEM SCHEMA (Global)                            │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────────┐    ┌─────────────────┐                                    │
│  │ system.tenants  │    │ system.users    │                                    │
│  ├─────────────────┤    ├─────────────────┤                                    │
│  │ id (PK)         │    │ id (PK)         │ ← auth.users.id                    │
│  │ name            │    │ tenant_id (FK)  │ → system.tenants.id                │
│  │ slug            │    │ email           │                                    │
│  │ domain          │    │ first_name      │                                    │
│  │ settings        │    │ last_name       │                                    │
│  │ is_active       │    │ role            │                                    │
│  │ created_at      │    │ is_active       │                                    │
│  │ updated_at      │    │ created_at      │                                    │
│  └─────────────────┘    │ updated_at      │                                    │
│           │             └─────────────────┘                                    │
│           │                        │                                           │
│           │                        │                                           │
└───────────┼────────────────────────┼───────────────────────────────────────────┘
            │                        │
            │                        │
            ▼                        ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              TENANT SCHEMA (Isolated)                          │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐             │
│  │ tenant.objects  │    │ tenant.fields   │    │ tenant.permission_sets │      │
│  ├─────────────────┤    ├─────────────────┤    ├─────────────────┤             │
│  │ id (PK)         │    │ id (PK)         │    │ id (PK)         │             │
│  │ tenant_id (FK)  │    │ tenant_id (FK)  │    │ tenant_id (FK)  │             │
│  │ name            │    │ object_id (FK)  │    │ name            │             │
│  │ label           │    │ name            │    │ description     │             │
│  │ description     │    │ label           │    │ api_name        │             │
│  │ is_active       │    │ type            │    │ license_type    │             │
│  │ created_at      │    │ is_required     │    │ created_at      │             │
│  │ updated_at      │    │ is_nullable     │    │ updated_at      │             │
│  └─────────────────┘    │ default_value   │    └─────────────────┘             │
│           │             │ validation_rules│             │                      │
│           │             │ display_order   │             │                      │
│           │             │ section         │             │                      │
│           │             │ width           │             │                      │
│           │             │ is_visible      │             │                      │
│           │             │ is_system_field │             │                      │
│           │             │ reference_table │             │                      │
│           │             │ created_at      │             │                      │
│           │             │ updated_at      │             │                      │
│           │             └─────────────────┘             │                      │
│           │                        │                    │                      │
│           │                        │                    │                      │
│           ▼                        ▼                    ▼                      │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐             │
│  │ tenant.layout_blocks │ tenant.picklist_values │ tenant.user_permission_sets │
│  ├─────────────────┤    ├─────────────────┤    ├─────────────────┤             │
│  │ id (PK)         │    │ id (PK)         │    │ id (PK)         │             │
│  │ tenant_id (FK)  │    │ tenant_id (FK)  │    │ user_id (FK)    │ → system.users.id
│  │ object_id (FK)  │    │ field_id (FK)   │    │ perm_set_id (FK)│ → tenant.permission_sets.id
│  │ block_type      │    │ value           │    │ assigned_at     │             │
│  │ field_id (FK)   │    │ label           │    │ assigned_by     │             │
│  │ related_list_id │    │ display_order   │    │ created_at      │             │
│  │ label           │    │ is_active       │    └─────────────────┘             │
│  │ section         │    │ created_at      │             │                      │
│  │ display_order   │    │ updated_at      │             │                      │
│  │ width           │    └─────────────────┘             │                      │
│  │ is_visible      │                                    │                      │
│  │ created_at      │                                    │                      │
│  │ updated_at      │                                    │                      │
│  └─────────────────┘                                    │                      │
│                                                         │                      │
│                                                         ▼                      │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐             │
│  │ tenant.permission_set_objects │ tenant.permission_set_fields │ tenant.tabs │
│  ├─────────────────┤    ├─────────────────┤    ├─────────────────┤             │
│  │ id (PK)         │    │ id (PK)         │    │ id (PK)         │             │
│  │ perm_set_id (FK)│    │ perm_set_id (FK)│    │ tenant_id (FK)  │             │
│  │ object_id (FK)  │    │ field_id (FK)   │    │ name            │             │
│  │ can_create      │    │ can_read        │    │ description     │             │
│  │ can_read        │    │ can_edit        │    │ api_name        │             │
│  │ can_update      │    │ created_at      │    │ is_visible      │             │
│  │ can_delete      │    │ updated_at      │    │ display_order   │             │
│  │ created_at      │    └─────────────────┘    │ created_at      │             │
│  │ updated_at      │                            │ updated_at      │             │
│  └─────────────────┘                            └─────────────────┘             │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## 🏗️ Object & Field Management System

### Standard vs Custom Objects/Fields

#### **Standard Objects/Fields** (System-Provided)
- **Created by**: System/Migration
- **Naming**: `accounts`, `contacts`, `leads`
- **Purpose**: Pre-configured business objects
- **Examples**: 
  - `accounts` (Companies)
  - `contacts` (People)
  - `leads` (Sales opportunities)

#### **Custom Objects/Fields** (User-Created)
- **Created by**: Users via UI
- **Naming**: `custom_object_name__a` (with `__a` extension)
- **Purpose**: User-defined business objects
- **Examples**:
  - `products__a` (User-created Products object)
  - `invoices__a` (User-created Invoices object)
  - `projects__a` (User-created Projects object)

### Naming Convention

```
Standard Objects: accounts, contacts, leads
Custom Objects:   products__a, invoices__a, projects__a

Standard Fields:  name, email, phone
Custom Fields:    sku__a, invoice_number__a, project_status__a
```

### Why `__a` Extension?

- **`__a`** stands for **"Adjusted"** (user-modified)
- **Prevents conflicts** with system objects
- **Easy identification** of user-created items
- **Future-proof** for system updates

## 🔄 Object Creation Flow

### 1. User Creates Object via UI
```
User clicks "Create Object" → ObjectManagerTab.tsx
```

### 2. System Generates Name
```
User enters: "Products"
System creates: "products__a"
```

### 3. Database Operations
```sql
-- Insert into tenant.objects
INSERT INTO tenant.objects (tenant_id, name, label, description)
VALUES (tenant_id, 'products__a', 'Products', 'User-created products object');

-- Create actual table
CREATE TABLE products__a (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    created_by UUID REFERENCES system.users(id),
    updated_by UUID REFERENCES system.users(id)
);

-- Add RLS policies
ALTER TABLE products__a ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Tenant isolation on products__a"
    ON products__a FOR ALL
    USING (tenant_id = (auth.jwt()->>'tenant_id')::uuid);
```

## 📋 Field Management

### Standard Fields (Pre-configured)
```sql
-- Account object standard fields
INSERT INTO tenant.fields (tenant_id, object_id, name, label, type, is_required)
VALUES 
    (tenant_id, account_object_id, 'name', 'Account Name', 'text', true),
    (tenant_id, account_object_id, 'industry', 'Industry', 'text', false),
    (tenant_id, account_object_id, 'website', 'Website', 'url', false);
```

### Custom Fields (User-created)
```sql
-- User adds custom field to Products object
INSERT INTO tenant.fields (tenant_id, object_id, name, label, type, is_required)
VALUES 
    (tenant_id, products_object_id, 'sku__a', 'SKU', 'text', true),
    (tenant_id, products_object_id, 'price__a', 'Price', 'number', false);
```

## 🎯 Permission System Flow

### 1. Permission Set Creation
```sql
-- Admin creates permission set
INSERT INTO tenant.permission_sets (tenant_id, name, description)
VALUES (tenant_id, 'Sales Manager', 'Can manage sales objects');
```

### 2. Object Permissions
```sql
-- Grant access to objects
INSERT INTO tenant.permission_set_objects (perm_set_id, object_id, can_create, can_read, can_update, can_delete)
VALUES 
    (sales_manager_id, accounts_object_id, true, true, true, false),
    (sales_manager_id, contacts_object_id, true, true, true, false),
    (sales_manager_id, products__a_object_id, true, true, true, true);
```

### 3. Field Permissions
```sql
-- Grant access to fields
INSERT INTO tenant.permission_set_fields (perm_set_id, field_id, can_read, can_edit)
VALUES 
    (sales_manager_id, name_field_id, true, true),
    (sales_manager_id, price__a_field_id, true, true),
    (sales_manager_id, cost__a_field_id, true, false); -- Can read but not edit
```

### 4. User Assignment
```sql
-- Assign permission set to user
INSERT INTO tenant.user_permission_sets (user_id, perm_set_id)
VALUES (user_id, sales_manager_id);
```

## 🔐 RLS Policy Examples

### Tenant Isolation
```sql
-- All tenant tables have this pattern
CREATE POLICY "Tenant Isolation" ON tenant.objects
FOR ALL USING (tenant_id = (auth.jwt()->>'tenant_id')::uuid)
WITH CHECK (tenant_id = (auth.jwt()->>'tenant_id')::uuid);
```

### Dynamic Object Access
```sql
-- For user-created tables like products__a
CREATE POLICY "Tenant isolation on products__a"
ON products__a FOR ALL
USING (tenant_id = (auth.jwt()->>'tenant_id')::uuid)
WITH CHECK (tenant_id = (auth.jwt()->>'tenant_id')::uuid);
```

## 🚀 Key Benefits

1. **Clear Separation**: Standard vs custom objects/fields
2. **No Conflicts**: `__a` extension prevents naming collisions
3. **Flexible Permissions**: Granular control at object and field level
4. **Multi-Tenant**: Complete isolation between tenants
5. **Scalable**: Easy to add new objects and fields
6. **Future-Proof**: System updates won't affect user data

---

This architecture provides a robust foundation for building dynamic, multi-tenant business applications with enterprise-grade security and flexibility. 