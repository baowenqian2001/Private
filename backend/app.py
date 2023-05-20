from fastapi import FastAPI

import uvicorn
from routers import route
from fastapi.middleware.cors import CORSMiddleware

import json
import random 


app = FastAPI()


def init_app(app):
    # 注册配置
    register_configs(app)
    # 注册中间件
    register_middlewares(app)
    # 注册路由
    register_routers(app)

def register_configs(app):
    pass  


def register_middlewares(app):
    # 跨域中间件
    origins = [
        "*"
    ]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

def register_routers(app):
    app.include_router(route.router)


if __name__ == '__main__':
    init_app(app)
    uvicorn.run(app, host="0.0.0.0", port=9092)
