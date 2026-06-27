# RIFT

**RIFT** is an opinionated FastAPI template framework for generating structured, multi-tenant backend projects from source-of-truth configuration files.

RIFT is designed for developers who want a consistent backend foundation across projects without repeatedly writing the same boilerplate for configuration, database access, models, routes, operations, permissions, tenancy, and RBAC.

It is intentionally strict. The goal is not to support every possible backend style. The goal is to support one strong backend style very well.

---

## Overview

RIFT generates FastAPI backend projects using a fixed architecture and a JSON-driven generation flow.

The core flow is:

**User input → Source-of-truth JSON → Generated backend code**

Instead of directly generating code from one-time prompts, RIFT first stores structured project and object definitions in configuration files. The backend code is then generated or regenerated from those files.

This makes the framework predictable, repeatable, and safer to maintain.

---

## Core Idea

Most backend projects need the same foundation:

- Application configuration
- Environment variable loading
- MongoDB setup
- API versioning
- Models
- Routes
- Database operations
- Auth dependencies
- Multi-tenancy
- Role-based access control
- Permission checks
- Tenant filtering
- Object ownership checks
- Route registration
- Collection name management

RIFT standardizes these decisions and generates the repetitive structure automatically.

The developer defines the business objects and rules. RIFT generates the backend structure around them.

---

## Design Philosophy

RIFT follows a strict and opinionated design philosophy.

### Fixed by the framework

RIFT assumes the following decisions by default:

- FastAPI as the backend framework
- MongoDB as the database
- Multi-tenancy enabled by default
- RBAC enabled by default
- One system organization
- Global user identity
- Tenant-specific memberships
- Custom roles
- Model-wise permissions
- API versioning from `v1`
- Environment-based configuration
- JSON source-of-truth files
- Deterministic code generation

### Controlled by the developer

The developer mainly defines:

- Project name
- Business objects
- Object fields
- Field types
- Field validations
- Object scope
- Object ownership behavior
- Custom object actions
- Separate update methods
- Permission behavior
- Default role templates

---

## Main Workflow

RIFT follows a three-step workflow.

### 1. Initialize Project

The project initialization step creates the base backend structure, required folders, source-of-truth files, and the initial project baseline.

It should also initialize Git and create the first commit so future generated changes can be reviewed safely.

### 2. Define Objects

The object definition step collects object details from the developer.

This includes object name, fields, validations, schema behavior, ownership behavior, model validators, field validators, and custom actions.

This step updates the source-of-truth configuration files only. It should not directly generate backend code.

### 3. Generate Backend

The generation step reads the source-of-truth configuration and generates or regenerates backend files.

Generated code should be deterministic. If the configuration does not change, the generated output should not unexpectedly change.

---

## Source of Truth

RIFT should maintain separate source-of-truth files instead of one large configuration file.

Suggested structure:

```text
.template/
  objects.json
  permissions.json
  roles.json
  generator.json
```

### objects.json

Defines business objects, fields, validations, schema behavior, ownership behavior, custom actions, route behavior, and object scope.

### permissions.json

Defines the generated permission catalog for each object.

This file represents available permissions, not runtime assignments.

### roles.json

Defines default role templates and initial role-permission mappings.

Runtime role assignment should still happen through the database.

### generator.json

Stores project metadata, generator version, last generated time, and generation safety settings.

---

## Suggested Generated Project Structure

A generated RIFT project should follow a predictable structure:

```text
product_name/
  __init__.py
  config.py
  cols.py
  db.py
  main.py

  .template/
    objects.json
    permissions.json
    roles.json
    generator.json
    removal.md

  v1/
    __init__.py

    models/
      __init__.py
      user_model.py
      org_model.py
      role_model.py
      membership_model.py
      permission_model.py
      <object>_model.py

    operations/
      __init__.py
      user_ops.py
      org_ops.py
      role_ops.py
      membership_ops.py
      permission_ops.py
      <object>_ops.py

    routes/
      __init__.py
      auth.py
      users.py
      orgs.py
      roles.py
      permissions.py
      <object>.py

    dependencies/
      __init__.py
      auth.py
      tenancy.py
      rbac.py

    security/
      __init__.py
      roles.py
      permissions.py
      role_permissions.py

    schemas/
      __init__.py
      common.py
```

---

## Object System

Objects are the main building blocks in RIFT.

An object can represent any backend resource such as a post, report, task, order, invoice, product, complaint, event, or document.

