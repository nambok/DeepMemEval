"""Programmatic persona generator for DeepMemEval.

Generates diverse personas with evolving timelines by combining template pools.
Each persona has 8-14 timeline entries with supersession chains and dependency edges.

All facts are phrased as STATES, not actions.
"""

import random
from datetime import datetime, timedelta

random.seed(42)

# --- Name pools ---
FIRST_NAMES = [
    "Alex", "Maria", "James", "Priya", "Tom", "Sarah", "Wei", "Carlos",
    "Yuki", "Fatima", "Dmitri", "Amara", "Liam", "Zara", "Henrik",
    "Sofia", "Raj", "Elena", "Omar", "Kenji", "Ines", "Marcus",
    "Aisha", "David", "Mei", "Andre", "Nadia", "Felix", "Leila",
    "Sven", "Rosa", "Kofi", "Hana", "Patrick", "Chiara", "Arjun",
    "Freya", "Leo", "Dina", "Hugo", "Mina", "Ravi", "Clara",
    "Noah", "Ayla", "Bruno", "Yara", "Theo", "Kira", "Emil",
]

LAST_NAMES = [
    "Chen", "Santos", "Kim", "Patel", "O'Brien", "Tanaka", "Al-Rashid",
    "Okafor", "Johansson", "Martinez", "Volkov", "Singh", "Muller",
    "Costa", "Nguyen", "Berg", "Rossi", "Petrov", "Yamamoto", "Khan",
    "Fernandez", "Larsson", "Park", "Ali", "Weber", "Torres",
    "Nakamura", "Schmidt", "Hernandez", "Sato", "Dubois", "Jensen",
    "Kovalenko", "Gupta", "Fischer", "Moreau", "Watanabe", "Reyes",
    "Andersen", "Takahashi", "Gonzalez", "Ivanov", "Das", "Berger",
    "Silva", "Eriksson", "Ito", "Cruz", "Hoffman", "Lee",
]

ROLES = [
    "Backend Developer", "Frontend Developer", "Full-Stack Developer",
    "DevOps Engineer", "Data Scientist", "ML Engineer", "Product Manager",
    "Mobile Developer", "Security Engineer", "Platform Engineer",
    "Data Engineer", "Site Reliability Engineer", "QA Engineer",
    "Solutions Architect", "Tech Lead",
]

EXPERIENCES = ["junior", "mid", "senior"]
STYLES = ["technical", "casual", "concise", "verbose", "business"]

COMPANIES = [
    ("DataFlow", "startup", 5), ("PixelCraft", "design agency", 12),
    ("PayScale", "fintech company", 50), ("MedInsight", "healthtech startup", 8),
    ("CloudMetrics", "B2B SaaS company", 30), ("NexGen Labs", "AI startup", 15),
    ("ShipFast", "logistics platform", 40), ("GreenTech", "cleantech company", 25),
    ("CodeForge", "dev tools company", 20), ("DataPipe", "data platform", 35),
    ("SecureNet", "cybersecurity firm", 45), ("AppVista", "mobile-first startup", 10),
    ("MLOps.io", "ML platform company", 18), ("DevHub", "developer community", 7),
    ("Quantum Labs", "quantum computing startup", 6), ("EdgeAI", "edge computing firm", 22),
    ("FinFlow", "payments company", 55), ("HealthBridge", "telehealth startup", 14),
    ("EduTech", "edtech company", 28), ("GameForge", "indie game studio", 9),
    ("AutoScale", "infrastructure startup", 11), ("DataVault", "data privacy company", 16),
    ("CloudNine", "cloud consulting", 32), ("BioCompute", "biotech startup", 13),
    ("RetailOS", "retail tech company", 42), ("TravelAI", "travel tech startup", 19),
    ("FoodChain", "food delivery platform", 38), ("PropTech", "real estate tech", 24),
    ("InsureTech", "insurance startup", 21), ("CryptoBase", "blockchain company", 17),
]

# --- Technology evolution pools ---
# Each pool is a list of (category, chains, stable_facts, dependency_edges)
# chains: list of supersession chains, each chain is [(fact, context), ...]
# stable: facts that don't change
# deps: (category, depends_on_category)

