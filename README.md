# 🧠 igbot-mcp

**IGBot MCP** is a Python microservice responsible for handling automation and integrations for **IG Networks**.
This project uses **Docker** for packaging and lightweight isolated execution, ensuring portability and simple deployment.

---

## 🚀 Requirements

* **Docker** installed and running
  👉 [Official Docker installation guide](https://docs.docker.com/get-docker/)
* Optional: **Git** (to clone the repository)

---

## 📦 Project structure

```
igbot-mcp/
├── Dockerfile
├── README.md
├── app.py
├── requirements.txt
├── src/
└── infra/
```

---

## 🧰 Build the Docker image

Run the following command in the project root:

```bash
docker build -t mcp-igbot-server .
```

> This command builds a Docker image named **mcp-igbot-server** using the `Dockerfile` in the current directory.

---

## ▶️ Run the container

To start the MCP container:

```bash
docker run -d --env-file ./.env --name mcp -p 8080:8080 mcp-igbot-server
```

* `-d` → runs in detached mode
* `--name mcp` → sets the container name
* `-p 8080:8080` → maps port 8080 on the host to port 8080 inside the container

---

## 🧾 View logs

To check logs in real time:

```bash
docker logs -f mcp
```

---

## 🛑 Stop and remove the container

```bash
docker stop mcp && docker rm mcp
```

---

## 🔍 Test the service

Verify if the application is responding:

```bash
curl http://localhost:8080
```

> The response will depend on what `app.py` implements (for example, a Flask or FastAPI API).

---

## 🧑‍💻 Run locally (without Docker)

If you prefer to run it directly on your host system:

```bash
pip install -r requirements.txt
python app.py
```

---

## 📄 License

Internal project of **IG Networks** — restricted use.
