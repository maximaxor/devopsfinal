const express = require('express');
const { createProxyMiddleware } = require('http-proxy-middleware');
const app = express();

app.use('/api/', createProxyMiddleware({
    target: 'http://orchestrator.default.svc.cluster.local:8000',
    changeOrigin: true,
    pathRewrite: {
        '^/api': '/',
    },
}));

app.use('/', createProxyMiddleware({
    target: 'http://frontend.default.svc.cluster.local:7233',
    changeOrigin: true,
}));

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`API Gateway running on port ${PORT}`));