BACKEND_STACKS = [
    {
        "chains": [
            ("language", [
                ("Uses Python with Flask for the backend", "Starting new microservices"),
                ("Uses Python with FastAPI for the backend", "Needed async support and auto-docs"),
            ]),
            ("database", [
                ("Uses MySQL for the primary database", "Legacy system"),
                ("Uses PostgreSQL for the primary database", "Better JSON support needed"),
                ("Uses CockroachDB for the primary database", "Needed horizontal scaling"),
            ]),
            ("cache", [
                ("Uses Redis for caching", "Standard setup"),
                ("Uses Memcached for caching", "Simpler caching needs"),
            ]),
        ],
        "stable": [
            ("api_style", "Uses REST with OpenAPI specs for the API"),
            ("auth", "Uses JWT tokens for authentication"),
        ],
        "deps": [
            ("testing", "language", "Uses pytest with coverage for backend tests"),
            ("migrations", "database", "Uses Alembic for database migrations"),
        ],
    },
    {
        "chains": [
            ("language", [
                ("Uses Node.js with Express for the backend", "Quick prototyping"),
                ("Uses TypeScript with NestJS for the backend", "Needed better type safety"),
            ]),
            ("database", [
                ("Uses MongoDB for the primary database", "Document model fit the data"),
                ("Uses PostgreSQL for the primary database", "Needed ACID transactions"),
            ]),
            ("message_queue", [
                ("Uses RabbitMQ for async messaging", "Event-driven architecture"),
                ("Uses Apache Kafka for async messaging", "Higher throughput requirements"),
            ]),
        ],
        "stable": [
            ("api_style", "Uses GraphQL with Apollo Server for the API"),
            ("auth", "Uses OAuth 2.0 with Auth0 for authentication"),
        ],
        "deps": [
            ("orm", "language", "Uses Prisma ORM for database access"),
            ("testing", "language", "Uses Jest for backend API tests"),
        ],
    },
    {
        "chains": [
            ("language", [
                ("Uses Java with Spring Boot for the backend", "Enterprise microservices"),
                ("Uses Kotlin with Ktor for the backend", "Modern JVM language preference"),
            ]),
            ("database", [
                ("Uses Oracle Database for the primary database", "Enterprise requirement"),
                ("Uses PostgreSQL for the primary database", "Cost reduction initiative"),
            ]),
        ],
        "stable": [
            ("api_style", "Uses gRPC for internal service communication"),
            ("auth", "Uses Keycloak for identity management"),
            ("search", "Uses Elasticsearch for full-text search"),
        ],
        "deps": [
            ("build", "language", "Uses Gradle for build automation"),
            ("testing", "language", "Uses JUnit 5 for backend tests"),
            ("profiling", "language", "Uses VisualVM for JVM profiling"),
        ],
    },
    {
        "chains": [
            ("language", [
                ("Uses Go for the backend services", "High-performance APIs"),
                ("Uses Rust for the backend services", "Needed memory safety guarantees"),
            ]),
            ("database", [
                ("Uses SQLite for the embedded database", "Single-server deployment"),
                ("Uses TiDB for the distributed database", "Scaled to multiple regions"),
            ]),
        ],
        "stable": [
            ("api_style", "Uses REST with Protocol Buffers for the API"),
            ("auth", "Uses mTLS for service-to-service authentication"),
        ],
        "deps": [
            ("testing", "language", "Uses the built-in testing framework for backend tests"),
            ("linting", "language", "Uses golangci-lint for code quality checks"),
        ],
    },
    {
        "chains": [
            ("language", [
                ("Uses Ruby on Rails for the backend", "Rapid prototyping"),
                ("Uses Elixir with Phoenix for the backend", "Needed real-time WebSocket support"),
            ]),
            ("database", [
                ("Uses PostgreSQL with PostGIS for the database", "Geospatial queries"),
                ("Uses SurrealDB for the database", "Wanted a multi-model database"),
            ]),
        ],
        "stable": [
            ("api_style", "Uses REST with JSON:API spec for the API"),
            ("queue", "Uses Sidekiq for background job processing"),
        ],
        "deps": [
            ("testing", "language", "Uses RSpec for backend tests"),
            ("package_mgr", "language", "Uses Bundler for dependency management"),
        ],
    },
    {
        "chains": [
            ("language", [
                ("Uses C# with ASP.NET Core for the backend", "Enterprise web services"),
                ("Uses F# with Giraffe for the backend", "Functional programming preference"),
            ]),
            ("database", [
                ("Uses SQL Server for the primary database", "Microsoft ecosystem"),
                ("Uses PostgreSQL for the primary database", "Cross-platform requirement"),
            ]),
        ],
        "stable": [
            ("api_style", "Uses minimal APIs with OpenAPI for the endpoints"),
            ("auth", "Uses Azure AD B2C for identity management"),
        ],
        "deps": [
            ("testing", "language", "Uses xUnit for backend tests"),
            ("ide_tooling", "language", "Uses OmniSharp for IDE integration"),
        ],
    },
]

