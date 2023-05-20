import { defineConfig } from 'umi';

export default defineConfig({
  nodeModulesTransform: {
    type: 'none',
  },
  hash: true,
  publicPath: './',
  history: { type: 'memory' },
  routes: [
    {
      path: '/',
      component: '@/pages/layout/index',
      routes: [
        {
          path: '/sa-call-eval',
          component: '@/pages/layout/sacalleavl/index',
          title: '口语评测_英语口语评测_语音评测-云知声AI开放平台',
        },
        {
          path: '/',
          redirect: 'sa-call-eval',
        },
      ],
    },
  ],

  theme: {
    'primary-color': '#1564FF',
    'border-radius-base': '4px',
  },
});
