# Craft App

A modern, multi-tenant SaaS platform built with Next.js and Supabase, providing a dynamic management system with enterprise-grade security and scalability.

## 🚀 Features

- **Multi-Tenant Architecture**: Complete tenant isolation with JWT-based Row Level Security (RLS)
- **Organization Management**: Join existing organizations or create new ones during sign-up
- **REST API Bridge Functions**: Secure access to system schema through public functions
- **Schema Separation**: Clean `system` vs `tenant` schema organization
- **Dynamic Object Creation**: Create custom database objects on-the-fly
- **Visual Layout Builder**: Drag-and-drop page layout editor
- **Enterprise Permissions**: Granular object and field-level permissions
- **User Management**: Complete user and role management system
- **App Management**: Create and manage multiple applications per tenant
- **Related Lists**: Dynamic relationship management between objects
- **JWT-Ready**: Future-proof architecture for advanced authentication
- **Permission Sets**: Flexible role-based access control (no Salesforce-style profiles)

## 🛠️ Tech Stack

- **Frontend**: Next.js 14 with TypeScript
- **Backend**: Supabase (PostgreSQL + Auth + RLS)
- **Styling**: Tailwind CSS
- **State Management**: React hooks + Context
- **Database**: PostgreSQL with JWT-based Row Level Security

## 📋 Prerequisites

- Node.js 18+ 
- npm or yarn
- Supabase account and project

## 🚀 Quick Start

### 1. Clone and Setup

```bash
# Navigate to the Craft App directory
cd "Craft App"

# Install dependencies
npm install
```

### 2. Environment Configuration

1. Copy the example environment file:
```bash
cp env.example .env.local
```

2. Update `.env.local` with your Supabase credentials:
```env
NEXT_PUBLIC_SUPABASE_URL=your_supabase_project_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key
```

### 3. Database Setup

1. Go to your Supabase project dashboard
2. Navigate to **SQL Editor**
3. Run migrations in order:

   **Migration 001** (Core Schema):
   - Copy and paste the content from `supabase/migrations/001_core_schema_rls.sql`
   - Click **Run** to execute the migration

   **Migration 002** (Helper Functions):
   - Copy and paste the content from `supabase/migrations/002_helper_functions_triggers.sql`
   - Click **Run** to execute the migration

   **Migration 003** (JWT Setup):
   - Copy and paste the content from `supabase/migrations/003_jwt_setup_dynamic_objects.sql`
   - Click **Run** to execute the migration

   **Migration 003a** (Fix Missing tenant_id):
   - Copy and paste the content from `supabase/migrations/003a_fix_missing_tenant_id.sql`
   - Click **Run** to execute the migration

   **Migration 004** (Permission Sets):
   - Copy and paste the content from `supabase/migrations/004_permission_sets_page_layouts.sql`
   - Click **Run** to execute the migration

   **Migration 006** (REST API Bridge Functions):
   - Copy and paste the content from `supabase/migrations/006_rest_api_bridge_functions.sql`
   - Click **Run** to execute the migration

   > **Important**: Run all migrations in order. Migration 006 enables the organization picklist functionality.

### 4. JWT Configuration (Critical for Multi-Tenancy)

1. Go to **Supabase Dashboard** → **Authentication** → **Settings**
2. Find **"JWT Custom Claims Function"**
3. Enter: `system.jwt_claims`
4. **Save** the settings

### 5. Start Development Server

```bash
npm run dev
```

The application will be available at `http://localhost:3000`

## 🏗️ Project Structure

```
Craft App/
├── app/                    # Next.js app directory
│   ├── components/         # React components
│   ├── lib/               # Supabase and utility functions
│   ├── types/             # TypeScript definitions
│   ├── utils/             # Helper functions
│   └── ...                # Next.js pages and layouts
├── supabase/
│   └── migrations/        # Database migrations
│       ├── 001_core_schema_rls.sql
│       ├── 002_helper_functions_triggers.sql
│       ├── 003_jwt_setup_dynamic_objects.sql
│       ├── 003a_fix_missing_tenant_id.sql
│       ├── 004_permission_sets_page_layouts.sql
│       └── 005_fix_rls_signup_policies.sql
├── env.example            # Environment variables template
├── DATABASE_RELATIONSHIPS.md  # Visual database diagrams & object management
├── JWT_SETUP_GUIDE.md     # Complete JWT configuration guide
└── README.md             # This file
```

## 🔐 Multi-Tenant Security

### Schema Organization
- **`system` schema**: Global tables shared across all tenants
  - `system.tenants` - Master list of tenants
  - `system.users` - Maps auth.users to tenants
