# 📋 Confluence Space Key Examples

## What is a Confluence Space Key?

A **Space Key** is a unique identifier for a Confluence space. It's a short alphanumeric code used to identify and access specific spaces in Confluence.

## How to Find Your Space Key

### Method 1: From URL
Look at your Confluence URL when viewing a space:

```
https://yourcompany.atlassian.net/wiki/spaces/SPACE_KEY/pages/123456/Page+Title
                                                      ^^^^^^^^^
                                                      This is the space key
```

### Method 2: Space Settings
1. Go to your Confluence space
2. Click **Space Settings** (gear icon)
3. Go to **Space Details**
4. The Space Key is displayed there

### Method 3: Using the API
```bash
curl -u your-email@example.com:your-api-token \
  https://yourcompany.atlassian.net/wiki/rest/api/space
```

## Examples of Space Keys

### Common Examples:

| Space Name | Example Space Key | Notes |
|------------|-------------------|-------|
| Human Resources | `HR` | Short and simple |
| Standard Operating Procedures | `SOP` | Abbreviation |
| Engineering Documentation | `ENG` | Department code |
| Product Documentation | `PROD_DOCS` | Descriptive |
| Marketing and Operations | `MKT_OPS` | Combined |
| IT Support | `IT` | Simple code |
| Customer Success | `CS` | Abbreviation |
| Development Team | `DEV` | Short code |
| Quality Assurance | `QA` | Standard abbreviation |
| Project Alpha | `PROJ_ALPHA` | Project-specific |

### Real-World Examples:

```
CONFLUENCE_SPACE_KEY=HR
CONFLUENCE_SPACE_KEY=SOP
CONFLUENCE_SPACE_KEY=ENG
CONFLUENCE_SPACE_KEY=PROD_DOCS
CONFLUENCE_SPACE_KEY=MKT_OPS
CONFLUENCE_SPACE_KEY=IT
CONFLUENCE_SPACE_KEY=CS
CONFLUENCE_SPACE_KEY=DEV
CONFLUENCE_SPACE_KEY=QA
```

## Space Key Rules

- **Alphanumeric**: Can contain letters (A-Z) and numbers (0-9)
- **Case insensitive**: `HR` and `hr` are the same
- **Unique**: Each space key must be unique in your Confluence instance
- **Length**: Usually 1-255 characters (typically 2-20)
- **No spaces**: Use underscores or hyphens instead

## Using Space Key in .env

### Example 1: Single Space
```env
CONFLUENCE_URL=https://yourcompany.atlassian.net
CONFLUENCE_USERNAME=your-email@example.com
CONFLUENCE_API_TOKEN=your-token-here
CONFLUENCE_SPACE_KEY=HR
```

### Example 2: Multiple Spaces (Leave Empty)
```env
CONFLUENCE_URL=https://yourcompany.atlassian.net
CONFLUENCE_USERNAME=your-email@example.com
CONFLUENCE_API_TOKEN=your-token-here
CONFLUENCE_SPACE_KEY=
```

If `CONFLUENCE_SPACE_KEY` is empty, the system will ingest from **all accessible spaces**.

## Testing Your Space Key

### Using the API:
```bash
# List all spaces
curl -u your-email@example.com:your-token \
  https://yourcompany.atlassian.net/wiki/rest/api/space

# Get specific space
curl -u your-email@example.com:your-token \
  https://yourcompany.atlassian.net/wiki/rest/api/space/HR
```

### Using Our Application:
```bash
# List all spaces
curl http://localhost:8000/confluence/spaces

# Get pages from a specific space
curl http://localhost:8000/confluence/spaces/HR/pages
```

## Common Space Key Patterns

### Department-Based:
- `HR` - Human Resources
- `IT` - Information Technology
- `ENG` - Engineering
- `MKT` - Marketing
- `FIN` - Finance
- `OPS` - Operations

### Project-Based:
- `PROJ_ALPHA` - Project Alpha
- `PROJ_BETA` - Project Beta
- `PROD_LAUNCH` - Product Launch

### Documentation-Based:
- `DOCS` - General Documentation
- `SOP` - Standard Operating Procedures
- `WIKI` - Wiki Space
- `KB` - Knowledge Base

## Tips

1. **Keep it short**: Shorter keys are easier to remember and type
2. **Be consistent**: Use a naming convention across your organization
3. **Use abbreviations**: Common abbreviations are easier to remember
4. **Avoid special characters**: Stick to letters, numbers, and underscores
5. **Check availability**: Make sure the key isn't already taken

## Example .env Configuration

```env
# Confluence Configuration
CONFLUENCE_URL=https://acme-corp.atlassian.net
CONFLUENCE_USERNAME=john.doe@acme-corp.com
CONFLUENCE_API_TOKEN=ATATT3xFfGF0...
CONFLUENCE_SPACE_KEY=HR

# Or leave empty to ingest all spaces:
# CONFLUENCE_SPACE_KEY=
```

## Need Help?

If you're not sure what your space key is:
1. Check the URL when viewing a space in Confluence
2. Use the API to list all spaces: `GET /confluence/spaces`
3. Check Space Settings in Confluence
4. Ask your Confluence administrator
