# Azure Solution Design Document

### Business Unit
- Business Unit Name: Enterprise Digital Services
- Business Unit Owner: Chief Technology Officer
- Cost Center: CC-2026-AZURE-001
- Data Classification: Confidential (contains customer data and business logic)

### Revision Information
- **Version**: 1.0
- **Date**: 2026-02-12
- **Author**: Azure Solutions Architect
- **Reviewer**: Enterprise Architecture Review Board
- **Approval Status**: Draft - Pending Review
- **Next Review Date**: 2026-03-12

### Abstract

This document defines the solution architecture for an Azure-based application that must be scalable, secure, and cost-effective. It outlines the end-to-end traffic flows, Azure services, security controls, operational practices, and assumptions required to deliver the solution. It also captures the decisions, constraints, and risks that guide implementation and ongoing operations.

### Table of Contents
- [ 1. KEY STAKEHOLDERS]
- [ 2. Solution Overview]
- - [2.1. Success Criteria]
- - [2.2. Assumptions]
- - [2.3. Project Timeline]
- - [2.4. Application Git Repository]
- [ 3. Azure Solution Architecture]
- - [3.1  Solution Diagram]
- - [3.2  Deployment Pattern / Isolation Zone Pattern]
- - [3.3  Design Decisions]
- - [3.4 Technical Assumptions]
- - [3.5  Security Considerations]
- - - [3.5.1  Network Security]
- - - [3.5.2  Data Security]
- - - [3.5.3  Identity and Access Management]
- - [3.6  Scalability and Performance]
- - [3.7 Naming Standards]
- - [3.8 Azure Tagging]
- - [3.9 Virtual Machine Instances & IaaS Services ]
- - [3.10 User Defined Routings]
- - [3.11 Azure Monitor]
- - [3.12 Cost Management]
- - [3.13 Azure Logging]
- - [3.14 Backups]
- - [3.15 Azure Policies]
- - [3.16 Resilience and Disaster Recovery]
- - [3.17 RTO and RPO]
- [ 4. Isolation Zone Networking]
- - [4.1 Isolation Zone Networking Architecture]
- - [4.2 Isolation Zone Networking Components]
- - [4.3 Isolation Zone Networking Security]
- [ 5. DNS Zones & Records]
- [ 6. Security]
- - [6.1 Identity and Access Management]
- - [6.2 Data Security]
- - [6.3 Network Security]
- - [6.4 Compliance and Regulatory Considerations]
- - [6.5 Security Considerations]
- - [6.6 Azure Firewall]
- - [6.7 Azure Policy]
- [ 7. Operations & Incident Response]
- - [7.1 Platform operation and incident response]
- - [7.2 TLA Incident Response Plan]
- [ 8. Risks]
- - [8.1 Risk Management]
- - [8.2 Risk Assessment]
- - [8.3 Risk Mitigation]
- - [8.4 Operational & Security Risk]
- [ 9. Estimated Costs]

# 1. KEY STAKEHOLDERS

| Role | Name | Responsibility | Contact |
|------|------|----------------|---------|
| Business Owner | TBD | Defines business goals, funding approval, ROI validation, success criteria sign-off | TBD |
| Product Owner | TBD | Prioritizes feature backlog, scope management, user story acceptance, sprint planning | TBD |
| Enterprise Architect | TBD | Alignment with enterprise standards, technology roadmap, architectural governance | TBD |
| Security Officer | TBD | Security approvals, compliance validation, vulnerability management, access reviews | TBD |
| Platform Operations Lead | TBD | Operational readiness, runbook development, 24x7 support, incident management | TBD |
| Data Owner | TBD | Data governance policies, data access approvals, data retention, privacy compliance | TBD |
| Cloud Engineering Lead | TBD | Platform build and automation, infrastructure-as-code, CI/CD pipeline management | TBD |
| DevOps Lead | TBD | Release management, deployment automation, environment configuration, rollback procedures | TBD |
| Network Architect | TBD | Network design, VNet peering, routing, DNS configuration, ExpressRoute setup | TBD |
| Database Administrator | TBD | Snowflake and PostgreSQL configuration, backup/restore, performance tuning | TBD |

**Communication Plan:**
- Weekly status meetings: Every Monday 10:00 AM
- Architecture review board: Bi-weekly Thursdays 2:00 PM
- Incident escalation: 24x7 on-call rotation via PagerDuty
- Documentation repository: Confluence space or SharePoint site (TBD)

# 2. Solution Overview

This document describes a comprehensive Azure-based microservices platform designed to serve both external customers and internal users with high availability, security, and performance. The solution leverages Azure's PaaS and managed services to minimize operational overhead while maximizing scalability and resilience.

**Business Context:**
The platform supports mission-critical applications requiring global reach, low latency, and enterprise-grade security. External traffic originates from customers worldwide and is protected by Akamai's edge services before entering Azure through Front Door. Internal users access the same services through private, secure channels optimized for corporate network routing.

**Architecture Overview:**
- **Edge Layer**: Akamai → Azure Front Door → Azure Static Web App (static content) or Application Gateway (API traffic)
- **API Gateway Layer**: Azure API Management enforces policies, throttling, authentication, and monitoring
- **Ingress Layer**: Nginx ingress controller in AKS provides L7 routing and SSL termination
- **Application Layer**: Spring Cloud Gateway routes requests to microservices deployed in AKS
- **Data Layer**: Snowflake (analytics/warehouse) and PostgreSQL (transactional) databases
- **Security Layer**: Azure Key Vault for secrets, managed identities for authentication, private endpoints for data services

**Key Benefits:**
- **Scalability**: Automatic horizontal scaling across all layers based on demand
- **Security**: Defense-in-depth with WAF, network segmentation, encryption, and zero-trust principles
- **Observability**: Centralized logging and monitoring with actionable alerts and dashboards
- **Cost Optimization**: Reserved capacity, autoscaling, and tag-based cost allocation
- **Reliability**: Multi-region deployment with automated failover and data replication

## 2.1. Success Criteria

**Availability & Reliability:**
- System Availability: 99.95% uptime (SLA target, measured monthly)
- API Success Rate: 99.9% of requests return 2xx or expected error codes
- Zero data loss during failover scenarios
- Maximum of 2 critical incidents per quarter

**Performance:**
- P50 API latency: < 150 ms (edge to response)
- P95 API latency: < 300 ms (edge to response)
- P99 API latency: < 500 ms (edge to response)
- Static content delivery: < 50 ms for cached resources globally
- Database query response time: P95 < 200 ms for transactional queries
- Time to first byte (TTFB): < 100 ms for cached content

**Scalability:**
- Support 10,000+ concurrent users without degradation
- Automatic horizontal scaling responds within 3 minutes to load spikes
- Handle 5x normal traffic during peak events
- Scale from baseline to peak capacity within 5 minutes

**Security:**
- Zero critical vulnerabilities at production deployment
- All data encrypted in transit (TLS 1.2+) and at rest
- Security scan results: No high/critical findings in production
- Incident response time: < 15 minutes for critical security events
- Successful penetration test completion before go-live

**Observability:**
- 100% of services emit structured logs to centralized Log Analytics
- Real-time dashboards for golden signals (latency, traffic, errors, saturation)
- Alert response time: < 5 minutes for critical alerts
- Log retention: 90 days in hot storage, 1 year in cold storage

**Cost Efficiency:**
- Monthly spend variance: Within ±10% of approved budget
- Cost per transaction tracked and optimized quarterly
- Reserved instance utilization: > 80% of predictable workloads
- Tag compliance: 100% of resources tagged per policy

**Operational Readiness:**
- Runbooks documented for top 10 incident scenarios
- Mean time to detect (MTTD): < 5 minutes
- Mean time to resolve (MTTR): < 2 hours for P1 incidents
- Post-incident reviews completed within 5 business days

## 2.2. Assumptions

**Infrastructure & Platform:**
- Azure regions deployed: Primary (East US 2), Secondary (West US 2) for multi-region resiliency
- Azure subscription limits are sufficient or can be increased via support requests
- AKS uses Azure CNI networking with private cluster endpoints enabled
- Kubernetes version: 1.28+ with support for at least 18 months
- Node pools use VM scale sets with availability zones for high availability
- Managed identities are the primary authentication mechanism for Azure resources

**Network & Connectivity:**
- Akamai configuration and WAF policies are managed by the CDN team (external to Azure scope)
- Akamai-to-Azure connectivity is established and tested before deployment
- Corporate network connectivity to Azure via ExpressRoute or Site-to-Site VPN (if required)
- DNS delegation for public and private zones is approved and configured
- Network bandwidth is sufficient for expected traffic volumes

**Security & Compliance:**
- Azure AD (Entra ID) is the identity provider for authentication and authorization
- Compliance frameworks required: SOC 2 Type II, ISO 27001, GDPR (to be confirmed)
- Security baseline follows CIS Azure Foundations Benchmark
- Vulnerability scanning is integrated into CI/CD pipelines
- Penetration testing is scheduled and approved for pre-production environments

**Data Management:**
- Snowflake account is provisioned in the same Azure region as primary AKS cluster
- PostgreSQL uses Azure Database for PostgreSQL Flexible Server with HA enabled
- Data retention policies: Transactional data (7 years), Log data (1 year), Backup data (30 days)
- Data residency requirements allow storage in selected Azure regions
- Database connection pooling is handled by application layer

**Application & Development:**
- Microservices follow 12-factor app principles
- Applications are containerized and publish health/readiness endpoints
- Spring Cloud Gateway configuration is managed via GitOps
- API versioning strategy is defined and followed (e.g., URI versioning, header versioning)
- Circuit breakers and retry logic implemented for resilience

**Operations & Support:**
- CI/CD pipelines use Azure DevOps, GitHub Actions, or Jenkins (to be confirmed)
- Infrastructure-as-Code using Terraform or Bicep with version control
- GitOps approach for Kubernetes manifests using Flux or ArgoCD
- 24x7 support coverage with defined SLAs for incident response
- Change management process follows enterprise ITIL practices

**Cost & Budget:**
- Initial budget approved for 12-month operational period
- Cost allocation by environment (dev: 10%, test: 15%, prod: 75%)
- Reserved instances purchased for predictable workloads (APIM, App Gateway, AKS baseline)
- Monthly cost reviews scheduled with finance and engineering teams

**Timeline & Resources:**
- Adequate staffing for build, test, and deployment phases
- Subject matter experts available for Snowflake, AKS, and Spring Cloud Gateway
- Training provided for operations team on new Azure services
- Business stakeholders available for UAT and sign-off

## 2.3. Project Timeline

**Phase 1: Discovery & Planning (Weeks 1-3)**
- Requirements gathering and stakeholder workshops: Week 1
- Architecture design and service selection: Week 2
- Security and compliance review: Week 3
- Architecture sign-off and approval: End of Week 3

**Phase 2: Environment Setup (Weeks 4-6)**
- Azure subscription and network infrastructure setup: Week 4
- Hub-and-spoke VNet topology deployment: Week 4-5
- Private DNS zones and connectivity validation: Week 5
- Identity and RBAC configuration: Week 6
- CI/CD pipeline foundation: Week 6

