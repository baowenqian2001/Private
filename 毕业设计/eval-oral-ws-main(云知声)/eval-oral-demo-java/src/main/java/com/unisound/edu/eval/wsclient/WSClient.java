package com.unisound.edu.eval.wsclient;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import org.java_websocket.client.WebSocketClient;
import org.java_websocket.handshake.ServerHandshake;

import java.net.URI;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;

public class WSClient extends WebSocketClient {
    private URI wsHostURI;
    private String evalResult;
    private String evalError;
    private Gson g;
    private CountDownLatch readResultLatch;


    public WSClient(String host) {
        this(URI.create(host));
    }

    public WSClient(URI serverURI) {
        super(serverURI);
        this.wsHostURI = serverURI;
        GsonBuilder b = new GsonBuilder();
        this.g = b.create();
        this.evalError = "";
        this.evalResult = "";
        this.readResultLatch = new CountDownLatch(1);
    }

    @Override
    public void onOpen(ServerHandshake handshakedata) {
        // 可以在这里发送初始化的JSON字段。
        System.out.println("opened connection");
    }

    @Override
    public void onMessage(String message) {
        if (!message.equals("")) {
            try {
                EvalReturn ret = g.fromJson(message, EvalReturn.class);
                if (ret.getErrorCode().equals("0")) {
                    this.evalResult = message;
                } else {
                    this.evalError = ret.toString();
                }
            } catch (Exception e) {
                this.evalError = message;
            }
        }
        if (this.readResultLatch != null) {
            this.readResultLatch.countDown();
            this.readResultLatch = null;
        }
    }

    @Override
    public void onClose(int code, String reason, boolean remote) {
    }

    @Override
    public void onError(Exception ex) {
        this.evalError = ex.toString();
        ex.printStackTrace();
        // if the error is fatal then onClose will be called additionally
    }

    public String getEvalResult() throws Exception {
        if (this.readResultLatch != null) {
            this.readResultLatch.await();
        }
        if (!this.evalError.equals("")) {
            throw new Exception("Eval error with msg " + this.evalError);
        }
        return this.evalResult;
    }

    public String getEvalError() throws Exception {
        if (this.readResultLatch != null) {
            this.readResultLatch.await(500, TimeUnit.MILLISECONDS);
        }
        return this.evalError;
    }
}
