"""Unit tests for scripts/bake_pipeline.py (the pure parts; no servers, no API).

Run: uv run --with pyyaml python3 -m unittest scripts/test_bake_pipeline.py
"""

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import bake_pipeline as bp  # noqa: E402

STACKER_YML = """
name: demo
app:
  type: custom
  image: demo/web:1.0
  ports:
    - "5678:5678"
monitoring:
  healthcheck:
    endpoint: /healthz
services:
  - name: db
    image: postgres:16
    ports:
      - "127.0.0.1:5432:5432"
config_contract:
  services:
    app:
      fields:
        N8N_ENCRYPTION_KEY: { mutability: generated, type: hex, length: 32 }
        N8N_HOST: { mutability: editable }
    db:
      fields:
        POSTGRES_PASSWORD: { mutability: generated, type: alphanumeric, length: 24 }
        POSTGRES_USER: { mutability: fixed }
      secret: [LEGACY_TOKEN]
"""

LOCK = """
target: cloud
server_ip: 203.0.113.7
ssh_user: root
ssh_port: 22
ssh_key: /home/me/.ssh/build_box
server_name: demo-build
deployment_id: 41
project_id: 12
deployed_at: "2026-10-15T09:00:00Z"
"""


class GeneratedKeys(unittest.TestCase):
    def test_generated_and_legacy_secret_fields_are_collected(self):
        self.assertEqual(
            bp.generated_keys(STACKER_YML),
            {"N8N_ENCRYPTION_KEY", "POSTGRES_PASSWORD", "LEGACY_TOKEN"},
        )

    def test_no_contract_means_no_generated_keys(self):
        self.assertEqual(bp.generated_keys("name: x\napp: {type: static}\n"), set())


BUYER_YML = """
name: demo
config_contract:
  services:
    studio:
      fields:
        OPENAI_API_KEY: {mutability: provided, pattern: "^sk-[A-Za-z0-9_-]+$", min_length: 40, max_length: 256}
        SUPABASE_SECRET_KEY: {mutability: provided, required: false, pattern: "^sb_secret_[A-Za-z0-9_-]+$"}
        PASSWORD: {mutability: generated, type: alphanumeric, min_length: 32}
        NOTE: {mutability: provided, required: false}
"""


class BuyerEnv(unittest.TestCase):
    """The smoke clone enters the buyer's keys, as a buyer does on Quick Deploy
    (2026-10-19: the clone of local-ai-packaged was refused with 422 because
    it sent none)."""

    def test_keys_with_a_pattern_get_a_random_value_of_that_shape(self):
        env = bp.buyer_env(BUYER_YML, overrides={})
        self.assertRegex(env["OPENAI_API_KEY"], r"^sk-[A-Za-z0-9]+$")
        self.assertTrue(40 <= len(env["OPENAI_API_KEY"]) <= 256)
        self.assertRegex(env["SUPABASE_SECRET_KEY"], r"^sb_secret_[A-Za-z0-9]+$")
        self.assertNotEqual(env, bp.buyer_env(BUYER_YML, overrides={}))

    def test_generated_and_optional_free_form_fields_are_left_alone(self):
        env = bp.buyer_env(BUYER_YML, overrides={})
        self.assertNotIn("PASSWORD", env)
        self.assertNotIn("NOTE", env)

    def test_an_override_wins(self):
        env = bp.buyer_env(BUYER_YML, overrides={"SMOKE_ENV_NOTE": "hello"})
        self.assertEqual(env["NOTE"], "hello")

    def test_a_required_key_with_no_known_shape_needs_an_override(self):
        yml = BUYER_YML + "        API_TOKEN: {mutability: provided}\n"
        with self.assertRaisesRegex(RuntimeError, "API_TOKEN"):
            bp.buyer_env(yml, overrides={})


class HealthUrl(unittest.TestCase):
    def test_app_port_and_declared_endpoint(self):
        self.assertEqual(
            bp.health_url("203.0.113.7", STACKER_YML), "http://203.0.113.7:5678/healthz"
        )

    def test_root_when_no_endpoint_and_80_without_a_port(self):
        yml = "name: x\napp:\n  ports: ['8080:80']\n"
        self.assertEqual(bp.health_url("203.0.113.7", yml), "http://203.0.113.7:8080/")
        self.assertEqual(bp.health_url("203.0.113.7", "name: x\n"), "http://203.0.113.7/")

    def test_a_loopback_bound_app_port_is_skipped(self):
        yml = "name: x\napp:\n  ports: ['127.0.0.1:9000:9000', '3000:3000']\n"
        self.assertEqual(bp.health_url("203.0.113.7", yml), "http://203.0.113.7:3000/")


class Lock(unittest.TestCase):
    def test_the_fields_the_bake_needs(self):
        lock = bp.parse_lock(LOCK)
        self.assertEqual(lock["deployment_id"], 41)
        self.assertEqual(lock["server_ip"], "203.0.113.7")
        self.assertEqual(lock["ssh_key"], "/home/me/.ssh/build_box")

    def test_a_lock_without_deployment_id_is_refused(self):
        with self.assertRaises(ValueError):
            bp.parse_lock("target: cloud\nserver_ip: 1.2.3.4\n")


