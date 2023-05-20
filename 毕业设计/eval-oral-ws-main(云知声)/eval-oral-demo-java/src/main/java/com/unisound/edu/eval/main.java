package com.unisound.edu.eval;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.unisound.edu.eval.wsclient.EvalParam;
import com.unisound.edu.eval.wsclient.WSClient;

import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.net.URI;
import java.util.concurrent.TimeUnit;

public class main {
    public static void main(String[] args) {
        WSClient client = new WSClient(URI.create("ws://101.231.106.182:18086/ws/eval/"));
        String appkey = "appkey";
        String mode = "sent";
        String audioFormat = "pcm";
        String displayTest = "eval test like nice to meet you";
        String eofString = "test eof string";
        String oriAudioFilePath = "/path/audio.pcm";

        InputStream in = null;

        try {
            client.connectBlocking();
            try {
                File f = new File(oriAudioFilePath);
                in = new FileInputStream(f);
                EvalParam.NormalEvalParam param = new EvalParam.NormalEvalParam(mode, appkey, audioFormat, displayTest, eofString);
                GsonBuilder builder = new GsonBuilder();
                Gson g = builder.create();
                String evalParamJSON = g.toJson(param);
                //第一个初始化的包可以放在client.onOpen()里面发送。
                client.send(evalParamJSON);
                try {
                    byte[] readBuf = new byte[3200];
                    int len;
                    String ret;
                    String err;
                    while (true) {
                        if ((len = in.read(readBuf)) == -1) {
                            break;
                        }
                        byte[] audioBuf = new byte[len];
                        System.arraycopy(readBuf, 0, audioBuf, 0, len);
                        System.out.printf("Send %d bytes\n", len);
                        client.send(audioBuf);
                        // 这里是使用已经存在的录音文件进行测试，根据采样率计算，一秒音频大小大概是32K，
                        // 所以这里需要等待一秒再发送下一个数据分片，模拟实时录音时的使用场景。
                        // 实际使用时需要根据上下文进行处理。
                        TimeUnit.SECONDS.sleep(1);
                        err = client.getEvalError();
                        if (!err.equals("")) {
                            System.out.printf("Error eval %s \n", err);
                            return;
                        }
                    }

                    client.send(eofString);
                    try {
                        ret = client.getEvalResult();
                    } catch (Exception e) {
                        e.printStackTrace();
                        err = client.getEvalError();
                        System.out.printf("Error eval with msg : %s\n", err);
                        return;
                    }
                    System.out.printf("Eval result is %s \n", ret);
                    client.close();
                } catch (Exception e) {
                    e.printStackTrace();
                    return;
                }
            } catch (Exception e) {
                e.printStackTrace();
                return;
            } finally {
                if (in != null) {
                    try {
                        in.close();
                    } catch (IOException e1) {
                    }
                }
            }
        } catch (Exception e) {
            e.printStackTrace();
            return;
        } finally {
            client.close();
        }
    }
}