- **`tenant` schema**: Tenant-specific tables with isolation
  - `tenant.permission_sets` - Permission collections
  - `tenant.objects` - Custom objects per tenant
  - `tenant.fields` - Dynamic field definitions
  - `tenant.layout_blocks` - Page layouts

### JWT-Based Row Level Security (RLS)
- All tables have RLS enabled with tenant isolation
- Uses `auth.jwt()->>'tenant_id'` for session-based security
- No cross-tenant data access possible
- Future-ready for JWT claim injection

### Permission System
- **No Salesforce-style Profiles**: Uses flexible Permission Sets only
- **Object-level permissions**: Create, Read, Update, Delete
- **Field-level permissions**: Read, Edit
- **User assignments**: Direct permission set assignments (multiple sets per user)
- **Admin-only settings**: Settings management restricted to admins

## 🔄 Complete User Lifecycle Flow

### A. User Sign-Up → System User Creation
```
1. User signs up → auth.users created (Supabase Auth)
2. Trigger fires → system.users created with tenant_id
3. User exists in both auth.users and system.users
```

### B. User Login → JWT with Tenant Claim
```
1. User logs in → Supabase Auth returns JWT
2. Custom JWT claim function adds tenant_id
3. RLS automatically filters by tenant_id
```

### C. Permission Set Assignment
```
1. Admin creates Permission Sets (e.g., "Admin", "Sales Rep")
2. Admin assigns sets to users via tenant.user_permission_sets
3. User gets access based on union of all assigned permission sets
```

### D. Access Enforcement
```
User → Permission Sets → Objects/Fields
Effective permissions = union of all assigned permission sets
```

## 🔐 Authentication Flow Details

### Login Flow
```
UI Form → Supabase Auth → JWT Token → User Profile → Dashboard
```

**Step-by-Step Process:**
1. **UI Layer**: User enters email/password in login form
2. **Form Validation**: Client-side validation of email format and password length
3. **Supabase Authentication**: `supabase.auth.signInWithPassword()` validates credentials
4. **JWT Generation**: Supabase returns JWT token with user metadata
5. **Token Storage**: JWT stored in browser localStorage
6. **Profile Loading**: `loadUserProfile()` queries `system.users` table
7. **Tenant Loading**: Fetches tenant information from `system.tenants`
8. **UI Update**: `useSupabase()` hook updates with user data
9. **Redirect**: `router.push('/dashboard')` navigates to dashboard

### Sign-Up Flow
```
UI Form → Supabase Auth → User Creation → Tenant Setup → Email Confirmation
```

**Step-by-Step Process:**
1. **UI Layer**: User fills signup form (name, email, password, organization)
2. **Organization Selection**: Choose existing organization or create new one
3. **Form Validation**: Validate all required fields and password confirmation
4. **Supabase Registration**: `supabase.auth.signUp()` creates user in `auth.users`
5. **Tenant Creation**: If new organization, `create_tenant()` RPC creates tenant
6. **User Profile**: `create_user()` RPC creates profile in `system.users`
7. **Role Assignment**: Admin role for new org, User role for existing org
8. **Email Confirmation**: Supabase sends confirmation email
9. **UI Feedback**: Shows email confirmation message
10. **Account Activation**: User clicks email link to activate account

### JWT Token Structure
```json
{
  "aud": "authenticated",
  "exp": 1234567890,
  "sub": "user-uuid",
  "email": "user@example.com",
  "app_metadata": {
    "tenant_id": "tenant-uuid",
    "role": "admin"
  }
}
```

### Security Features
- **Row Level Security (RLS)**: All queries filtered by `tenant_id`
- **JWT Claims**: Custom claims injected via `system.jwt_claims` function
- **Tenant Isolation**: Complete data separation between tenants
- **Role-Based Access**: Admin and User roles with different permissions
- **Email Verification**: Required email confirmation for new accounts

### Missing Features (Future Implementation)
- **Password Reset Flow**: Forgot password functionality
- **Account Deletion**: User account removal
- **Session Refresh**: Automatic token refresh
- **Multi-Factor Authentication**: 2FA support
- **Email Confirmation Callback**: Handle email confirmation redirects

## 🔧 Troubleshooting Authentication Issues

### Common Issues and Solutions

#### 1. "Loading Spinner Never Disappears"
**Cause**: SupabaseProvider stuck in loading state
**Solution**: 
- Check environment variables are correct
- Verify Supabase project is active
- Check browser console for connection errors

#### 2. "Login Form Not Working"
**Cause**: Missing Tailwind CSS configuration
**Solution**:
- Ensure `tailwind.config.js` and `postcss.config.js` exist
- Verify `globals.css` has `@tailwind` directives
- Restart development server