Each object can define:

- Name
- Scope
- Description
- Fields
- Field types
- Required fields
- Default values
- Field descriptions
- Validation rules
- Field validators
- Model validators
- Create schema behavior
- Update schema behavior
- Response schema behavior
- Custom actions
- Ownership rules
- Permission behavior

---

## Naming Rules

RIFT should normalize object names into consistent names across generated files.

For each object, RIFT should generate:

- PascalCase class name
- Snake case file name
- Plural route name
- Plural collection name
- Upper snake case collection constant
- Model class name
- Create schema name
- Update schema name
- Response schema name
- Operations class name

Field names must use snake_case.

---

## Field System

Each field should support:

- Field name
- Field type
- Required flag
- Default value
- Description
- Validation rules
- Field validator flag
- Create schema inclusion
- Update schema inclusion
- Response schema inclusion
- Separate update method flag

Supported field types for the MVP may include:

- string
- integer
- float
- boolean
- datetime
- list of strings
- literal values

Future versions may support:

- date
- dictionary
- object IDs
- email fields
- URL fields
- enum fields
- nested objects
- embedded schemas

---

## Validation System

RIFT should support common validation rules.

For text fields:

- Minimum length
- Maximum length
- Pattern matching
- Whitespace stripping
- Lowercase normalization
- Uppercase normalization
- Unique value checks

For numeric fields:

- Greater than
- Greater than or equal
- Less than
- Less than or equal
- Multiple of

For list fields:

- Minimum items
- Maximum items
- Unique items

RIFT should also support model-level validators for cross-field validation.

---

## Separate Update Methods

Some fields should not be updated through a normal update endpoint.

Examples include:

- Status
- Published state
- Approval state
- Rejection state
- Verification state
- Lock state
- Assignment state
- Priority state

These fields often represent workflow transitions and should use dedicated endpoints or actions.

For example, instead of updating a status field through a normal update request, RIFT can generate a dedicated action such as publish, approve, reject, archive, assign, verify, or lock.

This allows stronger permission control and cleaner business logic.

---

## Permission System

RIFT uses model-wise permissions.

The recommended permission format is:

```text
<object>:<action>:<scope>
```

Examples:

- blog:create:any
- blog:read:any
- blog:read:own
- blog:update:any
- blog:update:own
- blog:delete:any
- blog:delete:own
- blog:publish:any
- blog:publish:own

Permission scopes:

- `any` means the user can act on any record in the current tenant.
- `own` means the user can act only on records they own.
- `system` means the permission applies at system level.

RIFT should use generic ownership terminology such as `own` instead of object-specific terms like author, customer, or resident.

---

## RBAC Model

RIFT should use strict RBAC.

Normal generated routes should check permissions, not role names.

The access model should be:

- A user has one global identity.
- A user can belong to many organizations.
- A membership connects a user to an organization.
- A membership can have one or more roles.
- Roles contain allowed and denied permissions.
- Memberships may also contain allow or deny overrides.
- Deny permissions should always override allow permissions.

This makes the system flexible while keeping generated routes stable.

---

## Ownership Rules

RIFT should support owner-based access.

For example, a user may be allowed to create records and then read, update, or delete only the records they own.

Ownership should be enforced in the operation layer, not only in the route layer.

If the user has an `own` permission scope, generated database queries should include the owner field filter.

This prevents unauthorized access even if a user guesses another record ID.

---

## Multi-Tenancy

Multi-tenancy is a core requirement in RIFT.

Every tenant-scoped object must include organization context.

Every tenant-scoped operation must filter by organization ID.

This is a strict security rule.

A generated backend should include:

- One system organization
- Multiple tenant organizations
- Global users
- Organization memberships
- Tenant-scoped roles
- Tenant-scoped permissions
- Tenant-scoped object records

The system organization should control tenant organizations.

---

## RBAC Cache

Custom roles require permission resolution. To avoid repeated database calls on every request, RIFT should support RBAC caching.

The MVP should support in-memory RBAC caching.

The cache should store effective permissions per user per organization.

Recommended cache behavior:

- Lazy-load permissions when a user makes a request
- Store effective permissions in memory
- Use a TTL
- Invalidate cache when roles change
- Invalidate cache when memberships change
- Add Redis support later for multi-server deployments

---

## Generation Safety

RIFT should be Git-safe.

Recommended safety behavior:

