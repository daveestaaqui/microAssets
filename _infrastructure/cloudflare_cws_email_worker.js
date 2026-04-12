/**
 * Cloudflare Email Worker for CWS Wave Deployment
 * ===============================================
 * Parses incoming emails from the Chrome Web Store, extracts the extension name/status,
 * and POSTs the extracted state to the OmniSuite Railway Daemon webhook.
 */

export default {
    async email(message, env, ctx) {
      const allowedSenders = ["chromewebstore-noreply@google.com"];
      const fromAddress = message.headers.get("from");
      const subject = message.headers.get("subject") || "";
  
      // Ensure email actually comes from CWS. 
      // (This is a naive check; Cloudflare also ensures DKIM/SPF natively in the edge route)
      if (!allowedSenders.some(sender => fromAddress.includes(sender))) {
        console.log(`Skipping non-CWS email from: ${fromAddress}`);
        return;
      }
  
      // The payload we will send to our Railway Daemon
      const payload = {
        timestamp: new Date().toISOString(),
        extension_name: "unknown",
        event: "unknown",
        raw_subject: subject
      };
  
      // Parse Subject Line for Extension Name & Status
      // Examples:
      // "Your item 'JSON Formatter Pro' has been published"
      // "Action required: Your item 'Password Generator' was rejected"
      
      const publishedMatch = subject.match(/Your item '(.+?)' has been published/i);
      const rejectedMatch = subject.match(/Action required.*'(.+?)'/i);
  
      if (publishedMatch) {
        payload.extension_name = publishedMatch[1].trim();
        payload.event = "published";
      } else if (rejectedMatch) {
        payload.extension_name = rejectedMatch[1].trim();
        payload.event = "rejected";
      } else {
        console.log(`Skipping CWS email with unhandled subject: ${subject}`);
        return;
      }
  
      console.log(`Matched CWS Event: ${payload.event} for extension: ${payload.extension_name}`);
  
      // Ensure you set RAILWAY_WEBHOOK_URL and OMNISUITE_SECRET in your Cloudflare Worker environment variables
      const webhookUrl = env.RAILWAY_WEBHOOK_URL || "https://omnisuite-daemon.up.railway.app/webhook/cws-status";
      const webhookSecret = env.OMNISUITE_SECRET; // Random high-entropy string
  
      try {
        const response = await fetch(webhookUrl, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-Omnisuite-Token": webhookSecret
          },
          body: JSON.stringify(payload)
        });
  
        if (response.ok) {
          console.log(`Successfully notified Railway daemon: ${response.status}`);
        } else {
          console.error(`Railway daemon rejected the request. Status: ${response.status}`);
          const text = await response.text();
          console.error(`Response body: ${text}`);
        }
      } catch (err) {
        console.error(`Failed to trigger Railway webhook. Error:`, err);
      }
    }
  };
  
