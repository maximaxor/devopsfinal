const express = require('express');
const { createProxyMiddleware } = require('http-proxy-middleware');
const app = express();

app.use(express.static('public'));

app.use('/api', createProxyMiddleware({
    target: 'http://orchestrator:8000',
    changeOrigin: true,
    pathRewrite: {
        '^/api': '/',
    },
}));

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`API Gateway running on port ${PORT}`));