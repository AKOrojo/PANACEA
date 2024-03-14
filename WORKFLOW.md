# Research Project Workflow Documentation

This document outlines the data flow and code structure for a research project evaluating access control in NoSQL databases, specifically using MongoDB. Below is a detailed breakdown of each component involved in the project.

## 1. Database Connection

- **File**: `/src/database_interaction/mongo_connection.py`
- **Purpose**: Establishes a connection to MongoDB and provides a method to fetch data.
- **Implementation Detail**:
  - Utilizes `pymongo` to connect to the MongoDB instance.
  - Includes a function to connect to the `enron` database and the `messages` collection.

## 2. Data Preparation

- **File**: `src/database_interaction/data_preparation.py`
- **Purpose**: Prepares data for MapReduce processing, which may include cleaning or transforming data as necessary.
- **Implementation Detail**:
  - Queries the `messages` collection to retrieve relevant data.
  - Implements any necessary preprocessing steps, such as filtering or transformation.

## 3. Unifying Model

- **Mapping**:
  - File: `src/unifying_model/mapper.py`
  - Purpose: Maps the original data model to a unifying model that standardizes data for processing.
- **Reducing**:
  - File: `src/unifying_model/reducer.py`
  - Purpose: Aggregates data according to the unifying model, potentially summing or averaging fields.

## 4. Policy Specification and Evaluation

- **Specification**:
  - File: `src/policy/specification.py`
  - Purpose: Specifies access control policies and binds these policies to the unified data models.
- **Evaluation**:
  - File: `src/policy/evaluation.py`
  - Purpose: Evaluates policies against data to determine access rights, modifications, etc.

## 5. View Generation

- **Mapping Back**:
  - File: `src/view_generation/mapper.py`
  - Purpose: Maps data from the unified model back to native models or views tailored to specific needs.
- **Reducer**:
  - File: `src/view_generation/reducer.py`
  - Purpose: Further processes mapped data to finalize the views.
- **Projector**:
  - File: `src/view_generation/projector.py`
  - Purpose: Projects the final views based on policy evaluations, generating the output for users or systems.

## 6. Main Script

- **File**: `/src/main.py`
- **Overview**: Orchestrates the entire process, from database connection, data preparation, applying the unifying model, evaluating policies, and generating views.
- **Example flow**:
  1. Connect to MongoDB and fetch data.
  2. Prepare data for processing.
  3. Apply the unifying model (map and reduce).
  4. Specify and evaluate policies.
  5. Generate views based on the policy evaluations.
  6. Output the final views to `data/output`.

## 7. Testing and Dependencies

- **Testing**:
  - Implement tests in `tests/test_cases.py` to ensure each component behaves as expected.
- **Dependencies**:
  - Ensure all dependencies are listed in `requirements.txt` and installed in your environment. This likely includes `pymongo` for MongoDB interaction, and possibly other libraries for data processing and testing.
