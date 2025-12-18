"""
Skill Taxonomy for IT Industry

This module defines a comprehensive taxonomy of IT skills organized by category.
Each skill has a canonical name and a list of aliases for flexible matching.

Categories:
- programming_languages: Programming and scripting languages
- frameworks: Web frameworks, libraries, and tools
- databases: Database systems and data stores
- devops: DevOps tools, cloud platforms, and infrastructure
- infrastructure: System administration, OS, and enterprise IT tools
- networking: Network protocols, tools, and security
- compliance: Regulatory compliance and IT governance frameworks
- soft_skills: Non-technical professional skills
- ai_ml: AI/ML frameworks and tools
- it_management: IT team management, leadership, and organizational skills
- other: Skills not matching other categories (populated dynamically)
"""

from typing import Dict, List, TypedDict


class SkillEntry(TypedDict):
    """Type definition for a skill entry in the taxonomy."""
    canonical: str
    aliases: List[str]


# Main skill taxonomy organized by category
SKILL_TAXONOMY: Dict[str, List[SkillEntry]] = {
    "programming_languages": [
        {"canonical": "python", "aliases": ["python3", "py", "python2"]},
        {"canonical": "javascript", "aliases": ["js", "ecmascript", "es6", "es2015", "es2020"]},
        {"canonical": "typescript", "aliases": ["ts"]},
        {"canonical": "java", "aliases": ["java8", "java11", "java17", "java21", "jdk"]},
        {"canonical": "csharp", "aliases": ["c#", "c-sharp", "csharp"]},
        {"canonical": "cpp", "aliases": ["c++", "cplusplus", "c plus plus"]},
        {"canonical": "c", "aliases": ["c language", "clang"]},
        {"canonical": "go", "aliases": ["golang"]},
        {"canonical": "rust", "aliases": ["rustlang"]},
        {"canonical": "php", "aliases": ["php7", "php8"]},
        {"canonical": "ruby", "aliases": ["rb"]},
        {"canonical": "kotlin", "aliases": ["kt"]},
        {"canonical": "swift", "aliases": ["swift5", "swiftui"]},
        {"canonical": "scala", "aliases": []},
        {"canonical": "r", "aliases": ["r language", "rlang"]},
        {"canonical": "dart", "aliases": []},
        {"canonical": "perl", "aliases": []},
        {"canonical": "haskell", "aliases": []},
        {"canonical": "elixir", "aliases": []},
        {"canonical": "clojure", "aliases": []},
        {"canonical": "lua", "aliases": []},
        {"canonical": "groovy", "aliases": []},
        {"canonical": "objective-c", "aliases": ["objc", "objective c"]},
        {"canonical": "shell", "aliases": ["bash", "sh", "zsh", "shell scripting"]},
        {"canonical": "powershell", "aliases": ["ps1", "pwsh"]},
        {"canonical": "sql", "aliases": ["structured query language", "pl/sql", "plsql", "t-sql", "tsql"]},
        {"canonical": "html", "aliases": ["html5"]},
        {"canonical": "css", "aliases": ["css3", "cascading style sheets"]},
        {"canonical": "xml", "aliases": ["xslt", "xpath", "xsd"]},
        {"canonical": "vbnet", "aliases": ["vb.net", "visual basic .net", "visual basic net"]},
    ],
    
    "frameworks": [
        # Frontend frameworks
        {"canonical": "react", "aliases": ["reactjs", "react.js", "react js"]},
        {"canonical": "vue", "aliases": ["vuejs", "vue.js", "vue3", "vue2"]},
        {"canonical": "angular", "aliases": ["angularjs", "angular.js", "angular2", "angular4"]},
        {"canonical": "svelte", "aliases": ["sveltejs", "sveltekit"]},
        {"canonical": "nextjs", "aliases": ["next.js", "next js", "next"]},
        {"canonical": "nuxtjs", "aliases": ["nuxt.js", "nuxt"]},
        {"canonical": "gatsby", "aliases": ["gatsbyjs"]},
        {"canonical": "remix", "aliases": ["remix.run"]},
        
        # Backend frameworks - Python
        {"canonical": "fastapi", "aliases": ["fast-api", "fast api"]},
        {"canonical": "django", "aliases": ["django rest framework", "drf"]},
        {"canonical": "flask", "aliases": []},
        {"canonical": "tornado", "aliases": []},
        {"canonical": "pyramid", "aliases": []},
        
        # Backend frameworks - JavaScript/TypeScript
        {"canonical": "express", "aliases": ["expressjs", "express.js"]},
        {"canonical": "nestjs", "aliases": ["nest.js", "nest"]},
        {"canonical": "koa", "aliases": ["koajs"]},
        {"canonical": "fastify", "aliases": []},
        {"canonical": "hapi", "aliases": ["hapijs"]},
        
        # Backend frameworks - Java
        {"canonical": "spring", "aliases": ["spring boot", "springboot", "spring framework"]},
        {"canonical": "hibernate", "aliases": []},
        {"canonical": "struts", "aliases": []},
        
        # Backend frameworks - Other
        {"canonical": "rails", "aliases": ["ruby on rails", "ror"]},
        {"canonical": "laravel", "aliases": []},
        {"canonical": "symfony", "aliases": []},
        {"canonical": "dotnet", "aliases": [".net", ".net core", "asp.net", "dotnet core", "ado.net", "asp", "asp classic", "entity framework"]},
        {"canonical": "gin", "aliases": ["gin-gonic"]},
        {"canonical": "echo", "aliases": ["labstack echo"]},
        {"canonical": "fiber", "aliases": ["gofiber"]},
        
        # Mobile frameworks
        {"canonical": "react native", "aliases": ["react-native", "rn"]},
        {"canonical": "flutter", "aliases": []},
        {"canonical": "ionic", "aliases": []},
        {"canonical": "xamarin", "aliases": []},
        
        # UI libraries
        {"canonical": "tailwindcss", "aliases": ["tailwind", "tailwind css"]},
        {"canonical": "bootstrap", "aliases": []},
        {"canonical": "material-ui", "aliases": ["mui", "material ui"]},
        {"canonical": "chakra-ui", "aliases": ["chakra ui", "chakra"]},
        {"canonical": "ant-design", "aliases": ["antd", "ant design"]},
        {"canonical": "shadcn", "aliases": ["shadcn/ui", "shadcn ui"]},
        
        # Testing frameworks
        {"canonical": "jest", "aliases": []},
        {"canonical": "pytest", "aliases": ["py.test"]},
        {"canonical": "mocha", "aliases": []},
        {"canonical": "cypress", "aliases": []},
        {"canonical": "playwright", "aliases": []},
        {"canonical": "selenium", "aliases": ["selenium webdriver"]},
        
        # Build tools
        {"canonical": "webpack", "aliases": []},
        {"canonical": "vite", "aliases": ["vitejs"]},
        {"canonical": "rollup", "aliases": []},
        {"canonical": "esbuild", "aliases": []},
        {"canonical": "parcel", "aliases": []},
        
        # State management
        {"canonical": "redux", "aliases": ["redux toolkit", "rtk"]},
        {"canonical": "mobx", "aliases": []},
        {"canonical": "zustand", "aliases": []},
        {"canonical": "recoil", "aliases": []},
        {"canonical": "pinia", "aliases": []},
        {"canonical": "vuex", "aliases": []},
    ],
    
    "databases": [
        # Relational databases
        {"canonical": "postgresql", "aliases": ["postgres", "psql", "pg"]},
        {"canonical": "mysql", "aliases": ["mariadb"]},
        {"canonical": "sqlite", "aliases": ["sqlite3"]},
        {"canonical": "oracle", "aliases": ["oracle db", "oracle database"]},
        {"canonical": "sqlserver", "aliases": ["sql server", "mssql", "microsoft sql server"]},
        
        # NoSQL databases
        {"canonical": "mongodb", "aliases": ["mongo"]},
        {"canonical": "cassandra", "aliases": ["apache cassandra"]},
        {"canonical": "couchdb", "aliases": ["couch"]},
        {"canonical": "dynamodb", "aliases": ["dynamo", "aws dynamodb"]},
        {"canonical": "firestore", "aliases": ["firebase firestore", "cloud firestore"]},
        
        # In-memory/Cache
        {"canonical": "redis", "aliases": []},
        {"canonical": "memcached", "aliases": []},
        
        # Search engines
        {"canonical": "elasticsearch", "aliases": ["elastic", "es"]},
        {"canonical": "opensearch", "aliases": []},
        {"canonical": "solr", "aliases": ["apache solr"]},
        {"canonical": "algolia", "aliases": []},
        
        # Vector databases
        {"canonical": "pinecone", "aliases": []},
        {"canonical": "chromadb", "aliases": ["chroma"]},
        {"canonical": "weaviate", "aliases": []},
        {"canonical": "milvus", "aliases": []},
        {"canonical": "qdrant", "aliases": []},
        
        # Graph databases
        {"canonical": "neo4j", "aliases": []},
        {"canonical": "neptune", "aliases": ["amazon neptune"]},
        
        # Time-series databases
        {"canonical": "influxdb", "aliases": ["influx"]},
        {"canonical": "timescaledb", "aliases": ["timescale"]},
        
        # ORMs
        {"canonical": "sqlalchemy", "aliases": ["sql alchemy"]},
        {"canonical": "prisma", "aliases": []},
        {"canonical": "typeorm", "aliases": []},
        {"canonical": "sequelize", "aliases": []},
        {"canonical": "mongoose", "aliases": []},
    ],
    
    "devops": [
        # Containerization
        {"canonical": "docker", "aliases": ["docker compose", "docker-compose"]},
        {"canonical": "kubernetes", "aliases": ["k8s"]},
        {"canonical": "podman", "aliases": []},
        {"canonical": "containerd", "aliases": []},
        
        # Cloud providers
        {"canonical": "aws", "aliases": ["amazon web services", "amazon aws"]},
        {"canonical": "gcp", "aliases": ["google cloud", "google cloud platform"]},
        {"canonical": "azure", "aliases": ["microsoft azure"]},
        {"canonical": "digitalocean", "aliases": ["digital ocean", "do"]},
        {"canonical": "heroku", "aliases": []},
        {"canonical": "vercel", "aliases": []},
        {"canonical": "netlify", "aliases": []},
        {"canonical": "cloudflare", "aliases": []},
        
        # AWS services
        {"canonical": "ec2", "aliases": ["aws ec2", "amazon ec2"]},
        {"canonical": "s3", "aliases": ["aws s3", "amazon s3"]},
        {"canonical": "lambda", "aliases": ["aws lambda"]},
        {"canonical": "ecs", "aliases": ["aws ecs"]},
        {"canonical": "eks", "aliases": ["aws eks"]},
        {"canonical": "rds", "aliases": ["aws rds"]},
        {"canonical": "sqs", "aliases": ["aws sqs"]},
        {"canonical": "sns", "aliases": ["aws sns"]},
        
        # IaC tools
        {"canonical": "terraform", "aliases": ["tf"]},
        {"canonical": "ansible", "aliases": []},
        {"canonical": "pulumi", "aliases": []},
        {"canonical": "cloudformation", "aliases": ["aws cloudformation", "cfn"]},
        {"canonical": "chef", "aliases": []},
        {"canonical": "puppet", "aliases": []},
        
        # CI/CD
        {"canonical": "jenkins", "aliases": []},
        {"canonical": "github actions", "aliases": ["github-actions", "gha"]},
        {"canonical": "gitlab ci", "aliases": ["gitlab-ci", "gitlab ci/cd"]},
        {"canonical": "circleci", "aliases": ["circle ci"]},
        {"canonical": "travis ci", "aliases": ["travis-ci", "travisci"]},
        {"canonical": "azure devops", "aliases": ["azure pipelines"]},
        {"canonical": "argo cd", "aliases": ["argocd"]},
        
        # Monitoring & Logging
        {"canonical": "prometheus", "aliases": []},
        {"canonical": "grafana", "aliases": []},
        {"canonical": "datadog", "aliases": []},
        {"canonical": "newrelic", "aliases": ["new relic"]},
        {"canonical": "splunk", "aliases": []},
        {"canonical": "elk", "aliases": ["elk stack", "elastic stack"]},
        {"canonical": "kibana", "aliases": []},
        {"canonical": "logstash", "aliases": []},
        {"canonical": "fluentd", "aliases": []},
        {"canonical": "sentry", "aliases": []},
        
        # Networking
        {"canonical": "nginx", "aliases": []},
        {"canonical": "apache", "aliases": ["apache httpd", "httpd"]},
        {"canonical": "iis", "aliases": ["internet information services", "microsoft iis"]},
        {"canonical": "haproxy", "aliases": ["ha proxy"]},
        {"canonical": "traefik", "aliases": []},
        {"canonical": "envoy", "aliases": []},
        
        # Security
        {"canonical": "vault", "aliases": ["hashicorp vault"]},
        {"canonical": "oauth", "aliases": ["oauth2", "oauth 2.0"]},
        {"canonical": "jwt", "aliases": ["json web token"]},
        {"canonical": "ssl", "aliases": ["ssl/tls", "tls"]},
        
        # Version control
        {"canonical": "git", "aliases": []},
        {"canonical": "github", "aliases": []},
        {"canonical": "gitlab", "aliases": []},
        {"canonical": "bitbucket", "aliases": []},
        {"canonical": "tfs", "aliases": ["team foundation server", "azure devops server", "vsts"]},
        {"canonical": "svn", "aliases": ["subversion", "apache subversion"]},
        
        # Message queues
        {"canonical": "rabbitmq", "aliases": ["rabbit mq"]},
        {"canonical": "kafka", "aliases": ["apache kafka"]},
        {"canonical": "celery", "aliases": []},
        {"canonical": "zeromq", "aliases": ["zmq", "0mq"]},
        
        # API tools
        {"canonical": "graphql", "aliases": []},
        {"canonical": "rest", "aliases": ["restful", "rest api"]},
        {"canonical": "grpc", "aliases": []},
        {"canonical": "swagger", "aliases": ["openapi"]},
        {"canonical": "postman", "aliases": []},
    ],
    
    "soft_skills": [
        {"canonical": "communication", "aliases": ["verbal communication", "written communication"]},
        {"canonical": "teamwork", "aliases": ["team collaboration", "collaboration", "team player"]},
        {"canonical": "leadership", "aliases": ["team leadership", "technical leadership", "tech lead"]},
        {"canonical": "problem solving", "aliases": ["problem-solving", "analytical thinking", "critical thinking"]},
        {"canonical": "agile", "aliases": ["agile methodology", "agile development", "agile methodologies"]},
        {"canonical": "scrum", "aliases": ["scrum master", "scrum methodology"]},
        {"canonical": "kanban", "aliases": []},
        {"canonical": "project management", "aliases": ["pm", "project manager", "software project management"]},
        {"canonical": "time management", "aliases": ["time-management"]},
        {"canonical": "adaptability", "aliases": ["flexibility", "versatility"]},
        {"canonical": "mentoring", "aliases": ["coaching", "training"]},
        {"canonical": "code review", "aliases": ["code-review", "peer review"]},
        {"canonical": "documentation", "aliases": ["technical writing", "tech writing"]},
        {"canonical": "presentation", "aliases": ["public speaking", "presenting"]},
        {"canonical": "stakeholder management", "aliases": ["client communication"]},
        {"canonical": "sdlc", "aliases": ["software development lifecycle", "software development life cycle"]},
        {"canonical": "business analysis", "aliases": ["business analyst", "requirements analysis", "requirements gathering"]},
        {"canonical": "strategic planning", "aliases": ["it strategy", "tactical planning", "strategic thinking"]},
    ],
    
    "ai_ml": [
        # ML frameworks
        {"canonical": "tensorflow", "aliases": ["tf", "tensorflow 2"]},
        {"canonical": "pytorch", "aliases": ["torch"]},
        {"canonical": "keras", "aliases": []},
        {"canonical": "scikit-learn", "aliases": ["sklearn", "scikit learn"]},
        {"canonical": "xgboost", "aliases": []},
        {"canonical": "lightgbm", "aliases": ["light gbm"]},
        
        # NLP
        {"canonical": "nltk", "aliases": ["natural language toolkit"]},
        {"canonical": "spacy", "aliases": []},
        {"canonical": "huggingface", "aliases": ["hugging face", "transformers"]},
        {"canonical": "langchain", "aliases": ["lang chain"]},
        {"canonical": "llamaindex", "aliases": ["llama index", "gpt index"]},
        
        # Computer Vision
        {"canonical": "opencv", "aliases": ["open cv", "cv2"]},
        {"canonical": "yolo", "aliases": ["yolov5", "yolov8"]},
        
        # Data science
        {"canonical": "pandas", "aliases": []},
        {"canonical": "numpy", "aliases": []},
        {"canonical": "scipy", "aliases": []},
        {"canonical": "matplotlib", "aliases": []},
        {"canonical": "seaborn", "aliases": []},
        {"canonical": "plotly", "aliases": []},
        {"canonical": "jupyter", "aliases": ["jupyter notebook", "jupyter lab"]},
        
        # Business Intelligence
        {"canonical": "tableau", "aliases": ["tableau desktop", "tableau server"]},
        {"canonical": "power bi", "aliases": ["powerbi", "power bi desktop", "microsoft power bi"]},
        {"canonical": "looker", "aliases": ["google looker"]},
        {"canonical": "metabase", "aliases": []},
        {"canonical": "superset", "aliases": ["apache superset"]},
        {"canonical": "qlik", "aliases": ["qlikview", "qlik sense"]},
        
        # ML Ops
        {"canonical": "mlflow", "aliases": ["ml flow"]},
        {"canonical": "kubeflow", "aliases": ["kube flow"]},
        {"canonical": "airflow", "aliases": ["apache airflow"]},
        {"canonical": "dvc", "aliases": ["data version control"]},
        
        # LLM & AI
        {"canonical": "openai", "aliases": ["gpt", "chatgpt", "gpt-4", "gpt-3"]},
        {"canonical": "anthropic", "aliases": ["claude"]},
        {"canonical": "ollama", "aliases": []},
        {"canonical": "llama", "aliases": ["llama2", "llama 2", "llama3"]},
        {"canonical": "rag", "aliases": ["retrieval augmented generation"]},
    ],
    
    "infrastructure": [
        # Operating Systems
        {"canonical": "windows server", "aliases": ["windows 2000", "windows 2003", "windows 2008", "windows 2012", "windows 2016", "windows 2019", "windows 2022", "win server"]},
        {"canonical": "windows", "aliases": ["windows xp", "windows 7", "windows 10", "windows 11", "win xp", "win7", "win10", "win11"]},
        {"canonical": "linux", "aliases": ["linux server", "linux administration", "linux admin"]},
        {"canonical": "ubuntu", "aliases": ["ubuntu server"]},
        {"canonical": "centos", "aliases": ["centos linux"]},
        {"canonical": "redhat", "aliases": ["rhel", "red hat", "red hat enterprise linux"]},
        {"canonical": "debian", "aliases": []},
        {"canonical": "unix", "aliases": ["aix", "solaris", "hp-ux"]},
        {"canonical": "macos", "aliases": ["mac os", "osx", "os x"]},
        
        # Virtualization
        {"canonical": "vmware", "aliases": ["vsphere", "esxi", "vcenter", "vmware workstation"]},
        {"canonical": "hyper-v", "aliases": ["hyperv", "hyper v", "microsoft hyper-v"]},
        {"canonical": "virtualbox", "aliases": ["vbox", "oracle virtualbox"]},
        {"canonical": "proxmox", "aliases": ["proxmox ve"]},
        {"canonical": "citrix", "aliases": ["xenserver", "citrix xenapp", "citrix xendesktop"]},
        
        # Directory Services
        {"canonical": "active directory", "aliases": ["ad", "ldap", "windows ad", "microsoft ad"]},
        {"canonical": "azure ad", "aliases": ["azure active directory", "aad", "entra id"]},
        
        # Enterprise IT Tools
        {"canonical": "sccm", "aliases": ["system center", "mecm", "microsoft endpoint configuration manager", "configmgr"]},
        {"canonical": "intune", "aliases": ["microsoft intune", "endpoint manager"]},
        {"canonical": "landesk", "aliases": ["ivanti", "ivanti landesk"]},
        {"canonical": "jamf", "aliases": ["jamf pro", "casper suite"]},
        {"canonical": "servicenow", "aliases": ["service now", "snow"]},
        
        # Backup & Recovery
        {"canonical": "veeam", "aliases": ["veeam backup"]},
        {"canonical": "arcserve", "aliases": ["ca arcserve", "arcserve backup"]},
        {"canonical": "backup exec", "aliases": ["backupexec", "veritas backup exec", "symantec backup exec"]},
        {"canonical": "netbackup", "aliases": ["veritas netbackup", "net backup"]},
        {"canonical": "commvault", "aliases": []},
        {"canonical": "acronis", "aliases": ["acronis backup"]},
        
        # System Imaging
        {"canonical": "symantec ghost", "aliases": ["ghost", "norton ghost"]},
        {"canonical": "clonezilla", "aliases": []},
        {"canonical": "fog", "aliases": ["fog project", "fog server"]},
        
        # Legacy Systems
        {"canonical": "novell", "aliases": ["novell netware", "netware", "novell edir", "edirectory"]},
        {"canonical": "lotus notes", "aliases": ["ibm notes", "domino"]},
        {"canonical": "exchange", "aliases": ["microsoft exchange", "exchange server", "exchange online"]},
        {"canonical": "sharepoint", "aliases": ["microsoft sharepoint", "sharepoint online"]},
        
        # Storage
        {"canonical": "san", "aliases": ["storage area network"]},
        {"canonical": "nas", "aliases": ["network attached storage"]},
        {"canonical": "netapp", "aliases": ["net app", "ontap"]},
        {"canonical": "emc", "aliases": ["dell emc", "emc storage"]},
        
        # ITIL/Service Management
        {"canonical": "itil", "aliases": ["it service management", "itsm"]},
        {"canonical": "asset management", "aliases": ["it asset management", "itam"]},
    ],
    
    "networking": [
        # Protocols
        {"canonical": "tcp/ip", "aliases": ["tcp ip", "tcpip", "ip networking"]},
        {"canonical": "dns", "aliases": ["domain name system", "bind"]},
        {"canonical": "dhcp", "aliases": ["dynamic host configuration"]},
        {"canonical": "http/https", "aliases": ["http", "https", "http/s"]},
        {"canonical": "ftp", "aliases": ["sftp", "ftps", "file transfer protocol"]},
        {"canonical": "ssh", "aliases": ["secure shell", "openssh"]},
        {"canonical": "vpn", "aliases": ["virtual private network", "openvpn", "ipsec vpn"]},
        {"canonical": "smtp", "aliases": ["email protocol", "mail server"]},
        {"canonical": "snmp", "aliases": ["simple network management protocol"]},
        
        # Network Equipment
        {"canonical": "cisco", "aliases": ["cisco ios", "cisco networking", "cisco router", "cisco switch"]},
        {"canonical": "juniper", "aliases": ["junos", "juniper networks"]},
        {"canonical": "mikrotik", "aliases": ["routeros"]},
        {"canonical": "ubiquiti", "aliases": ["unifi", "ubnt"]},
        {"canonical": "palo alto", "aliases": ["palo alto networks", "pan-os"]},
        {"canonical": "fortinet", "aliases": ["fortigate", "fortios"]},
        
        # Network Services
        {"canonical": "load balancing", "aliases": ["load balancer", "f5", "f5 big-ip", "netscaler"]},
        {"canonical": "firewall", "aliases": ["network firewall", "firewall management"]},
        {"canonical": "proxy", "aliases": ["proxy server", "squid proxy", "reverse proxy"]},
        {"canonical": "wan", "aliases": ["wide area network", "sd-wan", "mpls"]},
        {"canonical": "lan", "aliases": ["local area network", "ethernet"]},
        {"canonical": "vlan", "aliases": ["virtual lan", "network segmentation"]},
        {"canonical": "wifi", "aliases": ["wireless", "wlan", "802.11", "wireless networking"]},
        
        # Network Monitoring
        {"canonical": "wireshark", "aliases": ["packet capture", "network analysis"]},
        {"canonical": "nagios", "aliases": ["nagios core", "nagios xi"]},
        {"canonical": "zabbix", "aliases": []},
        {"canonical": "prtg", "aliases": ["prtg network monitor"]},
        {"canonical": "netflow", "aliases": ["sflow", "network flow"]},
    ],
    
    "compliance": [
        # Healthcare
        {"canonical": "hipaa", "aliases": ["health insurance portability", "hipaa compliance", "hipaa/hitech"]},
        {"canonical": "hitech", "aliases": ["hitech act"]},
        {"canonical": "emr", "aliases": ["electronic medical records", "ehr", "electronic health records"]},
        {"canonical": "hl7", "aliases": ["hl7 fhir", "health level 7"]},
        {"canonical": "epic", "aliases": ["epic systems", "epic emr"]},
        {"canonical": "cerner", "aliases": ["cerner emr"]},
        {"canonical": "allscripts", "aliases": ["allscripts emr"]},
        {"canonical": "mckesson", "aliases": ["mckesson emr"]},
        
        # Financial/Payment
        {"canonical": "pci-dss", "aliases": ["pci dss", "pci compliance", "payment card industry"]},
        {"canonical": "sox", "aliases": ["sarbanes-oxley", "sarbanes oxley", "sox compliance"]},
        
        # Data Privacy
        {"canonical": "gdpr", "aliases": ["general data protection regulation", "gdpr compliance"]},
        {"canonical": "ccpa", "aliases": ["california consumer privacy act"]},
        {"canonical": "data privacy", "aliases": ["data protection", "privacy compliance"]},
        
        # Security Standards
        {"canonical": "iso 27001", "aliases": ["iso27001", "iso 27001 certification", "information security management"]},
        {"canonical": "nist", "aliases": ["nist framework", "nist cybersecurity", "nist 800"]},
        {"canonical": "cobit", "aliases": ["cobit framework"]},
        {"canonical": "fedramp", "aliases": ["fed ramp", "federal risk authorization"]},
        
        # Audit & Governance
        {"canonical": "it audit", "aliases": ["information systems audit", "is audit"]},
        {"canonical": "risk management", "aliases": ["it risk management", "risk assessment"]},
        {"canonical": "disaster recovery", "aliases": ["dr", "disaster recovery planning", "drp", "business continuity"]},
        {"canonical": "change management", "aliases": ["change control", "itil change management"]},
    ],
    
    "it_management": [
        # Team Leadership & Management
        {"canonical": "team management", "aliases": ["team lead", "team leader", "quan ly doi nhom", "quan ly team", "it team management", "managing teams"]},
        {"canonical": "engineering management", "aliases": ["engineering manager", "em", "software engineering management", "dev management"]},
        {"canonical": "technical leadership", "aliases": ["tech lead", "technical lead", "technical leader", "tech leadership"]},
        {"canonical": "people management", "aliases": ["people leader", "direct reports", "managing people", "staff management"]},
        {"canonical": "cross-functional leadership", "aliases": ["cross-functional teams", "cross functional collaboration", "matrix management"]},
        
        # Resource & Capacity Planning
        {"canonical": "resource planning", "aliases": ["resource allocation", "capacity planning", "workforce planning", "resource management"]},
        {"canonical": "headcount planning", "aliases": ["headcount management", "staffing plan", "team sizing"]},
        {"canonical": "skill gap analysis", "aliases": ["skills assessment", "competency mapping", "skill matrix"]},
        {"canonical": "succession planning", "aliases": ["leadership pipeline", "talent pipeline"]},
        
        # Performance & Development
        {"canonical": "performance management", "aliases": ["performance review", "performance evaluation", "kpi management", "okr", "okrs"]},
        {"canonical": "career development", "aliases": ["career path", "career growth", "professional development", "career coaching"]},
        {"canonical": "talent development", "aliases": ["talent management", "employee development", "learning and development", "l&d"]},
        {"canonical": "1-on-1", "aliases": ["one on one", "1:1", "one-on-one meetings", "1on1"]},
        {"canonical": "feedback", "aliases": ["giving feedback", "constructive feedback", "360 feedback", "continuous feedback"]},
        
        # Hiring & Recruiting
        {"canonical": "technical interviewing", "aliases": ["tech interview", "coding interview", "technical hiring", "interview process"]},
        {"canonical": "hiring", "aliases": ["recruitment", "recruiting", "talent acquisition", "hiring process"]},
        {"canonical": "onboarding", "aliases": ["new hire onboarding", "employee onboarding", "orientation"]},
        {"canonical": "employer branding", "aliases": ["tech branding", "engineering brand"]},
        
        # IT Strategy & Planning
        {"canonical": "it strategy", "aliases": ["technology strategy", "tech strategy", "it roadmap", "digital strategy"]},
        {"canonical": "technology roadmap", "aliases": ["tech roadmap", "product roadmap", "technical roadmap"]},
        {"canonical": "digital transformation", "aliases": ["dx", "digitalization", "modernization"]},
        {"canonical": "it governance", "aliases": ["technology governance", "it policies"]},
        {"canonical": "enterprise architecture", "aliases": ["ea", "solution architecture", "technical architecture"]},
        
        # Budget & Vendor Management
        {"canonical": "it budgeting", "aliases": ["it budget", "technology budget", "budget management", "cost management"]},
        {"canonical": "vendor management", "aliases": ["supplier management", "vendor relationship", "third-party management", "outsourcing management"]},
        {"canonical": "contract negotiation", "aliases": ["vendor negotiation", "it contracts", "software licensing"]},
        {"canonical": "procurement", "aliases": ["it procurement", "technology procurement", "purchasing"]},
        {"canonical": "cost optimization", "aliases": ["cost reduction", "it cost optimization", "cloud cost optimization", "finops"]},
        
        # Process & Methodology
        {"canonical": "process improvement", "aliases": ["process optimization", "continuous improvement", "kaizen", "lean it"]},
        {"canonical": "devops culture", "aliases": ["devops transformation", "devops practices", "sre culture"]},
        {"canonical": "engineering excellence", "aliases": ["technical excellence", "engineering practices", "best practices"]},
        {"canonical": "quality assurance management", "aliases": ["qa management", "quality management", "testing strategy"]},
        {"canonical": "release management", "aliases": ["deployment management", "release planning", "release coordination"]},
        
        # Communication & Stakeholder Management
        {"canonical": "executive communication", "aliases": ["c-level communication", "board presentation", "leadership communication"]},
        {"canonical": "technical communication", "aliases": ["tech communication", "engineering communication"]},
        {"canonical": "stakeholder management", "aliases": ["stakeholder engagement", "stakeholder communication", "managing stakeholders"]},
        {"canonical": "conflict resolution", "aliases": ["conflict management", "dispute resolution", "mediation"]},
        {"canonical": "influence without authority", "aliases": ["lateral leadership", "persuasion", "building consensus"]},
        
        # Team Culture & Organization
        {"canonical": "team building", "aliases": ["team bonding", "team culture", "building teams"]},
        {"canonical": "remote team management", "aliases": ["distributed team", "virtual team management", "remote leadership"]},
        {"canonical": "organizational design", "aliases": ["org design", "team structure", "org structure"]},
        {"canonical": "culture building", "aliases": ["engineering culture", "team culture", "company culture"]},
        {"canonical": "diversity and inclusion", "aliases": ["d&i", "dei", "inclusive leadership", "diverse teams"]},
        
        # Incident & Crisis Management
        {"canonical": "incident management", "aliases": ["incident response", "incident commander", "on-call management"]},
        {"canonical": "crisis management", "aliases": ["crisis response", "emergency management", "crisis leadership"]},
        {"canonical": "postmortem", "aliases": ["post-mortem", "retrospective", "blameless postmortem", "incident review"]},
        {"canonical": "escalation management", "aliases": ["escalation process", "escalation handling"]},
        
        # Metrics & Reporting
        {"canonical": "engineering metrics", "aliases": ["dora metrics", "team metrics", "productivity metrics", "development metrics"]},
        {"canonical": "kpi tracking", "aliases": ["key performance indicators", "metrics tracking", "performance tracking"]},
        {"canonical": "reporting", "aliases": ["status reporting", "executive reporting", "management reporting"]},
        {"canonical": "data-driven decision making", "aliases": ["data-driven management", "evidence-based management"]},
    ],
}


