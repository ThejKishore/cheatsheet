# 🛠️ Java Spring Boot Developer Task: Merge Microservices into a Modular Monolith

## 🎯 Objective

You are required to merge multiple existing **microservices** into a **modular monolith** using **Java** and **Spring Boot**.

---

## ✅ Goals

1. **Consolidate** all services into a **single codebase**, preserving modularity through clean package structures or module systems.
2. Represent each former microservice as an **independent module** or package with **clear API boundaries**.
3. Extract shared functionality (e.g., utilities, logging, security) into **shared/common modules**.
4. Ensure **loose coupling** by using service interfaces or in-process events for inter-module communication.

---

## 🧱 Technical Requirements

- Use **Spring Boot** (v3.x preferred).
- Retain existing **business logic** and **database schemas**.
- Replace inter-service **REST/gRPC calls** with **direct method calls** or **event-based communication** within the same process.
- Maintain **testability** — preferably with **separate test suites** for each module.
- Use **Maven/Gradle multi-module** structure (preferred) or structured packages for modular separation.
- Apply **Domain-Driven Design (DDD)** principles where possible (e.g., using bounded contexts).

---

## 📦 Deliverables

- A fully functional **modular monolith** application.
- Updated **README.md** with:
  - Architecture overview
  - Setup instructions
- Documentation showing:
  - Mapping from individual microservices to monolith modules
- Sample **unit/integration tests** showcasing inter-module interactions.

---

## ✨ Optional Enhancements

- Implement a **feature toggle sys**
