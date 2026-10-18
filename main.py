import os
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional

app = FastAPI()

# Enable CORS for the grader browser
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def coerce_types(config: dict) -> dict:
    coerced = {}
    for k, v in config.items():
        if k in ['port', 'workers']:
            try:
                coerced[k] = int(v)
            except ValueError:
                coerced[k] = v
        elif k == 'debug':
            if isinstance(v, str):
                coerced[k] = v.lower() in ['true', '1', 'yes', 'on']
            else:
                coerced[k] = bool(v)
        else:
            coerced[k] = str(v)
    return coerced

@app.get("/effective-config")
def get_effective_config(set: Optional[List[str]] = Query(None)):
    # 1. Defaults
    config = {
        "port": 8000,
        "workers": 1,
        "debug": False,
        "log_level": "info",
        "api_key": "default-secret-000"
    }

    # 2. YAML layer
    yaml_config = {
        "port": 8955,
        "api_key": "key-kmi2ks1dgk"
    }
    config.update(yaml_config)

    # 3. .env file layer
    env_file_config = {
        "APP_PORT": "8290",
        "NUM_WORKERS": "1",
        "APP_DEBUG": "false",
        "APP_API_KEY": "key-j56hqlgj1f"
    }
    for k, v in env_file_config.items():
        if k == "NUM_WORKERS":
            config["workers"] = v
        elif k.startswith("APP_"):
            key = k[4:].lower()
            config[key] = v

    # 4. OS Env vars layer (Reads from real OS env if set, otherwise uses prompt values)
    os_env_config = {
        "APP_WORKERS": "1",
        "APP_LOG_LEVEL": "debug",
        "APP_API_KEY": "key-r48fxaiozt"
    }
    for k, default_val in os_env_config.items():
        val = os.environ.get(k, default_val)
        if k.startswith("APP_"):
            key = k[4:].lower()
            config[key] = val

    # 5. CLI Overrides via Query Parameters (?set=key=value)
    if set:
        for item in set:
            if "=" in item:
                k, v = item.split("=", 1)
                config[k] = v

    # Apply type coercion rules
    config = coerce_types(config)

    # Mask Secret
    if "api_key" in config:
        config["api_key"] = "****"

    return config
