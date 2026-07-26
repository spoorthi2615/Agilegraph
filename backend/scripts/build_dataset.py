import os
import subprocess
import json
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# Define base paths
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BACKEND_DIR, "data")

DIRS = [
    os.path.join(DATA_DIR, "validation", "repos"),
    os.path.join(DATA_DIR, "validation", "certs"),
    os.path.join(DATA_DIR, "validation", "rules"),
    os.path.join(DATA_DIR, "validation", "osv"),
    os.path.join(DATA_DIR, "validation", "nist"),
    os.path.join(DATA_DIR, "training", "java"),
    os.path.join(DATA_DIR, "training", "python"),
    os.path.join(DATA_DIR, "training", "go"),
    os.path.join(DATA_DIR, "training", "processed"),
    os.path.join(BACKEND_DIR, "models", "checkpoints"),
    os.path.join(BACKEND_DIR, "models", "metrics"),
    os.path.join(BACKEND_DIR, "models", "plots"),
    os.path.join(BACKEND_DIR, "experiments", "confusion_matrix"),
    os.path.join(BACKEND_DIR, "experiments", "roc"),
    os.path.join(BACKEND_DIR, "experiments", "loss"),
    os.path.join(BACKEND_DIR, "experiments", "reports"),
]

REPOSITORIES = {
    "java": [
        "https://github.com/WebGoat/WebGoat.git",
        "https://github.com/spring-projects/spring-security.git",
        "https://github.com/keycloak/keycloak.git",
        "https://github.com/apache/camel.git",
        "https://github.com/jenkinsci/jenkins.git",
        "https://github.com/apache/kafka.git",
        "https://github.com/elastic/elasticsearch.git",
        "https://github.com/apache/tomcat.git",
        "https://github.com/apache/shiro.git",
        "https://github.com/apache/hadoop.git",
        "https://github.com/apache/cassandra.git",
        "https://github.com/jitsi/jitsi-meet.git",
    ],
    "python": [
        "https://github.com/paramiko/paramiko.git",
        "https://github.com/ansible/ansible.git",
        "https://github.com/saltstack/salt.git",
        "https://github.com/home-assistant/core.git",
        "https://github.com/openstack/keystone.git",
        "https://github.com/django/django.git",
        "https://github.com/Flask-Middleware/flask-security.git",
        "https://github.com/psf/requests.git",
        "https://github.com/certbot/certbot.git",
        "https://github.com/twisted/twisted.git",
        "https://github.com/borgbackup/borg.git",
        "https://github.com/apache/airflow.git",
    ],
    "go": [
        "https://github.com/hashicorp/vault.git",
        "https://github.com/moby/moby.git",
        "https://github.com/traefik/traefik.git",
        "https://github.com/caddyserver/caddy.git",
        "https://github.com/kubernetes/kubernetes.git",
        "https://github.com/etcd-io/etcd.git",
        "https://github.com/minio/minio.git",
        "https://github.com/cockroachdb/cockroach.git",
        "https://github.com/hashicorp/terraform.git",
        "https://github.com/coredns/coredns.git",
        "https://github.com/gravitational/teleport.git",
        "https://github.com/syncthing/syncthing.git",
    ],
}

NIST_STANDARDS = {
  "legacy_vulnerable": [
    {
      "algorithm": "RSA",
      "description": "Vulnerable to Shor's algorithm on a quantum computer.",
      "risk_score": 1.0,
      "minimum_key_size_for_classical": 2048
    },
    {
      "algorithm": "ECC",
      "description": "Vulnerable to Shor's algorithm on a quantum computer.",
      "risk_score": 1.0,
      "minimum_key_size_for_classical": 256
    }
  ],
  "pqc_standards": [
    {
      "algorithm": "ML-KEM",
      "fips": "FIPS 203",
      "risk_score": 0.0,
      "quantum_safe": True
    },
    {
      "algorithm": "ML-DSA",
      "fips": "FIPS 204",
      "risk_score": 0.0,
      "quantum_safe": True
    },
    {
      "algorithm": "SLH-DSA",
      "fips": "FIPS 205",
      "risk_score": 0.0,
      "quantum_safe": True
    }
  ]
}

def create_directories():
    logging.info("Creating directory structure...")
    for d in DIRS:
        os.makedirs(d, exist_ok=True)
    logging.info("Directories created.")

def create_nist_standards():
    nist_path = os.path.join(DATA_DIR, "validation", "nist", "nist_standards.json")
    logging.info(f"Writing NIST standards to {nist_path}...")
    with open(nist_path, "w") as f:
        json.dump(NIST_STANDARDS, f, indent=2)

def clone_repositories():
    logging.info("Starting repository clones (this may take a while)...")
    for lang, repos in REPOSITORIES.items():
        for repo_url in repos:
            repo_name = repo_url.split("/")[-1].replace(".git", "")
            dest = os.path.join(DATA_DIR, "training", lang, repo_name)
            if os.path.exists(dest):
                logging.info(f"Skipping {repo_name}, already exists.")
                continue
            
            logging.info(f"Cloning {repo_name} into {dest}...")
            try:
                subprocess.run(["git", "clone", "--depth", "1", repo_url, dest], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except subprocess.CalledProcessError:
                logging.error(f"Failed to clone {repo_name}")

if __name__ == "__main__":
    create_directories()
    create_nist_standards()
    clone_repositories()
    logging.info("Dataset initialization complete!")
