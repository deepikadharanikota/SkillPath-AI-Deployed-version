"""
roles_config.py
---------------
Comprehensive, extensible Target Role Taxonomy and Curriculum Syllabus for SkillPath AI.
Defines:
1. ROLES_REGISTRY: Detailed metadata, focus, core skills, and ordered roadmaps with prerequisites.
2. TOPIC_SYLLABUS: 4-module hierarchical curriculum breakdown per topic with concrete subtopics.
3. Helper functions for roadmap extraction, prerequisite ordering, and syllabus retrieval.
"""

from typing import Dict, List, Any, Optional

# ══════════════════════════════════════════════════════════════════════════════
# TOPIC SYLLABUS: 4 Hierarchical Modules per Topic
# ══════════════════════════════════════════════════════════════════════════════
TOPIC_SYLLABUS: Dict[str, Dict[str, Any]] = {
    "Docker": {
        "title": "Docker Containerization",
        "description": "Container virtualization, images, multi-container orchestration with Docker Compose",
        "modules": {
            "intro": {
                "title": "Module 1: Docker Fundamentals",
                "focus": "Core concepts and installation",
                "subtopics": [
                    "What is Docker & Containerization?",
                    "Containers vs Virtual Machines",
                    "Docker Architecture & Daemon",
                    "Installing & Configuring Docker"
                ]
            },
            "core": {
                "title": "Module 2: Docker Images & Dockerfiles",
                "focus": "Building and managing container images",
                "subtopics": [
                    "Understanding Base Images",
                    "Writing Efficient Dockerfiles",
                    "Docker Build, Tag & Push",
                    "Docker Hub & Image Registries"
                ]
            },
            "advanced": {
                "title": "Module 3: Containers & Networking",
                "focus": "Runtime lifecycle, volumes, and networking",
                "subtopics": [
                    "Container Lifecycle & CLI Commands",
                    "Port Publishing & Binding",
                    "Persistent Storage with Volumes & Bind Mounts",
                    "Bridge, Host & Overlay Networks"
                ]
            },
            "summary": {
                "title": "Module 4: Docker Compose & Orchestration",
                "focus": "Multi-container applications and best practices",
                "subtopics": [
                    "Docker Compose Fundamentals",
                    "Defining Multi-Container Architectures",
                    "Environment Variables & Secrets",
                    "Multi-Stage Builds & Production Optimization"
                ]
            }
        }
    },
    "Kubernetes": {
        "title": "Kubernetes Orchestration",
        "description": "Production container orchestration, scaling, pods, services, ingress, and Helm",
        "modules": {
            "intro": {
                "title": "Module 1: Kubernetes Architecture & Pods",
                "focus": "Cluster control plane and workload primitives",
                "subtopics": [
                    "Kubernetes Architecture (Control Plane & Worker Nodes)",
                    "kubectl CLI & Cluster Contexts",
                    "Pods & Multi-Container Pod Patterns",
                    "Namespaces & Resource Quotas"
                ]
            },
            "core": {
                "title": "Module 2: Deployments & Replicas",
                "focus": "Declarative workloads and updates",
                "subtopics": [
                    "Deployments & ReplicaSets",
                    "Rolling Updates & Rollbacks",
                    "Health Probes (Liveness, Readiness, Startup)",
                    "ConfigMaps & Secrets Management"
                ]
            },
            "advanced": {
                "title": "Module 3: Services, Ingress & Networking",
                "focus": "Service discovery and external traffic routing",
                "subtopics": [
                    "ClusterIP, NodePort & LoadBalancer Services",
                    "Ingress Controllers & Ingress Rules",
                    "PersistentVolumes & PVCs",
                    "NetworkPolicies & Cluster Security"
                ]
            },
            "summary": {
                "title": "Module 4: Helm & Cluster Troubleshooting",
                "focus": "Package management and production operations",
                "subtopics": [
                    "Helm Charts & Template Management",
                    "StatefulSets & DaemonSets",
                    "Cluster Logging & Metrics Troubleshooting",
                    "Production Best Practices & High Availability"
                ]
            }
        }
    },
    "Linux": {
        "title": "Linux Systems & Administration",
        "description": "Operating system fundamentals, bash scripting, file permissions, processes, and SSH",
        "modules": {
            "intro": {
                "title": "Module 1: Linux Fundamentals & File System",
                "focus": "File system navigation and core commands",
                "subtopics": [
                    "Linux File System Hierarchy (FHS)",
                    "Essential CLI Commands (ls, cd, grep, find, cat)",
                    "File Permissions (chmod, chown, umask)",
                    "Text Processing (sed, awk, cut, sort)"
                ]
            },
            "core": {
                "title": "Module 2: Processes, Services & Systemd",
                "focus": "Process management and service daemons",
                "subtopics": [
                    "Process Lifecycle & Monitoring (ps, top, htop, kill)",
                    "Systemd Services & systemctl Management",
                    "Crontab & Scheduled Jobs",
                    "Log Inspection with journalctl & /var/log"
                ]
            },
            "advanced": {
                "title": "Module 3: Bash Scripting & Automation",
                "focus": "Shell scripting, variables, logic, and functions",
                "subtopics": [
                    "Bash Script Anatomy & Shebang",
                    "Variables, Arguments & Environment Variables",
                    "Conditionals, Loops & Exit Codes",
                    "Writing Robust Automation Scripts"
                ]
            },
            "summary": {
                "title": "Module 4: Networking, SSH & Security",
                "focus": "Remote administration and system hardening",
                "subtopics": [
                    "SSH Key Pairs & Secure Remote Access",
                    "Network Tools (netstat, ss, curl, ip, dig)",
                    "User & Group Administration (sudoers)",
                    "Firewall Configuration (iptables, ufw)"
                ]
            }
        }
    },
    "Git": {
        "title": "Git & GitHub Version Control",
        "description": "Distributed version control, branching strategies, collaborative workflows, and merge conflicts",
        "modules": {
            "intro": {
                "title": "Module 1: Git Basics & Commits",
                "focus": "Working directory, staging area, and history",
                "subtopics": [
                    "Version Control Principles",
                    "Initializing Repositories & .gitignore",
                    "Staging, Committing & Git Log",
                    "Viewing Diffs and Inspecting History"
                ]
            },
            "core": {
                "title": "Module 2: Branching & Merging",
                "focus": "Branch creation, merges, and conflicts",
                "subtopics": [
                    "Creating & Switching Branches",
                    "Fast-Forward vs Three-Way Merges",
                    "Identifying & Resolving Merge Conflicts",
                    "Git Stash & Temporary Workspace"
                ]
            },
            "advanced": {
                "title": "Module 3: GitHub & Collaboration",
                "focus": "Remote repositories, PRs, and branch protection",
                "subtopics": [
                    "Remotes (git push, git pull, git fetch)",
                    "Pull Requests & Code Reviews",
                    "Branch Protection Rules & PR Approvals",
                    "Forking & Upstream Synchronization"
                ]
            },
            "summary": {
                "title": "Module 4: Advanced Git & Workflows",
                "focus": "Rebasing, cherry-pick, and team workflows",
                "subtopics": [
                    "Git Rebase vs Merge",
                    "Cherry-Picking & Reset vs Revert",
                    "Git Flow vs Trunk-Based Development",
                    "Git Hooks & Automated Quality Checks"
                ]
            }
        }
    },
    "CI/CD": {
        "title": "CI/CD Pipelines & Automation",
        "description": "Continuous Integration, automated testing, GitHub Actions, Jenkins, and delivery pipelines",
        "modules": {
            "intro": {
                "title": "Module 1: CI/CD Principles & Pipelines",
                "focus": "Continuous integration and build automation",
                "subtopics": [
                    "What is Continuous Integration & Continuous Delivery?",
                    "Anatomy of a Build Pipeline",
                    "Automated Testing in Pipelines",
                    "Artifact Generation & Versioning"
                ]
            },
            "core": {
                "title": "Module 2: GitHub Actions Workflows",
                "focus": "Declarative YAML workflows and triggers",
                "subtopics": [
                    "Workflow Syntax, Events & Triggers",
                    "Jobs, Steps & Community Actions",
                    "Secrets Management & Environment Variables",
                    "Matrix Builds & Parallel Execution"
                ]
            },
            "advanced": {
                "title": "Module 3: Jenkins & Pipeline as Code",
                "focus": "Enterprise Jenkins pipelines and agents",
                "subtopics": [
                    "Jenkins Architecture & Controller-Agent Model",
                    "Jenkinsfile (Declarative vs Scripted)",
                    "Pipeline Stages, Post Actions & Credentials",
                    "Integrating SonarQube & Security Scanners"
                ]
            },
            "summary": {
                "title": "Module 4: Deployment Strategies & Release",
                "focus": "Automated deployments and release safety",
                "subtopics": [
                    "Deploying to Staging & Production",
                    "Rolling, Blue-Green & Canary Deployments",
                    "Pipeline Rollbacks & Automated Health Gates",
                    "DevOps Metrics (DORA Metrics & Lead Time)"
                ]
            }
        }
    },
    "AWS Cloud": {
        "title": "AWS Cloud Architecture",
        "description": "Amazon Web Services infrastructure, compute, storage, networking, IAM, and deployment",
        "modules": {
            "intro": {
                "title": "Module 1: AWS Fundamentals & IAM",
                "focus": "Cloud foundations, regions, and security",
                "subtopics": [
                    "Cloud Computing Concepts & AWS Regions/AZs",
                    "AWS Identity & Access Management (IAM)",
                    "IAM Users, Roles, Policies & Groups",
                    "Least Privilege Security Practices"
                ]
            },
            "core": {
                "title": "Module 2: Compute & Storage (EC2 & S3)",
                "focus": "Virtual machines, auto scaling, and object storage",
                "subtopics": [
                    "Amazon EC2 Instances & AMIs",
                    "Auto Scaling Groups & Elastic Load Balancers (ALB)",
                    "Amazon S3 Buckets, Storage Classes & Lifecycle",
                    "Elastic Block Store (EBS) & Snapshot Backups"
                ]
            },
            "advanced": {
                "title": "Module 3: VPC Networking & Databases",
                "focus": "Virtual private clouds, subnets, and RDS",
                "subtopics": [
                    "VPC Architecture, Subnets & Internet Gateways",
                    "Route Tables, NAT Gateways & Security Groups",
                    "Amazon RDS & Aurora Relational Databases",
                    "Amazon DynamoDB NoSQL Database"
                ]
            },
            "summary": {
                "title": "Module 4: Serverless, Containers & CloudWatch",
                "focus": "ECS, EKS, Lambda, and CloudWatch monitoring",
                "subtopics": [
                    "AWS Lambda & API Gateway Serverless",
                    "Amazon ECS & Elastic Kubernetes Service (EKS)",
                    "CloudWatch Metrics, Alarms & Logs",
                    "CloudFormation & Cloud Deployment Automation"
                ]
            }
        }
    },
    "Terraform": {
        "title": "Infrastructure as Code with Terraform",
        "description": "Declarative infrastructure provisioning, HCL, state management, modules, and providers",
        "modules": {
            "intro": {
                "title": "Module 1: IaC Fundamentals & Terraform Syntax",
                "focus": "HashiCorp Configuration Language (HCL)",
                "subtopics": [
                    "What is Infrastructure as Code (IaC)?",
                    "Terraform Architecture & Providers",
                    "HCL Syntax (Resources, Data Sources, Variables)",
                    "Terraform CLI (init, plan, apply, destroy)"
                ]
            },
            "core": {
                "title": "Module 2: State Management & Backends",
                "focus": "Terraform state, locking, and remote storage",
                "subtopics": [
                    "Understanding terraform.tfstate",
                    "Remote State with AWS S3 & DynamoDB Locking",
                    "State Inspection & State Migration",
                    "Sensitive Variables & Outputs"
                ]
            },
            "advanced": {
                "title": "Module 3: Modular Architecture",
                "focus": "Reusable Terraform modules and environments",
                "subtopics": [
                    "Writing Custom Terraform Modules",
                    "Public Terraform Registry Modules",
                    "Multi-Environment Management (Dev, Stage, Prod)",
                    "Terraform Workspaces vs Directory Layouts"
                ]
            },
            "summary": {
                "title": "Module 4: CI/CD Integration & Security",
                "focus": "Automated Terraform pipelines and policy as code",
                "subtopics": [
                    "Running Terraform in GitHub Actions / GitLab",
                    "Static Code Analysis with tfsec & tflint",
                    "Drift Detection & Remediation",
                    "Ansible Integration for Configuration Management"
                ]
            }
        }
    },
    "Prometheus & Grafana": {
        "title": "Monitoring & Observability",
        "description": "Metrics collection, Prometheus server, PromQL, Alertmanager, and Grafana dashboards",
        "modules": {
            "intro": {
                "title": "Module 1: Observability Foundations",
                "focus": "Metrics, logs, traces, and Prometheus basics",
                "subtopics": [
                    "The Three Pillars of Observability",
                    "Prometheus Architecture & Pull Model",
                    "Metric Types (Counter, Gauge, Histogram, Summary)",
                    "Node Exporter Installation & Metrics Scraping"
                ]
            },
            "core": {
                "title": "Module 2: PromQL & Querying",
                "focus": "Writing expressive PromQL queries",
                "subtopics": [
                    "Instant Vectors vs Range Vectors",
                    "Rate, Increase & Aggregation Functions",
                    "Label Filtering & Regex Matching",
                    "PromQL for System & Application Performance"
                ]
            },
            "advanced": {
                "title": "Module 3: Grafana Dashboard Engineering",
                "focus": "Visualizing metrics and building actionable dashboards",
                "subtopics": [
                    "Connecting Prometheus Data Sources",
                    "Building Responsive Panels & Graphs",
                    "Dashboard Variables & Dynamic Templating",
                    "Golden Signals Dashboards (Latency, Traffic, Errors, Saturation)"
                ]
            },
            "summary": {
                "title": "Module 4: Alertmanager & Production Operations",
                "focus": "Alerting rules, notification channels, and on-call",
                "subtopics": [
                    "Defining Alerting Rules in Prometheus",
                    "Alertmanager Configuration & Grouping",
                    "Routing Alerts to Slack, PagerDuty & Email",
                    "SRE Best Practices: SLOs, SLIs, and Error Budgets"
                ]
            }
        }
    },
    "Networking": {
        "title": "DevOps Networking & Security",
        "description": "TCP/IP, DNS, HTTP/HTTPS, load balancers, reverse proxies, and firewalls",
        "modules": {
            "intro": {
                "title": "Module 1: OSI Model & TCP/IP Protocol",
                "focus": "Network layers and packet transport",
                "subtopics": [
                    "The OSI 7-Layer & TCP/IP Models",
                    "IP Addressing, Subnets & CIDR Notation",
                    "TCP 3-Way Handshake & UDP",
                    "Ports & Socket Connections"
                ]
            },
            "core": {
                "title": "Module 2: DNS, HTTP & SSL/TLS",
                "focus": "Web protocols and domain resolution",
                "subtopics": [
                    "How DNS Works (A, CNAME, MX, TXT Records)",
                    "HTTP/1.1 vs HTTP/2 vs HTTP/3",
                    "HTTPS, SSL/TLS Handshake & Certificates",
                    "Let's Encrypt & Automated Certificate Renewal"
                ]
            },
            "advanced": {
                "title": "Module 3: Reverse Proxies & Load Balancing",
                "focus": "Nginx, HAProxy, and traffic distribution",
                "subtopics": [
                    "Forward vs Reverse Proxies",
                    "Configuring Nginx as a Reverse Proxy",
                    "Load Balancing Algorithms (Round Robin, Least Connections)",
                    "Health Checks, Sticky Sessions & SSL Termination"
                ]
            },
            "summary": {
                "title": "Module 4: Network Security & Firewalls",
                "focus": "Security hardening and perimeter defense",
                "subtopics": [
                    "Firewalls & Packet Filtering (iptables, nftables)",
                    "VPNs, Bastion Hosts & SSH Tunnels",
                    "DDoS Mitigation & Web Application Firewalls (WAF)",
                    "Network Troubleshooting Tools (traceroute, tcpdump, Wireshark)"
                ]
            }
        }
    },
    "DevSecOps": {
        "title": "DevSecOps & Security Engineering",
        "description": "Security in CI/CD, container security, vulnerability scanning, secrets management, and compliance",
        "modules": {
            "intro": {
                "title": "Module 1: DevSecOps Fundamentals",
                "focus": "Shift-left security principles",
                "subtopics": [
                    "Introduction to DevSecOps & Shift-Left",
                    "OWASP Top 10 Security Risks",
                    "Static Application Security Testing (SAST)",
                    "Dynamic Application Security Testing (DAST)"
                ]
            },
            "core": {
                "title": "Module 2: Secrets Management",
                "focus": "Securing credentials and API keys",
                "subtopics": [
                    "Eliminating Hardcoded Secrets",
                    "HashiCorp Vault Architecture & Engines",
                    "AWS Secrets Manager & Parameter Store",
                    "Injecting Secrets into Kubernetes & CI/CD"
                ]
            },
            "advanced": {
                "title": "Module 3: Container & Supply Chain Security",
                "focus": "Image scanning, rootless containers, and SBOM",
                "subtopics": [
                    "Container Vulnerability Scanning (Trivy, Grype)",
                    "Non-Root Containers & Distroless Images",
                    "Software Bill of Materials (SBOM)",
                    "Image Signing & Verification with Cosign"
                ]
            },
            "summary": {
                "title": "Module 4: Policy as Code & Incident Response",
                "focus": "OPA, Gatekeeper, and automated governance",
                "subtopics": [
                    "Open Policy Agent (OPA) & Rego Policies",
                    "Kubernetes Admission Controllers & Kyverno",
                    "Audit Logging & Security Information (SIEM)",
                    "Automated Security Gates in Release Pipelines"
                ]
            }
        }
    },
    "React": {
        "title": "React UI Engineering",
        "description": "Modern React, hooks, state management, component architecture, and responsive design",
        "modules": {
            "intro": {
                "title": "Module 1: React Fundamentals & JSX",
                "focus": "Virtual DOM, JSX, components, and props",
                "subtopics": [
                    "React Architecture & Virtual DOM",
                    "JSX Syntax & Element Rendering",
                    "Functional Components & Props",
                    "Component Composition & Reusability"
                ]
            },
            "core": {
                "title": "Module 2: State & React Hooks",
                "focus": "useState, useEffect, and custom hooks",
                "subtopics": [
                    "useState & State Updates",
                    "useEffect & Component Lifecycles",
                    "Handling Forms & User Input Events",
                    "Building Reusable Custom Hooks"
                ]
            },
            "advanced": {
                "title": "Module 3: State Management & Routing",
                "focus": "Context API, Redux/Zustand, and React Router",
                "subtopics": [
                    "Prop Drilling & React Context API",
                    "Global State with Zustand or Redux Toolkit",
                    "Client-Side Routing with React Router",
                    "Performance Optimization (useMemo, useCallback, memo)"
                ]
            },
            "summary": {
                "title": "Module 4: API Integration & Testing",
                "focus": "REST APIs, testing, and production deployment",
                "subtopics": [
                    "Fetching Data with Axios & React Query",
                    "Error Boundaries & Suspense",
                    "Unit Testing with Jest & React Testing Library",
                    "Vite / Next.js Production Build & Deployment"
                ]
            }
        }
    },
    "JavaScript": {
        "title": "Modern JavaScript (ES6+)",
        "description": "Core language mechanics, asynchronous programming, DOM, closures, and modern patterns",
        "modules": {
            "intro": {
                "title": "Module 1: JavaScript Language Foundations",
                "focus": "Types, variables, operators, and control flow",
                "subtopics": [
                    "Data Types, Primitives & Objects",
                    "let, const, and Block Scoping",
                    "Arrow Functions & Template Literals",
                    "Destructuring, Spread & Rest Operators"
                ]
            },
            "core": {
                "title": "Module 2: Asynchronous JavaScript",
                "focus": "Event loop, promises, and async/await",
                "subtopics": [
                    "The JavaScript Event Loop & Call Stack",
                    "Callbacks & Callback Hell",
                    "Promises & Promise Combinators (all, race)",
                    "Async / Await and Error Handling"
                ]
            },
            "advanced": {
                "title": "Module 3: Closures, Prototypes & Scope",
                "focus": "Execution contexts, prototypes, and OOP",
                "subtopics": [
                    "Lexical Scope & Closures",
                    "The 'this' Keyword & Binding (bind, call, apply)",
                    "Prototypes, Prototypal Inheritance & Classes",
                    "ES Modules (import / export)"
                ]
            },
            "summary": {
                "title": "Module 4: Web APIs, Storage & Tooling",
                "focus": "Browser APIs, Fetch, and module bundlers",
                "subtopics": [
                    "Fetch API & Handling JSON Data",
                    "LocalStorage, SessionStorage & IndexedDB",
                    "Modern Build Tools (Vite, Webpack, Babel)",
                    "Clean Code & Design Patterns in JavaScript"
                ]
            }
        }
    },
    "TypeScript": {
        "title": "TypeScript for Enterprise Applications",
        "description": "Static typing, interfaces, generics, utility types, and TypeScript with React/Node",
        "modules": {
            "intro": {
                "title": "Module 1: TypeScript Fundamentals",
                "focus": "Basic types, type inference, and compiler",
                "subtopics": [
                    "Why TypeScript? Static Typing vs Dynamic",
                    "tsconfig.json & Compiler Options",
                    "Primitive Types, Arrays & Tuples",
                    "Type Annotations vs Type Inference"
                ]
            },
            "core": {
                "title": "Module 2: Interfaces & Type Aliases",
                "focus": "Modeling structured data and functions",
                "subtopics": [
                    "Interfaces vs Type Aliases",
                    "Optional, Readonly & Index Signatures",
                    "Union & Intersection Types",
                    "Type Narrowing & Type Guards"
                ]
            },
            "advanced": {
                "title": "Module 3: Generics & Advanced Types",
                "focus": "Reusable generic functions and utility types",
                "subtopics": [
                    "Generic Functions, Interfaces & Classes",
                    "Generic Constraints (extends keyof)",
                    "Built-in Utility Types (Partial, Pick, Omit, Record)",
                    "Conditional & Mapped Types"
                ]
            },
            "summary": {
                "title": "Module 4: TypeScript in Full-Stack Projects",
                "focus": "React with TypeScript, Node.js APIs, and strict mode",
                "subtopics": [
                    "Typing React Components, Props & Hooks",
                    "Typing Express & FastAPI Backend Payloads",
                    "Strict Null Checks & Eliminating 'any'",
                    "Production Compilation & Type Declarations (.d.ts)"
                ]
            }
        }
    },
    "Python": {
        "title": "Python Software Development",
        "description": "Python language, data structures, OOP, modules, exception handling, and virtual environments",
        "modules": {
            "intro": {
                "title": "Module 1: Python Basics & Data Structures",
                "focus": "Syntax, collections, and control flow",
                "subtopics": [
                    "Variables, Types & Formatting",
                    "Lists, Tuples, Dictionaries & Sets",
                    "Conditionals, Loops & List Comprehensions",
                    "Writing Modular Functions"
                ]
            },
            "core": {
                "title": "Module 2: Object-Oriented Python",
                "focus": "Classes, inheritance, and magic methods",
                "subtopics": [
                    "Classes, Instances & Attributes",
                    "Inheritance & Polymorphism",
                    "Dunder Methods (__str__, __repr__, __len__)",
                    "Properties & Encapsulation"
                ]
            },
            "advanced": {
                "title": "Module 3: Functional & Advanced Features",
                "focus": "Decorators, generators, and context managers",
                "subtopics": [
                    "Decorators & Higher-Order Functions",
                    "Generators & Iterators (yield)",
                    "Context Managers with 'with' Statements",
                    "Exception Handling & Custom Exceptions"
                ]
            },
            "summary": {
                "title": "Module 4: Virtual Envs, Testing & APIs",
                "focus": "Packaging, pytest, and FastAPI basics",
                "subtopics": [
                    "Virtual Environments (venv / poetry)",
                    "Unit Testing with pytest",
                    "Working with JSON, CSV & Files",
                    "Building REST Endpoints with FastAPI"
                ]
            }
        }
    },
    "SQL": {
        "title": "SQL & Relational Databases",
        "description": "Relational schema design, querying, complex joins, indexing, transactions, and PostgreSQL",
        "modules": {
            "intro": {
                "title": "Module 1: SQL Fundamentals & CRUD",
                "focus": "Table creation, basic queries, and filtering",
                "subtopics": [
                    "Relational Database Concepts (RDBMS)",
                    "CREATE, ALTER & DROP Tables",
                    "SELECT, WHERE, ORDER BY, LIMIT",
                    "INSERT, UPDATE & DELETE Operations"
                ]
            },
            "core": {
                "title": "Module 2: Joins, Aggregations & Grouping",
                "focus": "Multi-table queries and analytical aggregations",
                "subtopics": [
                    "INNER JOIN, LEFT JOIN, RIGHT JOIN, FULL JOIN",
                    "Aggregations: COUNT, SUM, AVG, MIN, MAX",
                    "GROUP BY & HAVING Clauses",
                    "Subqueries & Common Table Expressions (WITH / CTE)"
                ]
            },
            "advanced": {
                "title": "Module 3: Indexing, Transactions & Constraints",
                "focus": "ACID compliance, foreign keys, and indexes",
                "subtopics": [
                    "Primary Keys, Foreign Keys & Unique Constraints",
                    "ACID Properties & Transaction Control (COMMIT, ROLLBACK)",
                    "Database Indexes (B-Tree, Hash) & Query Execution Plans",
                    "Window Functions (ROW_NUMBER, RANK, PARTITION BY)"
                ]
            },
            "summary": {
                "title": "Module 4: Normalization & PostgreSQL Administration",
                "focus": "Schema design, migrations, and performance",
                "subtopics": [
                    "Database Normalization (1NF, 2NF, 3NF)",
                    "PostgreSQL Data Types (JSONB, UUID, Arrays)",
                    "Database Migrations & Connection Pooling",
                    "Query Performance Tuning (EXPLAIN ANALYZE)"
                ]
            }
        }
    },
    "System Design": {
        "title": "System Design & Software Architecture",
        "description": "Scalability, microservices, distributed systems, caching, message queues, and load balancing",
        "modules": {
            "intro": {
                "title": "Module 1: System Design Fundamentals",
                "focus": "Scale, latency, throughput, and trade-offs",
                "subtopics": [
                    "Vertical vs Horizontal Scaling",
                    "Latency, Throughput & Bandwidth",
                    "CAP Theorem & PACELC Theorem",
                    "Monolith vs Microservices Architecture"
                ]
            },
            "core": {
                "title": "Module 2: Caching, CDNs & Load Balancing",
                "focus": "High performance and traffic distribution",
                "subtopics": [
                    "Caching Strategies (Write-Through, Cache-Aside, Write-Back)",
                    "Redis & Memcached Architecture",
                    "Content Delivery Networks (CDNs)",
                    "Load Balancing & Reverse Proxies"
                ]
            },
            "advanced": {
                "title": "Module 3: Distributed Data & Message Queues",
                "focus": "Data partitioning, replication, and async workflows",
                "subtopics": [
                    "Database Sharding & Partitioning",
                    "Master-Slave & Multi-Master Replication",
                    "Message Queues (Kafka, RabbitMQ, SQS)",
                    "Event-Driven Architecture & Pub/Sub"
                ]
            },
            "summary": {
                "title": "Module 4: Reliability & Enterprise Case Studies",
                "focus": "Fault tolerance, rate limiting, and real architectures",
                "subtopics": [
                    "Rate Limiting Algorithms (Token Bucket, Leaky Bucket)",
                    "Circuit Breaker Pattern & Fault Tolerance",
                    "Designing a URL Shortener (TinyURL)",
                    "Designing a Collaborative Real-Time Notification System"
                ]
            }
        }
    },
    "QA Testing": {
        "title": "Software Quality Assurance & Test Automation",
        "description": "Manual testing, test planning, automated UI testing with Selenium/Cypress, and API testing",
        "modules": {
            "intro": {
                "title": "Module 1: Testing Fundamentals & Test Design",
                "focus": "Testing levels, test case design, and defect management",
                "subtopics": [
                    "Software Testing Life Cycle (STLC)",
                    "Test Case Design Techniques (Boundary Value, Equivalence)",
                    "Defect Lifecycle & Bug Tracking in Jira",
                    "Manual vs Automated Testing Strategy"
                ]
            },
            "core": {
                "title": "Module 2: Unit & Integration Testing",
                "focus": "Automated testing with Pytest and Jest",
                "subtopics": [
                    "Writing Unit Tests with Pytest / Jest",
                    "Test Fixtures, Parameterization & Assertions",
                    "Mocking Dependencies & Stubs",
                    "Code Coverage Metrics & Reporting"
                ]
            },
            "advanced": {
                "title": "Module 3: API & Web Automation",
                "focus": "API testing with Postman and UI testing with Selenium/Cypress",
                "subtopics": [
                    "REST API Testing with Postman / Requests",
                    "Validating Status Codes, Headers & JSON Payloads",
                    "Selenium / Cypress Architecture & Locators",
                    "Page Object Model (POM) Design Pattern"
                ]
            },
            "summary": {
                "title": "Module 4: End-to-End & CI/CD Testing",
                "focus": "Regression suites, headless execution, and pipeline gates",
                "subtopics": [
                    "End-to-End (E2E) Test Automation Suites",
                    "Headless Browser Execution in Docker",
                    "Integrating Test Automation into GitHub Actions",
                    "Performance & Load Testing Fundamentals (k6 / JMeter)"
                ]
            }
        }
    },
    "Machine Learning": {
        "title": "Machine Learning Engineering",
        "description": "Supervised & unsupervised learning, model evaluation, feature engineering, and Scikit-learn",
        "modules": {
            "intro": {
                "title": "Module 1: ML Foundations & Data Prep",
                "focus": "Data preprocessing, train/test splits, and linear models",
                "subtopics": [
                    "Supervised vs Unsupervised Learning",
                    "Data Preprocessing & Feature Scaling",
                    "Train/Validation/Test Splits",
                    "Linear & Logistic Regression"
                ]
            },
            "core": {
                "title": "Module 2: Tree-Based Models & Ensembles",
                "focus": "Decision trees, Random Forests, and Gradient Boosting",
                "subtopics": [
                    "Decision Tree Classification & Regression",
                    "Random Forests & Bagging Principles",
                    "Gradient Boosting (XGBoost / LightGBM)",
                    "Hyperparameter Tuning with GridSearch & Optuna"
                ]
            },
            "advanced": {
                "title": "Module 3: Model Evaluation & Metrics",
                "focus": "Overfitting, cross-validation, and performance metrics",
                "subtopics": [
                    "Confusion Matrix, Precision, Recall & F1-Score",
                    "ROC-AUC Curves & Threshold Optimization",
                    "K-Fold Cross-Validation & Preventing Leakage",
                    "Bias-Variance Tradeoff Analysis"
                ]
            },
            "summary": {
                "title": "Module 4: Unsupervised Learning & Deployment",
                "focus": "Clustering, dimensionality reduction, and ML APIs",
                "subtopics": [
                    "K-Means Clustering & Hierarchical Clustering",
                    "PCA (Principal Component Analysis)",
                    "Model Serialization (joblib / ONNX)",
                    "Deploying ML Inference APIs with FastAPI"
                ]
            }
        }
    },
    "Deep Learning": {
        "title": "Deep Learning & Neural Networks",
        "description": "Perceptrons, backpropagation, CNNs, RNNs, PyTorch, and TensorFlow architectures",
        "modules": {
            "intro": {
                "title": "Module 1: Neural Network Foundations",
                "focus": "Neurons, activation functions, and gradient descent",
                "subtopics": [
                    "Artificial Neurons & Multi-Layer Perceptrons",
                    "Activation Functions (ReLU, Sigmoid, Softmax)",
                    "Forward Propagation & Loss Functions",
                    "Backpropagation & Stochastic Gradient Descent"
                ]
            },
            "core": {
                "title": "Module 2: Building Models with PyTorch",
                "focus": "PyTorch tensors, autograd, and training loops",
                "subtopics": [
                    "PyTorch Tensors, GPU Acceleration (CUDA)",
                    "torch.nn Modules & Custom Architectures",
                    "Writing a Standard Training & Evaluation Loop",
                    "Regularization (Dropout, Weight Decay, BatchNorm)"
                ]
            },
            "advanced": {
                "title": "Module 3: Convolutional Neural Networks (CNNs)",
                "focus": "Image processing, convolution, pooling, and transfer learning",
                "subtopics": [
                    "Convolutional Layers, Kernels & Stride",
                    "Max Pooling & Spatial Downsampling",
                    "Classic Architectures (ResNet, VGG)",
                    "Transfer Learning & Fine-Tuning"
                ]
            },
            "summary": {
                "title": "Module 4: Sequence Models & Transformers",
                "focus": "RNNs, Attention mechanism, and Transformer blocks",
                "subtopics": [
                    "Recurrent Neural Networks (RNNs) & LSTMs",
                    "The Self-Attention Mechanism",
                    "Transformer Encoder-Decoder Architecture",
                    "Model Optimization & Quantization"
                ]
            }
        }
    },
    "MLOps": {
        "title": "MLOps & ML Production Engineering",
        "description": "Model versioning, MLflow, pipeline orchestration, model monitoring, and automated retraining",
        "modules": {
            "intro": {
                "title": "Module 1: MLOps Principles & Tracking",
                "focus": "Reproducibility, experiment tracking, and MLflow",
                "subtopics": [
                    "What is MLOps? The ML Lifecycle",
                    "Experiment Tracking with MLflow / Weights & Biases",
                    "Logging Hyperparameters, Metrics & Artifacts",
                    "Model Registry & Model Staging"
                ]
            },
            "core": {
                "title": "Module 2: Data & Model Versioning",
                "focus": "DVC, data pipelines, and dataset versioning",
                "subtopics": [
                    "Data Version Control (DVC) Fundamentals",
                    "Connecting DVC to Cloud Storage (S3 / GCS)",
                    "Feature Stores (Feast Architecture)",
                    "Automated Data Validation with Great Expectations"
                ]
            },
            "advanced": {
                "title": "Module 3: Continuous Training Pipelines",
                "focus": "Kubeflow, Airflow, and automated model builds",
                "subtopics": [
                    "Building ML Pipelines with Kubeflow / Airflow",
                    "Automated Model Retraining Triggers",
                    "Containerizing Model Training & Inference",
                    "Canary & Shadow Deployments for ML Models"
                ]
            },
            "summary": {
                "title": "Module 4: Model Monitoring & Drift Detection",
                "focus": "Data drift, concept drift, and performance monitoring",
                "subtopics": [
                    "Data Drift vs Concept Drift",
                    "Monitoring Model Latency, Throughput & Quality",
                    "Evidently AI & Prometheus for Model Metrics",
                    "Feedback Loops & Incident Response for ML Systems"
                ]
            }
        }
    },
    "Data Engineering": {
        "title": "Data Engineering & Pipelines",
        "description": "ETL pipelines, Apache Spark, PySpark, data warehousing, Kafka streaming, and data quality",
        "modules": {
            "intro": {
                "title": "Module 1: Data Engineering Foundations",
                "focus": "Data architectures, OLTP vs OLAP, and Pandas ETL",
                "subtopics": [
                    "Data Engineering Roles & Responsibilities",
                    "OLTP (Transactional) vs OLAP (Analytical) Systems",
                    "Batch vs Stream Processing",
                    "Building Reliable Python ETL Scripts with Pandas"
                ]
            },
            "core": {
                "title": "Module 2: Data Warehousing & SQL Modeling",
                "focus": "Snowflake, BigQuery, and Star/Snowflake schemas",
                "subtopics": [
                    "Data Warehouse Architecture (Snowflake / BigQuery)",
                    "Dimensional Modeling (Facts, Dimensions, Star Schema)",
                    "Data Lakes vs Data Warehouses vs Lakehouses",
                    "dbt (data build tool) for SQL Transformations"
                ]
            },
            "advanced": {
                "title": "Module 3: Big Data with Apache Spark",
                "focus": "Distributed processing, DataFrames, and PySpark",
                "subtopics": [
                    "Apache Spark Architecture (Driver, Executors)",
                    "PySpark DataFrames & SQL Queries",
                    "Transformations vs Actions & Lazy Evaluation",
                    "Partitioning, Shuffling & Performance Tuning"
                ]
            },
            "summary": {
                "title": "Module 4: Orchestration & Real-Time Streaming",
                "focus": "Airflow DAGs, Apache Kafka, and data quality",
                "subtopics": [
                    "Workflow Orchestration with Apache Airflow DAGs",
                    "Apache Kafka Architecture (Topics, Producers, Consumers)",
                    "Streaming Data Ingestion & Processing",
                    "Data Quality, Lineage & Metadata Governance"
                ]
            }
        }
    },
    "Data Structures & Algorithms": {
        "title": "Data Structures & Algorithms",
        "description": "Foundational complexity analysis, linear & non-linear data structures, trees, graphs, and dynamic programming",
        "modules": {
            "intro": {
                "title": "Module 1: Complexity & Linear Structures",
                "focus": "Big-O analysis, arrays, strings, and linked lists",
                "subtopics": [
                    "Asymptotic Analysis & Big-O Notation",
                    "Dynamic Arrays & amortized runtime",
                    "String manipulation & two-pointer techniques",
                    "Singly & Doubly Linked Lists implementation"
                ]
            },
            "core": {
                "title": "Module 2: Stacks, Queues, Hashing & Recursion",
                "focus": "Abstract data types, hashing, searching and sorting",
                "subtopics": [
                    "Stacks & Monotonic Stack patterns",
                    "Queues, Deques & Circular Buffers",
                    "Hash Tables, Hash Maps & Collision Resolution",
                    "Binary Search, Merge Sort & Quick Sort"
                ]
            },
            "advanced": {
                "title": "Module 3: Trees, Heaps & Graphs",
                "focus": "Hierarchical structures, priority queues, and graph traversals",
                "subtopics": [
                    "Binary Trees & Tree Traversals (BFS & DFS)",
                    "Binary Search Trees (BST) & Balanced Trees",
                    "Binary Heaps, Priority Queues & Top-K elements",
                    "Graph Representations, Dijkstra & Topological Sort"
                ]
            },
            "summary": {
                "title": "Module 4: Algorithmic Paradigms & Dynamic Programming",
                "focus": "Greedy algorithms, backtracking, memoization, and DP",
                "subtopics": [
                    "Greedy Strategies & Interval Scheduling",
                    "Backtracking & Combinatorial Search",
                    "Dynamic Programming: 1D & 2D Memoization",
                    "Advanced System Problem Solving & Complexity Tradeoffs"
                ]
            }
        }
    },
    "Data Structures & Algorithms": {
        "title": "Data Structures & Algorithms",
        "description": "Comprehensive 14-module curriculum spanning complexity analysis, linear structures, trees, graphs, greedy algorithms, dynamic programming, advanced structures, and interview patterns in C, C++, Python, or Java.",
        "modules": {
            "module_1": {
                "title": "Module 1: Complexity Analysis (DSA Fundamentals)",
                "phase": "Phase 1 — DSA Fundamentals",
                "icon": "⏱️",
                "focus": "Time & Space Complexity, Big-O Notation, and Operation Efficiency",
                "subtopics": [
                    "01. What are Data Structures?",
                    "02. What are Algorithms?",
                    "03. Time Complexity",
                    "04. Space Complexity",
                    "05. Big-O Notation",
                    "06. O(1), O(log n), O(n)",
                    "07. O(n log n), O(n²)",
                    "08. Best/Average/Worst Case",
                    "09. Complexity of common operations"
                ]
            },
            "module_2": {
                "title": "Module 2: Arrays & Strings",
                "phase": "Phase 2 — Arrays & Strings",
                "icon": "🧱",
                "focus": "Array fundamentals, string manipulation, two pointers, and sliding window",
                "subtopics": [
                    "01. Array Introduction & Memory Layout",
                    "02. Array Declaration & Initialization",
                    "03. Array Traversal & Bounds Checking",
                    "04. Insertion & Deletion Operations",
                    "05. Searching & In-Place Updating",
                    "06. Prefix Sum & Kadane's Algorithm",
                    "07. 2D Arrays & Matrix Traversals",
                    "08. String Basics & Immutability vs Mutability",
                    "09. String Traversal & Character Frequency",
                    "10. Palindrome & Anagram Validation",
                    "11. String Manipulation & Pattern Matching",
                    "12. Substrings vs Subsequences",
                    "13. Two Pointers Pattern",
                    "14. Sliding Window Pattern (Fixed & Dynamic)",
                    "15. Prefix/Suffix Arrays & Frequency Counting",
                    "16. Sorting + Two Pointers Strategy",
                    "17. Subarray Problem Patterns"
                ]
            },
            "module_3": {
                "title": "Module 3: Searching & Sorting",
                "phase": "Phase 3 — Searching & Sorting",
                "icon": "🔍",
                "focus": "Binary search variants, search on answers, divide-and-conquer, and linear-time sorts",
                "subtopics": [
                    "01. Linear Search Fundamentals",
                    "02. Binary Search Invariants & Boundaries",
                    "03. Binary Search Implementation",
                    "04. First & Last Occurrence of Elements",
                    "05. Lower Bound & Upper Bound",
                    "06. Search in Rotated Sorted Array",
                    "07. Binary Search on Answer Space",
                    "08. Why Sorting Matters & Tradeoffs",
                    "09. Bubble Sort, Selection Sort & Insertion Sort",
                    "10. Merge Sort (Divide & Conquer)",
                    "11. Quick Sort & 3-Way Partitioning",
                    "12. Heap Sort (In-Place Sift Down)",
                    "13. Counting Sort & Non-Comparison Sorts",
                    "14. Sorting Complexity Comparison & Stability"
                ]
            },
            "module_4": {
                "title": "Module 4: Linked Lists",
                "phase": "Phase 4 — Linked Lists",
                "icon": "🔗",
                "focus": "Pointers, node links, reversal, fast & slow pointers, and cycle detection",
                "subtopics": [
                    "01. Linked List Introduction vs Arrays",
                    "02. Node Structure & Memory Allocation",
                    "03. Traversal, Insertion & Deletion",
                    "04. Searching in Singly Linked Lists",
                    "05. In-Place Reversal of Linked List",
                    "06. Doubly Linked List (Prev & Next Pointers)",
                    "07. Circular Linked List Implementation",
                    "08. Fast & Slow Pointers (Tortoise & Hare)",
                    "09. Detect Cycle (Floyd's Algorithm)",
                    "10. Find Cycle Start & Remove Cycle",
                    "11. Merge Two Sorted Linked Lists",
                    "12. Remove Nth Node From End"
                ]
            },
            "module_5": {
                "title": "Module 5: Stack & Queue",
                "phase": "Phase 5 — Stack & Queue",
                "icon": "🥞",
                "focus": "LIFO/FIFO abstract data types, monotonic stacks, and circular buffers",
                "subtopics": [
                    "01. Stack Introduction & LIFO Principle",
                    "02. Stack Using Array & Dynamic Resizing",
                    "03. Stack Using Linked List",
                    "04. Push, Pop & Peek Operations",
                    "05. Balanced Parentheses & Validation",
                    "06. Infix, Prefix & Postfix Conversions",
                    "07. Monotonic Stack Pattern",
                    "08. Next Greater Element & Stock Span",
                    "09. Queue Introduction & FIFO Principle",
                    "10. Queue Using Array & Linked List",
                    "11. Circular Queue (Ring Buffer)",
                    "12. Double-Ended Queue (Deque)",
                    "13. Priority Queue Introduction",
                    "14. Queue-Based Problem Patterns"
                ]
            },
            "module_6": {
                "title": "Module 6: Hashing",
                "phase": "Phase 6 — Hashing",
                "icon": "🗝️",
                "focus": "Hash functions, collision resolution, HashMaps, HashSets, and O(1) lookups",
                "subtopics": [
                    "01. Hashing Introduction & Direct Addressing",
                    "02. Hash Functions & Uniform Distribution",
                    "03. Hash Tables & Load Factor",
                    "04. Collision Resolution: Chaining vs Open Addressing",
                    "05. HashMap & Key-Value Associative Mappings",
                    "06. HashSet & Unique Element Tracking",
                    "07. Frequency Counting & Histogram Maps",
                    "08. Duplicate Detection & Set Membership",
                    "09. Two Sum Problem & Complements",
                    "10. Group Anagrams using Hash Keys",
                    "11. Longest Consecutive Sequence in O(N)"
                ]
            },
            "module_7": {
                "title": "Module 7: Recursion & Backtracking",
                "phase": "Phase 7 — Recursion & Backtracking",
                "icon": "🔄",
                "focus": "Recursive call stacks, state-space trees, combinatorial search, and pruning",
                "subtopics": [
                    "01. Recursion Basics & Mathematical Induction",
                    "02. Base Case vs Recursive Case",
                    "03. Call Stack Execution & Stack Overflow",
                    "04. Recursion on Arrays & Sequences",
                    "05. Recursion on Strings & Palindromes",
                    "06. Recursion Complexity & Recurrence Relations",
                    "07. Tail Recursion & Optimization",
                    "08. Backtracking Introduction & Decision Trees",
                    "09. Generate Subsets (Power Set)",
                    "10. Generate Subsequences & Combinations",
                    "11. Permutations with & without Duplicates",
                    "12. Combination Sum (Unbounded & Bounded)",
                    "13. N-Queens Problem & Constraint Checking",
                    "14. Sudoku Solver with Pruning",
                    "15. Maze Problems & Rat in a Maze"
                ]
            },
            "module_8": {
                "title": "Module 8: Binary Trees & BSTs",
                "phase": "Phase 8 — Trees",
                "icon": "🌲",
                "focus": "Hierarchical structures, tree traversals, BST properties, and LCA",
                "subtopics": [
                    "01. Tree Introduction & Hierarchical Concepts",
                    "02. Binary Tree Properties & Types",
                    "03. Tree Terminology (Depth, Height, Degree)",
                    "04. Tree Representation in Memory",
                    "05. Preorder, Inorder & Postorder Traversals (DFS)",
                    "06. Level Order Traversal (BFS / Breadth-First)",
                    "07. Height & Maximum Depth of Binary Tree",
                    "08. Diameter of Binary Tree",
                    "09. Balanced Binary Tree Validation",
                    "10. Lowest Common Ancestor (LCA) in Binary Tree",
                    "11. Binary Search Tree (BST) Introduction & Invariant",
                    "12. BST Search, Insertion & Deletion",
                    "13. Minimum & Maximum in BST",
                    "14. Validate Binary Search Tree (Range Invariant)",
                    "15. Lowest Common Ancestor in BST",
                    "16. Kth Smallest Element in BST"
                ]
            },
            "module_9": {
                "title": "Module 9: Heaps & Priority Queues",
                "phase": "Phase 9 — Heaps & Priority Queues",
                "icon": "🏔️",
                "focus": "Binary heaps, heapify operations, priority queues, and Top-K paradigms",
                "subtopics": [
                    "01. Heap Introduction & Complete Binary Tree Property",
                    "02. Min Heap vs Max Heap Invariants",
                    "03. Array Representation of Binary Heaps",
                    "04. Heapify Operation (Sift-Up & Sift-Down)",
                    "05. Insertion & Extraction (O(log N))",
                    "06. Heap Sort Algorithm & Complexity",
                    "07. Priority Queue Implementation & Wrappers",
                    "08. Top-K Frequent Elements Pattern",
                    "09. Kth Largest & Smallest Element in Array",
                    "10. Merge K Sorted Lists Using Min Heap",
                    "11. Find Median from Data Stream (Two Heaps)"
                ]
            },
            "module_10": {
                "title": "Module 10: Graph Algorithms",
                "phase": "Phase 10 — Graphs",
                "icon": "🕸️",
                "focus": "Graph representations, BFS/DFS, topological sorting, shortest paths, and MST",
                "subtopics": [
                    "01. Graph Introduction, Vertices & Edges",
                    "02. Directed vs Undirected, Weighted vs Unweighted",
                    "03. Adjacency Matrix vs Adjacency List",
                    "04. Breadth-First Search (BFS) Traversal",
                    "05. Depth-First Search (DFS) Traversal",
                    "06. Connected Components & Number of Islands",
                    "07. Cycle Detection in Undirected & Directed Graphs",
                    "08. Bipartite Graph Verification (2-Coloring)",
                    "09. Topological Sort (DFS & Postorder Reversal)",
                    "10. Kahn's Algorithm (In-Degree BFS)",
                    "11. Shortest Path in Unweighted Graphs (BFS)",
                    "12. Dijkstra's Algorithm (Single Source Shortest Path)",
                    "13. Bellman-Ford Algorithm (Negative Weights & Cycles)",
                    "14. Floyd-Warshall Algorithm (All-Pairs Shortest Path)",
                    "15. Minimum Spanning Tree: Prim's Algorithm",
                    "16. Minimum Spanning Tree: Kruskal's Algorithm",
                    "17. Disjoint Set Union (DSU / Union-Find with Path Compression)"
                ]
            },
            "module_11": {
                "title": "Module 11: Greedy Algorithms",
                "phase": "Phase 11 — Greedy Algorithms",
                "icon": "🎯",
                "focus": "Greedy choice property, optimal substructure, interval scheduling, and platform optimization",
                "subtopics": [
                    "01. Greedy Introduction & Heuristic Choice",
                    "02. Greedy Choice Property & Proof by Induction",
                    "03. Activity Selection Problem (Interval Scheduling)",
                    "04. Fractional Knapsack Problem",
                    "05. Job Sequencing with Deadlines",
                    "06. Huffman Coding & Compression Trees",
                    "07. Non-Overlapping Intervals & Merging Intervals",
                    "08. Minimum Platforms Required for Trains"
                ]
            },
            "module_12": {
                "title": "Module 12: Dynamic Programming",
                "phase": "Phase 12 — Dynamic Programming",
                "icon": "📐",
                "focus": "Overlapping subproblems, optimal substructure, 1D/2D tabulation, and classic DP problems",
                "subtopics": [
                    "01. What is Dynamic Programming?",
                    "02. Overlapping Subproblems vs Divide & Conquer",
                    "03. Optimal Substructure Property",
                    "04. Top-Down Memoization Strategy",
                    "05. Bottom-Up Tabulation Strategy",
                    "06. Space Optimization in DP",
                    "07. 1D DP: Fibonacci & Climbing Stairs",
                    "08. 1D DP: House Robber & Maximum Subarray",
                    "09. 2D DP: Grid Unique Paths & Minimum Path Sum",
                    "10. 0/1 Knapsack Problem (Bounded)",
                    "11. Unbounded Knapsack & Rod Cutting",
                    "12. Coin Change I (Min Coins) & Coin Change II (Ways)",
                    "13. Longest Common Subsequence (LCS)",
                    "14. Longest Increasing Subsequence (LIS in O(N log N))",
                    "15. Edit Distance (Levenshtein Matrix)",
                    "16. Matrix Chain Multiplication (Partition DP)",
                    "17. DP on Trees & Subsequences"
                ]
            },
            "module_13": {
                "title": "Module 13: Advanced DSA",
                "phase": "Phase 13 — Advanced DSA",
                "icon": "⚡",
                "focus": "Prefix trees, range query segment trees, Fenwick trees, AVL balancing, and bit manipulation",
                "subtopics": [
                    "01. Trie (Prefix Tree) Implementation (Insert, Search, StartsWith)",
                    "02. Word Dictionary with Wildcards & Autocomplete",
                    "03. Segment Tree: Range Minimum & Sum Queries",
                    "04. Lazy Propagation in Segment Trees",
                    "05. Fenwick Tree (Binary Indexed Tree / BIT)",
                    "06. AVL Tree Self-Balancing & Rotations (LL, RR, LR, RL)",
                    "07. Tarjan's Strongly Connected Components (SCC)",
                    "08. Network Flow: Ford-Fulkerson & Edmonds-Karp",
                    "09. Bit Manipulation Fundamentals (Bitwise AND, OR, XOR, Shifts)",
                    "10. Bitmask DP & Computational Geometry Basics"
                ]
            },
            "module_14": {
                "title": "Module 14: Interview Problem Patterns",
                "phase": "Phase 14 — Interview Problem Patterns",
                "icon": "🏆",
                "focus": "The 18 high-yield coding interview patterns and comprehensive problem recognition",
                "subtopics": [
                    "01. Pattern 1: Arrays & Hashing Lookups",
                    "02. Pattern 2: Two Pointers (Converging & Diverging)",
                    "03. Pattern 3: Sliding Window (Fixed, Variable, At Most K)",
                    "04. Pattern 4: Binary Search & Search on Answer",
                    "05. Pattern 5: Monotonic Stack & Queue",
                    "06. Pattern 6: Fast & Slow Linked List Pointers",
                    "07. Pattern 7: Tree DFS Traversals & Depth Recursion",
                    "08. Pattern 8: Tree BFS / Level-Order Queue Processing",
                    "09. Pattern 9: Two Heaps (Median Finding)",
                    "10. Pattern 10: Top-K Elements & Heap Selection",
                    "11. Pattern 11: Backtracking (Subsets, Combinations, Permutations)",
                    "12. Pattern 12: Graph BFS / Multi-Source Matrix Search",
                    "13. Pattern 13: Graph DFS / Island Traversal / Topological Sort",
                    "14. Pattern 14: Dijkstra & Shortest Path Graph Optimization",
                    "15. Pattern 15: Greedy Choice & Activity Interval Sorting",
                    "16. Pattern 16: 1D Dynamic Programming (Decide & Take)",
                    "17. Pattern 17: 2D Dynamic Programming (Grid & String Matching)",
                    "18. Pattern 18: Mixed Interview Problems & Meta Problem Solving Strategy"
                ]
            },
            # ── Aliases for backward compatibility ──
            "intro": {
                "title": "Module 1: Complexity Analysis (DSA Fundamentals)",
                "phase": "Phase 1 — DSA Fundamentals",
                "icon": "⏱️",
                "focus": "Time & Space Complexity, Big-O Notation, and Operation Efficiency",
                "subtopics": ["01. What are Data Structures?", "02. What are Algorithms?", "03. Time Complexity", "04. Space Complexity", "05. Big-O Notation", "06. O(1), O(log n), O(n)", "07. O(n log n), O(n²)", "08. Best/Average/Worst Case", "09. Complexity of common operations"]
            },
            "core": {
                "title": "Module 2: Arrays & Strings",
                "phase": "Phase 2 — Arrays & Strings",
                "icon": "🧱",
                "focus": "Array fundamentals, string manipulation, two pointers, and sliding window",
                "subtopics": ["01. Array Introduction & Memory Layout", "02. Array Declaration & Initialization", "03. Traversal, Insertion & Deletion", "04. Prefix Sum & Kadane's Algorithm", "05. String Basics, Frequency & Palindromes", "06. Two Pointers & Sliding Window Patterns"]
            },
            "advanced": {
                "title": "Module 8: Binary Trees & BSTs",
                "phase": "Phase 8 — Trees",
                "icon": "🌲",
                "focus": "Hierarchical structures, tree traversals, BST properties, and LCA",
                "subtopics": ["01. Binary Tree Traversals (Pre, In, Post, Level Order)", "02. Tree Height, Diameter & Balanced Trees", "03. Binary Search Tree (BST) Operations", "04. Lowest Common Ancestor (LCA) in Tree & BST"]
            },
            "summary": {
                "title": "Module 14: Interview Problem Patterns",
                "phase": "Phase 14 — Interview Problem Patterns",
                "icon": "🏆",
                "focus": "The 18 high-yield coding interview patterns and comprehensive problem recognition",
                "subtopics": ["01. Two Pointers & Sliding Window Patterns", "02. Tree & Graph Search Patterns", "03. Dynamic Programming Patterns", "04. Mixed Interview Problems Strategy"]
            }
        }
    },
    "DSA": {
        "title": "Data Structures & Algorithms",
        "description": "Comprehensive 14-module curriculum spanning complexity analysis, linear structures, trees, graphs, greedy algorithms, dynamic programming, advanced structures, and interview patterns in C, C++, Python, or Java.",
        "modules": {}
    }
}

