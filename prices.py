from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs, urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
import json, os

RESOURCE_ID = os.getenv("DATA_GOV_RESOURCE_ID", "9ef84268-d588-465a-a308-a864a43d0070")
API_URL = f"https://api.data.gov.in/resource/{RESOURCE_ID}"
ALIASES = {
    "Corn": ["maize", "corn"], "Groundnut": ["groundnut", "peanut"],
    "Rice": ["paddy", "rice"], "Plantain": ["banana", "plantain"],
    "Onion": ["onion"], "Potato": ["potato"], "Chickpea": ["gram", "chana", "chickpea"],
    "Lentil": ["lentil", "masur"], "Pigeonpea": ["arhar", "tur", "pigeon"],
}

class handler(BaseHTTPRequestHandler):
    def _json(self, code, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "s-maxage=1800, stale-while-revalidate=3600")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        api_key = os.getenv("DATA_GOV_IN_API_KEY", "").strip()
        if not api_key:
            return self._json(503, {"error": "DATA_GOV_IN_API_KEY n'est pas défini dans les variables d'environnement."})
        query = parse_qs(urlparse(self.path).query)
        commodity = query.get("commodity", ["Onion"])[0]
        aliases = ALIASES.get(commodity, [commodity.lower()])
        params = {"api-key": api_key, "format": "json", "limit": "1000", "filters[commodity]": aliases[0]}
        req = Request(API_URL + "?" + urlencode(params), headers={"User-Agent": "HarvestAgriPrice/1.0"})
        try:
            with urlopen(req, timeout=20) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
            records = [r for r in payload.get("records", [])
                       if any(a in str(r.get("commodity", "")).lower() for a in aliases)]
            records.sort(key=lambda r: r.get("arrival_date", ""), reverse=True)
            return self._json(200, {"commodity": commodity, "records": records[:300],
                                    "source": "data.gov.in / AGMARKNET", "updated": payload.get("updated_date")})
        except HTTPError as exc:
            return self._json(exc.code, {"error": f"data.gov.in a répondu HTTP {exc.code}. Vérifiez la clé API."})
        except (URLError, TimeoutError, json.JSONDecodeError):
            return self._json(502, {"error": "Impossible de joindre l'API officielle des prix."})