- Initialize Git during project creation
- Create an initial commit after project generation
- Check for uncommitted changes before regeneration
- Stop generation if uncommitted changes exist
- Allow forced generation only through an explicit flag
- Support dry-run generation
- Support generation diff preview
- Clearly mark generated files

This reduces the chance of accidentally overwriting manual work.

---

## Removal Policy

RIFT should not automatically remove generated objects.

Object removal can be risky because files may have been edited manually or extended with business logic.

Instead of automated deletion, RIFT should provide a manual removal guide.

The guide should explain which JSON entries, model files, operation files, route files, collection entries, permissions, and route registrations need to be reviewed or removed manually.

---

## Doctor Command

RIFT should include a doctor command to validate project health.

The doctor command should check:

- Required folders exist
- Source-of-truth files exist
- Object definitions are valid
- Field names follow snake_case
- Object names are unique
- Collection names are unique
- Permission keys are valid
- Generated model files exist
- Generated operation files exist
- Generated route files exist
- Routes are registered
- Collection constants exist
- Tenant-scoped objects enforce organization filtering
- Ownership rules are applied
- No duplicate route names exist

---

## Initial Commands

The initial command set may include:

- `rift init`
- `rift object add`
- `rift object update`
- `rift generate`
- `rift generate --dry-run`
- `rift generate --force`
- `rift diff`
- `rift doctor`
- `rift removal-guide`

---

## Current Scope

The initial scope of RIFT is to generate a consistent backend foundation with strict architectural rules.

The first version should focus on:

- Project initialization
- Git initialization
- First commit creation
- Fixed folder structure
- FastAPI base application
- MongoDB setup
- Environment-based configuration
- Collection name management
- Source-of-truth JSON files
- Object definition flow
- Object-based model generation
- Object-based operation generation
- Object-based route generation
- Route registration
- Model-wise permission generation
- Own versus any permission scope
- Tenant-scoped object access
- System organization concept
- Global users
- Organization memberships
- Custom roles
- Allow and deny permissions
- RBAC dependency generation
- In-memory RBAC cache
- Doctor command
- Dry-run generation
- Manual removal guide

The main focus is repeatable backend generation, not runtime UI generation.

---

## Out of Scope for MVP

The following features should not be part of the first version:

- Admin UI generation
- Permission screen UI generation
- Frontend generation
- Redis cache backend
- Plugin system
- Complex migration engine
- Advanced deployment automation
- Multiple database support
- GraphQL support
- Background job generation
- Advanced audit log system
- File upload module
- Email notification module
- Test suite generation
- OpenAPI customization
- Multi-language SDK generation

These can be added later after the core generator is stable.

---

## Future Scope

Future versions of RIFT may include:

### Redis RBAC Cache

Add Redis support for permission caching across multiple server instances.

### Admin UI Generator

Generate a basic admin interface for managing users, organizations, roles, permissions, and generated objects.

### Permission Screen Generator

Generate a UI or API module for assigning allow and deny permissions to roles and memberships.

### Audit Log Module

Generate audit logging for create, update, delete, publish, approve, reject, and other important actions.

### File Upload Module

Generate standard upload handling with ownership, tenant filtering, validation, and access control.

### Notification Module

Generate email or in-app notification modules for workflow-based actions.

### Test Generation

Generate unit and integration tests for generated models, operations, routes, and permission behavior.

### Migration Helpers

Add helpers for managing schema changes, index creation, and MongoDB collection updates.

### Plugin System

Allow custom generator plugins while keeping the core architecture strict.

### Custom Template Overrides

Allow advanced users to override selected templates without changing the core generator.

### Deployment Templates

Generate Docker, Docker Compose, CI/CD, and deployment-related files.

### Advanced Schema Support

Support nested schemas, embedded objects, enums, object references, relation metadata, and advanced validation.

### OpenAPI Enhancements

Generate better tags, descriptions, examples, response schemas, and API documentation metadata.

---

## Long-Term Vision

RIFT should become a reliable backend generation framework for building secure, multi-tenant FastAPI applications quickly.

The long-term goal is to make backend project setup repeatable, structured, and safe.

RIFT should let developers focus on business objects and rules while the framework handles the repetitive backend architecture.

---

## Project Identity

RIFT is a strict, JSON-driven, RBAC-first, multi-tenant FastAPI and MongoDB backend generator.

Its most important rule is:

Generated routes check permissions. Generated operations enforce tenancy and ownership.
