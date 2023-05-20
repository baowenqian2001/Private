export enum AiCode {
  Eval = 'sa-call-eval',
}

export const Config = {
  [AiCode.Eval]: {
    appKey: 'uus46rhwq3x75562p2cd7f7qplwso6wt5xd4qqae',
    secret: '41834fffb1dbc925eddba3dca1e6f036',
    path: {
      cn: 'wss://wss-edu.hivoice.cn:443/ws/eval/',
      en: 'wss://wss-edu.hivoice.cn:443/ws/eval/',
    },
  },
};
