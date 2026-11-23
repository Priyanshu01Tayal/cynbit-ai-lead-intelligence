"""
Cynbit AI - Dataset Generation Script
Generates:
1. data/training_leads.csv - 240+ labeled inquiry texts for training/testing the NLP text classification model.
2. data/sample_leads.csv - 45+ comprehensive historical leads with full lifecycle metadata for the CRM database.
"""

import os
import random
import pandas as pd
from datetime import datetime, timedelta

random.seed(42)

CATEGORIES = [
    "AI/ML Development",
    "Web Development",
    "Mobile App Development",
    "Cloud & DevOps",
    "Business Automation",
    "Other"
]

# Diverse, realistic customer inquiries by category
INQUIRIES_DATA = {
    "AI/ML Development": [
        "We are looking for an AI team to build a custom computer vision model for defect detection on our manufacturing assembly line. We process 500 parts per minute and need inference speed under 50ms. Budget is around $45,000 and we need an initial prototype within 8 weeks.",
        "Need a machine learning engineer to develop a predictive customer churn model for our SaaS platform. We have 3 years of PostgreSQL user event logs and want integration with HubSpot. Budget is $20,000, deadline Q3.",
        "We want to develop an enterprise RAG (Retrieval-Augmented Generation) chatbot connected to our internal Confluence and SharePoint documentation. Must support multi-turn dialogue, strict RBAC, and zero data leakage. Budget: $35,000, urgent deployment needed within 1 month.",
        "Looking for experts in NLP to build a real-time sentiment analysis and brand monitoring pipeline across Twitter, Reddit, and customer reviews. We need daily alerts and an executive dashboard. Estimated budget $28,000, timeline 2 months.",
        "We need a recommendation engine for our online fashion marketplace. Should implement collaborative filtering and content-based embedding similarity. Budget $30,000, launch needed in 3 months.",
        "Our radiology clinic needs a deep learning model to assist with chest X-ray anomaly classification. High precision is required to avoid false negatives. Budget $65,000, timeline 4 months.",
        "We want to fine-tune an open-source LLM (Llama-3) on our domain-specific financial underwriting documents. Need local deployment on on-premise Nvidia GPUs. Budget $50,000, ASAP start.",
        "Looking to build a voice AI assistant for automated patient appointment booking via telephone. Must integrate with Twilio and Epic EHR. Budget $40,000, 10 weeks timeline.",
        "Need an ML specialist to build fraud detection models for crypto payment transactions. Low latency (<100ms) scoring is non-negotiable. Budget $55,000, timeline 6 weeks.",
        "We are building a smart resume parser and candidate ranking system using transformer models. Need parsing for PDF, DOCX, and LinkedIn profiles. Budget $25,000, timeline 2 months.",
        "We want to implement anomaly detection on time-series telemetry data from 10,000 IoT sensor devices in smart grid systems. Budget $35,000, need kickoff in 2 weeks.",
        "Need a generative AI image generation tool integrated into our marketing design platform using Stable Diffusion fine-tunes. Budget $30,000, timeline 6 weeks.",
        "Looking for an AI partner to develop an automated legal document summarizer and clause extraction system. Budget $45,000, timeline 3 months.",
        "We have an audio transcription project requiring speaker diarization and custom domain vocabulary fine-tuning for legal proceedings. Budget $22,000, timeline 2 months.",
        "Need an AI solution to analyze satellite imagery and calculate crop health indices (NDVI) for agriculture clients. Budget $40,000, timeline 3 months.",
        "We want to replace our rule-based search with semantic vector search using Pinecone and dense embeddings. Budget $18,000, immediate requirement within 3 weeks.",
        "Looking for reinforcement learning expertise to optimize warehouse robotic palletizing trajectories. Budget $60,000, timeline 4 months.",
        "Need an optical character recognition (OCR) pipeline to digitize hand-written invoice receipts with high accuracy. Budget $15,000, timeline 1 month.",
        "We need a predictive maintenance model for commercial fleet trucks based on CAN bus telematics data. Budget $32,000, timeline 2 months.",
        "Looking to build an automated pricing optimization model that dynamically adjusts prices based on competitor scrapes and inventory levels. Budget $25,000, timeline 6 weeks.",
        "We need an AI evaluation harness to benchmark multiple commercial LLMs against our proprietary evaluation datasets. Budget $18,000, timeline 4 weeks.",
        "Looking for an ML engineer to build automated translation and localization for our e-commerce catalog in 12 languages. Budget $22,000, timeline 2 months.",
        "We want to develop synthetic data generation pipelines to train computer vision models where real image data is scarce. Budget $30,000, timeline 3 months.",
        "Need a conversational AI agent to handle Tier-1 IT helpdesk tickets inside Slack and Microsoft Teams. Budget $26,000, urgent launch in 3 weeks.",
        "Looking for a partner to build a graph neural network (GNN) model for anti-money laundering detection on banking transfer graphs. Budget $70,000, timeline 4 months.",
        "We need a computer vision model for real-time human pose estimation in a fitness training mobile app. Budget $28,000, timeline 2 months.",
        "Looking to train custom small language models (SLMs) to run locally on mobile edge devices with minimal memory footprint. Budget $45,000, timeline 3 months.",
        "Need an AI scoring algorithm to qualify B2B marketing leads based on web behavior, technographic data, and email engagement. Budget $20,000, timeline 1 month.",
        "We want an AI-based automated code review bot that checks for company style compliance and security vulnerabilities in GitHub PRs. Budget $24,000, timeline 6 weeks.",
        "Looking for deep learning expertise in speech synthesis (TTS) to generate voice clones for our audiobook production service. Budget $38,000, timeline 2 months.",
        "Need automated video highlights generation using scene detection and audio peak detection for sports broadcasts. Budget $35,000, timeline 2 months.",
        "We require a tabular ML model for loan default prediction with SHAP explainability for regulatory compliance. Budget $30,000, timeline 8 weeks.",
        "Looking to build an AI content moderation filter for text, images, and audio on our live streaming app. Budget $42,000, urgent - need in 3 weeks.",
        "Need an ML model to forecast retail store customer footfall using weather, holidays, and promotional calendar data. Budget $16,000, timeline 1 month.",
        "We want to create a multi-agent system where specialized AI agents collaborate to generate automated financial research briefings. Budget $50,000, timeline 2 months.",
        "Looking for computer vision to detect PPE compliance (helmets, vests, goggles) at construction sites from IP camera feeds. Budget $38,000, timeline 3 months.",
        "Need a prompt engineering and LLM guardrails implementation to eliminate hallucinations in our healthcare guidance app. Budget $20,000, timeline 3 weeks.",
        "We want to predict hospital patient readmission risk within 30 days of discharge using EHR clinical notes. Budget $48,000, timeline 3 months.",
        "Looking for an AI model to detect deepfake video and audio uploads on our identity verification platform. Budget $60,000, urgent launch in 1 month.",
        "Need an AI assistant that extracts key metrics from PDF earnings reports and populates financial valuation models. Budget $28,000, timeline 6 weeks."
    ],
    "Web Development": [
        "We need a full-stack web application for our real estate agency. Features should include interactive map search, virtual tours, mortgage calculator, and CRM integration. We prefer Next.js and Tailwind CSS. Budget $25,000, timeline 2 months.",
        "Looking for a frontend agency to revamp our B2B SaaS marketing website and customer onboarding portal. Must be responsive, SEO-optimized, and lightning fast. Budget $15,000, launch in 4 weeks.",
        "We require a modern e-commerce storefront built on Shopify Plus or custom Next.js with headless Commerce. Must handle 10,000 SKUs and international currencies. Budget $30,000, timeline 8 weeks.",
        "Need a web developer to build a client portal with document uploads, electronic signatures, and billing invoices through Stripe. Budget $12,000, timeline 1 month.",
        "Looking to build a custom online learning management system (LMS) with video streaming, quiz engine, and certificate generation. Budget $28,000, timeline 3 months.",
        "We want a responsive web portal for booking doctor appointments and viewing lab reports. Must be HIPAA compliant. Budget $35,000, timeline 10 weeks.",
        "Need an experienced React and Django developer to rebuild our legacy PHP web platform into modern micro-frontends. Budget $40,000, timeline 4 months.",
        "Looking for a high-converting web landing page suite with A/B testing and analytics integration for a product launch. Budget $8,000, urgent delivery in 2 weeks.",
        "We need a community forum and knowledge base platform with markdown editor, user reputation scores, and badge rewards. Budget $18,000, timeline 6 weeks.",
        "Looking to develop an interactive data dashboard with rich web charts (D3.js / Chart.js) for logistics tracking. Budget $20,000, timeline 2 months.",
        "Need a progressive web app (PWA) for our restaurant chain enabling tabletop QR code ordering and loyalty rewards. Budget $22,000, timeline 8 weeks.",
        "We want to build a marketplace platform connecting freelance designers with local small businesses. Includes escrow payments and chat. Budget $32,000, timeline 3 months.",
        "Looking for frontend performance optimization. Our React site has poor Core Web Vitals (LCP > 4.5s) and needs code splitting and asset caching. Budget $6,000, 2 weeks.",
        "Need a web-based scheduling and dispatch software for our plumbing and HVAC field service business. Budget $25,000, timeline 2 months.",
        "We need a web application to manage inventory, supplier purchase orders, and warehouse barcode scanning. Budget $28,000, timeline 10 weeks.",
        "Looking for a custom CMS built on Strapi or Sanity with a Next.js frontend for an online publishing company. Budget $16,000, timeline 5 weeks.",
        "We want a web-based code editor and collaboration platform for our technical interview process. Budget $35,000, timeline 3 months.",
        "Need a customer feedback and NPS survey widget that embeds seamlessly into any web application. Budget $10,000, timeline 3 weeks.",
        "Looking to build an auction web portal with real-time bidding using WebSockets and automated countdown timers. Budget $30,000, timeline 2 months.",
        "We need a responsive corporate website redesign with multi-language support (English, German, Japanese) and headless CMS. Budget $18,000, timeline 6 weeks.",
        "Looking for a full-stack engineer to build an event ticketing website with interactive seat selection maps and Stripe checkout. Budget $26,000, timeline 8 weeks.",
        "Need a web app for digital asset management allowing creative teams to tag, search, and approve marketing assets. Budget $22,000, timeline 2 months.",
        "We want a custom web-based quotation generator that calculates complex manufacturing quotes based on CAD inputs. Budget $20,000, timeline 6 weeks.",
        "Looking to build a recruitment job board with candidate filters, applicant tracking, and employer subscription tiers. Budget $24,000, timeline 2 months.",
        "Need an interactive web portfolio with WebGL 3D model showcases for an architectural design firm. Budget $14,000, timeline 4 weeks.",
        "We want to migrate our monolith WordPress site into a modern Jamstack setup with Gatsby or Astro and headless CMS. Budget $12,000, timeline 1 month.",
        "Looking for a secure web platform for confidential peer review of academic scientific papers. Budget $25,000, timeline 2 months.",
        "Need a full-stack SaaS web application for social media post scheduling and analytics preview. Budget $28,000, timeline 3 months.",
        "We want a web-based dashboard to visualize financial portfolio performance and rebalancing suggestions. Budget $30,000, timeline 2 months.",
        "Looking for an accessible (WCAG 2.1 AA compliant) government portal for civic service applications. Budget $38,000, timeline 4 months.",
        "Need an interactive recipe and meal planning web application with grocery list auto-generation. Budget $15,000, timeline 6 weeks.",
        "We want a web portal for car dealership inventory management, trade-in valuations, and financing calculators. Budget $24,000, timeline 2 months.",
        "Looking for a partner to build an intranet employee portal with company directory, announcements, and leave management. Budget $19,000, timeline 6 weeks.",
        "Need a web application for booking coworking desks and meeting rooms with calendar sync. Budget $16,000, timeline 1 month.",
        "We want a real-time web-based multiplayer trivia quiz platform for corporate team building events. Budget $20,000, timeline 6 weeks.",
        "Looking for a custom B2B wholesale ordering portal with volume discount pricing tiers and invoice credit terms. Budget $27,000, timeline 2 months.",
        "Need an interactive website calculator for carbon footprint estimation and offset purchasing. Budget $11,000, timeline 4 weeks.",
        "We want a custom analytics dashboard for Shopify store owners aggregating marketing spend and ROAS across ad platforms. Budget $22,000, timeline 2 months.",
        "Looking for a web app that allows musicians to collaborate remotely on audio track stems and version control. Budget $32,000, timeline 3 months.",
        "Need a modern web app for gym membership management, class schedules, and trainer reservations. Budget $17,000, timeline 6 weeks."
    ],
    "Mobile App Development": [
        "We want to build a cross-platform mobile app in Flutter for both iOS and Android. It is a telemedicine app with video calling, prescription history, and push notifications. Budget $35,000, timeline 3 months.",
        "Looking for React Native experts to develop a personal finance budgeting app with bank account synchronization (Plaid) and spending analytics. Budget $30,000, timeline 10 weeks.",
        "Need a native iOS (Swift) app for our on-demand courier delivery service with live GPS courier tracking and turn-by-turn routing. Budget $40,000, launch in 3 months.",
        "We want a native Android (Kotlin) app for warehouse operators that scans QR codes, tracks inventory movements, and works offline. Budget $25,000, timeline 2 months.",
        "Looking to develop a mobile fitness workout tracking app with wearable Apple Watch and Garmin integration. Budget $32,000, timeline 3 months.",
        "Need a cross-platform mobile app for social media creators to edit short-form videos with custom filters and audio sync. Budget $45,000, timeline 4 months.",
        "We need a mobile app for hotel guests to check-in digitally, unlock smart room doors via Bluetooth BLE, and order room service. Budget $38,000, timeline 3 months.",
        "Looking for a Flutter developer to build an on-demand pet sitting and dog walking mobile application with live GPS walk maps. Budget $22,000, timeline 8 weeks.",
        "We want a mobile companion app for our smart home IoT thermostat with schedule management and energy consumption insights. Budget $28,000, timeline 2 months.",
        "Need a mobile banking app with biometric authentication (FaceID/Fingerprint), card freeze features, and instant P2P transfers. Budget $55,000, timeline 4 months.",
        "Looking to build a mobile learning app for kids with gamified spelling and math interactive puzzles. Budget $20,000, timeline 2 months.",
        "We need a ride-hailing mobile application for an electric scooter rental startup with geofencing and Stripe payments. Budget $36,000, timeline 3 months.",
        "Need a mobile app for digital business cards with NFC exchange, QR codes, and Apple Wallet integration. Budget $14,000, timeline 6 weeks.",
        "Looking for an iOS and Android app for community sports league scheduling, referee score logging, and live standings. Budget $18,000, timeline 2 months.",
        "We want a mobile shopping app for our retail boutique with augmented reality (AR) product preview in room spaces. Budget $42,000, timeline 3 months.",
        "Need a meditation and mindfulness mobile app with audio streaming, daily streak reminders, and offline sleep sounds. Budget $19,000, timeline 8 weeks.",
        "Looking to build a mobile app for food truck discovery with live vendor location beacons and mobile ordering. Budget $16,000, timeline 6 weeks.",
        "We need a construction site inspection mobile app allowing engineers to snap photos, pin defects onto floor plans, and generate PDF punch lists. Budget $30,000, timeline 2 months.",
        "Need a mobile app for university students featuring class timetables, campus navigation maps, and club event signups. Budget $22,000, timeline 8 weeks.",
        "Looking for an app to manage EV charging station reservations, charging status monitoring, and RFID payment activation. Budget $34,000, timeline 3 months.",
        "We want a mobile field service technician app for logging HVAC repair work orders, parts inventory, and capturing customer signatures. Budget $26,000, timeline 2 months.",
        "Need a mobile app for wine enthusiasts with label scanner, cellar inventory management, and community tasting notes. Budget $21,000, timeline 8 weeks.",
        "Looking to build a mobile dating app with location-based matching, prompt answers, and audio message introductions. Budget $38,000, timeline 3 months.",
        "We need a real-time language translation mobile app that translates spoken speech across 15 languages during international travel. Budget $32,000, timeline 2 months.",
        "Need a mobile app for parking spot reservation and automated license plate recognition payment in city garages. Budget $28,000, timeline 10 weeks.",
        "Looking for a mobile app for plant care identification, watering schedules, and disease diagnostics from camera photos. Budget $20,000, timeline 6 weeks.",
        "We want a private family social network mobile app with photo albums, shared calendar, and secure messaging. Budget $25,000, timeline 2 months.",
        "Need a mobile app for truck drivers with route optimization avoiding low bridges, logbook compliance, and fuel price tracker. Budget $35,000, timeline 3 months.",
        "Looking to develop a mobile marketplace for buying and selling second-hand luxury sneakers with authenticity verification steps. Budget $30,000, timeline 2 months.",
        "We need an iOS app for musicians featuring a multi-track loop recorder, tuner, metronome, and audio export to SoundCloud. Budget $24,000, timeline 8 weeks.",
        "Need a mobile companion app for museum visitors with interactive audio guide tours triggered by Bluetooth iBeacons. Budget $18,000, timeline 6 weeks.",
        "Looking to create a mobile micro-investing app that rounds up daily purchases and invests spare change into index funds. Budget $48,000, timeline 4 months.",
        "We want a mobile tenant portal for paying rent, submitting maintenance requests, and receiving building announcements. Budget $17,000, timeline 6 weeks.",
        "Need a mobile app for golf scorekeeping, GPS rangefinder distances to greens, and handicap calculation. Budget $22,000, timeline 2 months.",
        "Looking for a mobile app for secondhand book exchange with barcode scanning and local community drop-off points. Budget $15,000, timeline 5 weeks.",
        "We need a mobile app for mental health journaling with mood tracking charts and encrypted cloud sync. Budget $21,000, timeline 8 weeks.",
        "Need an iOS and Android app for boat and yacht charters with calendar availability and captain verification. Budget $29,000, timeline 2 months.",
        "Looking to build a mobile audio guide for walking tours in historical cities with offline GPS map navigation. Budget $19,000, timeline 6 weeks.",
        "We want a mobile app for emergency roadside assistance dispatch with GPS location pinging and live tow truck arrival tracking. Budget $33,000, timeline 3 months.",
        "Need a mobile app for personal stylists to curate lookbooks and recommend outfits from client wardrobe photos. Budget $23,000, timeline 2 months."
    ],
    "Cloud & DevOps": [
        "We need to migrate our on-premise infrastructure to AWS. We currently have 40 virtual machines, a monolithic MySQL database, and legacy filesystems. Looking for Terraform infrastructure-as-code, Dockerization, and zero-downtime database migration. Budget $35,000, timeline 2 months.",
        "Looking for a DevOps engineer to design and implement CI/CD pipelines in GitLab for our 15 microservices. Need automated testing, security scanning, and blue-green deployments to Kubernetes. Budget $20,000, timeline 6 weeks.",
        "Our AWS monthly bill has ballooned past $60,000. We need a cloud cost optimization and FinOps audit to right-size instances, implement spot fleets, and set up autoscaling. Budget $15,000, timeline 1 month.",
        "We need an enterprise Kubernetes (EKS) cluster setup with Helm charts, Istio service mesh, Prometheus and Grafana monitoring, and ArgoCD GitOps. Budget $28,000, timeline 8 weeks.",
        "Looking for a Cloud Architect to help us achieve SOC 2 Type II compliance on Google Cloud Platform. Need IAM tightening, CloudTrail auditing, KMS encryption, and vulnerability management. Budget $25,000, timeline 6 weeks.",
        "We need disaster recovery (DR) architecture implemented across multi-region Azure. Target RPO < 5 minutes and RTO < 15 minutes. Budget $30,000, timeline 2 months.",
        "Looking for DevOps consulting to migrate our application stack from Docker Swarm to AWS ECS Fargate with Terraform scripts. Budget $18,000, timeline 4 weeks.",
        "Need full observability implementation for our distributed backend: OpenTelemetry instrumentation, distributed tracing with Jaeger, and centralized ELK logging. Budget $22,000, timeline 6 weeks.",
        "We need automated database failover, automated point-in-time recovery, and read-replica scaling on Amazon Aurora PostgreSQL. Budget $16,000, timeline 3 weeks.",
        "Looking to build a secure multi-tenant cloud environment on GCP with VPC peering, Cloud Armor DDoS protection, and Cloudflare CDN. Budget $26,000, timeline 2 months.",
        "Need a site reliability engineering (SRE) review to eliminate frequent production outages, establish SLOs/SLIs, and configure PagerDuty incident response. Budget $20,000, timeline 5 weeks.",
        "We want to build a self-service developer platform (internal developer portal) using Backstage to automate environment provisioning on AWS. Budget $38,000, timeline 3 months.",
        "Looking for help setting up automated load testing using k6 and locust integrated into our GitHub Actions release pipelines. Budget $12,000, timeline 3 weeks.",
        "Need to containerize 12 legacy .NET Framework applications into Linux Docker containers and deploy on Azure Kubernetes Service (AKS). Budget $34,000, timeline 2 months.",
        "We need cloud infrastructure automated with Ansible and Terraform for hybrid cloud deployment spanning on-prem vSphere and AWS. Budget $28,000, timeline 2 months.",
        "Looking to set up a centralized secret management system with HashiCorp Vault, dynamic database credentials, and auto-rotation. Budget $22,000, timeline 6 weeks.",
        "Need to architect a high-throughput streaming data infrastructure with Apache Kafka on AWS MSK processing 50,000 events/sec. Budget $32,000, timeline 2 months.",
        "We need a serverless backend architecture migration using AWS Lambda, API Gateway, DynamoDB, and EventBridge to handle traffic spikes. Budget $25,000, timeline 6 weeks.",
        "Looking for a penetration testing and cloud security posture management (CSPM) remediation across our Azure tenant. Budget $19,000, timeline 4 weeks.",
        "Need to implement automated backup verification and immutable storage buckets (WORM compliance) for medical data archives. Budget $17,000, timeline 3 weeks.",
        "We want to modernize our build pipelines by transitioning from Jenkins to GitHub Actions with self-hosted autoscaling runners. Budget $15,000, timeline 4 weeks.",
        "Looking for a cloud networking engineer to configure AWS Transit Gateway, Direct Connect to our data centers, and route tables. Budget $24,000, timeline 6 weeks.",
        "Need to optimize Elasticsearch cluster indexing performance and reduce memory pressure on our 10TB log cluster. Budget $14,000, timeline 3 weeks.",
        "We need a zero-trust network access (ZTNA) implementation replacing traditional VPNs using Cloudflare Zero Trust or Tailscale. Budget $18,000, timeline 1 month.",
        "Looking for assistance creating staging and ephemeral preview environments for every pull request on AWS EKS. Budget $20,000, timeline 5 weeks.",
        "Need to configure cross-cloud replication between AWS S3 and Google Cloud Storage for business continuity. Budget $13,000, timeline 3 weeks.",
        "We want to set up an automated SSL certificate lifecycle manager with Let's Encrypt and cert-manager on Kubernetes. Budget $8,000, timeline 2 weeks.",
        "Looking for cloud database performance tuning on MySQL 8.0 handling 10,000 queries/sec with high query latency. Budget $12,000, timeline 2 weeks.",
        "Need assistance building a multi-cloud disaster recovery strategy between GCP and AWS with automated DNS failover via Route 53. Budget $30,000, timeline 2 months.",
        "We want to implement infrastructure compliance-as-code using Open Policy Agent (OPA) and Conftest in our CI/CD pipelines. Budget $16,000, timeline 4 weeks.",
        "Looking to deploy a private container registry with Harbor, automated vulnerability scanning with Trivy, and image signing with Cosign. Budget $14,000, timeline 3 weeks.",
        "Need an audit of our AWS IAM permissions to remove wildcards, implement principle of least privilege, and enforce MFA. Budget $10,000, timeline 2 weeks.",
        "We want to deploy a high-availability Redis Sentinel cluster for session caching and pub/sub message brokering. Budget $12,000, timeline 3 weeks.",
        "Looking to set up GitOps workflows for deploying infrastructure using Terraform Cloud and GitHub Actions. Budget $17,000, timeline 4 weeks.",
        "Need cloud migration assistance for 100TB of multimedia files from local NAS storage to Amazon S3 Glacier Instant Retrieval. Budget $15,000, timeline 1 month.",
        "We want to configure automated blue-green database schema migrations with Liquibase integrated into Kubernetes deployments. Budget $18,000, timeline 5 weeks.",
        "Looking for an AWS Solutions Architect to review our architecture before a major national TV product launch. Budget $10,000, urgent in 1 week.",
        "Need to set up automated uptime monitoring and synthetic user transaction monitors with Datadog across global regions. Budget $11,000, timeline 3 weeks.",
        "We want to migrate from self-hosted RabbitMQ to AWS SQS/SNS to reduce operational maintenance overhead. Budget $14,000, timeline 4 weeks.",
        "Looking to automate our end-to-end release process with automated semantic versioning, changelog generation, and tag releases. Budget $9,000, timeline 2 weeks."
    ],
    "Business Automation": [
        "We spend 40 hours a week manually copying invoice data from incoming supplier PDFs into QuickBooks and SAP. We need an automated intelligent document processing (IDP) workflow that extracts line items, validates totals, and automatically pushes to SAP. Budget $25,000, timeline 6 weeks.",
        "Looking for business automation to sync customer order updates between Shopify, Salesforce, and our warehouse 3PL inventory system. We want to eliminate manual entry errors. Budget $18,000, timeline 1 month.",
        "We need an automated employee onboarding and offboarding workflow that provisions Google Workspace, Slack, Jira, and GitHub accounts based on HR BambooHR triggers. Budget $15,000, timeline 4 weeks.",
        "Need a custom workflow automation using Make or n8n to capture leads from Facebook Ads, qualify them via SMS questionnaire, and route to sales reps. Budget $12,000, timeline 3 weeks.",
        "We want an automated contract review and approval workflow inside DocuSign and Slack with automatic CRM status updates. Budget $16,000, timeline 4 weeks.",
        "Looking to automate our monthly financial reconciliation process across Stripe, PayPal, Wise, and zero bank accounts. Budget $22,000, timeline 6 weeks.",
        "Need an RPA (Robotic Process Automation) bot to log into 8 state licensing portals daily, download renewal status reports, and notify compliance officers. Budget $28,000, timeline 8 weeks.",
        "We want automated email routing and ticket triage for our customer support inbox using AI classification to tag priority and assign agents. Budget $14,000, timeline 1 month.",
        "Looking to automate inventory reorder alerts and purchase order generation when stock levels drop below dynamic safety thresholds. Budget $16,000, timeline 4 weeks.",
        "Need an automated client reporting pipeline that pulls Google Analytics, Google Ads, and Meta Ads into weekly branded PDF client reports. Budget $13,000, timeline 3 weeks.",
        "We want an automated cold outbound email personalization engine that researches prospective companies and drafts contextual emails. Budget $17,000, timeline 4 weeks.",
        "Looking to automate our medical lab test result distribution via secure SMS links and automated reminder calls. Budget $24,000, timeline 2 months.",
        "Need automated data extraction from scanned real estate title deeds and property tax assessments into our legal case management system. Budget $20,000, timeline 6 weeks.",
        "We want to automate the supplier qualification process including document collection, credit score checks, and compliance approval checklists. Budget $19,000, timeline 5 weeks.",
        "Looking for an automated meeting scheduling and transcription pipeline that generates executive summaries and assigns action items in Asana. Budget $15,000, timeline 4 weeks.",
        "Need to automate our customer churn intervention workflow: when user engagement drops by 50%, trigger custom re-engagement email sequence and alert CSM. Budget $11,000, timeline 3 weeks.",
        "We want an automated hotel booking cancellation and refund management workflow between our booking engine and payment gateway. Budget $18,000, timeline 6 weeks.",
        "Looking to automate our warehouse return processing (RMA): scanning return labels, inspecting condition notes, and issuing store credit. Budget $21,000, timeline 8 weeks.",
        "Need an automated social media publishing workflow that cross-posts blog articles, creates teaser graphics, and schedules across 5 platforms. Budget $10,000, timeline 3 weeks.",
        "We want automated vendor invoice approval routing based on expense threshold rules and department budgets inside Microsoft Teams. Budget $14,000, timeline 4 weeks.",
        "Looking to automate client onboarding KYC checks: collecting ID photos, running verification APIs, and updating CRM records. Budget $26,000, timeline 2 months.",
        "Need an automated competitor price tracking scraper that alerts merchandisers when competitors discount identical products. Budget $15,000, timeline 4 weeks.",
        "We want an automated job applicant screening pipeline that filters resumes, schedules screening calls, and logs recruiter notes in Greenhouse. Budget $18,000, timeline 5 weeks.",
        "Looking for automated fleet vehicle maintenance scheduling based on GPS odometer readings and maintenance service intervals. Budget $17,000, timeline 6 weeks.",
        "Need to automate warranty claims processing: verifying purchase receipts, validating warranty coverage periods, and dispatching replacement units. Budget $23,000, timeline 2 months.",
        "We want an automated sales commission calculation engine that ingests Salesforce closed-won deals and calculates split commissions. Budget $16,000, timeline 4 weeks.",
        "Looking to automate customer address validation and delivery route clustering for our local grocery delivery business. Budget $14,000, timeline 1 month.",
        "Need an automated patient prescription refill request workflow connecting pharmacy faxes to the clinical triage queue. Budget $22,000, timeline 6 weeks.",
        "We want an automated digital rights management (DRM) licensing report generator for royalty payouts to music artists. Budget $20,000, timeline 2 months.",
        "Looking to automate lead enrichment: whenever a new lead fills a form, enrich with Clearbit data, company revenue, and employee count. Budget $12,000, timeline 3 weeks.",
        "Need an automated NDA generator that creates custom non-disclosure agreements from Google Form submissions and sends for signature. Budget $8,000, timeline 2 weeks.",
        "We want automated daily currency exchange rate updates pushed to our ERP pricing tables at 6 AM every morning. Budget $7,000, timeline 2 weeks.",
        "Looking to automate loan document collection with automated SMS reminders to borrowers for missing W2 and tax documents. Budget $19,000, timeline 6 weeks.",
        "Need an automated review collection workflow: sending SMS review requests 2 days after completed plumbing service and routing negative reviews to manager. Budget $9,000, timeline 2 weeks.",
        "We want an automated event attendee badge printing kiosk system linked to Eventbrite ticket registrations. Budget $15,000, timeline 4 weeks.",
        "Looking to automate customer refund requests according to 30-day policy rules and notify accounting via Slack. Budget $11,000, timeline 3 weeks.",
        "Need an automated compliance audit checklist that checks employee security training completions and notifies department heads. Budget $13,000, timeline 3 weeks.",
        "We want an automated system to backup critical client database snapshots to cold storage daily with Slack confirmation pings. Budget $10,000, timeline 2 weeks.",
        "Looking to automate trade show lead capture: scanning paper business cards at our booth and pushing contacts directly to HubSpot. Budget $12,000, timeline 3 weeks.",
        "Need automated translation of customer support tickets submitted in Spanish, French, and German into English for our support team. Budget $14,000, timeline 4 weeks."
    ],
    "Other": [
        "We are looking for general software consulting to evaluate our legacy tech stack and provide an independent architectural audit. No immediate coding, just advisory. Budget $8,000, timeline 3 weeks.",
        "Hello, we would like to know your general pricing for software development services and if you offer dedicated staffing models.",
        "Can you send us your company brochure and case studies? We are preparing our vendor shortlist for next year's RFP.",
        "We need a graphic design and branding package including brand guidelines, typography, color palettes, and presentation decks. Budget $6,000, timeline 4 weeks.",
        "Looking for technical writer to document our REST APIs and write comprehensive developer onboarding guides. Budget $7,500, timeline 1 month.",
        "We want to conduct a cybersecurity vulnerability assessment and penetration test on our internal office network. Budget $12,000, timeline 2 weeks.",
        "Hello team, do you have experience working with startups in the blockchain and Web3 domain? We want to discuss potential synergy.",
        "We need UX research and user usability testing sessions with 20 real users to evaluate our prototype. Budget $9,000, timeline 3 weeks.",
        "Looking for a consultant to help us define our 3-year digital transformation roadmap and IT budget allocation. Budget $15,000, timeline 6 weeks.",
        "Do you provide 24/7 technical support and maintenance contracts for enterprise applications that your team didn't build?",
        "We are looking for IT asset management and procurement guidance for 200 new remote employees laptops and software licenses.",
        "Can you help us migrate our emails and files from Google Workspace to Microsoft 365? Budget $5,000, timeline 2 weeks.",
        "Hi, I am looking for an internship or job opportunity at Cynbit Technologies in software development.",
        "We need assistance setting up our office networking, firewall hardware, and employee VPN infrastructure. Budget $7,000, timeline 2 weeks.",
        "Looking for a legal compliance consultant regarding GDPR and CCPA privacy policy requirements for our mobile application.",
        "We want to purchase existing software licenses or white-label solutions you might already have available.",
        "Is Cynbit available for a 30-minute introductory call to explore potential partnership opportunities?",
        "We need a trademark search and intellectual property strategy review for our new software brand name.",
        "Looking for a keynote speaker or panelist on emerging technology trends for our upcoming regional business tech conference.",
        "Can you provide quality assurance (QA) manual testing services for our existing web application before our next release? Budget $5,000, timeline 2 weeks.",
        "We need an independent valuation of our software intellectual property for an upcoming venture capital funding round.",
        "General inquiry regarding your hourly rates for senior engineering resources across different technology stacks.",
        "Looking for professional video production and animation explaining our B2B software product value proposition. Budget $8,000, timeline 4 weeks.",
        "Do you offer corporate training workshops for our in-house engineering team on clean architecture and microservices? Budget $6,000.",
        "We want an expert witness in a software copyright litigation matter to review code repositories and provide written deposition.",
        "Hi there, could you please remove our email address from your mailing list? Thank you.",
        "Looking for physical server colocation advice and data center migration planning. Budget $10,000, timeline 1 month.",
        "We need a freelance copywriter to write 10 technical SEO blog articles on AI and cloud computing. Budget $3,000, timeline 3 weeks.",
        "Looking to benchmark our customer support response times against global software industry standards.",
        "Can you help us setup Jira and Confluence project management workflows for an Agile engineering team of 25 people? Budget $4,500.",
        "We need a security awareness phishing simulation campaign conducted for our 500 company employees. Budget $6,000, timeline 3 weeks.",
        "Just wanted to congratulate your team on the recent product launch! Would love to connect on LinkedIn.",
        "Looking for translation and certified notarization of our software master service agreement into Japanese.",
        "We are evaluating software escrow services and want to know if Cynbit supports tripartite escrow agreements.",
        "Do you sponsor local tech hackathons and student developer community conferences?",
        "We need a UX audit of our checkout flow to identify why users are abandoning carts during payment. Budget $5,000, timeline 2 weeks.",
        "Looking for advice on open-source licensing compliance (GPL vs Apache vs MIT) for a commercial product.",
        "Can you provide a certificate of insurance (COI) and vendor onboarding documentation for your agency?",
        "We are looking to outsource customer support chat agents for weekend coverage. Do you provide staff augmentation?",
        "General inquiry about Cynbit's service level agreements (SLA) and incident response guarantees."
    ]
}