**Phase 3: Platform Build (Weeks 7-12)**
- Azure Front Door and Static Web App deployment: Week 7
- Application Gateway and WAF configuration: Week 8
- API Management deployment and policy configuration: Week 9
- AKS cluster deployment with Nginx ingress: Week 10
- Key Vault, Storage, and private endpoints: Week 11
- Database provisioning (Snowflake and PostgreSQL): Week 12

**Phase 4: Application Integration (Weeks 13-16)**
- Spring Cloud Gateway deployment and routing configuration: Week 13
- Microservices deployment to AKS: Week 13-14
- Database schema migration and seeding: Week 14
- Service-to-service authentication and authorization: Week 15
- End-to-end integration testing: Week 16

**Phase 5: Observability & Operations (Weeks 17-18)**
- Azure Monitor and Log Analytics configuration: Week 17
- Dashboard and alert rule creation: Week 17
- Runbook development and documentation: Week 18
- Operations team training and handoff: Week 18

**Phase 6: Testing & Validation (Weeks 19-22)**
- Functional testing and bug fixes: Week 19
- Performance and load testing: Week 20
- Security testing and vulnerability remediation: Week 21
- User acceptance testing (UAT): Week 22

**Phase 7: Pre-Production (Weeks 23-24)**
- Production environment deployment: Week 23
- DR testing and failover validation: Week 23
- Production readiness review: Week 24
- Go/No-Go decision: End of Week 24

**Phase 8: Production Launch (Week 25+)**
- Production cutover and traffic migration: Week 25
- Hypercare period (24x7 monitoring): Weeks 25-28
- Post-launch review and optimization: Week 29

**Key Milestones:**
- Architecture approval: End of Week 3
- Dev environment ready: End of Week 8
- Integration complete: End of Week 16
- UAT sign-off: End of Week 22
- Production go-live: Week 25

## 2.4. Application Git Repository

**Repository Structure:**
- Infrastructure Repository: `https://github.com/organization/azure-infrastructure` (or TBD)
- Application Microservices: `https://github.com/organization/app-microservices` (or TBD)
- Configuration Repository: `https://github.com/organization/app-config` (or TBD)
- Documentation: `https://github.com/organization/azure-docs` (or TBD)

**Branching Strategy:**
- **Main Branch**: Production-ready code, protected with required reviews
- **Develop Branch**: Integration branch for features
- **Feature Branches**: `feature/JIRA-XXX-description` - individual features
- **Release Branches**: `release/v1.2.3` - release preparation and testing
- **Hotfix Branches**: `hotfix/v1.2.4` - critical production fixes

**Branch Protection Rules:**
- Require pull request reviews (minimum 2 approvers)
- Require status checks to pass (build, test, security scan)
- Require branches to be up to date before merging
- Require signed commits
- Include administrators in restrictions

**Release Strategy:**
- **Versioning**: Semantic versioning (MAJOR.MINOR.PATCH)
  - MAJOR: Breaking changes
  - MINOR: New features (backward compatible)
  - PATCH: Bug fixes
- **Release Cadence**: Bi-weekly releases to production (or as required)
- **Release Tags**: Annotated Git tags for each release
- **Release Notes**: Auto-generated from commit messages and PR descriptions

**CI/CD Integration:**
- Feature branch: Build and unit tests
- Develop branch: Build, test, and deploy to dev environment
- Release branch: Deploy to test/staging environments
- Main branch: Deploy to production with approval gates

**Code Review Requirements:**
- Mandatory peer review for all code changes
- Security review for changes to authentication, authorization, or data handling
- Architecture review for significant design changes
- Automated code quality checks (linting, code coverage > 80%)

# 3. Azure Solution Architecture
The solution uses edge routing, centralized API management, and a Kubernetes-based runtime for microservices. It follows a layered ingress design to separate external and internal access, enforce security policies, and provide consistent observability.

## 3.1  Solution Diagram

**High-Level Architecture Flow:**

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                              EXTERNAL USERS                                  │
│                           (Internet / Mobile)                                │
└────────────────────────────────┬─────────────────────────────────────────────┘
                                 │
                    ┌────────────▼──────────────┐
                    │   Akamai CDN & WAF        │
                    │   - DDoS Protection       │
                    │   - SSL/TLS Offload       │
                    │   - Edge Caching          │
                    └────────────┬──────────────┘
                                 │
                    ┌────────────▼──────────────┐
                    │   Azure Front Door        │
                    │   - Premium Tier          │
                    │   - Global Load Balancer  │
                    │   - WAF Policies          │
                    │   - CDN Caching           │
                    └──────┬───────────┬────────┘
                           │           │
          ┌────────────────┘           └──────────────────┐
          │ Static Content                      API Calls │
          ▼                                               ▼
┌─────────────────────┐                    ┌──────────────────────────┐
│ Azure Static Web App│                    │ Azure Application Gateway│
│ - React/Angular SPA │                    │ - WAF v2                 │
│ - Global CDN        │                    │ - SSL Termination        │
│ - Custom Domain     │                    │ - URL Routing            │
└─────────────────────┘                    └──────────┬───────────────┘
                                                      │
                ┌─────────────────────────────────────┘
                │                    ┌─────────────────────────────────┐
                │                    │   INTERNAL USERS                │
                │                    │   (Corporate Network / VPN)     │
                │                    └────────────┬────────────────────┘
                │                                 │
                │                    ┌────────────▼──────────────┐
                │                    │   Azure Application       │
                │                    │   Gateway (Internal)      │
                │                    └────────────┬──────────────┘
                │                                 │
                └─────────────┬───────────────────┘
                              │
                    ┌─────────▼──────────-┐
                    │ Azure API Management│
                    │ - Internal VNet     │
                    │ - Policy Enforcement│
                    │ - OAuth2/JWT        │
                    │ - Rate Limiting     │
                    │ - Monitoring        │
                    └─────────┬──────────-┘
                              │
                              │
                    ┌─────────▼──────────┐
                    │ Azure Kubernetes   │
                    │ Service (AKS)      │
                    │ ┌────────────────┐ │
                    │ │ Nginx Ingress  │ │
                    │ │ Controller     │ │
                    │ └────────┬───────┘ │
                    │          │         │
                    │ ┌────────▼───────┐ │
                    │ │ Spring Cloud   │ │
                    │ │ Gateway        │ │
                    │ └────────┬───────┘ │
                    │          │         │
                    │ ┌────────▼───────┐ │
                    │ │ Microservices  │ │
                    │ │ - Service A    │ │
                    │ │ - Service B    │ │
                    │ │ - Service C    │ │
                    │ └────────┬───────┘ │
                    └──────────┼─────────┘
                               │
        ┌──────────────────────┼──────────────────────┐
        │                      │                      │
┌───────▼────────┐    ┌────────▼────────┐   ┌────────▼─────────┐
│ Snowflake DB   │    │ PostgreSQL      │   │ Azure Storage    │
│ - Native       │    │ - Flexible      │   │ - Blob (backups) │
│ - Data Warehouse    │ - HA Enabled    │   │ - Files (logs)   │
└────────────────┘    └─────────────────┘   └──────────────────┘