FRONTEND_STACKS = [
    {
        "chains": [
            ("framework", [
                ("Uses React with TypeScript for the frontend", "Standard SPA"),
                ("Uses Next.js with React for the frontend", "Needed SSR for SEO"),
                ("Uses Remix for the frontend", "Better data loading patterns"),
            ]),
            ("styling", [
                ("Uses Tailwind CSS for styling", "Utility-first approach"),
                ("Uses CSS Modules with PostCSS for styling", "Component-scoped styles"),
            ]),
        ],
        "stable": [
            ("bundler", "Uses Vite as the frontend build tool"),
            ("icons", "Uses Lucide React for icons"),
        ],
        "deps": [
            ("state", "framework", "Uses React Context with useReducer for state management"),
            ("testing", "framework", "Uses Vitest with React Testing Library for frontend tests"),
        ],
    },
    {
        "chains": [
            ("framework", [
                ("Uses Vue 3 with Composition API for the frontend", "Reactive UI"),
                ("Uses Nuxt 3 for the frontend with SSR", "SEO and performance"),
            ]),
            ("styling", [
                ("Uses UnoCSS for styling", "Atomic CSS approach"),
                ("Uses Vuetify for the component library and styling", "Material Design requirement"),
            ]),
        ],
        "stable": [
            ("bundler", "Uses Vite as the frontend build tool"),
            ("i18n", "Uses Vue I18n for internationalization"),
        ],
        "deps": [
            ("state", "framework", "Uses Pinia for state management"),
            ("testing", "framework", "Uses Vitest with Vue Test Utils for frontend tests"),
        ],
    },
    {
        "chains": [
            ("framework", [
                ("Uses Angular for the frontend", "Enterprise SPA"),
                ("Uses SolidJS for the frontend", "Better fine-grained reactivity"),
            ]),
            ("styling", [
                ("Uses SCSS with BEM methodology for styling", "Structured CSS"),
                ("Uses Tailwind CSS for styling", "Faster iteration"),
            ]),
        ],
        "stable": [
            ("bundler", "Uses esbuild as the frontend build tool"),
        ],
        "deps": [
            ("state", "framework", "Uses NgRx for state management"),
            ("testing", "framework", "Uses Karma with Jasmine for frontend tests"),
        ],
    },
    {
        "chains": [
            ("framework", [
                ("Uses Svelte for the frontend", "Minimal framework overhead"),
                ("Uses SvelteKit for the frontend", "Needed routing and SSR"),
            ]),
            ("styling", [
                ("Uses Tailwind CSS for styling", "Quick prototyping"),
                ("Uses vanilla CSS with Svelte scoped styles", "Simplicity"),
            ]),
        ],
        "stable": [
            ("animation", "Uses Motion One for frontend animations"),
        ],
        "deps": [
            ("testing", "framework", "Uses Playwright for end-to-end frontend tests"),
        ],
    },
]