# Mirror DSA to Data Structures & Algorithms
TOPIC_SYLLABUS["DSA"]["modules"] = TOPIC_SYLLABUS["Data Structures & Algorithms"]["modules"]

# ══════════════════════════════════════════════════════════════════════════════
# ROLES REGISTRY: Structured definitions for all primary and extended roles
# ══════════════════════════════════════════════════════════════════════════════
ROLES_REGISTRY: Dict[str, Dict[str, Any]] = {
    # ── 1. DevOps Engineer / SRE (Primary focus) ──
    "DevOps Engineer": {
        "category": "DevOps & Cloud Infrastructure",
        "description": "Automating software delivery, infrastructure, deployment, monitoring, scalability, and reliability.",
        "skills": [
            "Git", "GitHub", "Linux", "Docker", "Kubernetes", "CI/CD",
            "AWS", "Terraform", "Ansible", "Prometheus", "Grafana",
            "Networking", "DevSecOps", "Bash", "Python"
        ],
        "roadmap": [
            {
                "topic": "Git",
                "title": "1. Git & GitHub Version Control",
                "prerequisites": [],
                "description": "Distributed version control, branching, pull requests, and conflict resolution."
            },
            {
                "topic": "Linux",
                "title": "2. Linux Systems & Administration",
                "prerequisites": [],
                "description": "Operating system fundamentals, bash scripting, file permissions, and services."
            },
            {
                "topic": "Networking",
                "title": "3. DevOps Networking & Protocols",
                "prerequisites": [],
                "description": "TCP/IP, DNS, HTTP/HTTPS, load balancers, reverse proxies, and firewalls."
            },
            {
                "topic": "Docker",
                "title": "4. Docker Containers & Virtualization",
                "prerequisites": ["Linux"],
                "description": "Container virtualization, images, Dockerfiles, and Docker Compose."
            },
            {
                "topic": "CI/CD",
                "title": "5. CI/CD Automated Pipelines",
                "prerequisites": ["Git", "Docker"],
                "description": "Continuous integration, automated testing, GitHub Actions, and Jenkins."
            },
            {
                "topic": "Kubernetes",
                "title": "6. Kubernetes Container Orchestration",
                "prerequisites": ["Docker", "Linux"],
                "description": "Cluster architecture, Pods, Deployments, Services, Helm, and troubleshooting."
            },
            {
                "topic": "AWS Cloud",
                "title": "7. Cloud Infrastructure (AWS)",
                "prerequisites": ["Networking"],
                "description": "Cloud compute, S3, IAM security, VPC networking, and cloud deployment."
            },
            {
                "topic": "Terraform",
                "title": "8. Infrastructure as Code (Terraform)",
                "prerequisites": ["AWS Cloud"],
                "description": "Declarative cloud provisioning, state management, and reusable modules."
            },
            {
                "topic": "Prometheus & Grafana",
                "title": "9. Monitoring & Observability",
                "prerequisites": ["Linux", "Kubernetes"],
                "description": "Metrics collection, PromQL, Grafana visualization, and Alertmanager."
            },
            {
                "topic": "DevSecOps",
                "title": "10. DevSecOps & Security Hardening",
                "prerequisites": ["CI/CD", "Docker"],
                "description": "Secrets management, container security, vulnerability scanning, and policies."
            }
        ]
    },

    "Cloud DevOps Engineer": {
        "category": "DevOps & Cloud Infrastructure",
        "description": "Specializing in multi-cloud DevOps, automated cloud infrastructure, and Kubernetes.",
        "skills": ["AWS", "Docker", "Kubernetes", "Git", "CI/CD", "Terraform", "Linux", "Python", "Prometheus"],
        "roadmap": [
            {"topic": "Git", "title": "1. Git Version Control", "prerequisites": [], "description": "Version control fundamentals."},
            {"topic": "Linux", "title": "2. Linux Administration", "prerequisites": [], "description": "Linux and bash automation."},
            {"topic": "Docker", "title": "3. Containerization", "prerequisites": ["Linux"], "description": "Docker images and containers."},
            {"topic": "AWS Cloud", "title": "4. AWS Cloud Infrastructure", "prerequisites": [], "description": "Cloud architecture and IAM."},
            {"topic": "CI/CD", "title": "5. Automated CI/CD", "prerequisites": ["Git", "Docker"], "description": "Continuous delivery pipelines."},
            {"topic": "Kubernetes", "title": "6. Kubernetes Orchestration", "prerequisites": ["Docker"], "description": "Cluster management and Helm."},
            {"topic": "Terraform", "title": "7. Terraform IaC", "prerequisites": ["AWS Cloud"], "description": "Automated infrastructure code."},
            {"topic": "Prometheus & Grafana", "title": "8. Cloud Monitoring", "prerequisites": ["Kubernetes"], "description": "Observability and alerting."}
        ]
    },

    "Cloud Engineer": {
        "category": "DevOps & Cloud Infrastructure",
        "description": "Designing, deploying, and maintaining enterprise cloud infrastructure and security.",
        "skills": ["AWS", "Docker", "Kubernetes", "Git", "Python", "Linux", "Terraform", "Networking"],
        "roadmap": [
            {"topic": "Networking", "title": "1. Cloud Networking", "prerequisites": [], "description": "VPC, DNS, and protocols."},
            {"topic": "Linux", "title": "2. Linux Systems", "prerequisites": [], "description": "Linux administration and shell."},
            {"topic": "AWS Cloud", "title": "3. AWS Core Services", "prerequisites": ["Networking"], "description": "Compute, storage, IAM, and databases."},
            {"topic": "Docker", "title": "4. Containers on Cloud", "prerequisites": ["Linux"], "description": "Docker containerization."},
            {"topic": "Terraform", "title": "5. Terraform Provisioning", "prerequisites": ["AWS Cloud"], "description": "Infrastructure as Code."},
            {"topic": "Kubernetes", "title": "6. Managed Kubernetes (EKS)", "prerequisites": ["Docker"], "description": "Cluster operations on cloud."}
        ]
    },

    # ── 2. Frontend Developer ──
    "Frontend Developer": {
        "category": "Web & Mobile Development",
        "description": "Building modern, responsive user interfaces and client-side web applications.",
        "skills": [
            "HTML", "CSS", "JavaScript", "TypeScript", "React", "Angular", "Vue",
            "Responsive Design", "Git", "REST API", "Testing"
        ],
        "roadmap": [
            {
                "topic": "JavaScript",
                "title": "1. Modern JavaScript (ES6+)",
                "prerequisites": [],
                "description": "Core mechanics, async/await, closures, and modern DOM methods."
            },
            {
                "topic": "TypeScript",
                "title": "2. TypeScript Typing & Generics",
                "prerequisites": ["JavaScript"],
                "description": "Static typing, interfaces, generics, and enterprise architecture."
            },
            {
                "topic": "Git",
                "title": "3. Git & GitHub for Developers",
                "prerequisites": [],
                "description": "Branching, pull requests, and collaborative code reviews."
            },
            {
                "topic": "React",
                "title": "4. React Component Engineering",
                "prerequisites": ["JavaScript", "TypeScript"],
                "description": "Virtual DOM, hooks, state management, and modern component design."
            },
            {
                "topic": "QA Testing",
                "title": "5. Frontend Testing & Automation",
                "prerequisites": ["React"],
                "description": "Unit testing with Jest, React Testing Library, and E2E with Cypress."
            },
            {
                "topic": "CI/CD",
                "title": "6. Frontend Build & Deployment",
                "prerequisites": ["Git"],
                "description": "Vite builds, GitHub Actions deployment, and CDN hosting."
            }
        ]
    },

    "React Developer": {
        "category": "Web & Mobile Development",
        "description": "Specialized in building high-performance React applications, Next.js, and state management.",
        "skills": ["React", "JavaScript", "TypeScript", "HTML", "CSS", "Git", "REST API", "Redux"],
        "roadmap": [
            {"topic": "JavaScript", "title": "1. Advanced JavaScript", "prerequisites": [], "description": "Modern JS patterns."},
            {"topic": "TypeScript", "title": "2. TypeScript Foundations", "prerequisites": ["JavaScript"], "description": "Type systems for React."},
            {"topic": "React", "title": "3. React Mastery", "prerequisites": ["JavaScript", "TypeScript"], "description": "Hooks, performance, and architecture."},
            {"topic": "Git", "title": "4. Git Collaboration", "prerequisites": [], "description": "Version control workflows."},
            {"topic": "QA Testing", "title": "5. React Testing", "prerequisites": ["React"], "description": "Jest & component testing."}
        ]
    },

    # ── 3. Backend Developer ──
    "Backend Developer": {
        "category": "Backend & Systems Engineering",
        "description": "Server-side development, APIs, databases, authentication, and backend architecture.",
        "skills": [
            "Python", "Node.js", "Java", "SQL", "PostgreSQL", "MongoDB",
            "REST API", "GraphQL", "Docker", "Git", "Security", "FastAPI"
        ],
        "roadmap": [
            {
                "topic": "Python",
                "title": "1. Python Backend Foundations",
                "prerequisites": [],
                "description": "Python language, OOP, exception handling, and FastAPI development."
            },
            {
                "topic": "SQL",
                "title": "2. Relational Databases & SQL",
                "prerequisites": [],
                "description": "Schema design, joins, indexing, transactions, and PostgreSQL."
            },
            {
                "topic": "Git",
                "title": "3. Version Control & Git",
                "prerequisites": [],
                "description": "Branching, collaborative workflows, and pull requests."
            },
            {
                "topic": "Docker",
                "title": "4. Docker for Backend Services",
                "prerequisites": [],
                "description": "Containerizing backend services, database containers, and compose."
            },
            {
                "topic": "System Design",
                "title": "5. System Design & Scalability",
                "prerequisites": ["SQL"],
                "description": "Microservices, caching with Redis, message queues, and API design."
            },
            {
                "topic": "QA Testing",
                "title": "6. Backend Testing & Automation",
                "prerequisites": ["Python"],
                "description": "Pytest unit tests, integration tests, and API contract testing."
            },
            {
                "topic": "CI/CD",
                "title": "7. Automated API Deployment",
                "prerequisites": ["Git", "Docker"],
                "description": "Automated pipelines, staging environments, and container release."
            }
        ]
    },

    "Python Developer": {
        "category": "Backend & Systems Engineering",
        "description": "Building robust Python applications, backend services, automation scripts, and APIs.",
        "skills": ["Python", "SQL", "FastAPI", "Git", "Docker", "Pandas", "Pytest"],
        "roadmap": [
            {"topic": "Python", "title": "1. Python Advanced Mastery", "prerequisites": [], "description": "OOP, decorators, and concurrency."},
            {"topic": "SQL", "title": "2. SQL & Database Modeling", "prerequisites": [], "description": "Relational databases and ORM."},
            {"topic": "Git", "title": "3. Git & GitHub", "prerequisites": [], "description": "Version control best practices."},
            {"topic": "Docker", "title": "4. Dockerizing Python Apps", "prerequisites": [], "description": "Containerizing FastAPI services."},
            {"topic": "QA Testing", "title": "5. Pytest & Testing", "prerequisites": ["Python"], "description": "Unit testing and test automation."}
        ]
    },

    "Java Developer": {
        "category": "Backend & Systems Engineering",
        "description": "Enterprise backend systems, Spring Boot, microservices, and distributed architecture.",
        "skills": ["Java", "SQL", "Spring Boot", "Docker", "Git", "Microservices", "REST API"],
        "roadmap": [
            {"topic": "Python", "title": "1. Backend Foundations", "prerequisites": [], "description": "Core backend concepts."},
            {"topic": "SQL", "title": "2. SQL & Relational DBs", "prerequisites": [], "description": "Database queries and transactions."},
            {"topic": "System Design", "title": "3. Microservices Architecture", "prerequisites": ["SQL"], "description": "System design and distributed systems."},
            {"topic": "Docker", "title": "4. Containerization", "prerequisites": [], "description": "Containers and Docker Compose."},
            {"topic": "CI/CD", "title": "5. Enterprise CI/CD", "prerequisites": ["Docker"], "description": "Automated build and test pipelines."}
        ]
    },

    # ── 4. Full-Stack Developer ──
    "Full Stack Developer": {
        "category": "Engineering & Architecture",
        "description": "Building complete applications across frontend, backend, database, and deployment.",
        "skills": [
            "HTML", "CSS", "JavaScript", "TypeScript", "React", "Node.js", "Python",
            "REST API", "SQL", "MongoDB", "Git", "Docker", "CI/CD"
        ],
        "roadmap": [
            {"topic": "JavaScript", "title": "1. Modern JavaScript (ES6+)", "prerequisites": [], "description": "Core client and server JavaScript."},
            {"topic": "TypeScript", "title": "2. TypeScript for Full Stack", "prerequisites": ["JavaScript"], "description": "Unified types across frontend and backend."},
            {"topic": "React", "title": "3. Frontend with React", "prerequisites": ["JavaScript"], "description": "Modern UI development and state management."},
            {"topic": "Python", "title": "4. Backend APIs & Services", "prerequisites": [], "description": "Server-side RESTful API development."},
            {"topic": "SQL", "title": "5. Relational Databases & SQL", "prerequisites": [], "description": "Database design, queries, and migrations."},
            {"topic": "Docker", "title": "6. Containerized Full Stack", "prerequisites": [], "description": "Running frontend, backend, and DB with Docker."},
            {"topic": "CI/CD", "title": "7. CI/CD & Deployment", "prerequisites": ["Docker"], "description": "Automated end-to-end deployment."}
        ]
    },

    # ── 5. Quality Assurance / Test Engineer ──
    "QA / Automation Engineer": {
        "category": "Engineering & Architecture",
        "description": "Software testing, test automation, quality assurance, and defect prevention.",
        "skills": [
            "Selenium", "Cypress", "Pytest", "Jest", "Postman", "API Testing",
            "Unit Testing", "Jira", "CI/CD", "Git", "Python"
        ],
        "roadmap": [
            {
                "topic": "QA Testing",
                "title": "1. Testing Fundamentals & Automation",
                "prerequisites": [],
                "description": "Test design, unit testing, Selenium, Cypress, and API testing."
            },
            {
                "topic": "Python",
                "title": "2. Python for Test Automation",
                "prerequisites": [],
                "description": "Scripting automation frameworks and data-driven tests."
            },
            {
                "topic": "Git",
                "title": "3. Git for QA Engineers",
                "prerequisites": [],
                "description": "Managing test repositories and branch workflows."
            },
            {
                "topic": "Docker",
                "title": "4. Containerized Test Environments",
                "prerequisites": [],
                "description": "Running headless browsers and test grids in Docker."
            },
            {
                "topic": "CI/CD",
                "title": "5. CI/CD Automated Test Gates",
                "prerequisites": ["QA Testing", "Git"],
                "description": "Integrating automated smoke and regression tests into pipelines."
            }
        ]
    },

    # ── 6. Software Architect ──
    "Software Architect": {
        "category": "Engineering & Architecture",
        "description": "Designing scalable, reliable, maintainable distributed software systems.",
        "skills": [
            "System Design", "Microservices", "Design Patterns", "SOLID",
            "Distributed Systems", "SQL", "Docker", "Kubernetes", "Cloud Architecture"
        ],
        "roadmap": [
            {
                "topic": "System Design",
                "title": "1. Scalable System Design",
                "prerequisites": [],
                "description": "Scalability, high availability, caching, and distributed architecture."
            },
            {
                "topic": "SQL",
                "title": "2. Advanced Data Architecture",
                "prerequisites": [],
                "description": "Database sharding, replication, normalization, and ACID guarantees."
            },
            {
                "topic": "Docker",
                "title": "3. Microservices Packaging",
                "prerequisites": [],
                "description": "Service decomposition and containerized architectures."
            },
            {
                "topic": "Kubernetes",
                "title": "4. Distributed Container Orchestration",
                "prerequisites": ["Docker"],
                "description": "Service discovery, ingress, and resilient cloud orchestration."
            },
            {
                "topic": "AWS Cloud",
                "title": "5. Enterprise Cloud Architecture",
                "prerequisites": [],
                "description": "Designing multi-region, disaster-recovery cloud infrastructures."
            }
        ]
    },

    # ── 7. Data Engineer ──
    "Data Engineer": {
        "category": "Data & AI Engineering",
        "description": "Building data pipelines, data platforms, ETL systems, and large-scale data infrastructure.",
        "skills": [
            "Python", "SQL", "Spark", "Kafka", "Airflow", "ETL",
            "Docker", "Kubernetes", "AWS", "Git", "Pandas"
        ],
        "roadmap": [
            {
                "topic": "Python",
                "title": "1. Python for Data Engineering",
                "prerequisites": [],
                "description": "Python scripting, data manipulation with Pandas, and data validation."
            },
            {
                "topic": "SQL",
                "title": "2. Advanced SQL & Data Warehousing",
                "prerequisites": [],
                "description": "Analytical queries, window functions, and dimensional modeling."
            },
            {
                "topic": "Data Engineering",
                "title": "3. Distributed Processing with Spark",
                "prerequisites": ["Python", "SQL"],
                "description": "Apache Spark, PySpark, Airflow workflow DAGs, and Kafka streaming."
            },
            {
                "topic": "Docker",
                "title": "4. Containerized Data Workflows",
                "prerequisites": [],
                "description": "Running Airflow, Spark, and databases in containers."
            },
            {
                "topic": "AWS Cloud",
                "title": "5. Cloud Data Lakes & Storage",
                "prerequisites": [],
                "description": "S3 Data Lakes, Redshift/Snowflake, and IAM data security."
            }
        ]
    },

    # ── 8. AI & Machine Learning Roles ──
    "Machine Learning Engineer": {
        "category": "Data & AI Engineering",
        "description": "Training, evaluating, and deploying machine learning models into production systems.",
        "skills": [
            "Python", "Machine Learning", "Deep Learning", "TensorFlow", "PyTorch",
            "NumPy", "Pandas", "Docker", "Git", "Statistics"
        ],
        "roadmap": [
            {"topic": "Python", "title": "1. Python for Data & ML", "prerequisites": [], "description": "NumPy, Pandas, and data processing."},
            {"topic": "Machine Learning", "title": "2. Supervised & Unsupervised ML", "prerequisites": ["Python"], "description": "Scikit-learn, trees, ensembles, and evaluation."},
            {"topic": "Deep Learning", "title": "3. Deep Neural Networks", "prerequisites": ["Machine Learning"], "description": "PyTorch, CNNs, and backpropagation."},
            {"topic": "MLOps", "title": "4. Model Deployment & MLOps", "prerequisites": ["Machine Learning"], "description": "MLflow tracking, model APIs, and monitoring."},
            {"topic": "Docker", "title": "5. Containerized ML Inference", "prerequisites": [], "description": "Packaging models into Docker containers."}
        ]
    },

    "AI/ML Engineer": {
        "category": "Data & AI Engineering",
        "description": "Developing and scaling AI/ML systems, deep learning models, and production APIs.",
        "skills": ["Python", "Machine Learning", "Deep Learning", "TensorFlow", "PyTorch", "Docker", "Git", "MLOps"],
        "roadmap": [
            {"topic": "Python", "title": "1. Python Core", "prerequisites": [], "description": "Python programming and libraries."},
            {"topic": "Machine Learning", "title": "2. ML Algorithms", "prerequisites": ["Python"], "description": "Feature engineering and classification."},
            {"topic": "Deep Learning", "title": "3. Neural Networks", "prerequisites": ["Machine Learning"], "description": "PyTorch models and training loops."},
            {"topic": "MLOps", "title": "4. Production MLOps", "prerequisites": ["Machine Learning"], "description": "MLflow and model pipelines."}
        ]
    },

    "Generative AI Engineer": {
        "category": "Data & AI Engineering",
        "description": "Building LLM applications, retrieval-augmented generation (RAG), and fine-tuning models.",
        "skills": ["Python", "Deep Learning", "PyTorch", "NLP", "Git", "Docker", "FastAPI"],
        "roadmap": [
            {"topic": "Python", "title": "1. Python for AI", "prerequisites": [], "description": "Python async programming and APIs."},
            {"topic": "Deep Learning", "title": "2. Transformers & Attention", "prerequisites": ["Python"], "description": "Deep learning architectures and PyTorch."},
            {"topic": "Docker", "title": "3. Dockerizing AI Services", "prerequisites": [], "description": "Containerizing LLM inference servers."},
            {"topic": "System Design", "title": "4. Scalable RAG Systems", "prerequisites": ["Python"], "description": "Vector databases, caching, and rate limiting."}
        ]
    },

    "MLOps Engineer": {
        "category": "Data & AI Engineering",
        "description": "Automating machine learning lifecycles, model registries, CI/CD for ML, and monitoring.",
        "skills": ["Python", "Docker", "Kubernetes", "AWS", "Git", "Machine Learning", "FastAPI", "MLOps"],
        "roadmap": [
            {"topic": "Python", "title": "1. Python for ML", "prerequisites": [], "description": "Scripting and API development."},
            {"topic": "Docker", "title": "2. Containers for ML", "prerequisites": [], "description": "Docker images for training and inference."},
            {"topic": "MLOps", "title": "3. MLOps Pipelines & Tracking", "prerequisites": ["Python", "Docker"], "description": "MLflow, DVC, and model registry."},
            {"topic": "Kubernetes", "title": "4. Kubeflow & Cluster ML", "prerequisites": ["Docker"], "description": "Running distributed ML workloads."},
            {"topic": "CI/CD", "title": "5. Automated ML Pipelines", "prerequisites": ["Docker"], "description": "Continuous training and model release."}
        ]
    },

    "Data Scientist": {
        "category": "Data & AI Engineering",
        "description": "Analyzing complex datasets, statistical modeling, and actionable business intelligence.",
        "skills": ["Python", "SQL", "Pandas", "NumPy", "Statistics", "Machine Learning", "Git"],
        "roadmap": [
            {"topic": "Python", "title": "1. Python & Data Analysis", "prerequisites": [], "description": "Pandas, NumPy, and visualization."},
            {"topic": "SQL", "title": "2. SQL Analytics", "prerequisites": [], "description": "Advanced joins and aggregations."},
            {"topic": "Machine Learning", "title": "3. Predictive Modeling", "prerequisites": ["Python"], "description": "Classification, regression, and clustering."}
        ]
    },

    "Data Analyst": {
        "category": "Data & AI Engineering",
        "description": "Data exploration, SQL querying, dashboarding, statistical summaries, and metrics reporting.",
        "skills": ["Python", "SQL", "Pandas", "NumPy", "Statistics", "Git"],
        "roadmap": [
            {"topic": "SQL", "title": "1. SQL Querying & Joins", "prerequisites": [], "description": "Database queries and data extraction."},
            {"topic": "Python", "title": "2. Python for Data Exploration", "prerequisites": [], "description": "Pandas DataFrames and data cleaning."},
            {"topic": "Git", "title": "3. Git Collaboration", "prerequisites": [], "description": "Version control for analytics scripts."}
        ]
    },

    "Cybersecurity Engineer": {
        "category": "DevOps & Cloud Infrastructure",
        "description": "Securing systems, network defense, penetration testing, DevSecOps, and compliance.",
        "skills": ["Linux", "Networking", "DevSecOps", "Docker", "Python", "Git", "AWS"],
        "roadmap": [
            {"topic": "Linux", "title": "1. Linux Hardening", "prerequisites": [], "description": "Permissions, audit logs, and SSH security."},
            {"topic": "Networking", "title": "2. Network Defense & Protocols", "prerequisites": [], "description": "Firewalls, TLS/SSL, and intrusion detection."},
            {"topic": "DevSecOps", "title": "3. DevSecOps & Vulnerability Scanning", "prerequisites": ["Linux"], "description": "Shift-left security and secrets management."},
            {"topic": "Docker", "title": "4. Container Security", "prerequisites": ["Linux"], "description": "Securing container images and runtimes."}
        ]
    },

    "Mobile App Developer": {
        "category": "Web & Mobile Development",
        "description": "Building mobile applications with React Native, cross-platform frameworks, and mobile APIs.",
        "skills": ["React", "JavaScript", "TypeScript", "Git", "REST API"],
        "roadmap": [
            {"topic": "JavaScript", "title": "1. Modern JavaScript", "prerequisites": [], "description": "Core JS and async programming."},
            {"topic": "TypeScript", "title": "2. TypeScript Foundations", "prerequisites": ["JavaScript"], "description": "Type systems for mobile code."},
            {"topic": "React", "title": "3. React & Component Architecture", "prerequisites": ["JavaScript"], "description": "Component hierarchies, state, and hooks."},
            {"topic": "Git", "title": "4. Git Version Control", "prerequisites": [], "description": "Branching and app releases."}
        ]
    },

    "Software Engineer": {
        "category": "Engineering & Architecture",
        "description": "Generalist software engineering across backend APIs, testing, system design, and deployment.",
        "skills": ["Python", "Git", "Docker", "SQL", "System Design", "QA Testing"],
        "roadmap": [
            {"topic": "Python", "title": "1. Python Programming", "prerequisites": [], "description": "Core language syntax, functions, and OOP."},
            {"topic": "SQL", "title": "2. SQL & Relational DBs", "prerequisites": [], "description": "Database design and querying."},
            {"topic": "Git", "title": "3. Git & GitHub", "prerequisites": [], "description": "Version control best practices."},
            {"topic": "Docker", "title": "4. Docker Containers", "prerequisites": [], "description": "Containerizing applications."},
            {"topic": "System Design", "title": "5. System Architecture", "prerequisites": ["SQL"], "description": "Scalable design patterns."}
        ]
    },

    "Site Reliability Engineer (SRE)": {
        "category": "DevOps & Cloud Infrastructure",
        "description": "Applying software engineering principles to operations, reliability, uptime, SLOs, and incident response.",
        "skills": ["Linux", "Networking", "Docker", "Kubernetes", "CI/CD", "Prometheus", "Grafana", "AWS", "Python", "DevSecOps"],
        "roadmap": [
            {"topic": "Linux", "title": "1. Linux Internals & Systems", "prerequisites": [], "description": "Kernel parameters, systemd, and troubleshooting."},
            {"topic": "Networking", "title": "2. High Availability Networking", "prerequisites": [], "description": "DNS, TLS, load balancing, and failover."},
            {"topic": "Docker", "title": "3. Container Infrastructure", "prerequisites": ["Linux"], "description": "Container runtimes and resource limits."},
            {"topic": "Kubernetes", "title": "4. Cluster Reliability & Resiliency", "prerequisites": ["Docker"], "description": "Pod disruption budgets, auto-scaling, and probes."},
            {"topic": "Prometheus & Grafana", "title": "5. Observability, SLOs & Alerting", "prerequisites": ["Linux", "Kubernetes"], "description": "SLOs, error budgets, PromQL, and Grafana dashboards."},
            {"topic": "CI/CD", "title": "6. Safe Progressive Deployments", "prerequisites": ["Docker"], "description": "Canary rollouts, blue-green, and rollback automation."},
            {"topic": "System Design", "title": "7. Fault-Tolerant System Design", "prerequisites": ["Networking"], "description": "Circuit breakers, rate limiting, and chaos engineering."}
        ]
    },

    "Node.js Developer": {
        "category": "Backend & Systems Engineering",
        "description": "Building scalable event-driven backend services, REST APIs, and microservices with Node.js and Express.",
        "skills": ["JavaScript", "TypeScript", "SQL", "Git", "Docker", "REST API", "System Design", "QA Testing"],
        "roadmap": [
            {"topic": "JavaScript", "title": "1. Advanced JavaScript & Event Loop", "prerequisites": [], "description": "Asynchronous event-driven programming and streams."},
            {"topic": "TypeScript", "title": "2. TypeScript for Node.js", "prerequisites": ["JavaScript"], "description": "Type-safe backend architecture and decorators."},
            {"topic": "SQL", "title": "3. Relational Databases & ORMs", "prerequisites": [], "description": "PostgreSQL, connection pooling, and Prisma/TypeORM."},
            {"topic": "Git", "title": "4. Git Version Control", "prerequisites": [], "description": "Team workflows and branch management."},
            {"topic": "Docker", "title": "5. Containerizing Node.js Services", "prerequisites": [], "description": "Multi-stage Dockerfiles and Alpine images."},
            {"topic": "QA Testing", "title": "6. Node.js API Testing", "prerequisites": ["JavaScript"], "description": "Jest, Supertest, and integration test suites."},
            {"topic": "System Design", "title": "7. Scalable Backend Design", "prerequisites": ["SQL"], "description": "Caching with Redis, message queues, and clustering."}
        ]
    },

    "Android Developer": {
        "category": "Web & Mobile Development",
        "description": "Developing high-performance Android mobile applications with modern UI and API integration.",
        "skills": ["JavaScript", "TypeScript", "React", "Git", "REST API", "QA Testing"],
        "roadmap": [
            {"topic": "JavaScript", "title": "1. Mobile JavaScript Fundamentals", "prerequisites": [], "description": "Core JavaScript and mobile runtime concepts."},
            {"topic": "TypeScript", "title": "2. TypeScript for Mobile", "prerequisites": ["JavaScript"], "description": "Strong typing for mobile data models."},
            {"topic": "React", "title": "3. Mobile Component Architecture", "prerequisites": ["JavaScript"], "description": "Component layouts, navigation, and state management."},
            {"topic": "Git", "title": "4. Mobile Release Git Workflow", "prerequisites": [], "description": "Feature branches and app version tagging."},
            {"topic": "QA Testing", "title": "5. Mobile Testing & Automation", "prerequisites": ["React"], "description": "Unit testing and mobile UI automation."}
        ]
    },

    "iOS Developer": {
        "category": "Web & Mobile Development",
        "description": "Building responsive, modern iOS applications with fluid animations and secure networking.",
        "skills": ["JavaScript", "TypeScript", "React", "Git", "REST API", "QA Testing"],
        "roadmap": [
            {"topic": "JavaScript", "title": "1. Modern Scripting & Logic", "prerequisites": [], "description": "Async flows, reactive patterns, and JSON parsing."},
            {"topic": "TypeScript", "title": "2. TypeScript Architecture", "prerequisites": ["JavaScript"], "description": "Contract-first development and interfaces."},
            {"topic": "React", "title": "3. Cross-Platform Mobile UI", "prerequisites": ["JavaScript"], "description": "Declarative mobile UI and state containers."},
            {"topic": "Git", "title": "4. Version Control for Mobile", "prerequisites": [], "description": "Branching, PRs, and release workflows."},
            {"topic": "QA Testing", "title": "5. Automated UI & App Testing", "prerequisites": ["React"], "description": "Automated testing and continuous delivery."}
        ]
    },

    "Database Engineer": {
        "category": "Backend & Systems Engineering",
        "description": "Designing, tuning, indexing, and maintaining high-throughput relational and NoSQL databases.",
        "skills": ["SQL", "Python", "Linux", "Docker", "System Design", "AWS"],
        "roadmap": [
            {"topic": "SQL", "title": "1. Advanced SQL & Query Optimization", "prerequisites": [], "description": "Query execution plans, B-Tree indexes, and transactions."},
            {"topic": "Linux", "title": "2. Linux Performance & I/O Tuning", "prerequisites": [], "description": "Disk I/O, memory management, and system buffers."},
            {"topic": "Python", "title": "3. Database Automation Scripting", "prerequisites": [], "description": "Backup scripts, schema migrations, and benchmark harnesses."},
            {"topic": "Docker", "title": "4. Database Containerization", "prerequisites": ["Linux"], "description": "Running Postgres clusters and replicas in containers."},
            {"topic": "System Design", "title": "5. High-Scale Data Partitioning", "prerequisites": ["SQL"], "description": "Sharding, read replicas, replication lag, and CAP theorem."},
            {"topic": "AWS Cloud", "title": "6. Managed Cloud Databases (RDS / Aurora)", "prerequisites": ["SQL"], "description": "Automated failover, backups, and point-in-time recovery."}
        ]
    },

    "Data Architect": {
        "category": "Data & AI Engineering",
        "description": "Designing enterprise data pipelines, data lakehouses, governance, and analytical architectures.",
        "skills": ["SQL", "Data Engineering", "System Design", "AWS", "Python", "Docker"],
        "roadmap": [
            {"topic": "SQL", "title": "1. Enterprise Data Modeling", "prerequisites": [], "description": "Star schemas, snowflake schemas, and Data Vault 2.0."},
            {"topic": "Data Engineering", "title": "2. Lakehouse & Distributed Data Engines", "prerequisites": ["SQL"], "description": "Apache Spark, Delta Lake, and pipeline orchestration."},
            {"topic": "System Design", "title": "3. Distributed Systems & Streaming Architecture", "prerequisites": ["SQL"], "description": "Event sourcing, Kafka streaming, and lambda architectures."},
            {"topic": "AWS Cloud", "title": "4. Enterprise Cloud Data Platforms", "prerequisites": ["SQL"], "description": "S3 Data Lakes, Redshift, Snowflake, and governance."},
            {"topic": "DevSecOps", "title": "5. Data Security & Compliance", "prerequisites": [], "description": "Column-level encryption, role-based access, and GDPR/HIPAA."}
        ]
    },

    "Cloud Architect": {
        "category": "DevOps & Cloud Infrastructure",
        "description": "Architecting resilient, cost-effective, multi-region cloud infrastructures and enterprise governance.",
        "skills": ["AWS", "Networking", "Linux", "Terraform", "Docker", "Kubernetes", "System Design", "DevSecOps"],
        "roadmap": [
            {"topic": "Networking", "title": "1. Enterprise Cloud Networking & Transit", "prerequisites": [], "description": "VPC peering, Transit Gateway, Route 53, and Direct Connect."},
            {"topic": "AWS Cloud", "title": "2. Multi-Region AWS Architecture", "prerequisites": ["Networking"], "description": "Well-Architected Framework pillars and disaster recovery."},
            {"topic": "Terraform", "title": "3. Enterprise Infrastructure as Code", "prerequisites": ["AWS Cloud"], "description": "Terraform Cloud, modular landing zones, and state isolation."},
            {"topic": "Kubernetes", "title": "4. Managed Cloud Orchestration", "prerequisites": ["AWS Cloud"], "description": "Amazon EKS, multi-cluster federation, and GitOps."},
            {"topic": "System Design", "title": "5. Large-Scale Distributed Architecture", "prerequisites": ["Networking"], "description": "Zero-downtime migrations, caching, and edge acceleration."},
            {"topic": "DevSecOps", "title": "6. Cloud Governance & Security", "prerequisites": ["AWS Cloud"], "description": "IAM boundaries, SCPs, compliance auditing, and encryption."}
        ]
    },

    "Security Engineer": {
        "category": "DevOps & Cloud Infrastructure",
        "description": "Protecting systems, infrastructure, and networks from cyber threats and vulnerabilities.",
        "skills": ["Linux", "Networking", "DevSecOps", "Docker", "AWS", "Python", "Git"],
        "roadmap": [
            {"topic": "Linux", "title": "1. Linux Security Hardening", "prerequisites": [], "description": "SELinux/AppArmor, auditd, SSH hardening, and kernel tuning."},
            {"topic": "Networking", "title": "2. Network Security & Packet Analysis", "prerequisites": [], "description": "Wireshark, firewalls, IDS/IPS, TLS 1.3, and VPNs."},
            {"topic": "DevSecOps", "title": "3. Vulnerability Scanning & DevSecOps", "prerequisites": ["Linux"], "description": "Trivy, OWASP dependency check, SonarQube, and policy-as-code."},
            {"topic": "Docker", "title": "4. Container Security & Sandboxing", "prerequisites": ["Linux"], "description": "Rootless containers, distroless images, and runtime defense."},
            {"topic": "AWS Cloud", "title": "5. Cloud Identity & Access Security", "prerequisites": ["Networking"], "description": "AWS GuardDuty, Security Hub, KMS, and CloudTrail forensics."}
        ]
    },

    "Automation Engineer": {
        "category": "Engineering & Architecture",
        "description": "Building end-to-end automation frameworks across software testing, delivery pipelines, and environments.",
        "skills": ["Python", "QA Testing", "Git", "Linux", "Docker", "CI/CD", "Bash"],
        "roadmap": [
            {"topic": "Python", "title": "1. Python for Automation & Scripting", "prerequisites": [], "description": "Automation scripts, file handling, and CLI tools."},
            {"topic": "QA Testing", "title": "2. Automated Test Frameworks", "prerequisites": ["Python"], "description": "Pytest, Selenium, Cypress, and API automation."},
            {"topic": "Git", "title": "3. Git Automation & Hooks", "prerequisites": [], "description": "Pre-commit hooks, git automation, and release tags."},
            {"topic": "Docker", "title": "4. Containerized Test Runners", "prerequisites": [], "description": "Headless browser containers and parallel test execution."},
            {"topic": "CI/CD", "title": "5. Automated Deployment Pipelines", "prerequisites": ["Git", "Docker"], "description": "Automated regression gates and continuous delivery."}
        ]
    },

    "Embedded Systems Engineer": {
        "category": "Engineering & Architecture",
        "description": "Developing low-level software, real-time operating systems, firmware, and hardware-interfacing code.",
        "skills": ["Linux", "Git", "Python", "Networking", "QA Testing"],
        "roadmap": [
            {"topic": "Linux", "title": "1. Embedded Linux & Kernel Basics", "prerequisites": [], "description": "Kernel architecture, cross-compilation, and device trees."},
            {"topic": "Git", "title": "2. Version Control for Hardware/Firmware", "prerequisites": [], "description": "Tracking releases, submodules, and firmware revisions."},
            {"topic": "Python", "title": "3. Python for Hardware Prototyping", "prerequisites": [], "description": "Serial communication, hardware testing, and sensor polling."},
            {"topic": "Networking", "title": "4. Embedded IoT Protocols & Networking", "prerequisites": [], "description": "MQTT, CoAP, TCP/IP, and socket programming."},
            {"topic": "QA Testing", "title": "5. Firmware Testing & Verification", "prerequisites": ["Python"], "description": "Hardware-in-the-loop (HIL) testing and test harnesses."}
        ]
    },

    "AI Engineer": {
        "category": "Data & AI Engineering",
        "description": "Integrating foundational AI models, building intelligent agents, and deploying cognitive workflows.",
        "skills": ["Python", "Machine Learning", "Deep Learning", "MLOps", "Docker", "System Design"],
        "roadmap": [
            {"topic": "Python", "title": "1. Advanced Python for AI", "prerequisites": [], "description": "Asynchronous APIs, NumPy, and data manipulation."},
            {"topic": "Machine Learning", "title": "2. Machine Learning Foundations", "prerequisites": ["Python"], "description": "Supervised learning, feature engineering, and metrics."},
            {"topic": "Deep Learning", "title": "3. Deep Neural Networks & Transformers", "prerequisites": ["Machine Learning"], "description": "PyTorch, attention mechanisms, and fine-tuning."},
            {"topic": "Docker", "title": "4. Containerized AI Workloads", "prerequisites": [], "description": "GPU containerization with NVIDIA Docker runtime."},
            {"topic": "MLOps", "title": "5. Model Serving & Observability", "prerequisites": ["Machine Learning"], "description": "FastAPI inference, latency monitoring, and drift detection."},
            {"topic": "System Design", "title": "6. Scalable AI Systems Architecture", "prerequisites": ["Python"], "description": "Vector search, caching, embedding pipelines, and rate limiting."}
        ]
    },

    "Deep Learning Engineer": {
        "category": "Data & AI Engineering",
        "description": "Designing and training deep neural architectures, vision transformers, sequence models, and loss functions.",
        "skills": ["Python", "Machine Learning", "Deep Learning", "PyTorch", "Docker", "MLOps"],
        "roadmap": [
            {"topic": "Python", "title": "1. Scientific Python & Linear Algebra", "prerequisites": [], "description": "NumPy vectorization, tensor operations, and broadcasting."},
            {"topic": "Machine Learning", "title": "2. Statistical Foundations & Optimization", "prerequisites": ["Python"], "description": "Gradient descent, loss functions, and regularization."},
            {"topic": "Deep Learning", "title": "3. PyTorch Deep Neural Networks", "prerequisites": ["Machine Learning"], "description": "Custom PyTorch modules, autograd, CNNs, and transformers."},
            {"topic": "Docker", "title": "4. Distributed Training Containers", "prerequisites": [], "description": "Containerizing training jobs with CUDA support."},
            {"topic": "MLOps", "title": "5. Experiment Tracking & Model Registry", "prerequisites": ["Deep Learning"], "description": "Weights & Biases, MLflow, and model artifact checkpointing."}
        ]
    },

    "NLP Engineer": {
        "category": "Data & AI Engineering",
        "description": "Natural Language Processing, tokenization, transformer architectures, text generation, and semantic search.",
        "skills": ["Python", "Machine Learning", "Deep Learning", "Docker", "MLOps"],
        "roadmap": [
            {"topic": "Python", "title": "1. Python for Text Processing", "prerequisites": [], "description": "String parsing, regular expressions, and corpus preprocessing."},
            {"topic": "Machine Learning", "title": "2. Classical NLP & Classification", "prerequisites": ["Python"], "description": "TF-IDF, word embeddings, and text classification."},
            {"topic": "Deep Learning", "title": "3. Transformer Models & HuggingFace", "prerequisites": ["Machine Learning"], "description": "BERT, GPT, attention mechanics, and fine-tuning."},
            {"topic": "Docker", "title": "4. Deploying NLP Microservices", "prerequisites": [], "description": "Serving transformer models with FastAPI and Docker."},
            {"topic": "System Design", "title": "5. Semantic Search & Vector Databases", "prerequisites": ["Python"], "description": "Dense vector retrieval, cosine similarity, and RAG pipelines."}
        ]
    },

    "Computer Vision Engineer": {
        "category": "Data & AI Engineering",
        "description": "Computer vision algorithms, image classification, object detection (YOLO), segmentation, and OpenCV.",
        "skills": ["Python", "Machine Learning", "Deep Learning", "Docker", "MLOps"],
        "roadmap": [
            {"topic": "Python", "title": "1. Image Processing with Python & NumPy", "prerequisites": [], "description": "Pixel matrices, transformations, and color spaces."},
            {"topic": "Machine Learning", "title": "2. Feature Extraction & Traditional CV", "prerequisites": ["Python"], "description": "Edge detection, thresholding, and morphological operations."},
            {"topic": "Deep Learning", "title": "3. CNNs & Vision Transformers", "prerequisites": ["Machine Learning"], "description": "ResNet, YOLO object detection, segmentation, and PyTorch."},
            {"topic": "Docker", "title": "4. Real-Time Vision Inference Containers", "prerequisites": [], "description": "GPU-accelerated container inference pipelines."},
            {"topic": "MLOps", "title": "5. Edge Deployment & Optimization", "prerequisites": ["Deep Learning"], "description": "TensorRT, ONNX quantization, and latency optimization."}
        ]
    },

    "AI Research Engineer": {
        "category": "Data & AI Engineering",
        "description": "Novel architecture experimentation, theoretical deep learning, model benchmarking, and paper reproduction.",
        "skills": ["Python", "Machine Learning", "Deep Learning", "MLOps", "Data Engineering"],
        "roadmap": [
            {"topic": "Python", "title": "1. Python & Mathematical Computation", "prerequisites": [], "description": "Numerical computation, autograd internals, and vector calculus."},
            {"topic": "Machine Learning", "title": "2. Advanced Statistical Learning", "prerequisites": ["Python"], "description": "Probabilistic modeling, Bayesian methods, and empirical risk."},
            {"topic": "Deep Learning", "title": "3. Frontier Deep Learning Architectures", "prerequisites": ["Machine Learning"], "description": "Transformer variants, diffusion models, and self-supervised learning."},
            {"topic": "Data Engineering", "title": "4. Large-Scale Dataset Curation", "prerequisites": ["Python"], "description": "Distributed data preprocessing and tokenization pipelines."},
            {"topic": "MLOps", "title": "5. Distributed Experiment Reproducibility", "prerequisites": ["Deep Learning"], "description": "Multi-node training tracking, checkpointing, and evaluation suites."}
        ]
    },

    "Blockchain Developer": {
        "category": "Engineering & Architecture",
        "description": "Smart contract development, decentralized applications (dApps), cryptography, and blockchain protocols.",
        "skills": ["JavaScript", "TypeScript", "Python", "Git", "Docker", "Networking", "System Design"],
        "roadmap": [
            {"topic": "JavaScript", "title": "1. JavaScript & Async Mechanics", "prerequisites": [], "description": "Async programming, event handling, and JSON-RPC."},
            {"topic": "TypeScript", "title": "2. TypeScript for Smart Contracts", "prerequisites": ["JavaScript"], "description": "Type-safe blockchain interactions and Web3 contracts."},
            {"topic": "Networking", "title": "3. P2P Protocols & Cryptography", "prerequisites": [], "description": "Asymmetric encryption, digital signatures, hashing, and P2P networks."},
            {"topic": "Git", "title": "4. Git for Immutable Code Repositories", "prerequisites": [], "description": "Auditable commit histories, branch workflows, and releases."},
            {"topic": "Docker", "title": "5. Local Blockchain Node Containers", "prerequisites": [], "description": "Spinning up local testnet nodes and dev environments with Docker."},
            {"topic": "System Design", "title": "6. Decentralized System Architecture", "prerequisites": ["Networking"], "description": "Consensus mechanisms, state machines, and off-chain indexing."}
        ]
    },

    # ── Data Structures & Algorithms Target Role ──
    "Data Structures & Algorithms": {
        "category": "Algorithms & Problem Solving",
        "description": "Comprehensive algorithmic problem solving, linear and non-linear data structures, trees, graphs, greedy algorithms, and dynamic programming in C, C++, Python, or Java.",
        "skills": ["Data Structures & Algorithms", "C", "C++", "Python", "Java", "System Design", "Git"],
        "roadmap": [
            {
                "topic": "Data Structures & Algorithms",
                "title": "1. Data Structures & Algorithms Mastery",
                "prerequisites": [],
                "description": "Core linear structures, hashing, trees, graphs, greedy paradigms, and dynamic programming in your chosen language (C, C++, Python, or Java)."
            },
            {
                "topic": "Python",
                "title": "2. Algorithmic Scripting & Problem Solving",
                "prerequisites": [],
                "description": "Clean, optimal code implementation and standard library utilization."
            },
            {
                "topic": "System Design",
                "title": "3. Algorithmic Scalability & System Architecture",
                "prerequisites": ["Data Structures & Algorithms"],
                "description": "High-volume architectural patterns, caching, distributed algorithms, and complexity tradeoffs."
            },
            {
                "topic": "Git",
                "title": "4. Collaborative Engineering & Version Control",
                "prerequisites": [],
                "description": "Branching, code reviews, and structured repository workflows."
            }
        ]
    }
}

