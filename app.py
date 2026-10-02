import os

from fastapi import FastAPI
from pymysql import connect
from pymongo import MongoClient


app = FastAPI(
    title="Production Application",
    version="1.0.0"
)


# =====================================================
# MYSQL
# =====================================================

def mysql_connection():

    return connect(
        host=os.getenv("MYSQL_HOST", "mysql"),
        port=int(os.getenv("MYSQL_PORT", "3306")),
        user=os.getenv("MYSQL_USER", "appuser"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DATABASE", "appdb"),
    )


# =====================================================
# MONGODB
# =====================================================

def mongo_connection():

    username = os.getenv("MONGO_ROOT_USERNAME")
    password = os.getenv("MONGO_ROOT_PASSWORD")

    return MongoClient(
        f"mongodb://{username}:{password}@mongodb:27017/"
        "?authSource=admin"
    )


# =====================================================
# ROOT
# =====================================================

@app.get("/")
def root():

    return {
        "application": "Production Application",
        "status": "running"
    }


# =====================================================
# HEALTH CHECK
# =====================================================

@app.get("/health")
def health():

    mysql_status = "down"
    mongo_status = "down"

    # MySQL check
    try:

        connection = mysql_connection()

        cursor = connection.cursor()

        cursor.execute("SELECT 1")

        cursor.fetchone()

        cursor.close()

        connection.close()

        mysql_status = "up"

    except Exception as error:

        mysql_status = f"error: {error}"


    # MongoDB check
    try:

        client = mongo_connection()

        client.admin.command("ping")

        client.close()

        mongo_status = "up"

    except Exception as error:

        mongo_status = f"error: {error}"


    overall_status = (
        "healthy"
        if mysql_status == "up"
        and mongo_status == "up"
        else "unhealthy"
    )


    return {

        "status": overall_status,

        "services": {

            "application": "up",

            "mysql": mysql_status,

            "mongodb": mongo_status
        }
    }


# =====================================================
# API TEST
# =====================================================

@app.get("/api")
def api():

    return {

        "message": "Backend API is working",

        "database": {

            "mysql": "configured",

            "mongodb": "configured"
        }
    }
