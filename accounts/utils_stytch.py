# accounts/utils_stytch.py
from django.conf import settings

try:
    import stytch
    from stytch import Client as StytchClient
except Exception as e:
    raise ImportError("Stytch SDK not installed in this venv. Run: pip install stytch") from e

# Resolve environment object or fallback to the string ("test"/"live")
ENV_OBJECT = settings.STYTCH_ENV
try:
    from stytch import environments as _envs
    ENV_OBJECT = _envs.live if settings.STYTCH_ENV == "live" else _envs.test
except Exception:
    try:
        from stytch.core.environments import live as _live, test as _test
        ENV_OBJECT = _live if settings.STYTCH_ENV == "live" else _test
    except Exception:
        ENV_OBJECT = settings.STYTCH_ENV  # ok for many builds

# Error class (v8 vs v10+)
try:
    from stytch.error import StytchError
except Exception:
    try:
        from stytch.core.errors import StytchError
    except Exception:
        class StytchError(Exception):
            pass

client = StytchClient(
    project_id=settings.STYTCH_PROJECT_ID,
    secret=settings.STYTCH_SECRET,
    environment=ENV_OBJECT,
)

def _extract_method_id(resp: dict) -> str | None:
    """
    Return a method_id needed for client.otps.authenticate().
    Stytch responses may use 'method_id', or sometimes 'email_id'.
    """
    if not isinstance(resp, dict):
        return None
    return resp.get("method_id") or resp.get("email_id")

def start_email_otp(email: str) -> str | None:
    """
    Send OTP to email and return method_id to be used for verification.
    """
    resp = client.otps.email.login_or_create(email=email)
    return _extract_method_id(resp if isinstance(resp, dict) else getattr(resp, "__dict__", {}))

def verify_email_otp(code: str, *, method_id: str | None = None, email: str | None = None) -> bool:
    """
    Verify OTP. Prefer method_id + client.otps.authenticate().
    Fallback to client.otps.email.authenticate(email, code) if available.
    """
    try:
        if method_id:
            # Primary path for your SDK
            client.otps.authenticate(method_id=method_id, code=code)
            return True

        # Fallback path if SDK supports email.authenticate(email, code)
        # (some older builds do)
        if email and hasattr(client.otps, "email") and hasattr(client.otps.email, "authenticate"):
            client.otps.email.authenticate(email=email, code=code)
            return True

        # If neither path is available, fail clearly
        raise StytchError("No valid OTP authenticate path for this SDK version.")
    except StytchError:
        return False