# ══════════════════════════════════════════════════════════════════════════════
# DSA MASTER CURRICULUM (Language-Independent with C, C++, Python, Java only)
# ══════════════════════════════════════════════════════════════════════════════
DSA_MASTER_CURRICULUM: List[Dict[str, Any]] = [
    {
        "category": "DSA",
        "topic": "Programming Fundamentals",
        "order": 1,
        "difficulty": "Beginner",
        "prerequisites": [],
        "languages": {
            "c": {"videoUrl": "https://www.youtube.com/watch?v=KJgsSFOSQv0", "codeExamples": "// C Fundamentals: Pointers & Memory\n#include <stdio.h>\nint main() { int x = 10; int *ptr = &x; printf(\"%d\\n\", *ptr); return 0; }"},
            "cpp": {"videoUrl": "https://www.youtube.com/watch?v=vLnPwxZdW4Y", "codeExamples": "// C++ Fundamentals: References & IO\n#include <iostream>\nint main() { int x = 10; int &ref = x; std::cout << ref << std::endl; return 0; }"},
            "python": {"videoUrl": "https://www.youtube.com/watch?v=kqtD5dpn9C8", "codeExamples": "# Python Fundamentals: Dynamic Typing & Lists\nx = 10\nprint(f\"Value: {x}\")"},
            "java": {"videoUrl": "https://www.youtube.com/watch?v=eIrMbAQSU34", "codeExamples": "// Java Fundamentals: Classes & Types\npublic class Main { public static void main(String[] args) { int x = 10; System.out.println(x); } }"}
        }
    },
    {
        "category": "DSA",
        "topic": "Time & Space Complexity",
        "order": 2,
        "difficulty": "Beginner",
        "prerequisites": ["Programming Fundamentals"],
        "languages": {
            "c": {"videoUrl": "https://www.youtube.com/watch?v=V6mKVRU1evU", "codeExamples": "// Big-O: O(1) space, O(N) time loop in C\nfor(int i = 0; i < n; i++) { sum += arr[i]; }"},
            "cpp": {"videoUrl": "https://www.youtube.com/watch?v=V6mKVRU1evU", "codeExamples": "// Big-O: O(1) space, O(N) time in C++\nfor(const auto& val : vec) { sum += val; }"},
            "python": {"videoUrl": "https://www.youtube.com/watch?v=V6mKVRU1evU", "codeExamples": "# Big-O: O(N) sum in Python\nsum_val = sum(arr)"},
            "java": {"videoUrl": "https://www.youtube.com/watch?v=V6mKVRU1evU", "codeExamples": "// Big-O: O(N) traversal in Java\nfor(int num : arr) { sum += num; }"}
        }
    },
    {
        "category": "DSA",
        "topic": "Arrays",
        "order": 3,
        "difficulty": "Beginner",
        "prerequisites": ["Time & Space Complexity"],
        "languages": {
            "c": {"videoUrl": "https://www.youtube.com/watch?v=jWq1v_43jbc", "codeExamples": "// C Static Array & malloc\nint* arr = (int*)malloc(n * sizeof(int));\nfree(arr);"},
            "cpp": {"videoUrl": "https://www.youtube.com/watch?v=YwZlHjcm3O8", "codeExamples": "// C++ std::vector Dynamic Array\nstd::vector<int> nums = {1, 2, 3};\nnums.push_back(4);"},
            "python": {"videoUrl": "https://www.youtube.com/watch?v=YwZlHjcm3O8", "codeExamples": "# Python Dynamic List\nnums = [1, 2, 3]\nnums.append(4)"},
            "java": {"videoUrl": "https://www.youtube.com/watch?v=jWq1v_43jbc", "codeExamples": "// Java ArrayList\nArrayList<Integer> nums = new ArrayList<>();\nnums.add(4);"}
        }
    },
    {
        "category": "DSA",
        "topic": "Strings",
        "order": 4,
        "difficulty": "Beginner",
        "prerequisites": ["Arrays"],
        "languages": {
            "c": {"videoUrl": "https://www.youtube.com/watch?v=1pSBZzJgQYw", "codeExamples": "// C Null-terminated string\nchar str[] = \"SkillPath\";\nint len = strlen(str);"},
            "cpp": {"videoUrl": "https://www.youtube.com/watch?v=1pSBZzJgQYw", "codeExamples": "// C++ std::string\nstd::string s = \"SkillPath\";\nstd::reverse(s.begin(), s.end());"},
            "python": {"videoUrl": "https://www.youtube.com/watch?v=1pSBZzJgQYw", "codeExamples": "# Python String Slicing\ns = \"SkillPath\"\nreversed_s = s[::-1]"},
            "java": {"videoUrl": "https://www.youtube.com/watch?v=1pSBZzJgQYw", "codeExamples": "// Java StringBuilder\nStringBuilder sb = new StringBuilder(\"SkillPath\");\nsb.reverse();"}
        }
    },
    {
        "category": "DSA",
        "topic": "Searching",
        "order": 5,
        "difficulty": "Intermediate",
        "prerequisites": ["Arrays"],
        "languages": {
            "c": {"videoUrl": "https://www.youtube.com/watch?v=s4D9ydZ6GjI", "codeExamples": "int binarySearch(int a[], int n, int x) {\n    int l = 0, r = n - 1;\n    while(l <= r) {\n        int m = l + (r - l) / 2;\n        if (a[m] == x) return m;\n        if (a[m] < x) l = m + 1;\n        else r = m - 1;\n    }\n    return -1;\n}"},
            "cpp": {"videoUrl": "https://www.youtube.com/watch?v=s4D9ydZ6GjI", "codeExamples": "int binarySearch(const std::vector<int>& a, int x) {\n    int l = 0, r = a.size() - 1;\n    while(l <= r) {\n        int m = l + (r - l) / 2;\n        if (a[m] == x) return m;\n        if (a[m] < x) l = m + 1;\n        else r = m - 1;\n    }\n    return -1;\n}"},
            "python": {"videoUrl": "https://www.youtube.com/watch?v=s4D9ydZ6GjI", "codeExamples": "def binary_search(a: list[int], x: int) -> int:\n    l, r = 0, len(a) - 1\n    while l <= r:\n        m = (l + r) // 2\n        if a[m] == x: return m\n        elif a[m] < x: l = m + 1\n        else: r = m - 1\n    return -1"},
            "java": {"videoUrl": "https://www.youtube.com/watch?v=s4D9ydZ6GjI", "codeExamples": "public static int binarySearch(int[] a, int x) {\n    int l = 0, r = a.length - 1;\n    while(l <= r) {\n        int m = l + (r - l) / 2;\n        if (a[m] == x) return m;\n        if (a[m] < x) l = m + 1;\n        else r = m - 1;\n    }\n    return -1;\n}"}
        }
    },
    {
        "category": "DSA",
        "topic": "Sorting",
        "order": 6,
        "difficulty": "Intermediate",
        "prerequisites": ["Arrays", "Searching"],
        "languages": {
            "c": {"videoUrl": "https://www.youtube.com/watch?v=mB5HXBb_HY8", "codeExamples": "// C Merge Sort\nvoid merge(int arr[], int l, int m, int r);"},
            "cpp": {"videoUrl": "https://www.youtube.com/watch?v=mB5HXBb_HY8", "codeExamples": "// C++ std::sort (IntroSort)\nstd::sort(vec.begin(), vec.end());"},
            "python": {"videoUrl": "https://www.youtube.com/watch?v=mB5HXBb_HY8", "codeExamples": "# Python Timsort\nvec.sort()"},
            "java": {"videoUrl": "https://www.youtube.com/watch?v=mB5HXBb_HY8", "codeExamples": "// Java Dual-Pivot Quicksort\nArrays.sort(arr);"}
        }
    },
    {
        "category": "DSA",
        "topic": "Linked Lists",
        "order": 7,
        "difficulty": "Intermediate",
        "prerequisites": ["Arrays"],
        "languages": {
            "c": {"videoUrl": "https://www.youtube.com/watch?v=ch1uURPMr18", "codeExamples": "struct Node { int val; struct Node* next; };"},
            "cpp": {"videoUrl": "https://www.youtube.com/watch?v=G0_I-ZF0S38", "codeExamples": "struct ListNode { int val; ListNode* next; ListNode(int x) : val(x), next(nullptr) {} };"},
            "python": {"videoUrl": "https://www.youtube.com/watch?v=G0_I-ZF0S38", "codeExamples": "class ListNode:\n    def __init__(self, val=0, next=None):\n        self.val = val\n        self.next = next"},
            "java": {"videoUrl": "https://www.youtube.com/watch?v=G0_I-ZF0S38", "codeExamples": "class ListNode { int val; ListNode next; ListNode(int x) { val = x; } }"}
        }
    },
    {
        "category": "DSA",
        "topic": "Stack",
        "order": 8,
        "difficulty": "Intermediate",
        "prerequisites": ["Linked Lists"],
        "languages": {
            "c": {"videoUrl": "https://www.youtube.com/watch?v=L3ud3GEnGvg", "codeExamples": "// C Stack via Array & Top Pointer"},
            "cpp": {"videoUrl": "https://www.youtube.com/watch?v=L3ud3GEnGvg", "codeExamples": "std::stack<int> st; st.push(10); st.pop();"},
            "python": {"videoUrl": "https://www.youtube.com/watch?v=Dq_OBPhxP38", "codeExamples": "stack = []\nstack.append(10)\nval = stack.pop()"},
            "java": {"videoUrl": "https://www.youtube.com/watch?v=L3ud3GEnGvg", "codeExamples": "Deque<Integer> stack = new ArrayDeque<>();\nstack.push(10);"}
        }
    },
    {
        "category": "DSA",
        "topic": "Queue",
        "order": 9,
        "difficulty": "Intermediate",
        "prerequisites": ["Linked Lists"],
        "languages": {
            "c": {"videoUrl": "https://www.youtube.com/watch?v=IaG0cE_VpU8", "codeExamples": "// C Circular Queue via modulo arithmetic"},
            "cpp": {"videoUrl": "https://www.youtube.com/watch?v=IaG0cE_VpU8", "codeExamples": "std::queue<int> q; q.push(10); q.pop();"},
            "python": {"videoUrl": "https://www.youtube.com/watch?v=DfljaUwZsOk", "codeExamples": "from collections import deque\nq = deque()\nq.append(10)\nval = q.popleft()"},
            "java": {"videoUrl": "https://www.youtube.com/watch?v=IaG0cE_VpU8", "codeExamples": "Queue<Integer> q = new LinkedList<>();\nq.offer(10);\nq.poll();"}
        }
    },
    {
        "category": "DSA",
        "topic": "Hashing",
        "order": 10,
        "difficulty": "Intermediate",
        "prerequisites": ["Arrays", "Linked Lists"],
        "languages": {
            "c": {"videoUrl": "https://www.youtube.com/watch?v=2E54GqF0FY4", "codeExamples": "// C Hash Table with Separate Chaining buckets"},
            "cpp": {"videoUrl": "https://www.youtube.com/watch?v=knV86FlSXJ8", "codeExamples": "std::unordered_map<string, int> map;\nmap[\"key\"] = 42;"},
            "python": {"videoUrl": "https://www.youtube.com/watch?v=knV86FlSXJ8", "codeExamples": "h_map = {}\nh_map[\"key\"] = 42"},
            "java": {"videoUrl": "https://www.youtube.com/watch?v=knV86FlSXJ8", "codeExamples": "HashMap<String, Integer> map = new HashMap<>();\nmap.put(\"key\", 42);"}
        }
    },
    {
        "category": "DSA",
        "topic": "Recursion",
        "order": 11,
        "difficulty": "Intermediate",
        "prerequisites": ["Stack"],
        "languages": {
            "c": {"videoUrl": "https://www.youtube.com/watch?v=IJDJ0kBx2LM", "codeExamples": "int fact(int n) { return (n <= 1) ? 1 : n * fact(n - 1); }"},
            "cpp": {"videoUrl": "https://www.youtube.com/watch?v=IJDJ0kBx2LM", "codeExamples": "int fact(int n) { return (n <= 1) ? 1 : n * fact(n - 1); }"},
            "python": {"videoUrl": "https://www.youtube.com/watch?v=IJDJ0kBx2LM", "codeExamples": "def fact(n: int) -> int: return 1 if n <= 1 else n * fact(n - 1)"},
            "java": {"videoUrl": "https://www.youtube.com/watch?v=IJDJ0kBx2LM", "codeExamples": "static int fact(int n) { return (n <= 1) ? 1 : n * fact(n - 1); }"}
        }
    },
    {
        "category": "DSA",
        "topic": "Backtracking",
        "order": 12,
        "difficulty": "Intermediate",
        "prerequisites": ["Recursion"],
        "languages": {
            "c": {"videoUrl": "https://www.youtube.com/watch?v=REOH22Xwdkk", "codeExamples": "// C Backtracking template: choose, explore, unchoose"},
            "cpp": {"videoUrl": "https://www.youtube.com/watch?v=REOH22Xwdkk", "codeExamples": "void backtrack(vector<int>& curr, int start);"},
            "python": {"videoUrl": "https://www.youtube.com/watch?v=REOH22Xwdkk", "codeExamples": "def backtrack(curr, start):\n    res.append(list(curr))\n    for i in range(start, n):\n        curr.append(nums[i])\n        backtrack(curr, i + 1)\n        curr.pop()"},
            "java": {"videoUrl": "https://www.youtube.com/watch?v=REOH22Xwdkk", "codeExamples": "void backtrack(List<Integer> curr, int start) { ... }"}
        }
    },
    {
        "category": "DSA",
        "topic": "Trees",
        "order": 13,
        "difficulty": "Intermediate",
        "prerequisites": ["Recursion", "Queue"],
        "languages": {
            "c": {"videoUrl": "https://www.youtube.com/watch?v=fAAZixBzIAI", "codeExamples": "struct TreeNode { int val; struct TreeNode *left, *right; };"},
            "cpp": {"videoUrl": "https://www.youtube.com/watch?v=afTpieEZXck", "codeExamples": "struct TreeNode { int val; TreeNode *left; TreeNode *right; TreeNode(int x) : val(x), left(nullptr), right(nullptr) {} };"},
            "python": {"videoUrl": "https://www.youtube.com/watch?v=afTpieEZXck", "codeExamples": "class TreeNode:\n    def __init__(self, val=0, left=None, right=None):\n        self.val = val\n        self.left = left\n        self.right = right"},
            "java": {"videoUrl": "https://www.youtube.com/watch?v=afTpieEZXck", "codeExamples": "class TreeNode { int val; TreeNode left; TreeNode right; TreeNode(int x) { val = x; } }"}
        }
    },
    {
        "category": "DSA",
        "topic": "Binary Search Trees",
        "order": 14,
        "difficulty": "Intermediate",
        "prerequisites": ["Trees"],
        "languages": {
            "c": {"videoUrl": "https://www.youtube.com/watch?v=kI7Q_Uv9kbc", "codeExamples": "// BST Search in C\nTreeNode* search(TreeNode* root, int key);"},
            "cpp": {"videoUrl": "https://www.youtube.com/watch?v=s6ATEkipzow", "codeExamples": "bool isValidBST(TreeNode* root, long minVal, long maxVal);"},
            "python": {"videoUrl": "https://www.youtube.com/watch?v=s6ATEkipzow", "codeExamples": "def isValidBST(root, min_val=float('-inf'), max_val=float('inf')):"},
            "java": {"videoUrl": "https://www.youtube.com/watch?v=s6ATEkipzow", "codeExamples": "boolean isValidBST(TreeNode root, long min, long max);"}
        }
    },
    {
        "category": "DSA",
        "topic": "Heaps",
        "order": 15,
        "difficulty": "Intermediate",
        "prerequisites": ["Trees", "Arrays"],
        "languages": {
            "c": {"videoUrl": "https://www.youtube.com/watch?v=wptevk0bshY", "codeExamples": "// C Min-Heap sift-up & sift-down on array"},
            "cpp": {"videoUrl": "https://www.youtube.com/watch?v=wptevk0bshY", "codeExamples": "// C++ std::priority_queue (Max-Heap by default)\nstd::priority_queue<int> maxHeap;"},
            "python": {"videoUrl": "https://www.youtube.com/watch?v=YPTqKIgVk-k", "codeExamples": "import heapq\nheap = []\nheapq.heappush(heap, val)"},
            "java": {"videoUrl": "https://www.youtube.com/watch?v=wptevk0bshY", "codeExamples": "PriorityQueue<Integer> minHeap = new PriorityQueue<>();"}
        }
    },
    {
        "category": "DSA",
        "topic": "Priority Queue",
        "order": 16,
        "difficulty": "Intermediate",
        "prerequisites": ["Heaps"],
        "languages": {
            "c": {"videoUrl": "https://www.youtube.com/watch?v=HqPJF2L5h9U", "codeExamples": "// C Priority Queue via Binary Heap"},
            "cpp": {"videoUrl": "https://www.youtube.com/watch?v=wptevk0bshY", "codeExamples": "std::priority_queue<int, vector<int>, greater<int>> minPQ;"},
            "python": {"videoUrl": "https://www.youtube.com/watch?v=YPTqKIgVk-k", "codeExamples": "# Top K elements with heapq\nlargest = heapq.nlargest(k, nums)"},
            "java": {"videoUrl": "https://www.youtube.com/watch?v=wptevk0bshY", "codeExamples": "PriorityQueue<int[]> pq = new PriorityQueue<>((a, b) -> a[0] - b[0]);"}
        }
    },
    {
        "category": "DSA",
        "topic": "Graphs",
        "order": 17,
        "difficulty": "Advanced",
        "prerequisites": ["Queue", "Stack", "Trees"],
        "languages": {
            "c": {"videoUrl": "https://www.youtube.com/watch?v=09_LlHjoEiY", "codeExamples": "// C Adjacency List with Linked Nodes"},
            "cpp": {"videoUrl": "https://www.youtube.com/watch?v=tWVWeAqZ0WU", "codeExamples": "std::vector<std::vector<int>> adj(n);"},
            "python": {"videoUrl": "https://www.youtube.com/watch?v=tWVWeAqZ0WU", "codeExamples": "from collections import defaultdict\nadj = defaultdict(list)"},
            "java": {"videoUrl": "https://www.youtube.com/watch?v=tWVWeAqZ0WU", "codeExamples": "List<List<Integer>> adj = new ArrayList<>();"}
        }
    },
    {
        "category": "DSA",
        "topic": "Greedy Algorithms",
        "order": 18,
        "difficulty": "Intermediate",
        "prerequisites": ["Sorting", "Arrays"],
        "languages": {
            "c": {"videoUrl": "https://www.youtube.com/watch?v=ARvQcqJ_-NY", "codeExamples": "// C Fractional Knapsack Greedy sort by ratio"},
            "cpp": {"videoUrl": "https://www.youtube.com/watch?v=ARvQcqJ_-NY", "codeExamples": "// C++ Interval Scheduling sort by end time\nsort(intervals.begin(), intervals.end(), [](auto& a, auto& b){ return a[1] < b[1]; });"},
            "python": {"videoUrl": "https://www.youtube.com/watch?v=ARvQcqJ_-NY", "codeExamples": "# Python Interval Scheduling\nintervals.sort(key=lambda x: x[1])"},
            "java": {"videoUrl": "https://www.youtube.com/watch?v=ARvQcqJ_-NY", "codeExamples": "Arrays.sort(intervals, (a, b) -> Integer.compare(a[1], b[1]));"}
        }
    },
    {
        "category": "DSA",
        "topic": "Dynamic Programming",
        "order": 19,
        "difficulty": "Advanced",
        "prerequisites": ["Recursion", "Arrays"],
        "languages": {
            "c": {"videoUrl": "https://www.youtube.com/watch?v=nLmhmB6NzcM", "codeExamples": "// C 0/1 Knapsack 1D DP\nfor(int i = 0; i < n; i++) for(int w = W; w >= wt[i]; w--) dp[w] = max(dp[w], val[i] + dp[w - wt[i]]);"},
            "cpp": {"videoUrl": "https://www.youtube.com/watch?v=H9bfqozjoqs", "codeExamples": "// C++ 1D Space Optimized DP\nvector<int> dp(amount + 1, 1e9); dp[0] = 0;"},
            "python": {"videoUrl": "https://www.youtube.com/watch?v=oBt53YbR9Kk", "codeExamples": "# Python Memoization with @cache\nfrom functools import cache\n@cache\ndef dp(i, target): ..."},
            "java": {"videoUrl": "https://www.youtube.com/watch?v=nLmhmB6NzcM", "codeExamples": "int[] dp = new int[amount + 1];\nArrays.fill(dp, Integer.MAX_VALUE);"}
        }
    },
    {
        "category": "DSA",
        "topic": "Tries",
        "order": 20,
        "difficulty": "Advanced",
        "prerequisites": ["Trees", "Hashing"],
        "languages": {
            "c": {"videoUrl": "https://www.youtube.com/watch?v=oobqoCJlHA0", "codeExamples": "struct TrieNode { struct TrieNode* children[26]; bool isEnd; };"},
            "cpp": {"videoUrl": "https://www.youtube.com/watch?v=oobqoCJlHA0", "codeExamples": "struct TrieNode { TrieNode* children[26] = {}; bool isEnd = false; };"},
            "python": {"videoUrl": "https://www.youtube.com/watch?v=oobqoCJlHA0", "codeExamples": "class TrieNode:\n    def __init__(self):\n        self.children = {}\n        self.is_end = False"},
            "java": {"videoUrl": "https://www.youtube.com/watch?v=oobqoCJlHA0", "codeExamples": "class TrieNode { TrieNode[] children = new TrieNode[26]; boolean isEnd; }"}
        }
    },
    {
        "category": "DSA",
        "topic": "Segment Trees",
        "order": 21,
        "difficulty": "Advanced",
        "prerequisites": ["Trees", "Binary Search Trees"],
        "languages": {
            "c": {"videoUrl": "https://www.youtube.com/watch?v=ZBHKZF5w4dU", "codeExamples": "void build(int node, int start, int end);"},
            "cpp": {"videoUrl": "https://www.youtube.com/watch?v=ZBHKZF5w4dU", "codeExamples": "// C++ Range Minimum Query Segment Tree\nvector<int> tree(4 * n);"},
            "python": {"videoUrl": "https://www.youtube.com/watch?v=ZBHKZF5w4dU", "codeExamples": "# Python Segment Tree Range Sum Query\ntree = [0] * (4 * n)"},
            "java": {"videoUrl": "https://www.youtube.com/watch?v=ZBHKZF5w4dU", "codeExamples": "int[] tree = new int[4 * n];"}
        }
    },
    {
        "category": "DSA",
        "topic": "Fenwick Trees",
        "order": 22,
        "difficulty": "Advanced",
        "prerequisites": ["Segment Trees", "Arrays"],
        "languages": {
            "c": {"videoUrl": "https://www.youtube.com/watch?v=rgGAPV_4Qcw", "codeExamples": "// C Binary Indexed Tree: update with i += (i & -i)"},
            "cpp": {"videoUrl": "https://www.youtube.com/watch?v=rgGAPV_4Qcw", "codeExamples": "void add(int i, int delta) { for(; i < n; i += i & -i) bit[i] += delta; }"},
            "python": {"videoUrl": "https://www.youtube.com/watch?v=rgGAPV_4Qcw", "codeExamples": "def add(i, delta):\n    while i < n:\n        bit[i] += delta\n        i += i & -i"},
            "java": {"videoUrl": "https://www.youtube.com/watch?v=rgGAPV_4Qcw", "codeExamples": "void add(int i, int delta) { for(; i < n; i += i & -i) bit[i] += delta; }"}
        }
    },
    {
        "category": "DSA",
        "topic": "Advanced Graph Algorithms",
        "order": 23,
        "difficulty": "Advanced",
        "prerequisites": ["Graphs", "Priority Queue"],
        "languages": {
            "c": {"videoUrl": "https://www.youtube.com/watch?v=XB4MIexjvY0", "codeExamples": "// C Dijkstra Single Source Shortest Path"},
            "cpp": {"videoUrl": "https://www.youtube.com/watch?v=eL-KzMXWXXI", "codeExamples": "// C++ Kahn's Algorithm for Topological Sort\nvector<int> inDegree(n, 0); queue<int> q;"},
            "python": {"videoUrl": "https://www.youtube.com/watch?v=eL-KzMXWXXI", "codeExamples": "# Python Topological Sort Kahn's BFS\nq = deque([u for u in range(n) if in_degree[u] == 0])"},
            "java": {"videoUrl": "https://www.youtube.com/watch?v=XB4MIexjvY0", "codeExamples": "// Java Dijkstra's with PriorityQueue<int[]>"}
        }
    },
    {
        "category": "DSA",
        "topic": "Interview Patterns",
        "order": 24,
        "difficulty": "Advanced",
        "prerequisites": ["Dynamic Programming", "Advanced Graph Algorithms"],
        "languages": {
            "c": {"videoUrl": "https://www.youtube.com/watch?v=DjYZk8nrXVY", "codeExamples": "// Top C Coding Patterns for Systems & Embedded Interviews"},
            "cpp": {"videoUrl": "https://www.youtube.com/watch?v=DjYZk8nrXVY", "codeExamples": "// Top 20 C++ Interview Patterns: Sliding Window, Two Pointers, Monotonic Stack"},
            "python": {"videoUrl": "https://www.youtube.com/watch?v=DjYZk8nrXVY", "codeExamples": "# Top 20 Python Interview Patterns: Two Heaps, Fast & Slow, Backtracking"},
            "java": {"videoUrl": "https://www.youtube.com/watch?v=DjYZk8nrXVY", "codeExamples": "// Top 20 Java Interview Patterns: Sliding Window, Topological Sort, Interval Merging"}
        }
    }
]

