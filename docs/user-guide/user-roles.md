# User Roles

Agrync has two roles. The role is assigned when an administrator creates the account and can be changed at any time.

## Role overview

| Capability | Administrator | Editor |
|---|:---:|:---:|
| Log in and view dashboard | ✅ | ✅ |
| View charts | ✅ | ✅ |
| Change own name, email, password | ✅ | ✅ |
| Write a value to a writable variable | ✅ | ✅ |
| Start / stop monitoring tasks | ✅ | ❌ |
| View task logs | ✅ | ❌ |
| Create / edit / delete Modbus devices, slaves, variables | ✅ | ❌ |
| Upload a bulk configuration file | ✅ | ❌ |
| Create / edit / delete user accounts | ✅ | ❌ |
| Assign devices to users | ✅ | ❌ |

## Administrator

The **Administrator** has full access to every section of the application. This includes all configuration tasks (Modbus hierarchy, user accounts, device assignment) and operational tasks (starting and stopping background data-collection processes).

There must always be at least one active administrator account. Deleting the last administrator account is not allowed.

## Editor

The **Editor** has a read-only view of the system configuration and can interact with device data:

- View live values on the Dashboard.
- Explore historical data on the Charts page.
- Write a new value to any variable marked as **writable**, subject to the device-level access granted by an administrator.
- Update their own profile (name, email, password).

Editors cannot see the Administration section of the application.

!!! note
    Access to devices is per-user. Even as an Administrator, you only see on the Dashboard and Charts the variables from devices explicitly assigned to your account. See [User Management](user-management.md) for how to assign devices.