DEVOPS_STACKS = [
    {
        "chains": [
            ("orchestration", [
                ("Uses Kubernetes on EKS for container orchestration", "Cloud-native deployment"),
                ("Uses Docker Compose for container orchestration", "Simplified the stack"),
            ]),
            ("ci", [
                ("Uses GitHub Actions for CI/CD pipelines", "GitHub-native workflow"),
                ("Uses CircleCI for CI/CD pipelines", "Faster build times"),
            ]),
            ("iac", [
                ("Uses Terraform for infrastructure as code", "Multi-cloud IaC"),
                ("Uses Pulumi for infrastructure as code", "Preferred real programming languages"),
                ("Uses OpenTofu for infrastructure as code", "Open-source Terraform fork"),
            ]),
        ],
        "stable": [
            ("monitoring", "Uses Datadog for monitoring and observability"),
            ("secrets", "Uses HashiCorp Vault for secrets management"),
        ],
        "deps": [
            ("helm", "orchestration", "Uses Helm charts for Kubernetes deployments"),
            ("pipeline_config", "ci", "Uses reusable GitHub Actions workflows"),
        ],
    },
    {
        "chains": [
            ("orchestration", [
                ("Uses Docker Swarm for container orchestration", "Simple cluster management"),
                ("Uses Nomad for workload orchestration", "Lighter weight than Kubernetes"),
            ]),
            ("ci", [
                ("Uses Jenkins for CI/CD pipelines", "Self-hosted CI"),
                ("Uses Drone CI for CI/CD pipelines", "Container-native CI"),
            ]),
            ("iac", [
                ("Uses CloudFormation for infrastructure as code", "AWS-native IaC"),
                ("Uses CDK for infrastructure as code", "Programmatic AWS infrastructure"),
            ]),
        ],
        "stable": [
            ("monitoring", "Uses Prometheus with Grafana for monitoring"),
            ("logging", "Uses the ELK stack for centralized logging"),
        ],
        "deps": [
            ("service_mesh", "orchestration", "Uses Consul for service discovery"),
            ("pipeline_config", "ci", "Uses Jenkinsfile declarative pipelines"),
        ],
    },
]

DATA_STACKS = [
    {
        "chains": [
            ("ml_framework", [
                ("Uses PyTorch for model training", "Flexibility and debugging"),
                ("Uses JAX for model training", "Better performance on TPUs"),
            ]),
            ("notebook", [
                ("Uses Jupyter notebooks for data exploration", "Standard data science workflow"),
                ("Uses Marimo for reactive notebook exploration", "Better reproducibility"),
            ]),
            ("data_processing", [
                ("Uses pandas for data processing", "Standard tabular data tool"),
                ("Uses Polars for data processing", "10x faster on large datasets"),
            ]),
        ],
        "stable": [
            ("experiment", "Uses Weights & Biases for experiment tracking"),
            ("feature_store", "Uses Feast for the feature store"),
        ],
        "deps": [
            ("model_serving", "ml_framework", "Uses TorchServe for model serving"),
            ("preprocessing", "data_processing", "Uses pandas-compatible preprocessing pipelines"),
        ],
    },
    {
        "chains": [
            ("ml_framework", [
                ("Uses TensorFlow for model training", "Production-ready ecosystem"),
                ("Uses PyTorch Lightning for model training", "Better training loop abstraction"),
            ]),
            ("data_processing", [
                ("Uses Apache Spark for large-scale data processing", "Distributed computing"),
                ("Uses Dask for large-scale data processing", "Python-native distributed computing"),
                ("Uses Ray for large-scale data processing", "Better ML workload support"),
            ]),
        ],
        "stable": [
            ("experiment", "Uses MLflow for experiment tracking"),
            ("orchestrator", "Uses Apache Airflow for pipeline orchestration"),
        ],
        "deps": [
            ("model_serving", "ml_framework", "Uses TensorFlow Serving for model inference"),
            ("pipeline_testing", "data_processing", "Uses Great Expectations for data validation"),
        ],
    },
]

PM_STACKS = [
    {
        "chains": [
            ("pm_tool", [
                ("Uses Linear for project management", "Fast and keyboard-driven"),
                ("Uses Notion for project management", "All-in-one workspace"),
                ("Uses Linear for project management again", "Notion was too slow for sprints"),
            ]),
            ("analytics", [
                ("Uses Mixpanel for product analytics", "Event-based tracking"),
                ("Uses PostHog for product analytics", "Self-hosted and open source"),
            ]),
        ],
        "stable": [
            ("communication", "Team uses Slack for async communication"),
            ("design", "Design team uses Figma for mockups"),
            ("docs", "Uses Notion for internal documentation"),
        ],
        "deps": [
            ("sprint_board", "pm_tool", "Uses Linear's cycle feature for sprint planning"),
        ],
    },
    {
        "chains": [
            ("pm_tool", [
                ("Uses Jira for project management", "Enterprise Agile workflow"),
                ("Uses Shortcut for project management", "Simpler and faster"),
            ]),
            ("analytics", [
                ("Uses Amplitude for product analytics", "Advanced cohort analysis"),
                ("Uses Plausible for product analytics", "Privacy-first analytics"),
            ]),
        ],
        "stable": [
            ("communication", "Team uses Discord for real-time communication"),
            ("design", "Design team uses Penpot for open-source design"),
            ("docs", "Uses Confluence for documentation"),
        ],
        "deps": [
            ("backlog", "pm_tool", "Uses Jira epics for backlog grooming"),
        ],
    },
]