def get_dsa_master_curriculum() -> List[Dict[str, Any]]:
    return DSA_MASTER_CURRICULUM

# ══════════════════════════════════════════════════════════════════════════════
# Helper Functions
# ══════════════════════════════════════════════════════════════════════════════

def get_role_config(role_name: str) -> Dict[str, Any]:
    """Returns the full configuration for a target role, with safe fallback."""
    if not role_name:
        role_name = "DevOps Engineer"
    if role_name in ROLES_REGISTRY:
        return ROLES_REGISTRY[role_name]
    # Check normalized DSA aliases
    role_lower = role_name.lower().strip()
    if role_lower in ("data structures & algorithms", "dsa", "data structures & algorithms (dsa)", "dsa specialist", "data structures and algorithms"):
        if "Data Structures & Algorithms" in ROLES_REGISTRY:
            return ROLES_REGISTRY["Data Structures & Algorithms"]
    # Fuzzy / default fallback
    for k in ROLES_REGISTRY:
        if k.lower() in role_lower:
            return ROLES_REGISTRY[k]
    return ROLES_REGISTRY["DevOps Engineer"]

def get_all_roles() -> List[str]:
    """Returns sorted list of all available role names."""
    return list(ROLES_REGISTRY.keys())

def get_role_roadmap(role_name: str) -> List[Dict[str, Any]]:
    """Returns the ordered topic roadmap for a specific role."""
    conf = get_role_config(role_name)
    return conf.get("roadmap", [])

