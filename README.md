<table>
  <tr>
    <td width="65%" valign="top">
      <h1>Hi, I'm Sandesh.</h1>
      <h3>Building resilient systems at the intersection of <br/> <b>Security</b>, <b>AI</b>, and <b>Cloud Infrastructure</b>.</h3>
      <br/>
      <p>
        I focus on designing platforms that prioritize data sovereignty and fault tolerance. Currently refactoring legacy monoliths into secure microservices and researching adversarial machine learning.
      </p>
      <br/>
      <a href="https://linkedin.com/in/yourusername">
        <img src="https://img.shields.io/badge/Connect-LinkedIn-0077B5?style=for-the-badge&logo=linkedin" />
      </a>
      <a href="mailto:your@email.com">
        <img src="https://img.shields.io/badge/Contact-Email-D14836?style=for-the-badge&logo=gmail&logoColor=white" />
      </a>
    </td>
    <td width="35%" valign="top">
      <h3>⚡ Current Focus</h3>
      <ul>
        <li><b>Role:</b> Systems Architect</li>
        <li><b>Domain:</b> FinTech & Smart Cities</li>
        <li><b>Stack:</b> Go, Rust, Kubernetes</li>
        <li><b>Learning:</b> Zero-Knowledge Proofs</li>
      </ul>
    </td>
  </tr>
</table>

<div align="center">
  <br/>
  ---
  <br/>
</div>

### 🛠 Technical Arsenal

| **Infrastructure & Cloud** | **Security & DevOps** | **Core Engineering** |
| :--- | :--- | :--- |
| ![AWS](https://img.shields.io/badge/AWS-232F3E?style=flat-square&logo=amazon-aws&logoColor=white) ![Azure](https://img.shields.io/badge/Azure-0078D4?style=flat-square&logo=microsoft-azure&logoColor=white) | ![Kali](https://img.shields.io/badge/Kali_Linux-557C94?style=flat-square&logo=kali-linux&logoColor=white) ![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white) | ![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white) ![Go](https://img.shields.io/badge/Go-00ADD8?style=flat-square&logo=go&logoColor=white) |
| *Terraform, Ansible, K8s* | *Burp Suite, OWASP ZAP, CI/CD* | *gRPC, GraphQL, REST* |

### 📌 Selected Works

> *"Talk is cheap. Show me the code."*

| Repository | Role | The Problem & Solution |
| :--- | :--- | :--- |
| **[Sentinel-Auth](link)** | **Lead Dev** | **Auth Bottlenecks:** Built a distributed auth service using Redis & JWTs handling 50k req/s. |
| **[City-Grid-AI](link)** | **Architect** | **Traffic Optimization:** Computer vision pipeline reducing urban congestion by 15% via traffic light automation. |
| **[Secure-Audit-CLI](link)** | **Creator** | **Compliance:** Automated script to check CIS benchmarks against AWS infrastructure. |

<br/>
<img src="https://github-readme-stats.vercel.app/api?username=YOUR_USERNAME&show_icons=true&theme=minimal&hide_border=true&bg_color=00000000" alt="Stats" />

<div align="center">
  <h1>🛡️ Project Name</h1>
  <p><b>Secure, High-Performance Middleware for Financial Data</b></p>
  
  <img src="https://img.shields.io/github/license/username/repo?style=flat-square&color=blue" />
  <img src="https://img.shields.io/github/actions/workflow/status/username/repo/ci.yml?style=flat-square&label=Build" />
  <img src="https://img.shields.io/badge/Coverage-98%25-green?style=flat-square" />
  <img src="https://img.shields.io/badge/Security-A%2B-success?style=flat-square" />
</div>

<br/>

> **Executive Summary:** [Project Name] solves the latency issues found in traditional REST APIs by implementing a binary protocol over WebSockets, reducing payload size by 60%.

---

## 🏗 Architecture
This system utilizes a **Publisher/Subscriber** model to decouple data ingestion from analytics processing.

```mermaid
graph TD
    A[Client App] -->|WebSocket/TLS| B(Gateway Service)
    B -->|Protobuf| C{Message Broker}
    C -->|Topic: Txn| D[Fraud Detection Engine]
    C -->|Topic: Log| E[Audit Service]
    D --> F[(Redis Cache)]
    E --> G[(Cold Storage)]

    # 1. Clone the repo
git clone [https://github.com/username/project-name.git](https://github.com/username/project-name.git)

# 2. Run with Compose
docker-compose up -d --build

# 3. Verify Health
curl http://localhost:8080/health

### What makes these "Modified" versions better?

1.  **Table Layout in Profile:** It stops the profile from looking like a long, vertically scrolling blog post. It puts the most important info "above the fold."
2.  **Comparative Table in Repo:** The "Key Differentiators" table immediately answers "Why does this project exist?" which is the \#1 question a senior engineer asks when looking at code.
3.  **Mermaid Diagrams:** We swapped static images for Mermaid code blocks (in the repo README). These render natively on GitHub and show you understand *documentation as code*.
4.  **Security Section:** Explicitly mentioning OWASP and "Secrets Management" signals maturity.

**Would you like a specific template for the `CONTRIBUTING.md` file referenced in the repository template?**
