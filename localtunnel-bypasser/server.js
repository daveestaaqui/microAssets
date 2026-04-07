const http = require('http');
const https = require('https');

const TARGET_HOST = 'chubby-carrots-sleep.loca.lt';
const TARGET_URL = `https://${TARGET_HOST}`;

const server = http.createServer((req, res) => {
  const options = {
    hostname: TARGET_HOST,
    port: 443,
    path: req.url,
    method: req.method,
    headers: {
      ...req.headers,
      host: TARGET_HOST,
      'bypass-tunnel-reminder': 'true'
    }
  };

  const proxyReq = https.request(options, (proxyRes) => {
    res.writeHead(proxyRes.statusCode, proxyRes.headers);
    proxyRes.pipe(res, { end: true });
  });

  req.pipe(proxyReq, { end: true });
  
  proxyReq.on('error', (e) => {
    console.error('Proxy Error:', e.message);
    res.writeHead(500);
    res.end('Proxy Error: ' + e.message);
  });
});

const PORT = 3000;
server.listen(PORT, () => {
  console.log('====================================================');
  console.log('🚀 Localtunnel Bypasser is Running!');
  console.log(`🔗 Instead of Localtunnel, open this link in your browser:`);
  console.log(`👉 http://localhost:${PORT}`);
  console.log('====================================================');
  console.log('Press Ctrl+C to stop.');
});