def get_topic_syllabus(topic_name: str) -> Optional[Dict[str, Any]]:
    """Returns the 4-module syllabus for a given topic."""
    return TOPIC_SYLLABUS.get(topic_name)

def filter_gaps_with_prerequisites(
    role_name: str,
    existing_skills: List[str],
    completed_topics: List[str]
) -> List[Dict[str, Any]]:
    """
    Evaluates the role's sequential roadmap against existing resume skills and completed topics.
    Identifies what the user already knows, what they should learn first based on prerequisites,
    and returns an actionable, prioritized roadmap list.
    """
    conf = get_role_config(role_name)
    roadmap = conf.get("roadmap", [])
    
    existing_set = {s.lower().strip() for s in (existing_skills or [])}
    completed_set = {t.lower().strip() for t in (completed_topics or [])}

    prioritized_roadmap = []

    for item in roadmap:
        t = item["topic"]
        t_lower = t.lower().strip()
        
        # Check if already mastered via resume or completion
        is_in_resume = any(s in existing_set for s in [t_lower, f"{t_lower} basics", f"{t_lower} fundamentals"])
        is_completed = t_lower in completed_set
        
        # Check prerequisites
        prereqs = item.get("prerequisites", [])
        unmet_prereqs = []
        for p in prereqs:
            p_lower = p.lower().strip()
            p_satisfied = (p_lower in existing_set) or (p_lower in completed_set)
            if not p_satisfied:
                unmet_prereqs.append(p)

        if is_completed:
            status = "completed"
            action = "Review Content"
        elif is_in_resume:
            status = "mastered_via_resume"
            action = "Review Advanced"
        elif len(unmet_prereqs) > 0:
            status = "locked"
            action = f"Requires {', '.join(unmet_prereqs)}"
        else:
            status = "ready_to_learn"
            action = "Start Learning"

        prioritized_roadmap.append({
            "topic": t,
            "title": item.get("title", t),
            "description": item.get("description", ""),
            "prerequisites": prereqs,
            "unmet_prerequisites": unmet_prereqs,
            "status": status,
            "action_label": action,
            "syllabus": TOPIC_SYLLABUS.get(t)
        })

    return prioritized_roadmap