┌────────────────────────────────────────────────────────────────┐
│                    CROSS-CUTTING SERVICES                      │
├────────────────────────────────────────────────────────────────┤
│ - Azure Key Vault: Secrets, Keys, Certificates                 │
│ - Azure Monitor: Metrics, Logs, Alerts                         │
│ - Azure Log Analytics: Centralized Logging                     │
│ - Azure AD (Entra ID): Identity & Access Management            │
│ - Azure Firewall: Egress Control                               │
│ - Azure Private DNS: Name Resolution                           │
└────────────────────────────────────────────────────────────────┘
```

**Component Details:**

1. **Akamai (External)**: Edge CDN and DDoS protection before traffic enters Azure
2. **Azure Front Door Premium**: Global entry point with intelligent routing and WAF
3. **Azure Static Web App**: Hosts static frontend assets with integrated CDN
4. **Azure Application Gateway**: L7 load balancer with WAF for API traffic
5. **Azure API Management**: API gateway for policy enforcement and monitoring
6. **AKS + Nginx**: Container orchestration with ingress controller
7. **Spring Cloud Gateway**: Microservice routing and API composition
8. **Microservices**: Business logic containers
9. **Databases**: Snowflake (analytics) and PostgreSQL (transactional)
10. **Supporting Services**: Key Vault, Monitor, Storage, AD, Firewall

## 3.2  Deployment Pattern / Isolation Zone Pattern

**Hub-and-Spoke Topology:**

The solution implements a hub-and-spoke network architecture following Azure best practices for enterprise-scale deployments:

**Hub VNet (Shared Services):**
- **Address Space**: 10.0.0.0/24
- **Subnets**:
  - GatewaySubnet: 10.0.0.0/27 (VPN/ExpressRoute Gateway)
  - AzureFirewallSubnet: 10.0.0.32/27 (Azure Firewall)
  - ManagementSubnet: 10.0.0.64/27 (Jump boxes, management tools)
  - SharedServicesSubnet: 10.0.0.96/27 (DNS, monitoring agents)
- **Services**: Azure Firewall, Azure Bastion, VPN Gateway (optional), Log Analytics

**Spoke 1 - Edge Services VNet:**
- **Address Space**: 10.1.0.0/24
- **Subnets**:
  - ApplicationGatewaySubnet: 10.1.0.0/27 (Application Gateway with WAF)
  - APIMSubnet: 10.1.0.32/27 (API Management - Internal mode)
  - PrivateEndpointSubnet: 10.1.0.64/27 (Private endpoints for PaaS)
- **Peering**: Connected to Hub VNet with use remote gateway enabled

**Spoke 2 - Application VNet:**
- **Address Space**: 10.2.0.0/24
- **Subnets**:
  - AKSSystemSubnet: 10.2.0.0/27 (AKS system node pool - 32 IPs)
  - AKSUserSubnet: 10.2.0.32/27 (AKS user node pool - 32 IPs)
  - AKSPodsSubnet: 10.2.0.64/26 (Pod IP space for Azure CNI - 64 IPs)
  - IngressSubnet: 10.2.0.128/26 (Load balancer IPs)
- **Peering**: Connected to Hub VNet and Spoke 1 VNet

**Spoke 3 - Data Services VNet:**
- **Address Space**: 10.3.0.0/24
- **Subnets**:
  - DatabaseSubnet: 10.3.0.0/27 (PostgreSQL private endpoint)
  - SnowflakeSubnet: 10.3.0.32/27 (Snowflake private connectivity)
  - StorageSubnet: 10.3.0.64/27 (Storage account private endpoints)
  - BackupSubnet: 10.3.0.96/27 (Backup infrastructure)
- **Peering**: Connected to Hub VNet with restricted access

**Environment Isolation:**
- **Development**: Separate resource group within same subscription
- **Test/Staging**: Separate resource group or subscription
- **Production**: Dedicated subscription with production policies

**Network Segmentation Principles:**
- East-west traffic controlled via Network Security Groups (NSGs)
- North-south traffic routed through Azure Firewall in hub
- Private endpoints eliminate public internet exposure for PaaS services
- Service endpoints disabled in favor of private endpoints
- UDRs force specific traffic through firewall for inspection

## 3.3  Design Decisions

**1. Azure Front Door Premium**
- **Decision**: Use Azure Front Door Premium as the global entry point for external traffic
- **Rationale**: 
  - Provides global load balancing with intelligent traffic routing
  - Integrated Microsoft-managed WAF with OWASP rule sets
  - SSL/TLS offload at the edge reduces latency
  - Caching at 100+ Microsoft edge locations worldwide
  - Seamless integration with Azure services
- **Alternatives Considered**: 
  - Azure Traffic Manager (lacks WAF and edge caching)
  - Third-party CDN (additional management overhead)
- **Trade-offs**: Higher cost but superior performance and security

**2. Azure Static Web App**
- **Decision**: Host static frontend content (HTML, CSS, JS, images) in Azure Static Web App
- **Rationale**:
  - Built-in global CDN with automatic cache invalidation
  - Integrated GitHub Actions for CI/CD
  - Custom domain and SSL certificate management
  - Serverless architecture with zero infrastructure management
  - Cost-effective for static content delivery
- **Alternatives Considered**:
  - Azure Storage Static Website (fewer features)
  - VM-based web servers (operational overhead)
- **Trade-offs**: Limited to static content only

**3. Azure Application Gateway v2 with WAF**
- **Decision**: Use Application Gateway v2 as L7 load balancer for API traffic
- **Rationale**:
  - Web Application Firewall protects against OWASP Top 10 vulnerabilities
  - URL-based routing to different backend pools
  - SSL termination and re-encryption to backends
  - Autoscaling based on traffic patterns
  - Zone redundancy for high availability
  - Supports both external and internal listeners for dual traffic flows
- **Alternatives Considered**:
  - Azure Load Balancer (L4 only, no WAF)
  - Direct exposure of APIM (security concern)
- **Trade-offs**: Additional hop adds ~10-20ms latency but provides essential security

**4. Azure API Management (Internal VNet Mode)**
- **Decision**: Deploy APIM in internal VNet mode as the API gateway
- **Rationale**:
  - Centralized API governance and policy enforcement
  - Built-in authentication (OAuth2, JWT validation)
  - Rate limiting and quota management per subscription
  - Request/response transformation capabilities
  - Developer portal for API documentation
  - Detailed analytics and monitoring
  - Internal mode prevents direct internet exposure
- **Alternatives Considered**:
  - Kong or Nginx API Gateway (more operational overhead)
  - Direct access to AKS (no centralized policy enforcement)
- **Trade-offs**: Cost and complexity but provides enterprise API management capabilities

**5. Azure Kubernetes Service (AKS) with Azure CNI**
- **Decision**: Use AKS with Azure CNI networking for microservices runtime
- **Rationale**:
  - Fully managed Kubernetes reduces operational overhead
  - Azure CNI provides pod-level IP addressing for better network integration
  - Native integration with Azure Monitor, Key Vault, and Azure AD
  - Auto-scaling (cluster autoscaler and HPA)
  - Availability zones support for HA
  - Supports Windows and Linux workloads
  - Private cluster mode for secure API server access
- **Alternatives Considered**:
  - Azure Container Apps (less control, newer service)
  - Self-managed Kubernetes (high operational overhead)
  - Azure Container Instances (not suitable for complex orchestration)
- **Trade-offs**: Azure CNI requires larger IP address space but provides better performance

**6. Nginx Ingress Controller**
- **Decision**: Deploy Nginx ingress controller in AKS for internal routing
- **Rationale**:
  - Industry-standard ingress controller with broad community support
  - SSL/TLS termination at ingress layer
  - Path-based and host-based routing
  - Rate limiting and authentication at ingress level
  - Integration with cert-manager for certificate automation
- **Alternatives Considered**:
  - Azure Application Gateway Ingress Controller (tightly coupled to App Gateway)
  - Traefik (less mature in enterprise)
- **Trade-offs**: Requires separate deployment and management within cluster

**7. Spring Cloud Gateway**
- **Decision**: Use Spring Cloud Gateway as the microservice router
- **Rationale**:
  - Native integration with Spring Boot microservices
  - Dynamic routing based on service discovery
  - Circuit breaker and retry patterns
  - Request rate limiting per service
  - Filter chains for request/response transformation
  - Supports reactive programming model
- **Alternatives Considered**:
  - Service mesh (Istio/Linkerd) - more complex for current requirements
  - Direct service-to-service calls (no centralized routing)
- **Trade-offs**: Additional layer but provides essential microservice patterns

**8. Azure Key Vault**
- **Decision**: Use Azure Key Vault for secrets, keys, and certificate management
- **Rationale**:
  - Centralized secrets management with RBAC
  - Hardware Security Module (HSM) backed keys (Premium tier)
  - Automatic secret rotation capabilities
  - Integration with AKS via CSI driver or Pod Identity
  - Audit logging for all access
  - FIPS 140-2 Level 2 validated HSMs
- **Alternatives Considered**:
  - Kubernetes Secrets (not encrypted at rest by default)
  - HashiCorp Vault (additional operational overhead)
- **Trade-offs**: Network latency for secret retrieval but superior security

**9. Azure Storage Account**
- **Decision**: Use Azure Storage for logs, backups, and static assets
- **Rationale**:
  - Highly durable (LRS/ZRS/GRS options)
  - Blob lifecycle management for cost optimization
  - Soft delete and versioning for data protection
  - Private endpoint support
  - Integration with Azure Monitor for diagnostics
- **Alternatives Considered**:
  - Third-party storage (S3-compatible) - less integrated
  - File shares on VMs (operational overhead)
- **Trade-offs**: N/A - best fit for requirements

**10. Snowflake (Data Warehouse) + PostgreSQL (Transactional)**
- **Decision**: Use Snowflake for analytics/warehouse and Azure PostgreSQL for transactional workloads
- **Rationale**:
  - **Snowflake**: Best-in-class data warehouse with separation of compute and storage, automatic scaling, native Azure integration
  - **PostgreSQL**: ACID-compliant relational database for transactional workloads, managed service with HA, automated backups
  - Clear separation of concerns (OLAP vs OLTP)
- **Alternatives Considered**:
  - Single database (not optimal for mixed workloads)
  - Azure Synapse (considered but Snowflake preferred by data team)
- **Trade-offs**: Two database systems increase complexity but optimize for use case

## 3.4 Technical Assumptions
- TLS 1.2+ is enforced end-to-end.
- API Management is deployed in internal VNet mode for private routing to AKS.
- AKS uses managed identities for Azure resource access.
- CI/CD automates deployment to dev, test, and prod environments.
- Nginx is configured as the AKS ingress controller for routing to Spring Cloud Gateway.
- Service-to-service communication uses mTLS where required (TBD).

## 3.5  Security Considerations
Security is enforced at edge, network, identity, and data layers with least privilege, segmentation, and encryption.

### 3.5.1  Network Security
- WAF enabled on Front Door and Application Gateway.
- NSGs restrict inbound/outbound traffic by subnet.
- Private endpoints for Key Vault and Storage.
- AKS API server private endpoint with authorized IP ranges.
- DDoS Protection Standard enabled at the VNet level.

### 3.5.2  Data Security
- Data encryption at rest for Snowflake, PostgreSQL, and Storage.
- TLS in transit between services, including APIM to AKS.
- Key Vault for key and secret rotation.
- Data classification and masking enforced in Snowflake and PostgreSQL where required.

### 3.5.3  Identity and Access Management
- Entra ID (Azure AD) for user and service identities.
- Managed identities for AKS and APIM.
- RBAC at subscription, resource group, and AKS namespace levels.
- Privileged access managed via PIM (TBD).

## 3.6  Scalability and Performance
- Autoscale AKS nodes and pods based on CPU/memory and custom metrics.
- Front Door and SWA scale globally by design.
- APIM and Application Gateway scale units based on throughput.
- Caching at Front Door and SWA to reduce origin load.
- Read/write workload separation for databases where required (TBD).

## 3.7 Naming Standards
- Format: `{env}-{region}-{app}-{resource}`
- Example: `prod-eastus-appgw-core`
- Naming applies to resource groups, VNets, subnets, and core services.

## 3.8 Azure Tagging
- `Environment`: dev/test/prod
- `Application`: app name
- `Owner`: team or business unit
- `CostCenter`: finance code
- `Compliance`: data classification
- `Criticality`: low/medium/high

## 3.9 Virtual Machine Instances & IaaS Services
- No standalone VMs required; AKS node pools are managed.
- Any VM-based dependencies must follow hardened images and patching policies.

## 3.10 User Defined Routings
- UDRs route AKS egress through Azure Firewall or NAT Gateway.
- Separate routes for private endpoints and on-prem connectivity.
- Route tables managed per environment to prevent cross-environment access.

## 3.11 Azure Monitor
- Azure Monitor and Log Analytics for metrics, logs, and alerts.
- Container Insights for AKS.
- Alerts for latency, error rates, and resource saturation.
- Synthetic availability tests for public endpoints (TBD).

## 3.12 Cost Management
- Budgets per environment and service.
- Reserved capacity where predictable (e.g., APIM, App Gateway).
- Regular cost reviews with tagging compliance.
- Cost allocation via tags and subscriptions.

## 3.13 Azure Logging
- Centralized logging to Log Analytics.
- Diagnostic settings enabled on Front Door, App Gateway, APIM, AKS, Key Vault.
- Retention policy based on compliance requirements.
- Log export to Storage for long-term retention (TBD).

## 3.14 Backups
- PostgreSQL backups via managed backup policy.
- Snowflake time travel and fail-safe as per enterprise policy.
- Azure Storage soft delete and versioning enabled.
- Restore testing scheduled quarterly (TBD).

## 3.15 Azure Policies
- Enforce tagging, private endpoints, and approved SKUs.
- Restrict public IP usage outside approved gateways.
- Enforce TLS 1.2+ and deny legacy cipher suites.

## 3.16 Resilience and Disaster Recovery
- Multi-region Front Door routing for failover.
- Active-active AKS clusters per region or active-passive based on RTO.
- Data replication for PostgreSQL and Snowflake cross-region replication as required.
- DR runbooks and failover tests scheduled twice yearly (TBD).

## 3.17 RTO and RPO

**Recovery Time Objective (RTO):**
- **Target**: 2 hours for complete service restoration
- **Breakdown by Component**:
  - Azure Front Door: < 5 minutes (multi-region by design)
  - Static Web App: < 5 minutes (global CDN with automatic failover)
  - Application Gateway: < 15 minutes (redeploy to secondary region)
  - API Management: < 30 minutes (traffic switch to standby instance)
  - AKS Cluster: < 60 minutes (activate standby cluster or scale new)
  - Databases: < 30 minutes (failover to replica)
  - Overall RTO: 2 hours (includes validation and smoke testing)

**Recovery Point Objective (RPO):**
- **Target**: 15 minutes maximum data loss
- **Breakdown by Data Type**:
  - Transactional data (PostgreSQL): 5 minutes (continuous replication to read replica)
  - Analytical data (Snowflake): 15 minutes (Snowflake replication)
  - Application logs: 1 minute (Log Analytics ingestion)
  - Configuration data: 0 minutes (stored in Git, no data loss)
  - User-uploaded files: 15 minutes (geo-redundant storage with async replication)

**Disaster Recovery Strategy:**

**Active-Passive Multi-Region Setup:**
- **Primary Region**: East US 2 (active)
- **Secondary Region**: West US 2 (standby)
- **Failover Trigger**: Manual or automated based on health checks

**Component-Level DR:**

1. **Azure Front Door**
   - Configured with backend pools in both regions
   - Automatic health probe-based routing
   - Priority-based routing: Primary region (Priority 1), Secondary (Priority 2)
   - Failover time: < 1 minute (automatic)

2. **Azure Static Web App**
   - Deployed identically to both regions
   - Front Door routes traffic based on health
   - Deployment via CI/CD ensures consistency
   - Failover time: Automatic with Front Door

3. **Application Gateway**
   - Standby instance in secondary region
   - Updated via IaC (Terraform/Bicep)
   - DNS or Front Door switch for failover
   - Failover time: 10-15 minutes

4. **API Management**
   - Multi-region deployment with shared configuration
   - Backup/restore of APIM configuration stored in Git
   - Custom domain configured for both regions
   - Failover time: 20-30 minutes (DNS update or traffic manager switch)

5. **AKS Cluster**
   - **Option A (Recommended)**: Active-Passive with standby cluster
     - Standby cluster with minimal node pool running
     - Scale up on failover
     - Container images in shared Azure Container Registry with geo-replication
     - Configuration synced via GitOps
   - **Option B**: Deploy new cluster on failover (longer RTO)
   - Failover time: 30-60 minutes

6. **Databases**
   - **PostgreSQL**: 
     - Primary with read replica in secondary region
     - Automatic failover using Flexible Server HA
     - RPO: < 5 minutes
     - RTO: < 15 minutes
   - **Snowflake**:
     - Multi-cluster architecture with replication
     - Automated failover or manual switch
     - RPO: 15 minutes
     - RTO: 15-30 minutes

7. **Storage Accounts**
   - Geo-Redundant Storage (GRS) with read access (RA-GRS)
   - Automatic replication to secondary region
   - Read-only access during primary region outage
   - Manual failover for write access
   - RPO: < 15 minutes

**Failover Testing Schedule:**
- Quarterly DR drills (4 times per year)
- Annual full failover test with simulated outage
- Tabletop exercises for incident response team
- Post-test review and runbook updates

**Automated Health Monitoring:**
- Health probes every 30 seconds for critical endpoints
- Synthetic transactions for end-to-end validation
- Alert triggers for automated failover consideration
- Manual approval gate for production failover

**Data Backup Strategy:**
- **PostgreSQL**: Automated daily backups with 30-day retention, point-in-time restore
- **Snowflake**: Time Travel (90 days), Fail-safe (7 days)
- **Configuration**: Stored in Git with version history
- **Secrets**: Key Vault soft delete (90 days) and backup

**Failback Procedure:**
- Validate primary region recovery
- Restore data consistency between regions
- Sync any changes made in secondary region
- Gradual traffic shift back to primary (canary approach)
- Post-failback validation and monitoring

# 4. Isolation Zone Networking
Isolation zones separate edge, application, and data tiers with controlled ingress/egress.

## 4.1 Isolation Zone Networking Architecture

**Network Architecture Philosophy:**
The isolation zone architecture implements defense-in-depth security principles with multiple layers of network segmentation, access control, and traffic inspection. Each zone is isolated by VNet boundaries, NSGs, and routing policies.

**Hub VNet - Shared Services (10.0.0.0/24):**

The hub serves as the central point for shared networking and security services.

| Subnet Name | CIDR | Purpose | Key Resources |
|-------------|------|---------|---------------|
| GatewaySubnet | 10.0.0.0/27 | VPN/ExpressRoute Gateway | VPN Gateway (optional) |
| AzureFirewallSubnet | 10.0.0.32/27 | Azure Firewall | Azure Firewall Premium |
| AzureBastionSubnet | 10.0.0.64/27 | Azure Bastion | Secure VM access |
| ManagementSubnet | 10.0.0.96/27 | Jump boxes, DevOps agents | Management VMs |
| SharedServicesSubnet | 10.0.0.128/27 | Monitoring, DNS forwarders | Log Analytics agents |
| FirewallManagementSubnet | 10.0.0.160/27 | Firewall management | Firewall management IP |

**Spoke 1 - Edge Services VNet (10.1.0.0/24):**

Edge services handle inbound traffic routing and API management.

| Subnet Name | CIDR | Purpose | Key Resources | NSG Rules |
|-------------|------|---------|---------------|-----------|
| ApplicationGatewaySubnet | 10.1.0.0/27 | App Gateway | WAF_v2 instances | Allow 443, 80 inbound; Allow GatewayManager |
| APIMSubnet | 10.1.0.32/27 | API Management | APIM internal mode | Allow 443 from App Gateway; Allow 3443 for management |
| PrivateEndpointSubnet | 10.1.0.64/27 | Private endpoints | Key Vault, Storage PE | Allow specific ports from application subnets |
| FrontDoorPrivateEndpoint | 10.1.0.96/27 | Front Door PE | Front Door origin | Allow Front Door service tag |

**Spoke 2 - Application VNet (10.2.0.0/24):**

Application runtime hosting Kubernetes workloads.

| Subnet Name | CIDR | IPs Available | Purpose | Key Resources |
|-------------|------|---------------|---------|---------------|
| AKSSystemSubnet | 10.2.0.0/27 | 32 | System node pools | Critical system pods |
| AKSUserSubnet | 10.2.0.32/27 | 32 | User workload nodes | Application pods |
| AKSPodsSubnet | 10.2.0.64/26 | 64 | Pod IPs (CNI) | Direct pod IPs |
| IngressSubnet | 10.2.0.128/26 | 64 | Load balancer IPs | Nginx ingress controller LB |
| AKSManagementSubnet | 10.2.0.192/26 | 64 | AKS management | Private endpoint for K8s API |

**IP Allocation Calculation (Azure CNI):**
- Nodes: 5 max nodes per node pool (reduced for /24)
- Pods per node: 10 (reduced from default)
- Total IPs needed: 5 nodes × 10 pods = 50 IPs per node pool
- Recommendation: /27 provides 32 IPs, /26 provides 64 IPs (sufficient for smaller deployments)

**Spoke 3 - Data Services VNet (10.3.0.0/24):**

Data tier with database and storage services.

| Subnet Name | CIDR | Purpose | Key Resources | Access Control |
|-------------|------|---------|---------------|----------------|
| DatabaseSubnet | 10.3.0.0/27 | Database instances | PostgreSQL PE | Only from AKS pods |
| SnowflakeSubnet | 10.3.0.32/27 | Snowflake connectivity | Private Link | Only from AKS and APIM |
| StorageSubnet | 10.3.0.64/27 | Storage accounts | Blob, File PE | Read/write from authorized services |
| BackupSubnet | 10.3.0.96/27 | Backup infrastructure | Backup vault | Isolated backup network |

**VNet Peering Configuration:**

| Peering | Direction | Settings |
|---------|-----------|----------|
| Hub ↔ Spoke 1 | Bidirectional | Use remote gateway (Hub), Allow forwarded traffic |
| Hub ↔ Spoke 2 | Bidirectional | Use remote gateway (Hub), Allow forwarded traffic |
| Hub ↔ Spoke 3 | Bidirectional | Use remote gateway (Hub), Allow forwarded traffic |
| Spoke 1 ↔ Spoke 2 | Bidirectional | Allow peering, Use Hub as transit |
| Spoke 2 ↔ Spoke 3 | Bidirectional | Allow peering, Use Hub as transit |

**Routing Architecture:**

**Default Routes (via UDR):**
- 0.0.0.0/0 → Azure Firewall (10.0.0.36) for internet egress
- 10.0.0.0/8 → VNet local (internal traffic)
- On-premises network → VPN Gateway (if configured)

**Route Tables:**

| Route Table | Applied To | Routes |
|-------------|------------|--------|
| RT-Spoke1-AppGW | ApplicationGatewaySubnet | Default to Firewall, exception for health probes |
| RT-Spoke1-APIM | APIMSubnet | Default to Firewall, AKS subnet direct |
| RT-Spoke2-AKS | AKS subnets | Default to Firewall, internal subnets direct |
| RT-Spoke3-Data | Data subnets | Default to Firewall, deny internet egress |

**Traffic Flow Paths:**

**External User → Static Content:**
```
Internet → Akamai → Front Door → Static Web App (global)
```

**External User → API:**
```
Internet → Akamai → Front Door → App Gateway (10.1.0.0/27) 
→ APIM (10.1.0.32/27) → AKS Ingress (10.2.0.128/26) 
→ Spring Cloud Gateway (pod) → Microservice (pod)
```

**Internal User → API:**
```
Corporate Network → ExpressRoute/VPN → App Gateway Internal Listener (10.1.0.0/27)
→ APIM (10.1.0.32/27) → AKS Ingress (10.2.0.128/26) 
→ Spring Cloud Gateway (pod) → Microservice (pod)
```

**Microservice → Database:**
```
Pod (10.2.0.64/26) → Private Endpoint (10.3.0.0/27) → PostgreSQL
Pod (10.2.0.64/26) → Private Endpoint (10.3.0.32/27) → Snowflake
```

**Egress to Internet (e.g., external API calls):**
```
Pod → AKS subnet → UDR → Azure Firewall (10.0.0.36) → Internet
```

**Network Security Zones:**

| Zone | Security Level | Ingress Allowed From | Egress Allowed To |
|------|----------------|----------------------|-------------------|
| Public (Front Door) | High | Internet | App Gateway only |
| DMZ (App Gateway) | High | Front Door, Corporate | APIM only |
| Application (APIM) | Medium | App Gateway | AKS only |
| Compute (AKS) | Medium | APIM | Databases, Firewall |
| Data (Databases) | High | AKS only | None (no egress) |

**Zero Trust Principles Applied:**
- No implicit trust between zones
- Verify explicitly at each boundary
- Least-privilege access enforcement
- Assume breach and minimize blast radius

## 4.2 Isolation Zone Networking Components

**Network Security Groups (NSGs):**

NSGs provide Layer 4 traffic filtering for subnets and network interfaces. All rules follow least-privilege principles.

**NSG-ApplicationGateway:**
Applied to: ApplicationGatewaySubnet (10.1.0.0/27)

| Priority | Name | Direction | Source | Destination | Port | Action | Purpose |
|----------|------|-----------|--------|-------------|------|--------|---------|
| 100 | Allow-HTTPS-Inbound | In | Internet | * | 443 | Allow | Public HTTPS traffic |
| 110 | Allow-HTTP-Inbound | In | Internet | * | 80 | Allow | HTTP redirect to HTTPS |
| 120 | Allow-GatewayManager | In | GatewayManager | * | 65200-65535 | Allow | Azure infrastructure |
| 130 | Allow-AzureLoadBalancer | In | AzureLoadBalancer | * | * | Allow | Health probes |
| 200 | Allow-APIM-Outbound | Out | * | 10.1.0.32/27 | 443 | Allow | To APIM |
| 4096 | Deny-All-Inbound | In | * | * | * | Deny | Default deny |

**NSG-APIM:**
Applied to: APIMSubnet (10.1.0.32/27)

| Priority | Name | Direction | Source | Destination | Port | Action | Purpose |
|----------|------|-----------|--------|-------------|------|--------|---------|
| 100 | Allow-AppGW-Inbound | In | 10.1.0.0/27 | * | 443 | Allow | From App Gateway |
| 110 | Allow-APIM-Management | In | ApiManagement | * | 3443 | Allow | APIM management |
| 120 | Allow-AzureLoadBalancer | In | AzureLoadBalancer | * | * | Allow | Health probes |
| 200 | Allow-AKS-Outbound | Out | * | 10.2.0.128/26 | 443,80 | Allow | To AKS ingress |
| 210 | Allow-KeyVault-Outbound | Out | * | 10.1.0.64 | 443 | Allow | To Key Vault |
| 220 | Allow-Monitoring-Outbound | Out | * | AzureMonitor | 443 | Allow | Telemetry |
| 4096 | Deny-All-Inbound | In | * | * | * | Deny | Default deny |

**NSG-AKS:**
Applied to: AKSSystemSubnet and AKSUserSubnet

| Priority | Name | Direction | Source | Destination | Port | Action | Purpose |
|----------|------|-----------|--------|-------------|------|--------|---------|
| 100 | Allow-APIM-Inbound | In | 10.1.0.32/27 | * | 443,80 | Allow | From APIM |
| 110 | Allow-LoadBalancer-Inbound | In | AzureLoadBalancer | * | * | Allow | LB health probes |
| 120 | Allow-AKS-Internal | In | 10.2.0.0/24 | * | * | Allow | Inter-node communication |
| 200 | Allow-Database-Outbound | Out | * | 10.3.0.0/24 | 5432,443 | Allow | To databases |
| 210 | Allow-KeyVault-Outbound | Out | * | 10.1.0.64/27 | 443 | Allow | To Key Vault |
| 220 | Allow-ACR-Outbound | Out | * | AzureContainerRegistry | 443 | Allow | Pull images |
| 230 | Allow-Firewall-Outbound | Out | * | 10.0.0.36 | * | Allow | Internet via firewall |
| 4096 | Deny-All-Inbound | In | * | * | * | Deny | Default deny |

**NSG-PrivateEndpoint:**
Applied to: PrivateEndpointSubnet (10.1.0.64/27)

| Priority | Name | Direction | Source | Destination | Port | Action | Purpose |
|----------|------|-----------|--------|-------------|------|--------|---------|
| 100 | Allow-APIM-Inbound | In | 10.1.0.32/27 | * | 443 | Allow | APIM to Key Vault |
| 110 | Allow-AKS-Inbound | In | 10.2.0.0/24 | * | 443 | Allow | AKS to Key Vault |
| 4096 | Deny-All-Inbound | In | * | * | * | Deny | Default deny |

**NSG-Database:**
Applied to: DatabaseSubnet (10.3.0.0/27)

| Priority | Name | Direction | Source | Destination | Port | Action | Purpose |
|----------|------|-----------|--------|-------------|------|--------|---------|
| 100 | Allow-AKS-PostgreSQL | In | 10.2.0.0/24 | * | 5432 | Allow | AKS to PostgreSQL |
| 110 | Allow-AKS-Snowflake | In | 10.2.0.0/24 | * | 443 | Allow | AKS to Snowflake |
| 4095 | Deny-Internet-Outbound | Out | * | Internet | * | Deny | No internet egress |
| 4096 | Deny-All-Inbound | In | * | * | * | Deny | Default deny |

**Azure Firewall Configuration:**

**Deployed to**: Hub VNet (10.0.0.32/27)
**SKU**: Azure Firewall Premium
**Availability Zones**: Zones 1, 2, 3
**Threat Intelligence**: Alert and Deny mode

**Application Rules (FQDN filtering):**

| Rule Collection | Priority | Rules | Action |
|-----------------|----------|-------|--------|
| Allow-AKS-Required | 100 | *.microsoft.com, *.ubuntu.com, *.docker.io | Allow |
| Allow-Monitoring | 200 | *.ods.opinsights.azure.com, *.oms.opinsights.azure.com | Allow |
| Allow-Snowflake | 300 | *.snowflakecomputing.com | Allow |
| Allow-External-APIs | 400 | api.external-partner.com, auth.provider.com | Allow |

**Network Rules (IP-based filtering):**

| Rule Collection | Priority | Source | Destination | Ports | Action |
|-----------------|----------|--------|-------------|-------|--------|
| Allow-NTP | 100 | 10.0.0.0/8 | Internet | 123 | Allow |
| Allow-DNS | 110 | 10.0.0.0/8 | Internet | 53 | Allow |
| Allow-HTTPS | 120 | 10.2.0.0/24 | Internet | 443 | Allow |

**DNAT Rules (Inbound NAT - if applicable):**

| Rule | Source | Destination | Translated Address | Translated Port |
|------|--------|-------------|-------------------|-----------------|
| N/A | N/A | N/A | N/A | N/A |

*Note: Inbound traffic goes through Front Door and App Gateway, not firewall DNAT*

**Private Link / Private Endpoints:**

**Key Vault Private Endpoint:**
- Resource: Azure Key Vault (keyvault-prod)
- Subnet: PrivateEndpointSubnet (10.1.0.65)
- Private DNS Zone: privatelink.vaultcore.azure.net
- Access From: APIM, AKS (via managed identity)

**Storage Account Private Endpoint (Blob):**
- Resource: storageacctprod
- Subnet: StorageSubnet (10.3.0.65)
- Private DNS Zone: privatelink.blob.core.windows.net
- Access From: AKS, Backup services

**PostgreSQL Private Endpoint:**
- Resource: postgres-prod
- Subnet: DatabaseSubnet (10.3.0.5)
- Private DNS Zone: privatelink.postgres.database.azure.com
- Access From: AKS pods only

**Snowflake Private Link:**
- Resource: Snowflake account
- Subnet: SnowflakeSubnet (10.3.0.33)
- Configuration: Azure Private Link Service
- Access From: AKS, APIM (for admin tasks)

**Load Balancers:**

**Internal Load Balancer (Nginx Ingress):**
- Type: Azure Standard Load Balancer (Internal)
- Frontend IP: 10.2.0.129 (IngressSubnet)
- Backend Pool: AKS user node pool
- Health Probe: HTTP:15021 (Nginx health endpoint)
- Rules: HTTP:80, HTTPS:443

**Application Gateway (External):**
- Type: WAF_v2
- Public IP: Azure-assigned (static)
- Private IP: 10.1.0.5
- Backend Pools: APIM (10.1.0.33), Static Web App (FQDN)
- Listeners: HTTP:80 (redirect), HTTPS:443
- Rules: Path-based routing

**DDoS Protection:**
- **Standard DDoS Protection** enabled on Hub and Spoke VNets
- Real-time attack metrics and alerts
- Automatic attack mitigation (SYN flood, UDP flood, DNS amplification)
- Cost: ~$3,000/month (covers all VNets in subscription)

**Network Watcher:**
- Enabled in all regions
- NSG Flow Logs: Enabled on all NSGs → Log Analytics
- Connection Monitor: Monitor connectivity between critical components
- Packet Capture: Available for troubleshooting

**ExpressRoute / VPN (Optional for Hybrid):**
- If corporate network connectivity required:
  - ExpressRoute circuit: 1 Gbps or higher
  - Or Site-to-Site VPN for backup/test
  - BGP routing for automatic failover
  - Route filtering to prevent unwanted routes

## 4.3 Isolation Zone Networking Security
- WAF policies applied at edge.
- East-west traffic restricted to required ports.
- Egress control via Firewall or NAT Gateway.
- Private Link for PaaS services to avoid public exposure.

# 5. DNS Zones & Records

**Public DNS Zones (Azure DNS or External Provider):**

**Primary Domain: example.com**

| Record Type | Name | Value | TTL | Purpose |
|-------------|------|-------|-----|---------|
| A | @ | Akamai Edge IPs | 300 | Root domain to Akamai |
| CNAME | www | Akamai hostname | 300 | WWW subdomain |
| CNAME | api | Azure Front Door endpoint | 300 | API endpoint |
| CNAME | app | Azure Front Door endpoint | 300 | Application frontend |
| TXT | @ | Domain verification strings | 3600 | Ownership verification |
| CAA | @ | letsencrypt.org, digicert.com | 3600 | Certificate authority authorization |

**Subdomain: portal.example.com (Static Web App)**

| Record Type | Name | Value | TTL | Purpose |
|-------------|------|-------|-----|---------|
| CNAME | @ | Static Web App custom domain | 300 | Frontend portal |
| TXT | asuid | Azure verification token | 3600 | Domain ownership |

**Subdomain: api.example.com (API Endpoints)**

| Record Type | Name | Value | TTL | Purpose |
|-------------|------|-------|-----|---------|
| CNAME | @ | Azure Front Door custom domain | 300 | Primary API endpoint |
| CNAME | api-dr | Secondary Front Door endpoint | 300 | DR failover endpoint |

**Private DNS Zones (Azure Private DNS):**

**Zone: privatelink.vaultcore.azure.net**
- Purpose: Azure Key Vault private endpoint resolution
- Linked to: Hub VNet, Spoke 1, Spoke 2 VNets
- Records: Auto-registered for Key Vault private endpoints

| Record Type | Name | Value | Purpose |
|-------------|------|-------|---------|
| A | keyvault-prod | 10.1.0.65 | Production Key Vault |
| A | keyvault-nonprod | 10.1.0.66 | Non-production Key Vault |

**Zone: privatelink.blob.core.windows.net**
- Purpose: Azure Storage Account (Blob) private endpoint resolution
- Linked to: Hub VNet, Spoke 2, Spoke 3 VNets
- Records: Auto-registered for Storage private endpoints

| Record Type | Name | Value | Purpose |
|-------------|------|-------|---------|
| A | storageacctprod | 10.3.0.65 | Production storage blob |
| A | storageacctlog | 10.3.0.66 | Log storage account |

**Zone: privatelink.file.core.windows.net**
- Purpose: Azure Storage Account (File) private endpoint resolution
- Linked to: Hub VNet, Spoke 2 VNet

**Zone: privatelink.postgres.database.azure.com**
- Purpose: Azure PostgreSQL Flexible Server private endpoint resolution
- Linked to: Hub VNet, Spoke 2, Spoke 3 VNets

| Record Type | Name | Value | Purpose |
|-------------|------|-------|---------|
| A | postgres-prod | 10.3.0.5 | Production PostgreSQL |
| A | postgres-replica | 10.3.0.6 | PostgreSQL read replica (DR) |

**Internal DNS Zone: internal.example.com**
- Purpose: Internal application endpoints and service discovery
- Hosted in: Azure Private DNS Zone
- Linked to: All spoke VNets

| Record Type | Name | Value | Purpose |
|-------------|------|-------|---------|
| A | apim-internal | 10.1.0.33 | APIM private IP |
| A | appgw-internal | 10.1.0.5 | App Gateway internal IP |
| A | nginx-ingress | 10.2.0.129 | AKS Nginx ingress LB |
| CNAME | gateway | nginx-ingress.internal.example.com | Spring Cloud Gateway |

**DNS Configuration Details:**

**Public DNS Provider:**
- Managed by: Corporate IT or Azure DNS
- DNSSEC: Enabled for additional security
- Health checks: Integrated with monitoring for automatic failover

**Private DNS Integration:**
- Auto-registration enabled for VM-based resources
- Manual registration for private endpoints
- Conditional forwarding from on-premises DNS (if ExpressRoute connected)

**DNS Failover Strategy:**
- TTL set to 300 seconds (5 minutes) for quick failover
- Health-based routing in Azure Traffic Manager or Front Door
- Manual DNS update as backup failover mechanism

**Certificate Management:**
- Public certificates: Azure-managed or Let's Encrypt via Front Door/App Gateway
- Private certificates: Enterprise PKI or self-signed for internal services
- Auto-renewal configured via Key Vault and cert-manager (AKS)
- Certificate monitoring and expiry alerts (30 days before expiration)

**DNS Security:**
- Private DNS zones not exposed to internet
- DNS over HTTPS (DoH) support for client applications
- DNS query logging for audit and troubleshooting
- Access control via Azure RBAC for DNS zone management

# 6. Security
Security is managed across identity, network, and data domains to meet enterprise standards.

## 6.1 Identity and Access Management
- Entra ID integration for SSO and OAuth2.
- API Management validates JWT tokens.
- Least-privilege RBAC for operations and developers.
- Break-glass accounts and PIM enforced for privileged roles (TBD).

## 6.2 Data Security
- Key Vault stores secrets, TLS certificates, and encryption keys.
- Managed identities for service-to-service access.
- Data classification and masking in Snowflake and PostgreSQL.
- Backup encryption and access controls enforced.

## 6.3 Network Security
- WAF policies on Front Door and App Gateway.
- DDoS Protection Standard on VNets.
- Private ingress to AKS with restricted IP ranges.
- NSGs and UDRs enforce segmentation between tiers.

## 6.4 Compliance and Regulatory Considerations
- Data residency aligned with selected Azure regions.
- Logging and retention aligned with compliance (TBD).
- Access reviews and audit trails enabled.
- Compliance frameworks to be confirmed (e.g., SOC2, ISO 27001, PCI) (TBD).

## 6.5 Security Considerations
- Secrets rotated per policy.
- Vulnerability scanning for container images.
- Penetration testing on pre-prod environment.
- Security posture management via Defender for Cloud (TBD).

## 6.6 Azure Firewall
- Centralized egress control and logging.
- Application rules for outbound to Snowflake and external dependencies.
- Threat intelligence mode enabled (TBD).

## 6.7 Azure Policy
- Policies enforce private endpoints, TLS 1.2+, and approved SKUs.
- Deny public access to Storage and Key Vault unless explicitly allowed.
- Audit policies for logging and tagging compliance.

# 7. Operations & Incident Response
Operations focus on reliability, observability, and rapid recovery.

## 7.1 Platform operation and incident response

**Operations Model:**

**Support Tiers:**
1. **Tier 1 (L1)**: 24x7 monitoring and initial triage
2. **Tier 2 (L2)**: Application support and troubleshooting
3. **Tier 3 (L3)**: Platform engineering and architecture escalation
4. **Tier 4 (Vendor)**: Azure support, Snowflake support, third-party vendors

**On-Call Rotation:**
- Primary on-call: 1-week rotation
- Secondary on-call: Backup coverage
- Escalation manager: Available for P1/P0 incidents
- Tool: PagerDuty or Azure DevOps On-Call Management

**Service Level Objectives (SLOs):**

| Service Component | Availability SLO | Latency SLO (P95) | Error Budget |
|-------------------|------------------|-------------------|--------------|
| Static Web App | 99.95% | < 50 ms | 0.05% (21 min/month) |
| API Gateway (APIM) | 99.9% | < 300 ms | 0.1% (43 min/month) |
| Microservices | 99.9% | < 500 ms | 0.1% (43 min/month) |
| Database (PostgreSQL) | 99.95% | < 200 ms | 0.05% (21 min/month) |

**Incident Severity Levels:**

| Severity | Definition | Response Time | Resolution Target | Examples |
|----------|------------|---------------|-------------------|----------|
| P0/Critical | Complete service outage | 15 minutes | 2 hours | All users unable to access |
| P1/High | Major functionality impaired | 30 minutes | 4 hours | Database unavailable, auth failure |
| P2/Medium | Partial functionality degraded | 2 hours | 1 business day | Slow response times, some features down |
| P3/Low | Minor issue, no immediate impact | 1 business day | 3 business days | Cosmetic issues, minor bugs |

**Monitoring & Alerting:**

**Golden Signals Monitored:**
1. **Latency**: Response time for all API endpoints
2. **Traffic**: Requests per second, bandwidth utilization
3. **Errors**: 4xx/5xx HTTP status codes, application exceptions
4. **Saturation**: CPU, memory, disk, network utilization

**Critical Alerts:**

| Alert Name | Threshold | Action | Escalation |
|------------|-----------|--------|------------|
| Service Down | Health check fails 3 consecutive times | Page on-call immediately | P0 incident |
| High Error Rate | > 5% errors for 5 minutes | Page on-call | P1 incident |
| High Latency | P95 > 1 second for 10 minutes | Alert on-call | P1 incident |
| Database Connection Failure | Cannot connect for 1 minute | Page on-call immediately | P0 incident |
| AKS Node Not Ready | Node unschedulable > 5 minutes | Alert ops team | P2 incident |
| Certificate Expiry | < 30 days until expiry | Email ops team | P3 (prevent P0) |
| Cost Anomaly | 20% increase week-over-week | Email finance & engineering | P3 |

**Dashboards:**

**1. Executive Dashboard:**
- Overall system health (red/yellow/green)
- SLO compliance (current month)
- Incident count and MTTR
- Cost vs. budget

**2. Operations Dashboard:**
- Real-time traffic (requests/sec)
- Error rates by service
- Latency percentiles (P50, P95, P99)
- Infrastructure health (CPU, memory, disk)

**3. Application Dashboard (per microservice):**
- Request volume and latency
- Dependency health (database, external APIs)
- Top errors and exceptions
- Deployment history and rollback status

**Runbooks (Standard Operating Procedures):**

**Runbook 1: High API Latency**

*Symptoms*: P95 latency > 1 second for 10+ minutes

*Investigation Steps*:
1. Check Azure Application Gateway metrics for backend latency
2. Check APIM analytics for slow APIs
3. Review AKS pod CPU/memory utilization (kubectl top pods)
4. Check database query performance (slow query log)
5. Review external dependency latency (Snowflake, third-party APIs)

*Common Causes*:
- Database connection pool exhaustion
- Inefficient queries (missing indexes)
- Insufficient AKS node capacity
- External API degradation

*Remediation*:
- Scale AKS node pool if CPU/memory > 80%
- Restart pods with connection leaks
- Enable query caching if applicable
- Implement circuit breaker for failing dependencies

**Runbook 2: AKS Node Failure**

*Symptoms*: Node shows NotReady status, pods evicted

*Investigation Steps*:
1. Check node events: `kubectl describe node <node-name>`
2. Check node logs via Azure Monitor
3. Verify VM health in Azure portal
4. Check NSG and routing rules

*Remediation*:
- Cordon and drain node: `kubectl drain <node-name>`
- Delete node from scale set (will auto-recreate)
- Monitor pod rescheduling
- Update node pool if persistent issue

**Runbook 3: Database Connection Failure**

*Symptoms*: Applications cannot connect to PostgreSQL or Snowflake

*Investigation Steps*:
1. Verify database instance is running (Azure portal)
2. Check private endpoint connectivity
3. Test DNS resolution from AKS pod
4. Verify NSG rules allow traffic
5. Check connection string and credentials in Key Vault

*Remediation*:
- Restart database if hung (last resort)
- Recreate private endpoint if DNS issue
- Update NSG rules if blocked
- Failover to read replica if primary failure

**Runbook 4: Certificate Expiry**

*Symptoms*: SSL/TLS certificate expiring soon or expired

*Investigation Steps*:
1. Identify which certificate (Front Door, App Gateway, Key Vault)
2. Check certificate expiry date
3. Verify auto-renewal is configured

*Remediation*:
- Manually renew certificate if auto-renewal failed
- Update certificate in Key Vault
- Restart services if needed (App Gateway, APIM)
- Test HTTPS connectivity

**Runbook 5: Complete Service Outage (P0)**

*Symptoms*: All users unable to access application

*Investigation Steps*:
1. Check Azure Front Door health
2. Check Application Gateway backend health
3. Check APIM service status
4. Check AKS cluster and pod status
5. Check database availability

*Escalation Path*:
- Immediate: Page primary and secondary on-call
- +15 min: Engage incident commander
- +30 min: Notify stakeholders and activate DR plan if needed
- +1 hour: Engage Azure support if platform issue

*Communication*:
- Update status page within 10 minutes
- Provide updates every 30 minutes
- Post-incident report within 24 hours

**Maintenance Windows:**

**Scheduled Maintenance:**
- **Non-production**: Anytime with notice
- **Production**: 
  - Preferred: Sunday 2:00 AM - 6:00 AM (local time)
  - Change freeze: Last week of quarter
  - Emergency changes: Approved by change advisory board

**Patching Schedule:**
- **OS patches**: Automated via Azure Update Management (monthly)
- **AKS Kubernetes version**: Quarterly upgrade cycle
- **Database patches**: Coordinated with maintenance window
- **Application deployments**: Bi-weekly release cadence

**Backup & Restore Procedures:**

**Backup Schedule:**
- **PostgreSQL**: Automated daily backups at 2:00 AM, 30-day retention
- **Snowflake**: Continuous Time Travel (90 days), Fail-safe (7 days)
- **Configuration**: Git repository (version controlled)
- **Secrets**: Key Vault soft delete (90 days)

**Restore Testing:**
- Quarterly restore drill to verify backup integrity
- Document restore time and validate data consistency
- Update runbooks based on lessons learned

**Change Management:**

**Change Types:**
- **Standard**: Pre-approved, low risk (e.g., config changes)
- **Normal**: Requires change approval (e.g., deployments)
- **Emergency**: For critical incidents, post-approval allowed

**Change Approval Process:**
1. Submit change request with impact assessment
2. Review by change advisory board (CAB)
3. Schedule during approved maintenance window
4. Execute with rollback plan ready
5. Post-change validation and communication

**Post-Incident Review Process:**

**Timeline**:
- Incident resolved → 5 business days → Post-Incident Review (PIR) meeting

**PIR Agenda**:
1. Incident timeline and root cause analysis
2. What went well / What went poorly
3. Action items to prevent recurrence
4. Update runbooks and alerts
5. Share learnings with broader team

**PIR Output**:
- Written report (stored in wiki/documentation)
- Action items tracked in backlog with owners
- Metrics update (MTTR, incident count by category)

## 7.2 TLA Incident Response Plan
- Incident severity levels and response SLAs (TBD).
- Post-incident review within 5 business days.
- Root cause analysis and corrective action tracking.

# 8. Risks

## 8.1 Risk Management
- Risks reviewed during architecture and release milestones.
- Owners assigned for mitigation actions.
- Risk register maintained and updated quarterly.

## 8.2 Risk Assessment

**Risk Matrix:**

| Risk ID | Risk Description | Probability | Impact | Risk Level | Owner | Mitigation Strategy |
|---------|------------------|-------------|--------|------------|-------|---------------------|
| **Technical Risks** |
| R-001 | Akamai and Front Door configuration misalignment | Medium | High | **HIGH** | Network Architect | Detailed integration testing, configuration validation checklist |
| R-002 | Single-region Snowflake dependency | Low | Critical | **MEDIUM** | Data Owner | Enable cross-region replication, implement caching layer |
| R-003 | API throttling misconfiguration in APIM | Medium | Medium | **MEDIUM** | Cloud Engineer | Load testing, gradual rollout with monitoring |
| R-004 | AKS cluster capacity exhaustion during peak | Medium | High | **HIGH** | Platform Ops | Autoscaling with adequate limits, cluster autoscaler |
| R-005 | Private endpoint DNS resolution failures | Low | High | **MEDIUM** | Network Architect | Automated DNS testing, private DNS zone redundancy |
| R-006 | Kubernetes version end-of-support | Low | Medium | **LOW** | DevOps Lead | Quarterly upgrade schedule, test in non-prod first |
| R-007 | Container image vulnerabilities | Medium | Medium | **MEDIUM** | Security Officer | Automated scanning in CI/CD, image signing, approved base images |
| R-008 | Database connection pool exhaustion | Medium | High | **HIGH** | DBA | Connection pool tuning, monitoring, pod autoscaling |
| R-009 | Certificate expiration causing outage | Low | Critical | **MEDIUM** | Platform Ops | Automated renewal, 30-day expiry alerts, cert-manager |
| R-010 | Network latency between Azure and Snowflake | Low | Medium | **LOW** | Network Architect | Deploy Snowflake in same region, use private link |
| **Security Risks** |
| S-001 | Misconfigured NSG rules exposing services | Medium | Critical | **HIGH** | Security Officer | Infrastructure-as-code review, automated policy checks |
| S-002 | Inadequate WAF rules allowing attacks | Medium | High | **HIGH** | Security Officer | OWASP rule sets, regular rule testing, penetration testing |
| S-003 | Compromised managed identity | Low | Critical | **MEDIUM** | Security Officer | Least privilege RBAC, credential rotation, audit logging |
| S-004 | Key Vault access policy misconfiguration | Low | High | **MEDIUM** | Security Officer | IaC templates, regular access reviews |
| S-005 | Insider threat with elevated privileges | Low | Critical | **MEDIUM** | Security Officer | PIM for admin access, audit logs, background checks |
| S-006 | DDoS attack overwhelming resources | Low | High | **MEDIUM** | Network Architect | DDoS Protection Standard, rate limiting, auto-scaling |
| S-007 | SQL injection or API injection attacks | Medium | High | **HIGH** | DevOps Lead | Code reviews, SAST/DAST scanning, APIM policies |
| S-008 | Data breach via misconfigured storage | Low | Critical | **MEDIUM** | Security Officer | Private endpoints only, disable public access, encryption |
| **Operational Risks** |
| O-001 | Inadequate log retention or alert tuning | Medium | Medium | **MEDIUM** | Platform Ops | Log Analytics retention policy, alert validation |
| O-002 | Insufficient operations team training | Medium | High | **HIGH** | Platform Ops Lead | Training program, runbook documentation, shadowing |
| O-003 | Over-privileged identities in production | Medium | High | **HIGH** | Security Officer | Regular access reviews, JIT access with PIM |
| O-004 | Delayed patching for critical vulnerabilities | Medium | High | **HIGH** | DevOps Lead | Automated patching, vulnerability scanning |
| O-005 | Runbooks outdated or incorrect | Medium | Medium | **MEDIUM** | Platform Ops | Quarterly runbook review, post-incident updates |
| O-006 | Backup restore procedure not tested | Medium | Critical | **HIGH** | DBA | Quarterly restore testing, document restore times |
| O-007 | Inadequate monitoring causing delayed detection | Medium | High | **HIGH** | Platform Ops | Comprehensive alerting, synthetic monitoring |
| **Business Risks** |
| B-001 | Cost escalation from unbounded autoscaling | High | High | **CRITICAL** | Cloud Engineer | Max instance limits, budget alerts, cost reviews |
| B-002 | Vendor lock-in to Azure/Snowflake | Medium | Medium | **MEDIUM** | Enterprise Architect | Abstract data layer, use open standards where possible |
| B-003 | Compliance violation (GDPR, SOC2) | Low | Critical | **MEDIUM** | Compliance Officer | Regular audits, data classification, access controls |
| B-004 | Dependency on third-party APIs | Medium | High | **HIGH** | Product Owner | Circuit breakers, retry logic, alternative providers |
| B-005 | Insufficient budget for DR/multi-region | Medium | High | **HIGH** | Business Owner | Prioritize critical workloads, phased DR implementation |
| B-006 | Stakeholder delays impacting timeline | High | Medium | **HIGH** | Project Manager | Regular status meetings, escalation path, RACI matrix |
| **Data Risks** |
| D-001 | Data corruption during migration | Medium | Critical | **HIGH** | DBA | Migration testing, data validation, backups before migration |
| D-002 | Data residency compliance violation | Low | Critical | **MEDIUM** | Data Owner | Deploy in compliant regions, data classification |
| D-003 | Accidental data deletion | Low | High | **MEDIUM** | DBA | Soft delete, versioning, backup retention |
| D-004 | Cross-region data transfer costs | Medium | Medium | **MEDIUM** | Cloud Engineer | Minimize cross-region calls, use caching |

**Risk Scoring:**
- **Probability**: Low (1), Medium (2), High (3)
- **Impact**: Low (1), Medium (2), High (3), Critical (4)
- **Risk Level**: Probability × Impact
  - 1-2: LOW (green)
  - 3-4: MEDIUM (yellow)
  - 6: HIGH (orange)
  - 8-12: CRITICAL (red)

**Top 5 Critical/High Risks Requiring Immediate Attention:**

1. **B-001: Cost escalation from unbounded autoscaling**
   - **Mitigation**: Implement hard limits on AKS node count (max 20), APIM scale units (max 10)
   - **Status**: In progress (configuration pending)
   - **Target Date**: Before production launch

2. **R-001: Akamai and Front Door configuration misalignment**
   - **Mitigation**: Joint architecture review with Akamai team, integration testing
   - **Status**: Planned
   - **Target Date**: Week 16

3. **R-004: AKS cluster capacity exhaustion**
   - **Mitigation**: Cluster autoscaler enabled, HPA configured, load testing
   - **Status**: In progress
   - **Target Date**: Week 20 (before performance testing)

4. **S-001: Misconfigured NSG rules exposing services**
   - **Mitigation**: IaC templates peer-reviewed, Azure Policy enforcement
   - **Status**: In progress
   - **Target Date**: Week 12 (platform build phase)

5. **S-007: SQL injection or API injection attacks**
   - **Mitigation**: SAST/DAST in CI/CD, APIM input validation policies
   - **Status**: Planned
   - **Target Date**: Week 19 (security testing phase)

**Risk Monitoring:**
- Monthly risk review in architecture governance meeting
- Update risk register after each sprint
- Escalate new high/critical risks to steering committee immediately

## 8.3 Risk Mitigation
- Standardized configuration baselines for edge services.
- Multi-region failover testing.
- Rate-limit validation and load testing before release.
- Automated policy enforcement and drift detection.
- Cost alerts and scaling limits in AKS and APIM.

## 8.4 Operational & Security Risk
- Inadequate log retention or alert tuning.
- Over-privileged identities.
- Delayed patching for container images or dependencies.

# 9. Estimated Costs

**Monthly Cost Estimate (Production Environment):**

**Assumptions for Cost Estimation:**
- Traffic: 10 million API requests/month, 50 GB data transfer outbound
- Storage: 1 TB blob storage, 100 GB logs
- Database: PostgreSQL (General Purpose, 4 vCores), Snowflake (Medium warehouse, 8 hours/day)
- AKS: 3 system nodes (D4s_v3), 5 user nodes (D8s_v3) with autoscaling
- High availability enabled for critical components

| Service | SKU/Configuration | Estimated Monthly Cost | Notes |
|---------|-------------------|------------------------|-------|
| **Compute & Orchestration** | | | |
| AKS - System Node Pool | 3x Standard_D4s_v3 (4 vCPU, 16 GB) | $350 | Control plane free, pay for nodes |
| AKS - User Node Pool | 5x Standard_D8s_v3 (8 vCPU, 32 GB) | $1,170 | Autoscale 3-10 nodes |
| AKS - Reserved Instance Savings | 3-year reserved | -$380 | 40% savings on baseline nodes |
| **Networking & Security** | | | |
| Azure Front Door Premium | 100 GB outbound, 10M requests | $420 | Includes WAF rules |
| Application Gateway v2 | WAF_v2, 2 capacity units | $280 | Autoscaling enabled |
| Azure Firewall Premium | Standard deployment | $1,250 | Hub firewall for egress |
| VNet Peering | 50 GB data transfer | $25 | Hub-spoke traffic |
| Private Endpoints | 5 endpoints | $35 | $7 per endpoint |
| **API & Web Services** | | | |
| API Management | Developer or Premium tier | $675 | Premium for multi-region: $3,650/month |
| Azure Static Web App | Standard tier | $9 | Includes 100 GB bandwidth |
| **Storage** | | | |
| Azure Storage - Blob | 1 TB LRS, 50 GB hot access | $25 | Lifecycle management enabled |
| Azure Storage - GRS | 200 GB for backups | $45 | Geo-redundant |
| **Databases** | | | |
| PostgreSQL Flexible Server | General Purpose, 4 vCores, 256 GB | $340 | HA enabled: $680/month |
| Snowflake | Medium warehouse, 8 hrs/day | $1,200 | Varies by usage |
| **Security & Management** | | | |
| Azure Key Vault | Standard tier, 10K operations | $5 | HSM keys: +$1,000/month |
| Azure Monitor | 50 GB log ingestion | $115 | First 5 GB free |
| Log Analytics | 50 GB retention 90 days | $115 | Long-term retention in blob |
| Microsoft Defender for Cloud | Standard tier | $195 | Per resource pricing |
| **Identity & Access** | | | |
| Azure AD Premium P1 | 100 users | $600 | Identity protection |
| **Backup & DR** | | | |
| Azure Backup | 500 GB backup data | $125 | For VMs if used |
| **Total (Standard Configuration)** | | **~$6,300/month** | Single region, HA enabled |
| **Total (Multi-Region with Premium APIM)** | | **~$10,500/month** | Active-passive DR |

**Cost Breakdown by Environment:**

| Environment | Percentage | Estimated Monthly Cost | Notes |
|-------------|------------|------------------------|-------|
| Development | 10% | $630 | Smaller SKUs, single instance |
| Test/Staging | 15% | $945 | Production-like but smaller scale |
| Production | 75% | $4,725 | Full HA and multi-region (if enabled) |
| **Total All Environments** | 100% | **$6,300** | Or $10,500 with premium features |

**Annual Cost Projection:**
- Year 1: $75,600 - $126,000 (depending on configuration)
- 3-Year Reserved Instances: Save 40% on compute (~$18,000 savings)
- 1-Year Reserved Instances: Save 20% on compute (~$9,000 savings)

**Cost Optimization Strategies:**

**1. Right-Sizing:**
- Monitor CPU/memory utilization and downsize underutilized resources
- Use burstable VMs (B-series) for non-production environments
- Review and remove unused resources monthly

**2. Reserved Capacity:**
- Purchase 1-year or 3-year reserved instances for:
  - AKS baseline node pools (40% savings)
  - Application Gateway capacity units (20% savings)
  - API Management (up to 40% savings)
  - PostgreSQL compute (30% savings)

**3. Autoscaling:**
- Configure aggressive scale-in policies during off-peak hours
- Use Kubernetes HPA and VPA for pod-level optimization
- Scale down non-production environments after business hours

**4. Storage Optimization:**
- Implement lifecycle management policies:
  - Move to cool tier after 30 days
  - Archive after 90 days
  - Delete after retention period
- Use blob versioning judiciously to avoid storage bloat
- Compress logs before storage

**5. Network Optimization:**
- Use Azure CDN caching to reduce origin traffic
- Minimize cross-region data transfer
- Use VNet peering instead of VPN where possible
- Leverage Azure Storage replication for static content

**6. Database Optimization:**
- Use Snowflake auto-suspend and auto-resume (suspend after 5 minutes idle)
- Optimize queries to reduce warehouse compute time
- Use PostgreSQL read replicas efficiently (only when needed)
- Implement connection pooling to reduce database overhead

**7. Monitoring Cost Management:**
- Set up budgets and alerts at 50%, 75%, 90% thresholds
- Use Azure Cost Management + Billing for cost analysis
- Tag all resources for cost allocation and chargeback
- Review Azure Advisor cost recommendations weekly

**Cost Monitoring & Governance:**

**Budgets:**
- Production: $5,000/month with 10% buffer
- Non-production: $1,300/month
- Alert recipients: Cloud Engineering Lead, Finance

**Cost Allocation Tags (Mandatory):**
- Environment (dev/test/prod)
- Application name
- Cost center
- Owner team
- Criticality level

**Monthly Cost Review:**
- First week of each month: Review actual vs. budget
- Identify top 10 cost drivers
- Action items for optimization
- Report to stakeholders

**Cost Anomaly Detection:**
- Enable Azure Cost Management anomaly alerts
- Thresholds: 20% increase week-over-week
- Automated alert to ops team for investigation

**Potential Cost Risks:**
- Uncontrolled autoscaling (mitigation: max instance limits)
- Snowflake warehouse left running (mitigation: auto-suspend)
- Over-retention of logs and backups (mitigation: lifecycle policies)
- Premium tier services not fully utilized (mitigation: right-sizing)

**Cost Optimization Tools:**
- Azure Pricing Calculator: Pre-deployment estimation
- Azure Cost Management + Billing: Actual cost tracking
- Azure Advisor: Cost recommendations
- Third-party tools: CloudHealth, Spot.io (optional)

---

# 10. APPENDICES

## Appendix A: Glossary

| Term | Definition |
|------|------------|
| AKS | Azure Kubernetes Service - Managed Kubernetes container orchestration service |
| APIM | Azure API Management - API gateway and management platform |
| Azure CNI | Container Network Interface - Advanced networking for AKS pods |
| WAF | Web Application Firewall - Layer 7 firewall for HTTP/HTTPS protection |
| NSG | Network Security Group - Layer 4 network access control |
| UDR | User Defined Route - Custom routing tables in Azure |
| RBAC | Role-Based Access Control - Authorization model |
| HPA | Horizontal Pod Autoscaler - Kubernetes pod scaling based on metrics |
| VPA | Vertical Pod Autoscaler - Adjusts pod resource requests |
| SLO | Service Level Objective - Internal performance target |
| SLA | Service Level Agreement - Committed uptime guarantee |
| RTO | Recovery Time Objective - Maximum acceptable downtime |
| RPO | Recovery Point Objective - Maximum acceptable data loss |
| MTTR | Mean Time To Resolve - Average time to fix incidents |
| MTTD | Mean Time To Detect - Average time to detect incidents |
| PIM | Privileged Identity Management - Just-in-time admin access |
| PE | Private Endpoint - Private network connection to PaaS services |

## Appendix B: Azure Service SKU Recommendations

| Service | Development | Test/Staging | Production |
|---------|-------------|--------------|------------|
| AKS Nodes | D2s_v3 (2 vCPU, 8 GB) | D4s_v3 (4 vCPU, 16 GB) | D8s_v3 (8 vCPU, 32 GB) |
| Application Gateway | Standard_v2 | WAF_v2 (1 CU) | WAF_v2 (2+ CU, autoscale) |
| API Management | Developer tier | Developer or Standard | Premium (multi-region) |
| PostgreSQL | Burstable (1-2 vCore) | General Purpose (2 vCore) | General Purpose (4-8 vCore) HA |
| Azure Firewall | Basic (if available) | Standard | Premium |
| Storage | LRS | LRS or ZRS | GRS or GZRS |

## Appendix C: Naming Convention Examples

| Resource Type | Naming Pattern | Example |
|---------------|----------------|---------|
| Resource Group | rg-{env}-{region}-{app} | rg-prod-eastus2-webapp |
| VNet | vnet-{env}-{region}-{purpose} | vnet-prod-eastus2-hub |
| Subnet | snet-{purpose} | snet-aks-user |
| AKS Cluster | aks-{env}-{region}-{app} | aks-prod-eastus2-webapp |
| App Gateway | appgw-{env}-{region}-{app} | appgw-prod-eastus2-webapp |
| APIM | apim-{env}-{region}-{app} | apim-prod-eastus2-webapp |
| Key Vault | kv-{env}-{app}-{suffix} | kv-prod-webapp-001 |
| Storage Account | st{env}{app}{suffix} | stprodwebapp001 (max 24 chars, lowercase) |
| NSG | nsg-{subnet-name} | nsg-aks-user |
| PostgreSQL | psql-{env}-{region}-{app} | psql-prod-eastus2-webapp |

## Appendix D: Reference Architecture Links

**Azure Architecture Center:**
- Hub-Spoke Network Topology: https://learn.microsoft.com/azure/architecture/reference-architectures/hybrid-networking/hub-spoke
- Microservices on AKS: https://learn.microsoft.com/azure/architecture/reference-architectures/containers/aks-microservices/aks-microservices
- API Management Landing Zone: https://learn.microsoft.com/azure/architecture/example-scenario/integration/app-gateway-internal-api-management-function

**Azure Well-Architected Framework:**
- Cost Optimization: https://learn.microsoft.com/azure/well-architected/cost/
- Operational Excellence: https://learn.microsoft.com/azure/well-architected/operational-excellence/
- Performance Efficiency: https://learn.microsoft.com/azure/well-architected/performance-efficiency/
- Reliability: https://learn.microsoft.com/azure/well-architected/reliability/
- Security: https://learn.microsoft.com/azure/well-architected/security/

**Best Practice Guides:**
- AKS Baseline Architecture: https://learn.microsoft.com/azure/architecture/reference-architectures/containers/aks/baseline-aks
- Azure Front Door Best Practices: https://learn.microsoft.com/azure/frontdoor/best-practices
- Private Link and Private Endpoints: https://learn.microsoft.com/azure/private-link/private-endpoint-overview

## Appendix E: Compliance and Security Standards

**Applicable Standards:**
- CIS Microsoft Azure Foundations Benchmark v1.5.0
- NIST Cybersecurity Framework
- OWASP Top 10 (Web Application Security)
- PCI DSS 3.2.1 (if payment card data)
- GDPR (if EU personal data)
- SOC 2 Type II (service organization controls)
- ISO/IEC 27001:2013 (information security management)

**Azure Compliance Offerings:**
- Microsoft Compliance Manager: Track compliance posture
- Azure Policy: Enforce compliance controls
- Microsoft Defender for Cloud: Security posture management
- Azure Blueprints: Deploy compliant environments

## Appendix F: Contact Information

**Support Contacts:**
- Azure Support: Portal-based support tickets, P1/P2/P3 response SLAs
- Snowflake Support: support@snowflake.com, 24x7 for production
- Akamai Support: TAM (Technical Account Manager) - TBD
- Internal IT Help Desk: TBD
- Security Incident Response: security@company.com (or TBD)

**Vendor Account Managers:**
- Azure TAM: TBD
- Snowflake TAM: TBD
- Akamai TAM: TBD

## Appendix G: Change History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 0.1 | 2026-01-15 | Azure Architect | Initial draft |
| 0.5 | 2026-02-01 | Azure Architect | Added detailed architecture sections |
| 1.0 | 2026-02-12 | Azure Architect | Complete document for review |

## Appendix H: Acronyms

ACR = Azure Container Registry  
AD = Active Directory (now Entra ID)  
AKS = Azure Kubernetes Service  
APIM = API Management  
ARM = Azure Resource Manager  
CAA = Certificate Authority Authorization  
CDN = Content Delivery Network  
CIDR = Classless Inter-Domain Routing  
CNI = Container Network Interface  
CNAME = Canonical Name (DNS record)  
DDoS = Distributed Denial of Service  
DNS = Domain Name System  
DR = Disaster Recovery  
FQDN = Fully Qualified Domain Name  
GRS = Geo-Redundant Storage  
HA = High Availability  
HPA = Horizontal Pod Autoscaler  
HSM = Hardware Security Module  
IaaS = Infrastructure as a Service  
IaC = Infrastructure as Code  
JWT = JSON Web Token  
K8s = Kubernetes  
LB = Load Balancer  
LRS = Locally Redundant Storage  
MTTR = Mean Time To Resolve  
MTTD = Mean Time To Detect  
NSG = Network Security Group  
OAuth = Open Authorization  
OWASP = Open Web Application Security Project  
PaaS = Platform as a Service  
PE = Private Endpoint  
PIM = Privileged Identity Management  
RBAC = Role-Based Access Control  
RPO = Recovery Point Objective  
RTO = Recovery Time Objective  
SLA = Service Level Agreement  
SLO = Service Level Objective  
SQL = Structured Query Language  
SSL = Secure Sockets Layer  
SSO = Single Sign-On  
SWA = Static Web App  
TLS = Transport Layer Security  
UAT = User Acceptance Testing  
UDR = User Defined Route  
VNet = Virtual Network  
VPA = Vertical Pod Autoscaler  
VPN = Virtual Private Network  
WAF = Web Application Firewall  
ZRS = Zone-Redundant Storage  

---

**END OF DOCUMENT**

*This Solution Design Document is a living document and should be updated as the solution evolves. All stakeholders should review and provide feedback during the architecture review process.*

