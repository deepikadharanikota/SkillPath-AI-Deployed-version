/**
 * rolesConfig.js
 * Comprehensive client-side taxonomy of target roles, organized into logical categories
 * with descriptions, icons, and helper methods.
 */

export const ROLE_CATEGORIES = [
  {
    name: "DevOps & Cloud Infrastructure",
    icon: "☁️",
    badgeColor: "#0284c7",
    roles: [
      { name: "DevOps Engineer", description: "Automated delivery, CI/CD, Docker, Kubernetes, Terraform, and Linux." },
      { name: "Site Reliability Engineer (SRE)", description: "Production reliability, SLOs, uptime, Prometheus, and disaster recovery." },
      { name: "Cloud DevOps Engineer", description: "Multi-cloud automation, infrastructure as code, and cluster orchestration." },
      { name: "Cloud Engineer", description: "AWS infrastructure, cloud networking, compute, storage, and IAM." },
      { name: "Cloud Architect", description: "Multi-region architecture, high availability, disaster recovery, and governance." },
      { name: "Cybersecurity Engineer", description: "System hardening, network defense, penetration testing, and DevSecOps." },
      { name: "Security Engineer", description: "Vulnerability scanning, infrastructure security, TLS/SSL, and compliance." }
    ]
  },
  {
    name: "Backend & Systems Engineering",
    icon: "⚙️",
    badgeColor: "#10b981",
    roles: [
      { name: "Backend Developer", description: "FastAPI, Python, SQL, RESTful microservices, and databases." },
      { name: "Python Developer", description: "Advanced Python, OOP, backend APIs, automation, and testing." },
      { name: "Node.js Developer", description: "Event-driven asynchronous APIs, Express, TypeScript, and microservices." },
      { name: "Java Developer", description: "Enterprise services, Spring Boot, microservices, and database persistence." },
      { name: "Database Engineer", description: "Database optimization, indexing, replication, sharding, and high-throughput SQL." }
    ]
  },
  {
    name: "Web & Mobile Development",
    icon: "💻",
    badgeColor: "#8b5cf6",
    roles: [
      { name: "Frontend Developer", description: "Modern React, TypeScript, state management, and responsive interfaces." },
      { name: "React Developer", description: "Component engineering, custom hooks, performance tuning, and SPA state." },
      { name: "Mobile App Developer", description: "Cross-platform mobile apps with React Native, hooks, and native APIs." },
      { name: "Android Developer", description: "High-performance Android client applications and mobile testing." },
      { name: "iOS Developer", description: "Modern iOS client applications, reactive flows, and app store delivery." }
    ]
  },
  {
    name: "Data & AI Engineering",
    icon: "🤖",
    badgeColor: "#f59e0b",
    roles: [
      { name: "Data Engineer", description: "ETL pipelines, Apache Spark, Airflow orchestration, Kafka, and data lakes." },
      { name: "Data Architect", description: "Enterprise lakehouses, dimensional modeling, Delta Lake, and data platforms." },
      { name: "Data Scientist", description: "Statistical modeling, predictive analytics, feature engineering, and Pandas." },
      { name: "Data Analyst", description: "SQL querying, reporting, data cleansing, and business intelligence." },
      { name: "Machine Learning Engineer", description: "Scikit-learn, supervised/unsupervised ML, tree models, and ML APIs." },
      { name: "AI/ML Engineer", description: "Applied machine learning, deep learning, PyTorch, and production inference." },
      { name: "Generative AI Engineer", description: "LLMs, Transformers, RAG architecture, vector search, and fine-tuning." },
      { name: "MLOps Engineer", description: "Automated ML pipelines, MLflow experiment tracking, and model monitoring." },
      { name: "AI Engineer", description: "Integrating intelligent agents, foundational models, and cognitive APIs." },
      { name: "Deep Learning Engineer", description: "PyTorch neural architectures, CNNs, vision transformers, and CUDA training." },
      { name: "NLP Engineer", description: "Natural Language Processing, text classification, BERT, GPT, and vector embeddings." },
      { name: "Computer Vision Engineer", description: "OpenCV, YOLO object detection, image segmentation, and edge vision models." },
      { name: "AI Research Engineer", description: "Frontier deep learning architectures, empirical modeling, and mathematical rigor." }
    ]
  },
  {
    name: "Engineering & Architecture",
    icon: "🏗️",
    badgeColor: "#ec4899",
    roles: [
      { name: "Full Stack Developer", description: "End-to-end full-stack development across React, Python, SQL, and Docker." },
      { name: "Software Engineer", description: "Generalist software engineering across data structures, APIs, and systems." },
      { name: "Software Architect", description: "Scalable distributed system design, microservices, caching, and resiliency." },
      { name: "QA / Automation Engineer", description: "Automated test suites, Pytest, Cypress, Selenium, and CI/CD quality gates." },
      { name: "Automation Engineer", description: "End-to-end testing, delivery automation, test runners, and script automation." },
      { name: "Embedded Systems Engineer", description: "Embedded Linux, IoT protocols, firmware testing, and hardware automation." },
      { name: "Blockchain Developer", description: "Smart contracts, decentralized systems, cryptography, and Web3 architecture." }
    ]
  },
  {
    name: "Algorithms & Problem Solving",
    icon: "⚡",
    badgeColor: "#818cf8",
    roles: [
      { 
        name: "Data Structures & Algorithms", 
        description: "Mastery of linear & non-linear structures, graphs, trees, dynamic programming, and algorithmic problem solving in C, C++, Python, or Java." 
      }
    ]
  }
];

export const ALL_ROLES = ROLE_CATEGORIES.flatMap(cat => cat.roles.map(r => r.name));

export const ROLE_LOOKUP = {};
ROLE_CATEGORIES.forEach(cat => {
  cat.roles.forEach(r => {
    ROLE_LOOKUP[r.name] = {
      ...r,
      category: cat.name,
      categoryIcon: cat.icon,
      badgeColor: cat.badgeColor
    };
  });
});

export function getRoleMeta(roleName) {
  if (!roleName) return null;
  if (ROLE_LOOKUP[roleName]) return ROLE_LOOKUP[roleName];
  // Case-insensitive match
  const lower = roleName.toLowerCase();
  for (const k in ROLE_LOOKUP) {
    if (k.toLowerCase() === lower || k.toLowerCase().includes(lower)) {
      return ROLE_LOOKUP[k];
    }
  }
  return {
    name: roleName,
    description: "Career learning track",
    category: "Specialized Track",
    categoryIcon: "🎯",
    badgeColor: "#3b82f6"
  };
}
