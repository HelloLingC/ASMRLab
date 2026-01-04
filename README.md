# AudioLab - AI音频处理应用

一个整合了Python后端和Vue前端的AI音频处理应用。

## 项目结构

```
AudioLab/
├── backend/              # Python后端 (FastAPI)
│   ├── main.py          # 主应用文件
│   ├── requirements.txt # Python依赖
│   └── uploads/         # 上传文件目录（自动创建）
├── src/                 # Vue前端
│   ├── components/      # Vue组件
│   ├── views/           # 页面视图
│   ├── services/        # API服务
│   └── router/          # 路由配置
├── package.json         # 前端依赖
└── vite.config.js       # Vite配置（包含代理设置）
```

## 快速开始

### 1. 安装前端依赖

```bash
npm install
```

### 2. 安装后端依赖

```bash
# 创建虚拟环境（推荐）
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 安装依赖
cd backend
pip install -r requirements.txt
```

### 3. 启动后端服务

```bash
cd backend
python main.py
```

后端将在 `http://localhost:8000` 启动

### 4. 启动前端开发服务器

```bash
npm run dev
```

前端将在 `http://localhost:5173` 启动

## API端点

- `GET /` - API信息
- `GET /api/health` - 健康检查
- `POST /api/upload` - 上传音频文件
- `POST /api/process` - 处理音频文件

## 开发说明

### 前端开发

- 前端使用Vue 3 + Vite
- API调用通过 `/api` 路径，Vite会自动代理到后端 `http://localhost:8000`
- API服务文件位于 `src/services/api.js`

### 后端开发

- 后端使用FastAPI框架
- 支持CORS，允许前端跨域访问
- 上传的文件保存在 `backend/uploads/` 目录

### 添加新的音频处理功能

1. 在 `backend/main.py` 中添加新的处理逻辑
2. 在 `src/services/api.js` 中添加对应的API调用方法
3. 在 `src/views/AudioProcessView.vue` 中添加UI按钮和功能

## 技术栈

- **前端**: Vue 3, Vite, Vue Router, Axios
- **后端**: FastAPI, Uvicorn, Python

## 注意事项

- 确保后端在启动前端之前运行
- 上传的音频文件会保存在 `backend/uploads/` 目录
- 开发时，Vite代理会自动处理跨域问题