class EnvFiles(unittest.TestCase):
    def test_parse_env(self):
        text = '# c\nA=1\nexport B="two words"\nC=\'x=y\'\n\nbad line\n'
        self.assertEqual(bp.parse_env(text), {"A": "1", "B": "two words", "C": "x=y"})


class ResetCheck(unittest.TestCase):
    KEYS = {"N8N_ENCRYPTION_KEY", "POSTGRES_PASSWORD"}

    def test_every_generated_value_differs(self):
        build = {"N8N_ENCRYPTION_KEY": "a" * 32, "POSTGRES_PASSWORD": "p1", "N8N_HOST": "h"}
        clone = {"N8N_ENCRYPTION_KEY": "b" * 32, "POSTGRES_PASSWORD": "p2", "N8N_HOST": "h"}
        self.assertEqual(bp.values_not_reset(build, clone, self.KEYS), [])

    def test_a_value_kept_or_missing_on_the_clone_is_reported(self):
        build = {"N8N_ENCRYPTION_KEY": "same", "POSTGRES_PASSWORD": "p1"}
        clone = {"N8N_ENCRYPTION_KEY": "same", "POSTGRES_PASSWORD": ""}
        self.assertEqual(
            bp.values_not_reset(build, clone, self.KEYS),
            ["N8N_ENCRYPTION_KEY (same value)", "POSTGRES_PASSWORD (empty on the clone)"],
        )


    def test_no_generated_value_found_on_the_build_box_is_not_a_pass(self):
        # An unreadable .env must not let the check pass with nothing compared.
        self.assertEqual(
            bp.values_not_reset({}, {"N8N_ENCRYPTION_KEY": "x"}, self.KEYS),
            ["none of the generated keys found on the build box"],
        )


class BakesRow(unittest.TestCase):
    def test_the_row_lists_the_servers_to_remove(self):
        row = bp.bakes_row(
            stack="n8n",
            version="1.2.0",
            image_id=555,
            smoke="ok",
            servers=["build box demo-build 203.0.113.7", "clone 9001 198.51.100.4"],
            date="2026-10-15",
        )
        self.assertEqual(
            row,
            "| 2026-10-15 | n8n | 1.2.0 | 555 | ok | build box demo-build 203.0.113.7; clone 9001 198.51.100.4 |",
        )


class SmokeAndPromote(unittest.TestCase):
    """smoke() with the API and the servers faked: what it asks stacker for."""

    def run_smoke(self, healthy=True, promote_status=200, job_id="job-1"):
        calls = []

        def api(method, path, body=None, timeout=60):
            calls.append((method, path, body))
            if path == "/api/v1/deploy/clone":
                return 200, {"server_id": 9001, "public_ipv4": "198.51.100.4",
                             "ssh_private_key": "KEY"}
            if path.endswith("/promote"):
                return promote_status, {"item": {"promoted": True}}
            raise AssertionError(f"unexpected call {method} {path}")

        fakes = {
            "api": api,
            "wait_http": lambda url, timeout=900: (healthy, "fake"),
            "ssh": lambda *a, **k: "N8N_ENCRYPTION_KEY=new\nPOSTGRES_PASSWORD=new\n",
            "host_key": lambda ip: "clone-key",
        }
        saved = {name: getattr(bp, name) for name in fakes}
        for name, fake in fakes.items():
            setattr(bp, name, fake)
        try:
            with tempfile.TemporaryDirectory() as d:
                bakes = Path(d) / "BAKES.md"
                ok = bp.smoke(
                    "demo", "1.0", 555, STACKER_YML,
                    {"N8N_ENCRYPTION_KEY": "old", "POSTGRES_PASSWORD": "old"},
                    "build-key", ["N8N_ENCRYPTION_KEY", "POSTGRES_PASSWORD"],
                    ["build box demo-build 203.0.113.7"], bakes,
                    log=lambda *a: None, job_id=job_id,
                )
                row = bakes.read_text().splitlines()[-1]
        finally:
            for name, real in saved.items():
                setattr(bp, name, real)
        return ok, calls, row

    def test_the_smoke_clone_asks_for_the_unpromoted_bake(self):
        _, calls, _ = self.run_smoke()
        clone = [body for _, path, body in calls if path == "/api/v1/deploy/clone"]
        self.assertEqual(clone[0]["channel"], "unstable")

    def test_a_green_smoke_promotes_the_bake(self):
        ok, calls, row = self.run_smoke()
        self.assertTrue(ok)
        self.assertIn(("POST", "/api/admin/bake/job-1/promote", None), calls)
        self.assertIn("| ok, promoted |", row)

    def test_a_failed_smoke_does_not_promote(self):
        ok, calls, _ = self.run_smoke(healthy=False)
        self.assertFalse(ok)
        self.assertFalse([c for c in calls if c[1].endswith("/promote")])

    def test_a_refused_promote_is_not_a_pass(self):
        ok, _, row = self.run_smoke(promote_status=409)
        self.assertFalse(ok)
        self.assertIn("promote refused 409", row)

    def test_a_smoke_repeated_on_its_own_promotes_nothing(self):
        ok, calls, row = self.run_smoke(job_id=None)
        self.assertTrue(ok)
        self.assertFalse([c for c in calls if c[1].endswith("/promote")])
        self.assertIn("| ok |", row)


if __name__ == "__main__":
    unittest.main()
