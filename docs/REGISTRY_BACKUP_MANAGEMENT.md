# Registry Backup Management

## Backup Storage Location

All registry backups are stored in:
- **Windows**: `C:\Users\<Username>\AppData\Local\Temp\hayward_techsuite_registry_backups\`
- **Direct Path**: `%TEMP%\hayward_techsuite_registry_backups\`

## Automatic Cleanup

- **Maximum Backups**: 10 most recent backups are kept
- **Automatic Deletion**: Older backups are automatically deleted when this limit is exceeded
- **Manual Cleanup**: You can safely delete backup files from the storage location

## Backup File Format

- **Format**: `.reg` files (Windows Registry Editor format)
- **Encoding**: UTF-16 LE (Little Endian)
- **Naming**: `reg_backup_YYYYMMDD_HHMMSS.reg`

## Metadata

Backup metadata is stored in `registry_metadata.json` in the same directory.

## Manual Cleanup Instructions

To manually delete old backups:
1. Navigate to `%TEMP%\hayward_techsuite_registry_backups\`
2. Delete `.reg` files you no longer need
3. Optionally delete `registry_metadata.json` to clear all metadata

⚠️ **Warning**: Do not delete backups you may need for recovery!

## Backup Creation

Registry backups are created automatically:
- Before applying any registry tweak in the DANGER ZONE tab
- When manually initiated through the "Backup Registry Now" button

## Restoration

To restore a registry backup:
1. Navigate to the DANGER ZONE tab
2. View the backup history section
3. Select the backup you want to restore
4. Click the "Restore Registry" button
5. Or use the "Undo Last Change" button to revert the most recent modification

## Technical Details

### Direct Export Method

The application uses the native Windows `reg export` command to create backups. This ensures:
- Valid UTF-16 LE encoding
- Proper registry file format
- Compatibility with Windows registry import tools

### Single Key Limitation

For reliability and to maintain proper file format:
- Only one registry key can be backed up at a time
- Multiple keys require separate backup operations
- This design prevents potential file concatenation issues that could corrupt the registry file format

### Backup Verification

Each backup is verified after creation:
- File existence check
- Non-zero file size validation
- Ensures backup integrity before metadata is saved