MOBILE_STACKS = [
    {
        "chains": [
            ("framework", [
                ("Uses React Native for the mobile app", "Cross-platform development"),
                ("Uses Flutter for the mobile app", "Better performance and widget system"),
            ]),
            ("state", [
                ("Uses MobX for mobile state management", "Observable state pattern"),
                ("Uses Riverpod for mobile state management", "Type-safe dependency injection"),
            ]),
        ],
        "stable": [
            ("ci", "Uses Fastlane for mobile CI/CD"),
            ("analytics", "Uses Firebase Analytics for mobile tracking"),
        ],
        "deps": [
            ("testing", "framework", "Uses Detox for mobile end-to-end tests"),
            ("navigation", "framework", "Uses React Navigation for mobile routing"),
        ],
    },
    {
        "chains": [
            ("framework", [
                ("Uses SwiftUI for the iOS app", "Native iOS development"),
                ("Uses Kotlin Multiplatform for the mobile app", "Shared business logic"),
            ]),
            ("backend", [
                ("Uses Firebase as the mobile backend", "Serverless approach"),
                ("Uses Supabase as the mobile backend", "Open-source Firebase alternative"),
            ]),
        ],
        "stable": [
            ("design_system", "Uses a custom design system for the mobile UI"),
        ],
        "deps": [
            ("testing", "framework", "Uses XCTest for iOS unit tests"),
            ("data_layer", "backend", "Uses Supabase Swift SDK for data access"),
        ],
    },
]

SECURITY_STACKS = [
    {
        "chains": [
            ("scanner", [
                ("Uses Snyk for dependency vulnerability scanning", "SCA tool"),
                ("Uses Grype for dependency vulnerability scanning", "Open-source and local"),
            ]),
            ("sast", [
                ("Uses SonarQube for static analysis", "Enterprise SAST"),
                ("Uses Semgrep for static analysis", "Custom rule authoring"),
            ]),
        ],
        "stable": [
            ("secrets", "Uses truffleHog for secrets detection in CI"),
            ("policy", "Uses Open Policy Agent for policy enforcement"),
        ],
        "deps": [
            ("ci_integration", "scanner", "Uses Snyk GitHub integration for automated PR checks"),
            ("ide_plugin", "sast", "Uses SonarLint IDE plugin for real-time feedback"),
        ],
    },
]

# Map role keywords to applicable stacks
ROLE_STACKS = {
    "Backend": [BACKEND_STACKS],
    "Frontend": [FRONTEND_STACKS],
    "Full-Stack": [BACKEND_STACKS, FRONTEND_STACKS],
    "DevOps": [DEVOPS_STACKS],
    "Data Scientist": [DATA_STACKS],
    "ML Engineer": [DATA_STACKS],
    "Product Manager": [PM_STACKS],
    "Mobile": [MOBILE_STACKS],
    "Security": [SECURITY_STACKS],
    "Platform": [DEVOPS_STACKS, BACKEND_STACKS],
    "Data Engineer": [DATA_STACKS, DEVOPS_STACKS],
    "Site Reliability": [DEVOPS_STACKS],
    "QA": [FRONTEND_STACKS],
    "Solutions Architect": [BACKEND_STACKS, DEVOPS_STACKS],
    "Tech Lead": [BACKEND_STACKS, FRONTEND_STACKS],
}


def _pick_stacks_for_role(role: str) -> list:
    """Select technology stacks matching a role."""
    for keyword, stacks in ROLE_STACKS.items():
        if keyword in role:
            pool = stacks
            break
    else:
        pool = [BACKEND_STACKS]

    result = []
    for stack_pool in pool:
        result.append(random.choice(stack_pool))
    return result