# ══════════════════════════════════════════════════════════════════════════════
# DSA 14-MODULE KEYS, ALIASES & PHASE 0 FOUNDATION
# ══════════════════════════════════════════════════════════════════════════════
DSA_MODULE_KEYS = [
    "module_1",
    "module_2",
    "module_3",
    "module_4",
    "module_5",
    "module_6",
    "module_7",
    "module_8",
    "module_9",
    "module_10",
    "module_11",
    "module_12",
    "module_13",
    "module_14"
]

DSA_MODULE_ALIASES = {
    "intro": "module_1",
    "core": "module_2",
    "advanced": "module_8",
    "summary": "module_14"
}

DSA_PHASE0_FOUNDATION = {
    "c": {
        "language": "C",
        "title": "Phase 0 — C Programming Foundation Check",
        "description": "Verify your understanding of foundational C constructs before advancing into complexity analysis and linear data structures.",
        "checklist": [
            {"id": "c_syntax", "title": "C Syntax & Structure", "desc": "Headers (#include <stdio.h>), main entrypoint, compilation with gcc"},
            {"id": "c_types", "title": "Variables & Primitive Types", "desc": "int, char, float, double, signed/unsigned ranges, sizeof operator"},
            {"id": "c_io", "title": "Standard Input / Output", "desc": "printf, scanf, format specifiers (%d, %c, %s, %p), buffer handling"},
            {"id": "c_operators", "title": "Operators & Expressions", "desc": "Arithmetic, relational, logical, bitwise (&, |, ^, ~), precedence"},
            {"id": "c_conditions", "title": "Conditional Branching", "desc": "if, else if, else, switch-case, ternary operator (? :)"},
            {"id": "c_loops", "title": "Loops & Iteration", "desc": "for loops, while loops, do-while, break and continue mechanics"},
            {"id": "c_functions", "title": "Functions & Call Stack", "desc": "Prototypes, pass-by-value, return types, stack frames"},
            {"id": "c_arrays", "title": "Arrays & Indexing", "desc": "1D and 2D arrays, contiguous memory layout, array decay to pointer"},
            {"id": "c_strings", "title": "Strings (Char Arrays)", "desc": "Null-terminated char arrays, strlen, strcpy, strcmp from <string.h>"},
            {"id": "c_pointers", "title": "Pointers & Memory Addresses", "desc": "Address-of (&), dereference (*), pointer arithmetic, void* pointers"},
            {"id": "c_dynamic_mem", "title": "Dynamic Memory Allocation", "desc": "malloc, calloc, realloc, free, heap vs stack, memory leak prevention"},
            {"id": "c_structs", "title": "Structures & Typedefs", "desc": "struct declarations, typedef, pointer member access (->), self-referential node structs"}
        ]
    },
    "cpp": {
        "language": "C++",
        "title": "Phase 0 — C++ Programming Foundation Check",
        "description": "Verify your understanding of modern C++ syntax, references, pointers, and STL basics before starting algorithmic problem solving.",
        "checklist": [
            {"id": "cpp_syntax", "title": "C++ Syntax & Namespaces", "desc": "#include <iostream>, using namespace std, modern C++ conventions"},
            {"id": "cpp_types", "title": "Variables & Data Types", "desc": "int, double, char, bool, long long, auto type deduction"},
            {"id": "cpp_io", "title": "Fast Input / Output", "desc": "std::cin, std::cout, cin.tie(NULL), ios_base::sync_with_stdio(false)"},
            {"id": "cpp_operators", "title": "Operators & Expressions", "desc": "Arithmetic, logical, bitwise, assignment, ternary operator"},
            {"id": "cpp_conditions", "title": "Conditions & Flow Control", "desc": "if, else if, else, switch-case, conditional logic"},
            {"id": "cpp_loops", "title": "Loops & Range-based For", "desc": "for, while, do-while, range-based for loops (for (const auto& x : vec))"},
            {"id": "cpp_functions", "title": "Functions & Pass-by-Reference", "desc": "Pass-by-value vs pass-by-reference (&), const references, default arguments"},
            {"id": "cpp_arrays", "title": "Arrays & std::vector", "desc": "Fixed arrays, std::array, dynamic vectors (push_back, pop_back, size)"},
            {"id": "cpp_strings", "title": "Strings & std::string", "desc": "std::string methods (substr, size, find, concatenation +), string_view"},
            {"id": "cpp_pointers", "title": "Pointers & References", "desc": "Raw pointers, references (&), nullptr, address-of operator, memory addresses"},
            {"id": "cpp_stl", "title": "STL Basics & Standard Containers", "desc": "std::vector, std::pair, std::unordered_map, std::unordered_set, std::sort"}
        ]
    },
    "python": {
        "language": "Python",
        "title": "Phase 0 — Python Programming Foundation Check",
        "description": "Verify your understanding of Pythonic syntax, dynamic typing, built-in collections, and functions before beginning DSA.",
        "checklist": [
            {"id": "py_syntax", "title": "Python Syntax & Indentation", "desc": "Clean syntax, 4-space whitespace indentation, comments (#)"},
            {"id": "py_types", "title": "Variables & Dynamic Types", "desc": "int (unbounded size), float, str, bool, NoneType, type conversion"},
            {"id": "py_io", "title": "Input / Output & Formatting", "desc": "print(), f-strings (f'{val}'), input().split(), sys.stdin.readline"},
            {"id": "py_conditions", "title": "Conditions & Logic", "desc": "if, elif, else, logical and, or, not, truthy/falsy evaluation"},
            {"id": "py_loops", "title": "Loops & Comprehensions", "desc": "for x in range(), while, enumerate(), zip(), break, continue"},
            {"id": "py_functions", "title": "Functions & Arguments", "desc": "def function_name(), return values, default args, *args, **kwargs"},
            {"id": "py_lists", "title": "Lists & List Operations", "desc": "append, pop, indexing, slicing (arr[::-1]), list comprehensions"},
            {"id": "py_tuples", "title": "Tuples & Immutability", "desc": "Tuple packing, unpacking (a, b = b, a), immutable sequence types"},
            {"id": "py_dicts", "title": "Dictionaries (Hash Maps)", "desc": "Key-value mappings, dict.get(), keys(), values(), items(), defaultdict"},
            {"id": "py_sets", "title": "Sets & Uniqueness", "desc": "Unique element collections, add(), in operator (O(1)), union, intersection"},
            {"id": "py_strings", "title": "Strings & Methods", "desc": "Immutable strings, join(), split(), strip(), find(), slicing"},
            {"id": "py_classes", "title": "Classes & OOP Objects", "desc": "class Node: def __init__(self, val): self.val = val; self.next = None"}
        ]
    },
    "java": {
        "language": "Java",
        "title": "Phase 0 — Java Programming Foundation Check",
        "description": "Verify your understanding of Java syntax, OOP, references, and the Java Collections Framework (JCF) before beginning DSA.",
        "checklist": [
            {"id": "java_syntax", "title": "Java Syntax & Class Structure", "desc": "public class Main, main method signature (public static void main)"},
            {"id": "java_types", "title": "Variables & Primitive Types", "desc": "int, long, double, char, boolean vs Wrapper classes (Integer, Double)"},
            {"id": "java_io", "title": "Input / Output", "desc": "Scanner vs BufferedReader/StringTokenizer for fast algorithmic IO"},
            {"id": "java_conditions", "title": "Control Flow & Conditions", "desc": "if, else if, else, switch with String/enum support, ternary operator"},
            {"id": "java_loops", "title": "Loops & Enhanced For Loop", "desc": "for, while, do-while, enhanced for-each (for (int x : arr))"},
            {"id": "java_methods", "title": "Methods & Signatures", "desc": "Static methods, return types, pass-by-value of object references"},
            {"id": "java_arrays", "title": "Arrays & Multi-dimensional Arrays", "desc": "int[] arr = new int[n], arr.length, Arrays.sort(), Arrays.fill()"},
            {"id": "java_strings", "title": "Strings & StringBuilder", "desc": "Immutable String, charAt(), length(), substring(), StringBuilder for O(1) appends"},
            {"id": "java_classes", "title": "Classes, Objects & Constructors", "desc": "Defining class ListNode, constructors, getters/setters, this keyword"},
            {"id": "java_references", "title": "Object References & Memory", "desc": "Heap vs Stack, garbage collection, null references, NullPointerException"},
            {"id": "java_collections", "title": "Java Collections Framework (JCF)", "desc": "List (ArrayList), Map (HashMap), Set (HashSet), Queue (LinkedList), Deque (ArrayDeque), PriorityQueue"}
        ]
    }
}

def get_dsa_modules_def() -> List[Dict[str, Any]]:
    """Returns the ordered 14 DSA module metadata list."""
    syl = TOPIC_SYLLABUS.get("Data Structures & Algorithms", {}).get("modules", {})
    return [
        {
            "key": k,
            "title": syl.get(k, {}).get("title", k),
            "phase": syl.get(k, {}).get("phase", ""),
            "icon": syl.get(k, {}).get("icon", "📚"),
            "focus": syl.get(k, {}).get("focus", ""),
            "subtopics": syl.get(k, {}).get("subtopics", [])
        }
        for k in DSA_MODULE_KEYS
    ]

def get_dsa_phase0(language: str = "cpp") -> Dict[str, Any]:
    """Returns Phase 0 foundation checklist for the selected language."""
    code = language.strip().lower()
    if code in ("c++", "cpp"):
        code = "cpp"
    elif code not in DSA_PHASE0_FOUNDATION:
        code = "cpp"
    res = dict(DSA_PHASE0_FOUNDATION[code])
    if "topics" not in res and "checklist" in res:
        res["topics"] = [item["title"] for item in res["checklist"]]
    return res

