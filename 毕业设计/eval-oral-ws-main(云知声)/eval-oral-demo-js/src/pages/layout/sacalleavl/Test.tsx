import React, { useState, useEffect, Fragment, useRef } from 'react';
import cstyle from '../common.less';
import style from './test.less';
import Recorder from '@/utils/Recorder';
import { message, Button } from 'antd';
import guid from '@/utils/guid';
import { Config, AiCode } from '@/config';

function getColor(type: number, score: number = 0) {
  if (type != 4) {
    return score >= 7.5 ? '#00FF8E' : score >= 6 ? '#FFB700' : '#FF1F00';
  }
  return '#000';
}

const sentenceArr = {
  en: [
    'Reading  a  good  book  is  like  making  a  good  friend.',
    'Everything  that  you  learn  becomes  a  part  of  you  and  changes  you.',
    'We  should  learn  how  to  make  good  use  of  artificial  intelligence.',
    'Children  need  love,  especially  when  they  do  not  deserve  it.',
    'Learn  as  much  as  you  can  while  you  are  young,  since  life  becomes  too  busy  later.',
  ],
  cn: [
    '离离原上草，一岁一枯荣。野火烧不尽，  春风吹又生。',
    '北国风光，千里冰封，万里雪飘。望长城内外，惟余莽莽；大河上下，顿失滔滔。',
    '山不在高，有仙则名。水不在深，有龙则灵。斯是陋室，惟吾德馨。',
    '采莲是江南的旧俗，似乎很早就有，而六朝时为盛；从诗歌里可以约略知道。',
    '乌云越来越暗，越来越低，向海面直压下来，而波浪一边歌唱，一边冲向高空，去迎接那雷声。',
  ],
};

let recorder: any;
let ws: any;
let sid: string;

