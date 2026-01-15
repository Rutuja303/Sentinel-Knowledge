# 🔒 Fixing IP Allowlist for Confluence API Access

## Current Issue

You can see Confluence in the IP allowlist settings, but you're unable to enable it or add your IP. This is likely blocking your API access even though you have proper permissions.

## Your Current IP Address

**Your IP:** `125.20.250.6`

⚠️ **Note:** If your IP changes (dynamic IP), you'll need to update the allowlist.

## Step-by-Step: Configure IP Allowlist

### Option 1: Add IP via Atlassian Admin (Recommended)

1. **Go to IP Allowlist:**
   - Visit: https://admin.atlassian.com
   - Navigate to: **Security** → **IP allowlist**
   - Or: **Settings** → **Security** → **IP allowlist**

2. **Create or Edit Allowlist:**
   - Click **"Add IP address"** or **"Create allowlist"**
   - Name it: "Confluence API Access" or similar

3. **Add Your IP:**
   - IP Address: `125.20.250.6`
   - Or use CIDR notation: `125.20.250.6/32` (single IP)
   - Description: "My development machine"

4. **Select Products:**
   - ✅ Check **Confluence**
   - You can also check Jira if needed
   - Click **Save**

5. **Enable the Allowlist:**
   - Make sure the allowlist is **enabled/toggled ON**
   - Some interfaces require you to toggle it on after creation

### Option 2: If "Enable" Button Doesn't Work

If you can't enable the allowlist:

1. **Check Your Permissions:**
   - You need **Organization admin** or **Site admin** permissions
   - The `confluence-admins-yashbgv2002` group should have this

2. **Try Different Approach:**
   - Delete the existing allowlist entry
   - Create a new one from scratch
   - Make sure to select Confluence when creating

3. **Check Organization vs Site Level:**
   - IP allowlists can be at **Organization** level or **Site** level
   - Try creating it at the **Site** level: `yashbgv2002.atlassian.net`
   - Go to: **Site settings** → **Security** → **IP allowlist**

### Option 3: Disable IP Allowlist (If Not Required)

If IP restrictions aren't necessary for your use case:

1. **Temporarily Disable:**
   - Go to IP allowlist settings
   - Toggle OFF or disable the allowlist
   - This allows all IPs (less secure but works for development)

2. **Test API Access:**
   - After disabling, test your API calls
   - If it works, the issue was the IP allowlist

## Troubleshooting "Can't Enable" Issue

### Issue 1: Button is Grayed Out
**Cause:** You might not have admin permissions at the right level

**Solution:**
- Verify you're in the `confluence-admins-yashbgv2002` group
- Try accessing from: https://admin.atlassian.com/o/[org-id]/security/ip-allowlist
- Or use site-level admin: https://yashbgv2002.atlassian.net/admin

### Issue 2: Allowlist Exists But Not Applied
**Cause:** The allowlist might not be associated with Confluence

**Solution:**
1. Edit the existing allowlist
2. Make sure **Confluence** is checked in the products list
3. Save and enable

### Issue 3: IP Format Issue
**Cause:** IP might be in wrong format

**Solution:**
- Use format: `125.20.250.6` (single IP)
- Or: `125.20.250.0/24` (IP range)
- Avoid: `125.20.250.6/32` unless specifically needed

## Testing After Configuration

Once you've added your IP:

```bash
# Test 1: Check if IP is allowed
curl -v https://yashbgv2002.atlassian.net/wiki/rest/api/space \
  -u yashbgv2002@gmail.com:YOUR_TOKEN \
  -H "Accept: application/json"

# Test 2: Via application
curl http://localhost:8000/confluence/spaces

# Test 3: Diagnostic script
python diagnose_confluence.py
```

## Expected Results

### ✅ Success:
- API calls return 200 or 403 (not 401)
- 403 means authentication works, just need permissions
- Application can connect to Confluence

### ❌ Still Failing:
- If still getting 401: IP allowlist might not be enabled
- If getting 403: Permissions issue (different from IP allowlist)
- Check allowlist status in admin panel

## Alternative: Use Dynamic IP Range

If your IP changes frequently:

1. **Use Your ISP's IP Range:**
   - Contact your ISP for your IP range
   - Add as CIDR: `125.20.250.0/24` (example)

2. **Use VPN with Static IP:**
   - Use a VPN service with static IP
   - Add that IP to allowlist

3. **Temporarily Disable for Development:**
   - Disable IP allowlist during development
   - Re-enable for production

## Quick Checklist

- [ ] Your IP: `125.20.250.6` is added to allowlist
- [ ] Confluence is selected in the allowlist products
- [ ] Allowlist is enabled/toggled ON
- [ ] You have admin permissions to modify allowlist
- [ ] Tested API access after configuration
- [ ] If IP changes, updated allowlist

## Important Notes

1. **IP Allowlist Blocks API Access:**
   - Even with valid credentials, IP allowlist can block API calls
   - This is a security feature to restrict access by location

2. **Organization vs Site Level:**
   - Organization-level allowlists apply to all sites
   - Site-level allowlists apply only to that site
   - Make sure you're configuring at the right level

3. **Allowlist Takes Effect Immediately:**
   - Changes should apply within seconds
   - No need to wait for propagation

## Next Steps

1. Add your IP (`125.20.250.6`) to the allowlist
2. Ensure Confluence is selected
3. Enable the allowlist
4. Test API access
5. If still not working, check if you need to configure at site level instead of org level