def _generate_dates(start: str, count: int, min_gap: int = 14, max_gap: int = 60) -> list:
    """Generate a sorted list of dates spaced realistically."""
    base = datetime.strptime(start, "%Y-%m-%d")
    dates = [base]
    for _ in range(count - 1):
        gap = timedelta(days=random.randint(min_gap, max_gap))
        dates.append(dates[-1] + gap)
    return [d.strftime("%Y-%m-%d") for d in dates]


CONTEXTS = [
    "Performance wasn't meeting requirements",
    "Team decided to standardize",
    "Cost reduction initiative",
    "Better developer experience",
    "New project requirements",
    "Scaling challenges",
    "Security audit recommendation",
    "Community support was better",
    "Licensing concerns",
    "Simpler setup and maintenance",
    "Better integration with existing tools",
    "New team member brought experience with it",
    "Evaluated alternatives in a spike",
    "Production incident prompted the change",
    "Better documentation and ecosystem",
]


def generate_persona(pid: int) -> dict:
    """Generate a single persona with evolving timeline."""
    name = f"{FIRST_NAMES[pid % len(FIRST_NAMES)]} {LAST_NAMES[pid % len(LAST_NAMES)]}"
    role = ROLES[pid % len(ROLES)]
    company = COMPANIES[pid % len(COMPANIES)]

    stacks = _pick_stacks_for_role(role)

    # Build timeline from stacks
    timeline = []
    date_cursor = datetime(2025, 1, random.randint(1, 28))

    for stack in stacks:
        # Add supersession chains
        for category, chain in stack["chains"]:
            base_idx = len(timeline)
            first_date = date_cursor + timedelta(days=random.randint(0, 14))

            for j, (fact, ctx) in enumerate(chain):
                entry_date = first_date + timedelta(days=j * random.randint(30, 75))
                entry = {
                    "date": entry_date.strftime("%Y-%m-%d"),
                    "category": category,
                    "fact": fact,
                }
                if j > 0:
                    entry["supersedes"] = base_idx + j - 1
                    entry["context"] = ctx if ctx else random.choice(CONTEXTS)
                timeline.append(entry)

        # Add stable facts
        for category, fact in stack["stable"]:
            timeline.append({
                "date": (date_cursor + timedelta(days=random.randint(0, 7))).strftime("%Y-%m-%d"),
                "category": category,
                "fact": fact,
            })

        # Add dependency edges
        for dep_cat, depends_on_cat, dep_fact in stack["deps"]:
            timeline.append({
                "date": (date_cursor + timedelta(days=random.randint(1, 14))).strftime("%Y-%m-%d"),
                "category": dep_cat,
                "fact": dep_fact,
                "depends_on": depends_on_cat,
            })

    # Add identity facts
    timeline.append({
        "date": date_cursor.strftime("%Y-%m-%d"),
        "category": "name",
        "fact": f"Name is {name}",
    })
    timeline.append({
        "date": date_cursor.strftime("%Y-%m-%d"),
        "category": "team",
        "fact": f"Works at {company[1]} called {company[0]} with {company[2]} engineers"
        if "Leads" not in role else f"Leads {role.lower()} at {company[1]} called {company[0]}",
    })

    return {
        "id": f"p{pid:03d}",
        "name": name,
        "role": role,
        "experience": random.choice(EXPERIENCES),
        "style": random.choice(STYLES),
        "timeline": timeline,
    }


def generate_all_personas(count: int = 50) -> list:
    """Generate a pool of diverse personas."""
    personas = []
    for i in range(count):
        personas.append(generate_persona(i))
    return personas


if __name__ == "__main__":
    personas = generate_all_personas()
    # Stats
    total_facts = sum(len(p["timeline"]) for p in personas)
    chains = sum(
        1 for p in personas for t in p["timeline"] if "supersedes" in t
    )
    deps = sum(
        1 for p in personas for t in p["timeline"] if "depends_on" in t
    )
    print(f"Generated {len(personas)} personas")
    print(f"  Total timeline facts: {total_facts}")
    print(f"  Supersession entries: {chains}")
    print(f"  Dependency entries: {deps}")
    print(f"  Avg facts/persona: {total_facts/len(personas):.1f}")