def generate_training_data():
    """Generates the labeled text dataset for ML model training and evaluation."""
    records = []
    for cat, inquiries in INQUIRIES_DATA.items():
        for text in inquiries:
            records.append({
                "inquiry_text": text,
                "category": cat
            })
    
    df = pd.DataFrame(records)
    # Shuffle
    df = df.sample(frac=1.0, random_state=42).reset_index(drop=True)
    out_path = os.path.join("data", "training_leads.csv")
    df.to_csv(out_path, index=False)
    print(f"Generated {len(df)} training records -> {out_path}")
    print(df["category"].value_counts())
    return df

def generate_sample_leads():
    """Generates 50 pre-populated realistic leads for the CRM database and analytics."""
    companies = [
        ("Aura Health Inc.", "Sarah Jenkins", "s.jenkins@aurahealth.io"),
        ("Apex Logistics Global", "Marcus Vance", "marcus.v@apexlogistics.com"),
        ("FinVanguard Partners", "Elena Rostova", "erostova@finvanguard.com"),
        ("Nova Retail Group", "David Chen", "dchen@novaretail.com"),
        ("Nexus Cyber Solutions", "Priya Sharma", "priya@nexuscyber.net"),
        ("BioSynth Labs", "Dr. Robert Langley", "rlangley@biosynthlabs.org"),
        ("Kite Financial", "Liam O'Connor", "liam@kitefin.co"),
        ("UrbanNest Properties", "Chloe Dupont", "chloe@urbannest.com"),
        ("OmniStream Media", "Julian Hayes", "julian@omnistream.tv"),
        ("Stratum Manufacturing", "Hans Gruber", "hgruber@stratum-mfg.de"),
        ("ClearPath Mobility", "Tara Patel", "tara@clearpath.io"),
        ("Synapse EdTech", "Kevin Miller", "kevin@synapse-ed.com"),
        ("Veritas Legal Tech", "Rachel Adams", "r.adams@veritaslegal.com"),
        ("Pulse Fitness Systems", "Brad Cooper", "bcooper@pulsefit.com"),
        ("Zenith Cloud Ops", "Fatima Al-Mansoor", "fatima@zenithops.ae"),
        ("Hyperion Dynamics", "Arthur Pendelton", "arthur@hyperiondyn.com"),
        ("SwiftCargo Express", "Carlos Mendez", "cmendez@swiftcargo.mx"),
        ("GreenGrid Energy", "Ingrid Lindholm", "ilindholm@greengrid.se"),
        ("Beacon Hospitality", "Anthony Rossi", "arossi@beaconhotels.com"),
        ("Quantum Horizon AI", "Siddharth Rao", "srao@quantumhorizon.ai"),
        ("Starlight E-Commerce", "Emily Watson", "emily@starlightstore.com"),
        ("Vanguard Robotics", "Viktor Petrov", "vpetrov@vanguardrobotics.com"),
        ("BlueSky Insurance", "Hannah Schmidt", "hannah@blueskyins.com"),
        ("Crestview Capital", "Jonathan Sterling", "jsterling@crestviewcap.com"),
        ("Acrobat Creative Agency", "Mia Thorne", "mia@acrobatcreative.com")
    ]
    
    statuses = ["New", "Contacted", "Qualified", "Proposal Sent", "Negotiation", "Closed-Won", "Closed-Lost"]
    status_weights = [0.20, 0.22, 0.18, 0.16, 0.10, 0.08, 0.06]
    
    records = []
    base_date = datetime.now() - timedelta(days=60)
    
    lead_idx = 1
    # Sample from each category to ensure balanced historical leads
    for cat, inquiries in INQUIRIES_DATA.items():
        sample_inquiries = inquiries[:8]  # 8 per category = 48 leads
        for inq in sample_inquiries:
            comp_idx = (lead_idx - 1) % len(companies)
            comp_name, client_name, client_email = companies[comp_idx]
            
            # Extract synthetic details
            created_at = base_date + timedelta(days=random.randint(1, 58), hours=random.randint(1, 23))
            lead_id = f"CYN-2026-{lead_idx:03d}"
            
            # Determine score, priority, budget from text or heuristics
            if cat == "AI/ML Development":
                budget_est = random.choice([35000, 45000, 55000, 65000, 40000])
                budget_raw = f"${budget_est:,}"
                urgency = random.choice(["High", "High", "Medium"])
                timeline_raw = random.choice(["6 weeks", "8 weeks", "2 months", "1 month"])
                score = random.randint(78, 96)
                priority = "Hot"
                intent = "New Product Development"
            elif cat == "Cloud & DevOps":
                budget_est = random.choice([25000, 30000, 35000, 20000])
                budget_raw = f"${budget_est:,}"
                urgency = random.choice(["High", "Medium"])
                timeline_raw = random.choice(["1 month", "6 weeks", "2 months"])
                score = random.randint(72, 89)
                priority = "Hot" if score >= 75 else "Warm"
                intent = "Infrastructure Modernization"
            elif cat == "Business Automation":
                budget_est = random.choice([18000, 25000, 22000, 15000])
                budget_raw = f"${budget_est:,}"
                urgency = random.choice(["Medium", "High"])
                timeline_raw = random.choice(["4 weeks", "6 weeks", "1 month"])
                score = random.randint(68, 84)
                priority = "Hot" if score >= 75 else "Warm"
                intent = "Process Automation & Integration"
            elif cat == "Web Development":
                budget_est = random.choice([15000, 25000, 30000, 18000, 12000])
                budget_raw = f"${budget_est:,}"
                urgency = random.choice(["Medium", "Low"])
                timeline_raw = random.choice(["2 months", "3 months", "8 weeks"])
                score = random.randint(55, 76)
                priority = "Warm" if score >= 50 else "Cold"
                if score >= 75: priority = "Hot"
                intent = "Web Platform Engineering"
            elif cat == "Mobile App Development":
                budget_est = random.choice([25000, 35000, 40000, 30000])
                budget_raw = f"${budget_est:,}"
                urgency = random.choice(["Medium", "Low"])
                timeline_raw = random.choice(["3 months", "4 months", "10 weeks"])
                score = random.randint(62, 82)
                priority = "Warm" if score < 75 else "Hot"
                intent = "Mobile Application Development"
            else: # Other
                budget_est = random.choice([5000, 8000, 10000, None])
                budget_raw = f"${budget_est:,}" if budget_est else "Unspecified"
                urgency = random.choice(["Low", "Low", "Medium"])
                timeline_raw = random.choice(["Flexible", "3 weeks", "Unspecified"])
                score = random.randint(25, 48)
                priority = "Cold"
                intent = "Consulting & General Inquiries"

            status = random.choices(statuses, weights=status_weights)[0]
            
            records.append({
                "lead_id": lead_id,
                "created_at": created_at.strftime("%Y-%m-%d %H:%M:%S"),
                "client_name": client_name,
                "client_email": client_email,
                "client_company": comp_name,
                "inquiry_text": inq,
                "service_category": cat,
                "category_confidence": round(random.uniform(0.85, 0.98), 3),
                "customer_intent": intent,
                "extracted_requirements": f"Key Requirements: Domain-tailored requirements for {cat}; scalable solution architecture.",
                "budget_estimated": budget_est if budget_est else 0.0,
                "budget_raw": budget_raw,
                "timeline_raw": timeline_raw,
                "urgency_level": urgency,
                "score": score,
                "priority": priority,
                "status": status,
                "notes": f"Historical lead imported from CRM logs. Handled by Cynbit Account Exec."
            })
            lead_idx += 1
            
    df_sample = pd.DataFrame(records)
    out_sample = os.path.join("data", "sample_leads.csv")
    df_sample.to_csv(out_sample, index=False)
    print(f"Generated {len(df_sample)} sample historical leads -> {out_sample}")
    print(df_sample["priority"].value_counts())
    return df_sample

if __name__ == "__main__":
    generate_training_data()
    generate_sample_leads()
