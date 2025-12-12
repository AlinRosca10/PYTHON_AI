from flask import Blueprint, request, jsonify
from ai_utils import generate_palette_ai

bp = Blueprint("api", __name__, url_prefix="/api")

@bp.route("/generate_palette", methods=["POST"])
def generate_palette():
    """
    Body JSON: { "prompt": "night cyberpunk", "hint": "neon, dark", "nocache": false }
    Răspuns: { colors: [...], caption: "...", source: "openai|fallback", raw: "..."}
    """
    data = request.get_json(force=True, silent=True) or {}
    prompt = (data.get("prompt") or "").strip()
    hint = (data.get("hint") or "").strip()

    if not prompt:
        return jsonify({"error": "Missing prompt"}), 400

    # protecții simple
    if len(prompt) > 300:
        return jsonify({"error": "Prompt too long"}), 400

    result = generate_palette_ai(prompt, style_hint=hint)
    return jsonify(result)