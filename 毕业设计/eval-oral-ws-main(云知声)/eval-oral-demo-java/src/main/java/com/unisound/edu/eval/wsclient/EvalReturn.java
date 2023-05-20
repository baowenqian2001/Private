package com.unisound.edu.eval.wsclient;

import com.google.gson.annotations.SerializedName;

public class EvalReturn {
    @SerializedName("errcode")
    private String ErrorCode;

    @SerializedName("errmsg")
    private String ErrorMsg;

    public String getErrorCode() {
        return ErrorCode;
    }

    public void setErrorCode(String errorCode) {
        ErrorCode = errorCode;
    }

    public String getErrorMsg() {
        return ErrorMsg;
    }

    public void setErrorMsg(String errorMsg) {
        ErrorMsg = errorMsg;
    }

    public String toString() {
        return String.format("%s@%s", this.ErrorCode, this.ErrorMsg);
    }
}
