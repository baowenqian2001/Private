package com.unisound.edu.eval.wsclient;

import com.google.gson.annotations.SerializedName;

public class EvalParam {
    public static class NormalEvalParam {
        /**
         * (必填) mode 可设置的内容值为word,sent,para,qa,retell，设置评测模式
         */
        @SerializedName("mode")
        private String Mode;

        /**
         * (普通评测必填) displayText 评测文本
         */
        @SerializedName("displayText")
        private String DisplayText;

        /**
         * (必填) appkey 访问凭证
         */
        @SerializedName("appkey")
        private String Appkey;

        /**
         * (可选值) scoreCoefficient 打分系数
         */
        @SerializedName("scoreCoefficient")
        private String ScoreCoefficient;

        /**
         * (可选值) userID 用户信息
         */
        @SerializedName("userID")
        private String UserID;

        /**
         * (必填)audioFormat 音频格式，支持16K单声道mp3,speex格式
         */
        @SerializedName("audioFormat")
        private String AudioFormat;

        /**
         * (必填)eof 设置eof消息包内容，客户端需要该内容的唯一性，可选用uuid。
         */
        @SerializedName("eof")
        private String EOF;

        public NormalEvalParam(String mode,
                               String appkey,
                               String audioFormat,
                               String displayText,
                               String eofString) {
            this(mode, appkey, "user id", "1.6", audioFormat, displayText, eofString);
        }

        public NormalEvalParam(String mode,
                               String appkey,
                               String userID,
                               String scoreCoefficient,
                               String audioFormat,
                               String displayText,
                               String eofString) {
            this.Mode = mode;
            this.Appkey = appkey;
            this.UserID = userID;
            this.ScoreCoefficient = scoreCoefficient;
            this.AudioFormat = audioFormat;
            this.DisplayText = displayText;
            this.EOF = eofString;
        }

        public String getMode() {
            return Mode;
        }

        public void setMode(String mode) {
            Mode = mode;
        }

        public String getDisplayText() {
            return DisplayText;
        }

        public void setDisplayText(String displayText) {
            DisplayText = displayText;
        }

        public String getAppkey() {
            return Appkey;
        }

        public void setAppkey(String appkey) {
            Appkey = appkey;
        }

        public String getScoreCoefficient() {
            return ScoreCoefficient;
        }

        public void setScoreCoefficient(String scoreCoefficient) {
            ScoreCoefficient = scoreCoefficient;
        }

        public String getUserID() {
            return UserID;
        }

        public void setUserID(String userID) {
            UserID = userID;
        }

        public String getAudioFormat() {
            return AudioFormat;
        }

        public void setAudioFormat(String audioFormat) {
            AudioFormat = audioFormat;
        }

        public String getEOF() {
            return EOF;
        }

        public void setEOF(String EOF) {
            this.EOF = EOF;
        }
    }
}