# Hot/in-demand skills for 2024 IT industry
HOT_SKILLS_2024: Dict[str, List[str]] = {
    "programming_languages": ["python", "typescript", "go", "rust"],
    "frameworks": ["react", "nextjs", "fastapi", "nestjs"],
    "databases": ["postgresql", "mongodb", "redis", "chromadb"],
    "devops": ["docker", "kubernetes", "aws", "terraform", "github actions"],
    "ai_ml": ["pytorch", "langchain", "huggingface", "openai", "rag"],
    "it_management": ["engineering management", "technical leadership", "devops culture", "remote team management"],
}


def get_all_skills() -> Dict[str, List[str]]:
    """
    Get a flat list of all canonical skill names organized by category.
    
    Returns:
        Dict mapping category names to lists of canonical skill names.
        
    Example:
        >>> skills = get_all_skills()
        >>> skills["programming_languages"]
        ['python', 'javascript', 'typescript', ...]
    """
    result: Dict[str, List[str]] = {}
    for category, skills in SKILL_TAXONOMY.items():
        result[category] = [skill["canonical"] for skill in skills]
    return result


def get_skill_aliases() -> Dict[str, str]:
    """
    Get a mapping from all skill aliases to their canonical names.
    
    This includes:
    - The canonical name itself (maps to itself)
    - All aliases for each skill
    
    Returns:
        Dict mapping lowercase alias strings to canonical skill names.
        
    Example:
        >>> aliases = get_skill_aliases()
        >>> aliases["reactjs"]
        'react'
        >>> aliases["python"]
        'python'
    """
    result: Dict[str, str] = {}
    for category, skills in SKILL_TAXONOMY.items():
        for skill in skills:
            canonical = skill["canonical"]
            # Add canonical name itself
            result[canonical.lower()] = canonical
            # Add all aliases
            for alias in skill["aliases"]:
                result[alias.lower()] = canonical
    return result


def get_skill_to_category() -> Dict[str, str]:
    """
    Get a mapping from canonical skill names to their categories.
    
    Returns:
        Dict mapping canonical skill names to category names.
        
    Example:
        >>> mapping = get_skill_to_category()
        >>> mapping["python"]
        'programming_languages'
        >>> mapping["react"]
        'frameworks'
    """
    result: Dict[str, str] = {}
    for category, skills in SKILL_TAXONOMY.items():
        for skill in skills:
            result[skill["canonical"]] = category
    return result


def is_hot_skill(skill: str) -> bool:
    """
    Check if a skill is in the hot skills list for 2024.
    
    Args:
        skill: Canonical skill name to check.
        
    Returns:
        True if the skill is a hot/in-demand skill.
        
    Example:
        >>> is_hot_skill("python")
        True
        >>> is_hot_skill("perl")
        False
    """
    for category_skills in HOT_SKILLS_2024.values():
        if skill.lower() in [s.lower() for s in category_skills]:
            return True
    return False
