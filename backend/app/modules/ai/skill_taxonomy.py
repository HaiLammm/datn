"""
Skill Taxonomy for IT Industry

This module defines a comprehensive taxonomy of IT skills organized by category.
Each skill has a canonical name and a list of aliases for flexible matching.

Categories:
- programming_languages: Programming and scripting languages
- frameworks: Web frameworks, libraries, and tools
- databases: Database systems and data stores
- devops: DevOps tools, cloud platforms, and infrastructure
- soft_skills: Non-technical professional skills
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
        {"canonical": "sql", "aliases": ["structured query language"]},
        {"canonical": "html", "aliases": ["html5"]},
        {"canonical": "css", "aliases": ["css3", "cascading style sheets"]},
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
        {"canonical": "dotnet", "aliases": [".net", ".net core", "asp.net", "dotnet core"]},
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
        {"canonical": "agile", "aliases": ["agile methodology", "agile development"]},
        {"canonical": "scrum", "aliases": ["scrum master", "scrum methodology"]},
        {"canonical": "kanban", "aliases": []},
        {"canonical": "project management", "aliases": ["pm", "project manager"]},
        {"canonical": "time management", "aliases": ["time-management"]},
        {"canonical": "adaptability", "aliases": ["flexibility", "versatility"]},
        {"canonical": "mentoring", "aliases": ["coaching", "training"]},
        {"canonical": "code review", "aliases": ["code-review", "peer review"]},
        {"canonical": "documentation", "aliases": ["technical writing", "tech writing"]},
        {"canonical": "presentation", "aliases": ["public speaking", "presenting"]},
        {"canonical": "stakeholder management", "aliases": ["client communication"]},
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
}


# Hot/in-demand skills for 2024 IT industry
HOT_SKILLS_2024: Dict[str, List[str]] = {
    "programming_languages": ["python", "typescript", "go", "rust"],
    "frameworks": ["react", "nextjs", "fastapi", "nestjs"],
    "databases": ["postgresql", "mongodb", "redis", "chromadb"],
    "devops": ["docker", "kubernetes", "aws", "terraform", "github actions"],
    "ai_ml": ["pytorch", "langchain", "huggingface", "openai", "rag"],
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
