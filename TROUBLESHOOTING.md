# Troubleshooting Guide - SecuGen WebAPI Connection Issues

## Error: "TypeError: Failed to fetch"

This error occurs when the browser cannot connect to the SecuGen WebAPI service.

### Common Causes:

1. **SGIBIOSRV Service Not Running**
   - The SecuGen WebAPI client application is not started
   - The service may have crashed or stopped

2. **Service Not Accessible**
   - The service is not running on `https://localhost:8443`
   - Port 8443 may be blocked or in use by another application

3. **SSL Certificate Issues**
   - Browser doesn't trust the self-signed certificate
   - Certificate needs to be accepted manually

4. **Firewall Blocking Connection**
   - Windows Firewall or antivirus blocking the connection
   - Network security policies preventing localhost HTTPS

5. **Device Not Connected**
   - Fingerprint scanner not connected via USB
   - Device drivers not installed properly

## Solutions:

### Step 1: Verify SecuGen WebAPI is Running

1. **Check if the service is running:**
   - Look for "SecuGen WebAPI" or "SGIBIOSRV" in running processes
   - Check Windows Task Manager for the process

2. **Start the SecuGen WebAPI client:**
   - Locate and run the SecuGen WebAPI application
   - Usually found in: `C:\Program Files\SecuGen\` or similar
   - Look for `SgiBioSrv.exe` or similar executable

3. **Verify the service is listening:**
   - Open a web browser
   - Navigate to: `https://localhost:8443`
   - You should see a response (may need to accept SSL certificate)

### Step 2: Accept SSL Certificate

1. **In your browser:**
   - Navigate to `https://localhost:8443` directly
   - You may see a security warning
   - Click "Advanced" → "Proceed to localhost (unsafe)" or similar
   - This allows the browser to trust the self-signed certificate

2. **For Chrome/Edge:**
   - Click "Advanced"
   - Click "Proceed to localhost (unsafe)"

3. **For Firefox:**
   - Click "Advanced"
   - Click "Accept the Risk and Continue"

### Step 3: Check Firewall Settings

1. **Windows Firewall:**
   - Open Windows Defender Firewall
   - Check if port 8443 is blocked
   - Add an exception if needed

2. **Antivirus Software:**
   - Check your antivirus settings
   - Add SecuGen WebAPI to exceptions
   - Temporarily disable to test (re-enable after testing)

### Step 4: Verify Device Connection

1. **Check USB Connection:**
   - Ensure fingerprint scanner is connected via USB
   - Try a different USB port
   - Check if device appears in Device Manager

2. **Install/Update Drivers:**
   - Download latest SecuGen drivers from: http://www.secugen.com/download/drivers.htm
   - Install drivers as Administrator
   - Restart computer if needed

3. **Test Device:**
   - Use SecuGen's test utilities to verify device works
   - Check Device Manager for any error indicators

### Step 5: Test Connection Manually

1. **Using Browser:**
   ```javascript
   // Open browser console (F12) and run:
   fetch('https://localhost:8443/SGIFPCapture', {
       method: 'POST',
       headers: {'Content-Type': 'application/x-www-form-urlencoded'},
       body: 'timeout=1000&quality=50&licstr=&templateformat=ISO&imagewsqrate=0.75'
   })
   .then(r => r.json())
   .then(console.log)
   .catch(console.error);
   ```

2. **Using PowerShell:**
   ```powershell
   Invoke-WebRequest -Uri "https://localhost:8443/SGIFPCapture" -Method POST -ContentType "application/x-www-form-urlencoded" -Body "timeout=1000&quality=50"
   ```

### Step 6: Check Service Configuration

1. **Verify Port:**
   - Check SecuGen WebAPI configuration
   - Ensure it's set to port 8443
   - Check if HTTPS is enabled

2. **Check Logs:**
   - Look for SecuGen WebAPI log files
   - Usually in: `C:\Program Files\SecuGen\Logs\` or similar
   - Check for error messages

### Step 7: Alternative: Use HTTP Instead of HTTPS

If HTTPS continues to cause issues, you may need to:
1. Configure SecuGen WebAPI to use HTTP (port 8080 or similar)
2. Update the application URLs from `https://localhost:8443` to `http://localhost:8080`
3. **Note:** This is less secure and not recommended for production

## Quick Checklist:

- [ ] SecuGen WebAPI client application is running
- [ ] Service is accessible at `https://localhost:8443` in browser
- [ ] SSL certificate has been accepted in browser
- [ ] Fingerprint device is connected via USB
- [ ] Device drivers are installed and working
- [ ] Firewall is not blocking port 8443
- [ ] Antivirus is not blocking the connection
- [ ] No other application is using port 8443

## Still Having Issues?

1. **Restart Services:**
   - Stop SecuGen WebAPI
   - Disconnect and reconnect fingerprint device
   - Restart SecuGen WebAPI
   - Restart your web browser

2. **Check System Requirements:**
   - Windows 10/11 (x64)
   - Python 3.12.3
   - Latest SecuGen drivers
   - Modern browser (Chrome, Edge, Firefox)

3. **Contact Support:**
   - SecuGen Support: http://www.secugen.com/support/
   - Check SecuGen documentation
   - Review WebAPI installation guide

## Common Error Codes:

- **Error 3:** Failure to reach SecuGen Fingerprint Scanner
- **Error 53:** Device not found
- **Error 54:** Fingerprint image capture timeout
- **Error 55:** No device available
- **Error 56:** Driver load failed
- **Error 63:** SgiBioSrv didn't start

If you see these errors, the service is running but there's a device/driver issue.