export default () => {
  const [current, setCurrent] = useState<string>('en');
  const [recording, setRecording] = useState(false);

  const [sidx, setIdx] = useState<number>(0);
  const [result, setResult] = useState<any>(null);
  const { appKey, path } = Config[AiCode.Eval];
  const audio: any = useRef();
  let snArr = current === 'en' ? sentenceArr.en : sentenceArr.cn;
  const sentence = snArr[sidx % snArr.length];
  function startRecording() {
    doRecording();
    setRecording(true);
  }
  function endRecording() {
    stopRecording();
    setRecording(false);
  }

  function doRecording() {
    createWs();
    recorder = new Recorder(onaudioprocess);
    setResult(null);

    function onaudioprocess(buffer: any) {
      if (ws && ws.readyState === 1) {
        ws.send(buffer);
      }
    }
    function createWs() {
      let wpsPath: string = '';
      let params = {};
      sid = guid();
      if (current === 'cn') {
        wpsPath = path['cn'];
        params = {
          EvalType: 'sentence',
          Language: 'cn',
          displayText: sentence,
          appkey: appKey,
          audioFormat: 'pcm',
          eof: sid,
        };
      } else if (current === 'en') {
        wpsPath = path['en'];
        params = {
          mode: 'sent',
          appkey: appKey,
          displayText: sentence,
          audioFormat: 'pcm',
          eof: sid,
          scoreCoefficient: '1.6',
        };
      }

      ws = new WebSocket(wpsPath);
      ws.onopen = () => {
        ws.send(JSON.stringify(params));
      };

      ws.onmessage = (evt: any) => {
        const result = JSON.parse(evt.data);
        if (result.errcode === 0) {
          setResult(result.result);
        }
        ws.close();
        recorder && recorder.stop();
      };

      ws.onclose = () => {
        ws = null;
      };
    }
    recorder.ready().then(
      () => {
        recorder.start();
        // if (current == 'en')
      },
      () => {
        message.warn('录音启动失败！');
        setRecording(false);
      },
    );
  }

  function stopRecording() {
    if (!recorder) return;
    if (!ws) return;

    audio.current.src = window.URL.createObjectURL(recorder.getWAVBlob(true));
    if (ws.readyState === 1) ws.send(sid);
  }
  console.log(result);
  return (
    <div
      style={{
        backgroundColor: '#f7f9fb',
      }}
      className={cstyle.bigBlock}
      id="test"
    >
      <div className={cstyle.title}>口语评测</div>
      <div className={style.boxContainer}>
        <div className={style.box}>
          <div className={cstyle.subTitle}>评测内容</div>
          <div className={style.borderBox}>
            <ul className={style.tabs}>
              <li
                className={`${style.tab} ${
                  current === 'en' ? style.active : ''
                }`}
                onClick={() => !recording && setCurrent('en')}
              >
                英语
              </li>
              <li
                className={`${style.tab} ${
                  current === 'cn' ? style.active : ''
                }`}
                onClick={() => !recording && setCurrent('cn')}
              >
                汉语
              </li>
            </ul>
            <div className={style.micbox}>
              {/* {recording && (
                <img
                  src={require('@/assets/icon_micwave.png')}
                  height="33"
                  style={{ position: 'absolute', zIndex: 0 }}
                />
              )} */}
              <div className={style.text}>{sentence}</div>
              <div className={style.desc}>
                点击开始录音后，朗读文本内容，点击停止提交评测
              </div>
              <div className={style.buttons}>
                <span
                  style={{ cursor: 'pointer' }}
                  onClick={() => {
                    setIdx(sidx + 1);
                  }}
                >
                  <img
                    src={require('@/assets/oneword/icon_change.png')}
                    alt=""
                  />
                  &nbsp;换一换
                </span>
                <div>
                  {!recording && (
                    <Button
                      type="primary"
                      onClick={() => {
                        audio.current && audio.current.pause();
                        startRecording();
                      }}
                    >
                      录音
                    </Button>
                  )}
                  {recording && (
                    <Button
                      type="primary"
                      onClick={() => {
                        endRecording();
                      }}
                    >
                      停止
                    </Button>
                  )}
                  <Button
                    style={{
                      marginLeft: 20,
                      background: 'transparent',
                      color: '#fff',
                    }}
                    onClick={() => {
                      audio.current.play();
                    }}
                  >
                    回放
                  </Button>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div className={style.box}>
          <div className={cstyle.subTitle}>评测结果</div>
          <div className={style.borderBox + ' ' + style.result}>
            {result && (
              <div className={style.showRes}>
                <div className={style.rstRow}>
                  <div className={style.rstBox}>
                    <div className={style.rstScore}>
                      {(+result.score).toFixed(2)}
                    </div>
                    <div className={style.rstDesc}>总分</div>
                  </div>
                </div>
                {result.lines.map((line: any, index: number) => (
                  <Fragment key={index}>
                    <div className={style.rstRow}>
                      <div className={style.rstBox}>
                        <div className={style.rstScore}>
                          {(+line.integrity).toFixed(2)}
                        </div>
                        <div className={style.rstDesc}>完整度</div>
                      </div>
                      <div className={style.rstBox}>
                        <div className={style.rstScore}>
                          {(+line.fluency).toFixed(2)}
                        </div>
                        <div className={style.rstDesc}>流利度</div>
                      </div>
                      <div className={style.rstBox}>
                        <div className={style.rstScore}>
                          {(+line.pronunciation).toFixed(2)}
                        </div>
                        <div className={style.rstDesc}>标准度</div>
                      </div>
                    </div>
                    <div className={style.rstWords}>
                      {line.words.map((word: any, index: number) => {
                        if (word.type != 4) {
                          if (word.type === 7)
                            return (
                              <span
                                key={word.text + index}
                                style={{ color: '#fff' }}
                              >
                                {word.text}
                              </span>
                            );
                          return (
                            <span
                              key={word.text + index}
                              style={{
                                color: getColor(word.type, word.score),
                              }}
                            >
                              {word.text}
                            </span>
                          );
                        }
                        return null;
                      })}
                    </div>
                  </Fragment>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
      <audio ref={audio} />
    </div>
  );
};