#### 3. "JWT Claims Not Working"
**Cause**: JWT custom claims function not configured
**Solution**:
- Go to Supabase Dashboard → Authentication → Settings
- Set JWT Custom Claims Function to: `system.jwt_claims`
- Save settings

#### 4. "User Profile Not Loading"
**Cause**: Missing user in `system.users` table
**Solution**:
- Check if user exists in `auth.users`
- Verify RPC functions `create_user` and `create_tenant` are working
- Check database migrations are applied

#### 5. "Tenant Isolation Not Working"
**Cause**: RLS policies not applied correctly
**Solution**:
- Verify all tables have RLS enabled
- Check RLS policies include `tenant_id` filtering
- Ensure JWT contains correct `tenant_id`

### Debug Steps
1. **Check Browser Console**: Look for JavaScript errors
2. **Check Network Tab**: Verify API calls are successful
3. **Check Supabase Logs**: Look for authentication errors
4. **Verify Environment Variables**: Ensure all required vars are set
5. **Test Database Connection**: Verify Supabase connection is working

## 📊 Database Schema

### System Tables (Global)
- `system.tenants` - Multi-tenant foundation
- `system.users` - User accounts with tenant mapping

### Tenant Tables (Isolated)
- `tenant.permission_sets` - Permission collections
- `tenant.objects` - Custom object definitions
- `tenant.fields` - Dynamic field configuration
- `tenant.permission_set_objects` - Object-level access control
- `tenant.permission_set_fields` - Field-level access control
- `tenant.user_permission_sets` - User-permission assignments
- `tenant.tabs` - Navigation management
- `tenant.apps` - Application management
- `tenant.layout_blocks` - Dynamic page layouts
- `tenant.related_list_metadata` - Related list definitions
- `tenant.picklist_values` - Dropdown options

### Dynamic Tables
- Created on-demand via Object Manager
- Automatic `tenant_id` and RLS policies
- Audit trail with `created_by`/`updated_by`

## 🏗️ Object Management System

### Standard vs Custom Objects/Fields
- **Standard Objects**: `accounts`, `contacts`, `leads` (system-provided)
- **Custom Objects**: `products__a`, `invoices__a` (user-created with `__a` extension)
- **`__a` Extension**: Prevents conflicts with system objects

### Naming Convention
```
Standard Objects: accounts, contacts, leads
Custom Objects:   products__a, invoices__a, projects__a

Standard Fields:  name, email, phone
Custom Fields:    sku__a, invoice_number__a, project_status__a
```

📖 **For detailed visual database relationships and object management flow, see [DATABASE_RELATIONSHIPS.md](./DATABASE_RELATIONSHIPS.md)**

📖 **For complete JWT setup instructions, see [JWT_SETUP_GUIDE.md](./JWT_SETUP_GUIDE.md)**

## 🎨 Key Components

### Settings Management
- **Object Manager**: Create and configure business objects
- **Field Manager**: Add and configure fields with various types
- **Layout Editor**: Drag-and-drop page layout builder
- **Permission Sets**: Granular permission management
- **User Management**: Complete user lifecycle management

### Dynamic Features
- **Visual Builder**: Drag-and-drop interface for layouts
- **Related Lists**: Connect objects with foreign key relationships
- **Field Types**: Text, Number, Date, Boolean, Reference, Picklist
- **Validation Rules**: Configurable field validation

## 🔧 Development

### Available Scripts

```bash
npm run dev          # Start development server
npm run build        # Build for production
npm run start        # Start production server
npm run lint         # Run ESLint
npm run type-check   # Run TypeScript type checking
```

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `NEXT_PUBLIC_SUPABASE_URL` | Your Supabase project URL | Yes |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Your Supabase anon key | Yes |
| `SUPABASE_SERVICE_ROLE_KEY` | Your Supabase service role key | Yes |
| `NEXT_PUBLIC_APP_NAME` | Application name | No |
| `NEXT_PUBLIC_APP_DESCRIPTION` | Application description | No |

## 🚀 Deployment

### Vercel (Recommended)

1. Push your code to GitHub
2. Connect your repository to Vercel
3. Add environment variables in Vercel dashboard
4. Deploy

### Other Platforms

The app can be deployed to any platform that supports Next.js:
- Netlify
- Railway
- DigitalOcean App Platform
- AWS Amplify

## 🔒 Security Best Practices

1. **Never expose service role key** in client-side code
2. **Use RLS policies** for all data access
3. **Validate user permissions** before operations
4. **Use HTTPS** in production
5. **Regular security audits** of RLS policies
6. **JWT claim validation** for tenant isolation

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For support and questions:
- Check the documentation
- Review the code comments
- Open an issue on GitHub

---

**Craft App** - Building the future of dynamic business applications with enterprise-grade multi-tenant architecture. 