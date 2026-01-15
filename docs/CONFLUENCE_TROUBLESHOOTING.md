# 🔧 Confluence Connection Troubleshooting

## Current Status

Based on the test, we're getting a **401 Unauthorized** error. This means the authentication is failing.

## Common Issues & Solutions

### 1. ❌ API Token Invalid or Expired

**Symptoms:** 401 Unauthorized error

**Solution:**
1. Go to: https://id.atlassian.com/manage-profile/security/api-tokens
2. Check if your token is still active
3. **Generate a new token:**
   - Click "Create API token"
   - Give it a name (e.g., "Knowledge Gap Detector")
   - Copy the token immediately (you won't see it again!)
4. Update your `.env` file with the new token

### 2. ❌ URL Format Incorrect

**Current URL:** `https://yashbgv2002.atlassian.net` ✅ (This looks correct)

**Should be:**
- ✅ `https://your-domain.atlassian.net` (without /wiki)
- ❌ `https://your-domain.atlassian.net/wiki` (wrong)

### 3. ❌ Username Format

**Current:** `yashbgv2002@gmail.com` ✅ (Email format is correct)

**Should be:**
- Your Atlassian account email address
- Not your username, but your email

### 4. ✅ Space Key

**Current:** `SD` ✅ (This looks correct)

## Manual Testing

Test your credentials manually:

```bash
# Replace YOUR_TOKEN with your actual API token
curl -u yashbgv2002@gmail.com:YOUR_TOKEN \
  https://yashbgv2002.atlassian.net/wiki/rest/api/space
```

If this works, you should see JSON with your spaces.

## Quick Fix Steps

1. **Regenerate API Token:**
   ```
   1. Visit: https://id.atlassian.com/manage-profile/security/api-tokens
   2. Create new token
   3. Copy it
   ```

2. **Update .env:**
   ```env
   CONFLUENCE_API_TOKEN=your_new_token_here
   ```

3. **Test Again:**
   ```bash
   python test_confluence.py
   ```

## Testing via Application API

Once the API server is running:

```bash
# Test Confluence spaces endpoint
curl http://localhost:8000/confluence/spaces

# Should return:
# {"spaces": [...], "count": X}
```

## Verify Your Setup

Your current configuration:
- ✅ URL: `https://yashbgv2002.atlassian.net` (correct format)
- ✅ Username: `yashbgv2002@gmail.com` (email format)
- ⚠️  Token: Needs verification/regeneration
- ✅ Space Key: `SD` (if you want to limit to this space)

## Next Steps

1. **Regenerate your API token** (most likely issue)
2. **Update .env** with the new token
3. **Run test again:** `python test_confluence.py`
4. **Test in application:** `curl http://localhost:8000/confluence/spaces`

## Still Having Issues?

If regenerating the token doesn't work:

1. **Check Confluence permissions:**
   - Make sure your account has access to the spaces
   - Verify you can access Confluence in a browser

2. **Check token permissions:**
   - Some tokens might need specific scopes
   - Try creating a token with full access

3. **Test with different authentication:**
   - Some Confluence instances use different auth methods
   - Check if your instance uses OAuth instead

4. **Contact support:**
   - If nothing works, the issue might be with your Confluence instance configuration
