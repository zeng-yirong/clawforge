from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from .environment import SecureVaultEnvironment

_HIDDEN_HELP_MARKERS = ("prepare-rollout", "reset-rollout", "evaluate", "==SUPPRESS==")


def _get_data_root() -> Path:
    return Path(__file__).parent / "data"


def _get_state_root() -> Path:
    default = Path.home() / ".vault_state"
    return Path(os.environ.get("VAULT_STATE_ROOT", default))


def _get_session_id() -> str | None:
    return os.environ.get("VAULT_SESSION_ID")


class VaultArgumentParser(argparse.ArgumentParser):
    def format_help(self) -> str:
        help_text = super().format_help()
        lines = [
            line
            for line in help_text.splitlines()
            if not any(marker in line for marker in _HIDDEN_HELP_MARKERS)
        ]
        return "\n".join(lines) + ("\n" if help_text.endswith("\n") else "")

    def exit(self, status=0, message=None):
        if message:
            print(json.dumps({"status": "error", "message": message}, ensure_ascii=False), file=sys.stderr)
        sys.exit(status)


def main():
    base_parser = VaultArgumentParser(add_help=False)
    base_parser.add_argument("--session-id", dest="session_id", default=None, help=argparse.SUPPRESS)

    main_parser = VaultArgumentParser(description="Secure Vault CLI")
    sub = main_parser.add_subparsers(dest="command", metavar="")

    hidden = VaultArgumentParser(add_help=False)
    hidden.add_argument("--show-bindings", action="store_true")
    hidden.add_argument("--scenario-id", dest="scenario_id")
    hidden.add_argument("--session-id", dest="session_id", default=None, help=argparse.SUPPRESS)

    list_sc = sub.add_parser("list-scenarios", parents=[base_parser], help="List available scenarios")
    list_sc.set_defaults(func=lambda args, env: {"status": "success", "data": {"scenarios": env.repo.list_scenarios()}})

    prep = sub.add_parser("prepare-rollout", parents=[hidden], help=argparse.SUPPRESS)
    prep.set_defaults(func=lambda args, env: env.prepare_rollout(args.scenario_id, show_bindings=args.show_bindings))

    reset = sub.add_parser("reset-rollout", parents=[hidden], help=argparse.SUPPRESS)
    reset.set_defaults(func=lambda args, env: env.reset_rollout(args.session_id or _get_session_id()))

    gen_pw = sub.add_parser("generate-password", parents=[base_parser], help="Generate a password")
    gen_pw.add_argument("--length", type=int, default=16)
    gen_pw.add_argument("--charset", default="alphanumeric")
    gen_pw.set_defaults(func=lambda args, env: _execute(env, args.session_id, "generate_password", length=args.length, charset=args.charset))

    store_cred = sub.add_parser("store-credential", parents=[base_parser], help="Store a credential")
    store_cred.add_argument("--platform", required=True)
    store_cred.add_argument("--username", required=True)
    store_cred.add_argument("--password", required=True)
    store_cred.add_argument("--category-id", dest="category_id", default=None)
    store_cred.add_argument("--url", default=None)
    store_cred.set_defaults(func=lambda args, env: _execute(env, args.session_id, "store_credential", credential_data={
        "platform": args.platform,
        "username": args.username,
        "password": args.password,
        "category_id": args.category_id,
        "url": args.url,
    }))

    retrieve_cred = sub.add_parser("retrieve-credential", parents=[base_parser], help="Retrieve a credential")
    retrieve_cred.add_argument("--platform", required=True)
    retrieve_cred.set_defaults(func=lambda args, env: _execute(env, args.session_id, "retrieve_credential", platform=args.platform))

    list_creds = sub.add_parser("list-credentials", parents=[base_parser], help="List all credentials")
    list_creds.set_defaults(func=lambda args, env: _execute(env, args.session_id, "list_credentials"))

    classify_cred = sub.add_parser("classify-credential", parents=[base_parser], help="Classify a credential")
    classify_cred.add_argument("--credential-id", dest="credential_id", required=True)
    classify_cred.add_argument("--category-id", dest="category_id", required=True)
    classify_cred.set_defaults(func=lambda args, env: _execute(env, args.session_id, "classify_credential", credential_id=args.credential_id, category_id=args.category_id))

    setup_af = sub.add_parser("setup-autofill", parents=[base_parser], help="Setup autofill for a platform")
    setup_af.add_argument("--platform", required=True)
    setup_af.add_argument("--field-mappings", dest="field_mappings", default="{}")
    setup_af.set_defaults(func=lambda args, env: _execute(env, args.session_id, "setup_autofill", platform=args.platform, field_mappings=json.loads(args.field_mappings)))

    check_str = sub.add_parser("check-strength", parents=[base_parser], help="Check password strength")
    check_str.add_argument("--password", required=True)
    check_str.add_argument("--policy", default="{}")
    check_str.set_defaults(func=lambda args, env: _execute(env, args.session_id, "check_password_strength", password=args.password, policy=json.loads(args.policy)))

    summary_p = sub.add_parser("session-summary", parents=[base_parser], help="Get session summary")
    summary_p.set_defaults(func=lambda args, env: {"status": "success", "data": env.get_session_summary(args.session_id or _get_session_id())})

    eval_p = sub.add_parser("evaluate", parents=[base_parser], help=argparse.SUPPRESS)
    eval_p.set_defaults(func=lambda args, env: {"status": "success", "data": env.get_reward(args.session_id or _get_session_id())})

    args = main_parser.parse_args()

    data_root = _get_data_root()
    state_root = _get_state_root()
    env = SecureVaultEnvironment(data_root, state_root)

    if not args.command:
        main_parser.print_help()
        return

    try:
        result = args.func(args, env)
    except Exception as e:
        result = {"status": "error", "message": str(e)}

    print(json.dumps(result, ensure_ascii=False))


def _execute(env: SecureVaultEnvironment, session_id: str | None, action_type: str, **kwargs) -> dict:
    sid = session_id or _get_session_id()
    if not sid:
        return {"status": "error", "message": "No session bound"}
    session = env.store.load_session(sid)
    if not session:
        return {"status": "error", "message": f"Session {sid} not found"}
    action_idx = session["meta"]["action_index"]
    result = env.execute_action(sid, action_type, action_idx, **kwargs)
    return {"status": "success", "data": result}


if __name__ == "__main__":
    main()
