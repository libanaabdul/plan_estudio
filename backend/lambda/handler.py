"""
Lambda handler for Plan de Estudio — AWS backend.

Maintains the same action-based interface as the original Google Apps Script
so the frontend only needs to change the API_URL constant.

Actions:
  GET  ?action=getAll        → scan all items
  POST {action:'saveRow'}    → put/update one item
  POST {action:'saveAll'}    → batch write all items
  POST {action:'deleteRow'}  → delete one item
"""

import json
import os
from decimal import Decimal

import boto3
from boto3.dynamodb.conditions import Attr

TABLE_NAME = os.environ["TABLE_NAME"]
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(TABLE_NAME)

CORS = {
    "Access-Control-Allow-Origin": "https://tracker.cloudreviews.me",
    "Access-Control-Allow-Headers": "Content-Type,Authorization",
    "Access-Control-Allow-Methods": "GET,POST,OPTIONS",
}


# ── helpers ──────────────────────────────────────────────────────────────────

def _serial(obj):
    """JSON serialiser that converts Decimal → int/float."""
    if isinstance(obj, Decimal):
        return int(obj) if obj % 1 == 0 else float(obj)
    raise TypeError(f"Object of type {type(obj)} is not JSON serialisable")


def ok(body, status=200):
    return {
        "statusCode": status,
        "headers": CORS,
        "body": json.dumps(body, default=_serial),
    }


def err(msg, status=400):
    return {"statusCode": status, "headers": CORS, "body": json.dumps({"error": msg})}


def _normalise(item: dict) -> dict:
    """Ensure id is always stored as a string (DynamoDB PK)."""
    item = dict(item)
    item["id"] = str(item.get("id", ""))
    # Store booleans natively
    for key in ("done", "postponed"):
        val = item.get(key, False)
        if isinstance(val, str):
            item[key] = val.lower() in ("true", "1", "yes")
    return item


# ── handler ──────────────────────────────────────────────────────────────────

def lambda_handler(event, _context):
    method = event.get("httpMethod", "GET")
    qs = event.get("queryStringParameters") or {}

    # CORS preflight
    if method == "OPTIONS":
        return ok({})

    # GET ?action=getAll
    if method == "GET":
        if qs.get("action") == "getAll":
            items = []
            scan_kwargs = {}
            while True:
                resp = table.scan(**scan_kwargs)
                items.extend(resp.get("Items", []))
                if "LastEvaluatedKey" not in resp:
                    break
                scan_kwargs["ExclusiveStartKey"] = resp["LastEvaluatedKey"]

            items.sort(key=lambda x: (x.get("date", ""), x.get("id", "")))
            return ok(items)
        return err("Unknown action")

    # POST actions
    if method == "POST":
        try:
            body = json.loads(event.get("body") or "{}")
        except json.JSONDecodeError:
            return err("Invalid JSON body")

        action = body.get("action")

        if action == "saveRow":
            item = body.get("row")
            if not item:
                return err("Missing 'row'")
            table.put_item(Item=_normalise(item))
            return ok({"ok": True})

        if action == "saveAll":
            rows = body.get("rows", [])
            # DynamoDB batch_writer handles batches of 25 automatically
            with table.batch_writer() as batch:
                for row in rows:
                    batch.put_item(Item=_normalise(row))
            return ok({"ok": True, "count": len(rows)})

        if action == "deleteRow":
            item_id = str(body.get("id", ""))
            if not item_id:
                return err("Missing 'id'")
            table.delete_item(Key={"id": item_id})
            return ok({"ok": True})

        return err(f"Unknown action: {action}")

    return err(f"Method not allowed: {method}", 405)
